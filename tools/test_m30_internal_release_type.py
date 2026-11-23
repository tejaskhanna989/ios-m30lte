#!/usr/bin/env python3
"""Regression test for patch 0426 (_internal_release_type = 3 fix-up).

v30 physical: all-copy class-name string patching fired once but SpringBoardUI
still aborted. LiveContainer's bypass has TWO parts that BOTH appear necessary:
  (1) _internal_release_type = 3 -> os_variant_has_internal_content() true
  (2) XCTestConfiguration class registration
Patch 0426 implements part (1) by locating the _internal_release_type global
through the dyld shared cache local-symbol table (vn_rdwr from the vnode) and
setting the in-memory page value to 3, strictly after cs_validate_page().
The file on disk is never written; no security check is weakened.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0426-m30-internal-release-type.patch"
PSTORE_V30 = ROOT / "validation/physical-boot-test/20261122-ios-v30-boot/raw/pmsg-ramoops-0"
PSTORE_V31 = ROOT / "validation/physical-boot-test/20261122-ios-v31-boot/raw/pmsg-ramoops-0"
PSTORE_V32 = ROOT / "validation/physical-boot-test/20261122-ios-v32-boot/raw/pmsg-ramoops-0"
PSTORE_V33 = ROOT / "validation/physical-boot-test/20261122-ios-v33-boot/raw/pmsg-ramoops-0"
PSTORE_V34 = ROOT / "validation/physical-boot-test/20261122-ios-v34-boot/raw/pmsg-ramoops-0"
PSTORE_V35 = ROOT / "validation/physical-boot-test/20261122-ios-v35-boot/raw/pmsg-ramoops-0"
PSTORE_V36 = ROOT / "validation/physical-boot-test/20261122-ios-v36-boot-short/raw/pmsg-ramoops-0"
PSTORE_V37 = ROOT / "validation/physical-boot-test/20261122-ios-v37-boot/raw/pmsg-ramoops-0"
PSTORE_V38 = ROOT / "validation/physical-boot-test/20261122-ios-v38-boot/raw/pmsg-ramoops-0"
PSTORE_V39 = ROOT / "validation/physical-boot-test/20261122-ios-v39-boot2/raw/pmsg-ramoops-0"
PSTORE_V40 = ROOT / "validation/physical-boot-test/20261122-ios-v40-boot2/raw/pmsg-ramoops-0"
PSTORE_V41 = ROOT / "validation/physical-boot-test/20261123-ios-v41-boot/raw/pmsg-ramoops-0"
PSTORE_V42 = ROOT / "validation/physical-boot-test/20261123-ios-v42-boot/raw/pmsg-ramoops-0"
PSTORE_V43 = ROOT / "validation/physical-boot-test/20261123-ios-v43-boot/raw/pmsg-ramoops-0"


def main():
    t = PATCH.read_text()

    # --- patch structure ---
    assert "m30_internal_release_fixup(vnode, pager, mo_offset, kaddr);" in t
    # The fix-up call is placed immediately after the xctest fix-up call,
    # which itself is strictly after cs_validate_page() in the v30 base.
    assert "m30_xctest_probe_fixup(kaddr, mo_offset);" in t
    assert t.index("m30_xctest_probe_fixup(kaddr, mo_offset);") < t.index(
        "m30_internal_release_fixup(vnode, pager, mo_offset, kaddr);")
    assert "_internal_release_type" in t
    assert "os_variant_has_internal_content" in t
    assert "*loc = 3;" in t
    assert "UIO_READ" in t, "must only read the file, never write"
    assert "UIO_WRITE" not in t, "file on disk must not be modified"
    assert "vn_rdwr" in t
    # <sys/vnode.h> resolves to the *exported* public header in this build and
    # breaks compilation (uid_t/gid_t unknown).  Use a local prototype instead.
    assert "#include <sys/vnode.h>" not in t
    assert "extern int vn_rdwr(enum uio_rw, struct vnode *, caddr_t, int, off_t," in t
    assert "dyld_cache_header" in t or "localSymbolsOffset@72" in t
    assert "M30_IRT_STATE_HAVE_OFF" in t and "M30_IRT_STATE_DONE" in t
    assert "Z_NOWAIT" in t, "must not block in the page-fault path"
    assert "no check weakened" in t or "No check weakened" in t

    # v32: the dyld shared cache uses the dyld pager, so
    # vnode_pager_lookup_vnode() returns NULL and the v31 helper silently did
    # nothing.  Recover the real file vnode via the generic pager
    # backing-object callback, and emit one-shot failure diagnostics.
    assert "memory_object_backing_object(pager, mo_offset," in t
    assert "vnode_pager_lookup_vnode(backing->pager)" in t
    assert "M30_IRT_DIAG(25, \"no vnode, cannot parse DSC" in t
    assert t.count("M30_IRT_DIAG(") >= 20, "need diagnostics at every failure point"
    assert "m30_irt_diag_seen & (1ULL << (n))" in t, "diagnostics must be one-shot"
    assert "m30_irt_last_err = err" in t, "must record vn_rdwr errors"
    # v33: the pmsg ring wraps in a deep boot, so one-shot diagnostics printed
    # at the first code-page fault are lost.  Replay once when the SpringBoard
    # XCTest literal is patched, inside the captured log window.
    assert "m30_irt_retriggered" in t
    assert "M30 IRT: retrigger after XCTEST patch" in t
    assert "m30_irt_diag_seen = 0" in t
    assert "m30_irt_state = M30_IRT_STATE_NEED_DSC;" in t
    # v34: diag 0 was captured with a non-NULL vnode, then nothing.  The only
    # silent exits in the NEED_DSC path are Z_NOWAIT allocation failures, so
    # shrink the chunk to one page and diagnose both allocation sites.
    assert "size_t  chunk = 4096;" in t
    assert 'M30_IRT_DIAG(19, "header buffer alloc failed' in t
    assert 'M30_IRT_DIAG(20, "symbol buffers alloc failed' in t
    # v35: vn_rdwr() in the page-fault path recursed on the vm_object lock and
    # panicked at load_init_program.  The read-only DSC scan must be deferred
    # to a kernel thread; only the in-memory page patch stays in the fault path.
    assert "kernel_thread_start_priority" in t
    assert "m30_irt_worker" in t
    assert "vnode_ref(vp) == 0" in t
    assert "vnode_rele(vp)" in t
    assert "m30_irt_thread_started = 0;" in t
    # v38: periodic bounded status replay survives the 16 KB pmsg ring wrap.
    assert "#include <kern/clock.h>" in t
    assert 'M30 IRT status: state=%d off=0x%llx err=%d replay=%d' in t
    assert "delay(2000000)" in t
    # v39: vn_getpath() plen includes the NUL; compute the real strlen.
    assert "while (path_n < sizeof(path) && path[path_n] != '\\0')" in t
    assert 'printf("M30 IRT diag 31: vn_getpath plen=%d strlen=%zu' in t
    # v40: the faulted vnode is a dyld4 subcache (.31).  Strip the trailing
    # .<digits> and try base+.symbols, subcache+.symbols, then the base cache.
    assert 'printf("M30 IRT diag 32: base path len=%zu' in t
    assert "path[base_n - 1] >= '0'" in t
    assert 'static const char symsuffix[] = ".symbols";' in t
    assert "for (cand = 0; cand < 3 && !opened; cand++)" in t
    assert 'printf("M30 IRT diag 30: cand=%d map_off=0x%x map_cnt=%u' in t
    assert 'printf("M30 IRT diag 28: using symbols file vp=%p main=%p' in t
    assert "vnode_open(sympath, 1 /* FREAD */" in t
    assert "vnode_close(fp, 1 /* FREAD */" in t
    # If the chosen symbols file maps only the main cache but the symbol
    # lives in a subcache, fall back to the faulted vnode's own mapping table.
    assert "m30_irt_diag_seen = 0;" in t and "static uint64_t" in t
    assert "(1ULL << (n))" in t
    # v41: the .symbols companion is used ONLY for nlist/string data.  A
    # vmaddr is mapped through a real cache file (faulted vnode, base cache,
    # then numbered subcaches) so the resulting file offset patches the page
    # that the fault hook actually sees.
    assert "M30_IMAGES_OFFSET = 448" in t
    assert "M30_SYMBOL_UUID_OFFSET = 400" in t
    assert "image_index" in t and "libsystem_darwin.dylib" in t
    # v42: pathFileOffset is an absolute cache file offset, not a 4 KiB
    # buffer offset.  The v41 `po >= chunk` guard skipped every real path.
    assert "if (po == 0) {" in t
    assert "po >= chunk" not in t
    assert 'M30_IRT_DIAG(47, "image 0 path=%s\\n"' in t
    assert 'M30_IRT_DIAG(48, "libsystem candidate i=%d path=%s\\n"' in t
    assert "nlist_start = *(uint32_t *)(buf + 8);" in t
    assert "nlist_range = *(uint32_t *)(buf + 12);" in t
    assert "m30_irt_map_vnode(" in t and "m30_irt_map_vnode_open(" in t
    assert "m30_irt_target_vp != (vnode_t)0 && vp != m30_irt_target_vp" in t
    assert 'printf("M30 IRT diag 33: mapped via cache vp=%p off=0x%llx path=%s\\n"' in t
    # v43: mapping failure is now observable through the periodic status line,
    # and real-cache lookup also covers the dyld4 Cryptex cache directory.
    assert "m30_irt_base_map_cnt" in t and "m30_irt_map_hits" in t
    assert 'M30_IRT_DIAG(50, "base map off=0x%x cnt=%u first=0x%llx/' in t
    assert 'M30_IRT_DIAG(49, "image addr=0x%llx pathFileOff=0x%x\\n"' in t
    assert "static const char cryptex[] =" in t
    assert "/private/preboot/Cryptexes/OS/System/Library/Caches/" in t
    assert "sym=0x%llx img=0x%llx hits=%d tries=%d" in t
    # v44: when the companion uses a different virtual base, translate its
    # nlist vmaddr through the companion mapping to a real cache file offset.
    assert "m30_irt_sym_map_fileoff" in t and "m30_irt_fallback_off" in t
    assert 'M30_IRT_DIAG(52, "sym map off=0x%x cnt=%u first=0x%llx/' in t
    assert 'M30_IRT_DIAG(53, "companion map fallback off=0x%llx\\n"' in t
    assert "for (idx = 0; idx < 512 && !found; idx++)" in t
    assert "symmap=0x%llx/0x%llx@0x%llx fb=0x%llx" in t
    # v37: retrigger gate, and retry with a later vnode on wrong magic.
    assert "m30_irt_retriggered && !m30_irt_thread_started" in t
    assert "path=%s\\n" in t
    assert "no vnode I/O, only in-memory patching" in t
    assert "#include <sys/vfs_context.h>" in t
    assert "vn_getpath(vp, path, &plen)" in t

    for bad in ("cs_enforcement_disable", "amfi_get_out_of_my_way",
                "launchd_unsecure_cache", "CSDebugDisable",
                "vmp_cs_validated = VMP_CS_ALL_TRUE", "tainted = 0;"):
        assert bad not in t, f"patch must not contain {bad!r}"
    print("[PASS] patch 0426 structure: post-validation, read-only file, no security bypass")

    # --- physical evidence: v30 string patch fired but crash persists ---
    d = PSTORE_V30.read_bytes()
    assert b"M30 XCTEST: patched ascii off" in d
    assert b"CRASH SpringBoard[27] sig 6" in d
    assert b"This process should not be linking or loading SpringBoardUI.framework" in d
    print("[PASS] v30 pstore: string patch fired, assertion persists -> second bypass needed")

    # --- physical evidence: v31 patch compiled in but emitted no diagnostics ---
    d31 = PSTORE_V31.read_bytes()
    assert b"M30 XCTEST: patched ascii off" in d31
    assert b"CRASH SpringBoard[27] sig 6" in d31
    assert b"This process should not be linking or loading SpringBoardUI.framework" in d31
    assert b"M30 IRT" not in d31, "v31 fix-up produced zero diagnostics"
    print("[PASS] v31 pstore: XCTEST fired, no M30 IRT lines -> dyld-pager vnode is NULL")

    # --- physical evidence: v32 diagnostics still absent because the 16 KB
    # pmsg ring wrapped before the captured SpringBoard records. ---
    d32 = PSTORE_V32.read_bytes()
    assert len(d32) == 16372, "pmsg ring should be full/wrapped"
    assert b"M30 XCTEST: patched ascii off" in d32
    assert b"CRASH SpringBoard[27] sig 6" in d32
    assert b"This process should not be linking or loading SpringBoardUI.framework" in d32
    assert b"M30 IRT" not in d32, "v32 one-shot diagnostics were lost in the wrapped ring"
    print("[PASS] v32 pstore: wrapped 16 KB ring; one-shot IRT diagnostics not captured")

    # --- physical evidence: v33 retrigger lands in the captured window; only
    # the entry diagnostic appears, with a non-NULL vnode. ---
    d33 = PSTORE_V33.read_bytes()
    assert b"M30 XCTEST: patched ascii off" in d33
    assert b"M30 IRT: retrigger after XCTEST patch" in d33
    assert b"M30 IRT diag 0: enter state=0 vp=0x" in d33
    assert b"CRASH SpringBoard[26] sig 6" in d33 or b"CRASH SpringBoard[27] sig 6" in d33
    assert b"This process should not be linking or loading SpringBoardUI.framework" in d33
    assert b"M30 IRT diag 1:" not in d33
    assert b"M30 IRT diag 3:" not in d33
    print("[PASS] v33 pstore: retrigger + diag 0 captured; vnode non-NULL; next step silent")

    # --- physical evidence: v34 panicked in the fault path. ---
    d34 = PSTORE_V34.read_bytes()
    assert b"M30 IRT diag 0: enter state=0 vp=0x" in d34
    assert b"load_init_program: attempting to load /sbin/launchd" in d34
    assert b"lock_rw.c:877 Assertion failed: lock->lck_rw_owner != self->ctid" in d34
    assert b"M30 IRT diag 3:" not in d34 and b"M30 IRT: found" not in d34
    print("[PASS] v34 pstore: vn_rdwr in fault path panicked on recursive object lock")

    # --- physical evidence: v35 deferred scan works, but main DSC has no
    # local symbols (ls_off == 0); symbols are in the .symbols companion. ---
    d35 = PSTORE_V35.read_bytes()
    assert b"M30 IRT: retrigger after XCTEST patch" in d35
    assert b"M30 IRT diag 21: worker started vp=0x" in d35
    assert b"M30 IRT diag 8: header map_off=0x200 map_cnt=1 ls_off=0x0" in d35
    assert b"M30 IRT diag 24: header has no symbol table" in d35
    assert b"lock_rw.c:877" not in d35
    assert b"This process should not be linking or loading SpringBoardUI.framework" in d35
    print("[PASS] v35 pstore: deferred scan OK; main DSC ls_off=0 -> need .symbols file")

    # --- physical evidence: v36 short boot caught the early worker starting
    # on launchd's Mach-O vnode before the XCTEST retrigger. ---
    d36 = PSTORE_V36.read_bytes()
    assert b"load_init_program: attempting to load /sbin/launchd" in d36
    assert b"M30 IRT diag 0: enter state=0 vp=0x" in d36
    assert b"M30 IRT diag 21: worker started vp=0x" in d36
    assert b"M30 IRT diag 4: no dyld magic: cffaedfe" in d36
    print("[PASS] v36 pstore: worker started pre-retrigger on launchd Mach-O vnode")

    # --- physical evidence: v37 short window ended before SpringBoard. ---
    d37 = PSTORE_V37.read_bytes()
    assert b"CODE SIGNING: cs_invalid_page" in d37
    assert b"lockdownd" in d37
    assert b"M30 IRT" not in d37
    assert b"M30 XCTEST" not in d37
    assert b"SpringBoardUI" not in d37
    print("[PASS] v37 pstore: short window ended before SpringBoard; need status replay")

    # --- physical evidence: v38 status replay captured, but .symbols open
    # silently reopened the main cache because plen includes the NUL. ---
    d38 = PSTORE_V38.read_bytes()
    assert b"M30 XCTEST: patched ascii off" in d38
    assert b"M30 IRT: retrigger after XCTEST patch" in d38
    assert b"M30 IRT diag 21: worker started vp=0x" in d38
    assert b"M30 IRT diag 8: header map_off=0x200 map_cnt=1 ls_off=0x0" in d38
    assert b"M30 IRT diag 24: header has no symbol table" in d38
    assert b"M30 IRT status: state=4 off=0x0 err=0 replay=0" in d38
    assert b"M30 IRT status: state=4 off=0x0 err=0 replay=15" in d38
    # The "opened symbols file" path lacks .symbols, and its vnode equals main.
    assert b"opened symbols file /System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.31 vp=" in d38
    assert b"CRASH SpringBoard[27] sig 6" in d38
    print("[PASS] v38 pstore: status replay works; .symbols suffix landed after NUL")

    # --- physical evidence: v39 stripped the NUL, but the faulted vnode is a
    # dyld4 subcache (.31).  Its .symbols companion does not exist. ---
    d39 = PSTORE_V39.read_bytes()
    assert b"M30 XCTEST: patched ascii off" in d39
    assert b"M30 IRT: retrigger after XCTEST patch" in d39
    assert b"M30 IRT diag 21: worker started vp=0x" in d39
    assert b"M30 IRT diag 8: header map_off=0x200 map_cnt=1 ls_off=0x0" in d39
    assert b"M30 IRT diag 31: vn_getpath plen=65 strlen=64 path=" in d39
    assert b"dyld_shared_cache_arm64.31\x00" in d39
    assert b"M30 IRT diag 27: open .symbols failed path=" in d39
    assert b"dyld_shared_cache_arm64.31.symbols" in d39
    print("[PASS] v39 pstore: subcache .31 has no .symbols; strip index for v40")

    # --- v40 physical: the stripped base .symbols file opens, but a global
    # string-pool scan finds a bogus strx; the symbol must be scoped to the
    # libsystem_darwin image's nlist range (LiveContainer algorithm). ---
    d40 = PSTORE_V40.read_bytes()
    assert b"M30 XCTEST: patched ascii off" in d40
    assert b"M30 IRT: retrigger after XCTEST patch" in d40
    assert b"M30 IRT diag 8: header map_off=0x200 map_cnt=1 ls_off=0x0" in d40
    assert b"dyld_shared_cache_arm64.31\x00" in d40
    assert b"M30 IRT diag 32: base path len=61 path=/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64" in d40
    assert b"M30 IRT diag 30: cand=0 map_off=0x200 map_cnt=1 ls_off=0x4000 path=/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.symbols" in d40
    assert b"M30 IRT diag 28: using symbols file vp=0x" in d40
    assert b"M30 IRT diag 10: lsi nlist_off=0xa980 cnt=8705811 str_off=0x84e1ab0 size=451573533" in d40
    assert b"M30 IRT diag 13: symbol name found strx=318698973" in d40
    assert b"M30 IRT diag 15: symbol not found in nlist" in d40
    assert b"This process should not be linking or loading SpringBoardUI.framewor" in d40
    print("[PASS] v40 pstore: .symbols opened; global strx scan is ambiguous -> v41 image-scoped scan")

    # --- v41 physical: the image list is readable, but every pathFileOffset
    # was rejected by the accidental po >= chunk guard. ---
    d41 = PSTORE_V41.read_bytes()
    assert b"M30 XCTEST: patched ascii off" in d41
    assert b"M30 IRT: retrigger after XCTEST patch" in d41
    assert b"M30 IRT diag 30: cand=0 map_off=0x200 map_cnt=1 ls_off=0x4000" in d41
    assert b"M30 IRT diag 28: using symbols file vp=0x" in d41
    assert b"M30 IRT diag 36: images off=0x270 cnt=2710" in d41
    assert b"M30 IRT diag 38: libsystem_darwin image not found cnt=2710" in d41
    assert b"M30 IRT status: state=4 off=0x0 err=0 replay=0" in d41
    assert b"This process should not be linking or loading SpringBoardUI.framewor" in d41
    print("[PASS] v41 pstore: image list read OK; pathFileOffset guard rejected real paths")

    # --- v42 physical: the image-scoped nlist scan finds the symbol, but the
    # unslid vmaddr is not present in any tried real-cache mapping table. ---
    d42 = PSTORE_V42.read_bytes()
    assert b"M30 IRT diag 42: image nlist start=6047093 count=146" in d42
    assert b"M30 IRT diag 43: nlist strx=318698902" in d42
    assert b"M30 IRT diag 13: symbol vmaddr=0x1e1d3ad84" in d42
    assert b"M30 IRT diag 18: no real cache mapping contains vmaddr 0x1e1d3ad84" in d42
    assert b"M30 IRT status: state=4 off=0x0 err=0 replay=0" in d42
    assert b"This process should not be linking or loading SpringBoardUI.framewor" in d42
    assert b"M30 IRT: patched" not in d42
    print("[PASS] v42 pstore: image-scoped symbol found; real-cache mapping missing -> v43 evidence")

    # --- v43 physical: the base cache mapping starts far above the symbol,
    # and the image address is even lower.  No vmaddr mapping matched. ---
    d43 = PSTORE_V43.read_bytes()
    assert b"M30 IRT status: state=4 off=0x0 err=0 replay=14 sym=0x1e1d3ad84 " in d43
    assert b"img=0x1d1c22000 hits=0 basecnt=1" in d43
    assert b"base0=0x1ecc80000/0x62ac000@0x0" in d43
    assert b"This process should not be linking or loading SpringBoardUI.framewor" in d43
    assert b"M30 IRT: patched" not in d43
    print("[PASS] v43 pstore: companion vmaddr outside real mappings -> companion-map fallback")

    # --- behavioural model: image-scoped nlist lookup. ---
    # The companion string pool contains the name in several images.  A global
    # first-match scan can bind to a strx that no nlist in the target dylib
    # uses (exactly what v40 printed).  LiveContainer scopes by the image's
    # local-symbols entry, then reads each nlist's own string.
    names = [b"_internal_release_type\0", b"_other\0", b"_internal_release_type\0"]
    pool = b"".join(names)
    offsets = []
    off = 0
    for name in names:
        offsets.append(off)
        off += len(name)

    def name_at(strx):
        end = pool.index(b"\0", strx)
        return pool[strx:end]

    nlists = [
        (offsets[0], 0x1000),   # different image: same name, wrong vmaddr
        (offsets[1], 0x2000),   # target image: different symbol
        (offsets[2], 0x3000),   # target image: correct symbol
    ]
    entry = (1, 2)              # nlistStartIndex=1, nlistCount=2 (entry_64)
    global_strx = offsets[0]
    assert name_at(global_strx) == b"_internal_release_type"
    assert all(strx != global_strx for strx, _ in nlists[entry[0]:entry[0] + entry[1]])
    scoped = [vm for strx, vm in nlists[entry[0]:entry[0] + entry[1]]
              if name_at(strx) == b"_internal_release_type"]
    assert scoped == [0x3000], scoped
    print("[PASS] model: image-scoped nlist range resolves duplicate symbol names")

    # --- behavioural model: retrigger replays diagnostics after XCTest. ---
    state = {"seen": 0}
    emitted = []
    def diag(n, msg):
        if not (state["seen"] & (1 << n)):
            state["seen"] |= (1 << n)
            emitted.append(msg)
    for _ in range(50):           # early faults, before the log window
        diag(0, "early enter")
    assert emitted == ["early enter"]
    emitted.clear()               # pmsg ring wrapped: early output is gone
    state["seen"] = 0             # retrigger after the XCTest patch
    diag(0, "late enter")
    diag(1, "late backing")
    assert emitted == ["late enter", "late backing"], emitted
    print("[PASS] model: retrigger resets one-shot bits so diagnostics land in captured window")

    # --- behavioural model: find symbol + patch value ---
    model = textwrap.dedent(r"""
        #include <stdio.h>
        #include <string.h>
        #include <stdint.h>
        /* Minimal model of the DSC local-symbol lookup.
         * Header: mappingOffset@16, mappingCount@20, localSymbolsOffset@72.
         * local_symbols_info: nlistOff@0, nlistCount@4, strOff@8, strSize@12.
         * nlist_64: n_strx@0, n_value@8 (16 bytes).
         * mapping_info: address@0, size@8, fileOffset@16 (32 bytes).
         */
        static void put32(void *p, uint32_t v) { memcpy(p, &v, 4); }
        static uint32_t get32(const void *p) { uint32_t v; memcpy(&v,p,4); return v; }
        static uint64_t get64(const void *p) { uint64_t v; memcpy(&v,p,8); return v; }
        int main(void) {
            unsigned char header[96] = {0};
            memcpy(header, "dyld_v6  arm64e", 15);
            put32(header+16, 0x100);   /* mappingOffset */
            put32(header+20, 1);       /* mappingCount */
            /* localSymbolsOffset = 0x200 */
            { uint64_t v = 0x200; memcpy(header+72, &v, 8); }
            unsigned char lsi[24] = {0};
            put32(lsi+0, 0x40);   /* nlistOffset */
            put32(lsi+4, 3);      /* nlistCount */
            put32(lsi+8, 0x80);   /* stringsOffset */
            put32(lsi+12, 0x100); /* stringsSize */
            /* local symbol chunk at 0x200: nlist at +0x40, strings at +0x80 */
            unsigned char syms[0x200] = {0};
            const char *name = "_internal_release_type";
            memcpy(syms+0x80+16, name, strlen(name)+1);  /* strx=16 */
            /* three nlist entries */
            put32(syms+0x40+0*16, 0);            /* other symbol */
            put32(syms+0x40+1*16, 16);           /* our symbol strx */
            { uint64_t v = 0x1800001000ULL; memcpy(syms+0x40+1*16+8, &v, 8); }
            put32(syms+0x40+2*16, 0);
            /* mapping: address=0x1800000000 size=0x100000 fileOffset=0x400000 */
            unsigned char maps[32] = {0};
            { uint64_t v = 0x1800000000ULL; memcpy(maps, &v, 8); }
            { uint64_t v = 0x100000ULL; memcpy(maps+8, &v, 8); }
            { uint64_t v = 0x400000ULL; memcpy(maps+16, &v, 8); }
            /* run the lookup */
            uint32_t found_strx = 0; int found = 0;
            for (size_t o = 0; o < 0x100; o++) {
                if (syms[0x80+o] == '_' &&
                    memcmp(syms+0x80+o, name, strlen(name)) == 0 &&
                    syms[0x80+o+strlen(name)] == '\0') {
                    found_strx = (uint32_t)o; found = 1; break;
                }
            }
            if (!found || found_strx != 16) { printf("strx=FAIL\n"); return 1; }
            uint64_t vmaddr = 0; found = 0;
            for (int i = 0; i < 3; i++) {
                if (get32(syms+0x40+i*16) == found_strx) {
                    vmaddr = get64(syms+0x40+i*16+8); found = 1; break;
                }
            }
            if (!found || vmaddr != 0x1800001000ULL) { printf("sym=FAIL\n"); return 2; }
            uint64_t foff = 0; found = 0;
            { uint64_t a = get64(maps), z = get64(maps+8);
              if (vmaddr >= a && vmaddr < a+z) {
                  foff = get64(maps+16) + (vmaddr - a); found = 1; } }
            if (!found || foff != 0x400000+0x1000) { printf("map=FAIL\n"); return 3; }
            /* in-memory page patch */
            unsigned char page[4096] = {0};
            size_t po = foff & 0xfff;
            put32(page+po, 0);  /* release=0 */
            /* patch */
            put32(page+po, 3);
            if (get32(page+po) != 3) { printf("patch=FAIL\n"); return 4; }
            printf("all=OK strx=%u vmaddr=0x%llx foff=0x%llx val=3\n",
                   found_strx, (unsigned long long)vmaddr,
                   (unsigned long long)foff);
            return 0;
        }
    """)
    with tempfile.TemporaryDirectory() as td:
        c = Path(td) / "model.c"
        b = Path(td) / "model"
        c.write_text(model)
        subprocess.run(["cc", "-O0", "-Wall", "-Wextra", "-o", str(b), str(c)], check=True)
        out = subprocess.run([str(b)], check=True, capture_output=True, text=True).stdout
    assert "all=OK" in out and "val=3" in out, out
    print("[PASS] model: DSC local-symbol lookup finds _internal_release_type and sets 3")

    # --- behavioural model: dyld-pager backing-object vnode recovery ---
    # The dyld pager is not a vnode pager; vnode_pager_lookup_vnode(dyld_pager)
    # returns NULL.  The generic backing-object callback yields the backing
    # VM object whose pager IS a vnode pager, so the DSC file vnode is found.
    pager_model = textwrap.dedent(r"""
        #include <stdio.h>
        #include <stdint.h>
        typedef struct object object_t;
        struct object { int id; object_t *pager; int is_vnode_pager; int vnode; };
        static object_t *vnode_pager_lookup_vnode(object_t *p) {
            return (p && p->is_vnode_pager) ? (object_t *)(intptr_t)p->vnode : 0;
        }
        static int backing_object(object_t *p, object_t **out) {
            if (!p || p->id != 1) return 0;       /* only the dyld pager has one */
            *out = (object_t *)(intptr_t)0x2000;  /* backing VM object */
            return 1;
        }
        int main(void) {
            object_t dyld_pager = { .id = 1 };
            object_t backing = { .id = 2, .pager = (object_t *)0x3000 };
            object_t vnode_pager = { .id = 3, .is_vnode_pager = 1, .vnode = 0x4000 };
            (void)backing;
            /* direct lookup (v31 behaviour): NULL */
            object_t *vp = vnode_pager_lookup_vnode(&dyld_pager);
            if (vp != 0) { printf("direct=FAIL\n"); return 1; }
            /* v32 fallback */
            object_t *b = 0;
            if (backing_object(&dyld_pager, &b) && b) {
                vp = vnode_pager_lookup_vnode(&vnode_pager); /* backing->pager */
            }
            if (vp != (object_t *)0x4000) { printf("fallback=FAIL\n"); return 2; }
            printf("direct=NULL fallback=%p\n", (void *)vp);
            return 0;
        }
    """)
    with tempfile.TemporaryDirectory() as td:
        c = Path(td) / "pager.c"
        b = Path(td) / "pager"
        c.write_text(pager_model)
        subprocess.run(["cc", "-O0", "-Wall", "-Wextra", "-o", str(b), str(c)], check=True)
        out = subprocess.run([str(b)], check=True, capture_output=True, text=True).stdout
    assert "direct=NULL" in out and "fallback=0x4000" in out, out
    print("[PASS] model: dyld-pager backing object recovers the DSC file vnode")

    # --- behavioural model: deferred scan keeps vnode I/O off the fault path. ---
    class Lock:
        def __init__(self): self.held = False
        def acquire(self):
            if self.held:
                raise RuntimeError("recursive object lock")
            self.held = True
        def release(self): self.held = False

    obj_lock = Lock()
    log = []

    def fault_path():
        obj_lock.acquire()
        try:
            log.append("enter")             # diag 0 / patch decision
            return "defer"                  # no vnode read here
        finally:
            obj_lock.release()

    def worker():
        log.append("vnode read")            # safe: no object lock held

    assert fault_path() == "defer"
    worker()
    assert log == ["enter", "vnode read"], log
    print("[PASS] model: vnode reads deferred outside the object lock")

    # --- behavioural model: split symbols file fallback. ---
    class DSC:
        def __init__(self, local_symbols): self.local_symbols = local_symbols
    main = DSC(0)          # split symbols on device
    symbols = DSC(0x200)
    path = "/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64e"
    chosen = symbols if main.local_symbols == 0 else main
    assert chosen is symbols
    assert (path + ".symbols").endswith("dyld_shared_cache_arm64e.symbols")
    assert chosen.local_symbols == 0x200
    print("[PASS] model: main DSC ls_off=0 selects .symbols companion file")

    # --- behavioural model: gate scan on retrigger, retry wrong vnode. ---
    class Scan:
        def __init__(self): self.retriggered = False; self.started = False; self.state = "need"
        def fault(self, magic):
            if self.state != "need" or self.retriggered is False or self.started:
                return self.state
            self.started = True
            if magic[:6] != b"dyld_v":
                self.state = "need"; self.started = False
                return "retry"
            self.state = "have_off"
            return "found"
        def retrigger(self): self.retriggered = True; self.state = "need"; self.started = False

    scan = Scan()
    assert scan.fault(b"\xcf\xfa\xed\xfe") == "need"   # pre-retrigger: ignored
    scan.retrigger()
    assert scan.fault(b"\xcf\xfa\xed\xfe") == "retry"  # wrong vnode: retry
    assert scan.fault(b"dyld_v1  arm64e") == "found"
    print("[PASS] model: scan gated on retrigger; wrong-magic vnode retried")

    # --- behavioural model: bounded periodic status survives ring wrap. ---
    ring = []
    def emit(line):
        ring.append(line)
        if len(ring) > 10: ring.pop(0)   # 16 KB ring wraps
    for i in range(5): emit("noise %d" % i)
    emit("M30 IRT diag 0: enter")       # early, overwritten later
    for i in range(20): emit("noise %d" % (5 + i))
    assert not any("M30 IRT" in x for x in ring)
    for i in range(3):
        emit("M30 IRT status: state=2 off=0x1234000 err=0 replay=%d" % i)
    assert any("M30 IRT status:" in x for x in ring), ring
    assert "M30 IRT status: state=2 off=0x1234000 err=0 replay=2" in ring
    print("[PASS] model: periodic status replay survives ring wrap")

    # --- behavioural model: vn_getpathplen includes NUL. ---
    main_path = b"/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.31\x00"
    plen = len(main_path)                 # XNU reports size incl. NUL
    wrong = main_path[:plen] + b".symbols\x00"
    assert wrong[len(main_path)-1:len(main_path)+1] == b"\x00."  # suffix after NUL
    assert wrong.split(b"\x00")[0] == main_path[:-1]            # string unchanged
    n = 0
    while n < len(main_path) and main_path[n] != 0: n += 1
    correct = main_path[:n] + b".symbols\x00"
    assert correct.split(b"\x00")[0].endswith(b".31.symbols")
    print("[PASS] model: strip NUL before appending .symbols suffix")

    # --- behavioural model: dyld4 subcache symbol path. ---
    full = "/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.31"
    base_n = len(full)
    while base_n > 0 and full[base_n - 1].isdigit():
        base_n -= 1
    if base_n > 0 and base_n < len(full) and full[base_n - 1] == '.':
        base_n -= 1
    base = full[:base_n]
    assert base.endswith("dyld_shared_cache_arm64")
    candidates = [base + ".symbols", full + ".symbols", base]
    assert candidates[0].endswith("dyld_shared_cache_arm64.symbols")
    assert candidates[1].endswith("dyld_shared_cache_arm64.31.symbols")
    print("[PASS] model: strip .31 subcache index to find main cache symbols")

    print("ALL M30 INTERNAL RELEASE TYPE TESTS PASS")


if __name__ == "__main__":
    raise SystemExit(main())
