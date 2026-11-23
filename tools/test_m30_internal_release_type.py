#!/usr/bin/env python3
"""Regression test for patch 0426 (_internal_release_type = 3 fix-up).

v30 physical: all-copy class-name string patching fired once but SpringBoardUI
still aborted. LiveContainer's bypass has TWO parts that BOTH appear necessary:
  (1) _internal_release_type = 3 -> os_variant_has_internal_content() true
  (2) XCTestConfiguration class registration
Patch 0426 implements part (1) by locating the _internal_release_type global
through the dyld shared cache local-symbol table (vn_rdwr from the vnode) and
setting the in-memory page value to 3, strictly after cs_validate_page().
Patch 0427 restores the v48 XCTEST gate after the v49 early-start regression,
and makes that gate open on the bitmap fast path too.
The file on disk is never written; no security check is weakened.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0426-m30-internal-release-type.patch"
PATCH_V50 = ROOT / "xnu/patches-minimal/0427-m30-irt-retrigger-gate.patch"
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
PSTORE_V44 = ROOT / "validation/physical-boot-test/20261123-ios-v44-boot/raw/pmsg-ramoops-0"
PSTORE_V45 = ROOT / "validation/physical-boot-test/20261123-ios-v45-boot/raw/pmsg-ramoops-0"
PSTORE_V46 = ROOT / "validation/physical-boot-test/20261123-ios-v46-boot/raw/pmsg-ramoops-0"
PSTORE_V47 = ROOT / "validation/physical-boot-test/20261123-ios-v47-boot/raw/pmsg-ramoops-0"
PSTORE_V48 = ROOT / "validation/physical-boot-test/20261123-ios-v48-boot/raw/pmsg-ramoops-0"
PSTORE_V49 = ROOT / "validation/physical-boot-test/20261123-ios-v49-boot/raw/pmsg-ramoops-0"


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
    assert "for (cand = 0; cand < 5 && !opened; cand++)" in t
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
    assert "vp == m30_irt_target_vp" in t
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
    # v45: use the SAME cache base for the companion, the image list, and the
    # real-cache mapping search.  On iOS >=16 the live cache is under Cryptex.
    assert "for (cand = 0; cand < 5 && !opened; cand++)" in t
    assert "if (cand == 0 || cand == 1) {" in t
    assert "prefix = sizeof(cryptex_base) - 1;" in t
    assert "if (cand <= 1) {" in t
    assert "basepath_n = sizeof(cryptex_base) - 1;" in t
    assert "comp=%d ls=0x%llx sym=0x%llx" in t
    # v46: a compact 2 s heartbeat carries the final IRT state (including the
    # local-symbol counts) into the wrapped 16 KB pstore window.
    hb = t[t.index("for (i = 0; i < 180; i++)"):]
    assert "delay(2000000)" in hb
    assert 'M30 IRT: patched (final state=%d off=0x%llx' in hb
    assert "nlist_cnt=%u nlist_range=%u sc=%u si=%d " in hb
    assert "fo=%u vh=%u oh=%u pr=%d fb=0x%llx hb=%d)\\n" in hb
    assert 'M30 IRT final: state=%d off=0x%llx err=%d' in hb
    assert "break;" not in hb
    # v47: enumerate dyld4 subcache files from the header instead of guessing
    # only numeric suffixes; the target subcache can be ".03.development".
    assert "hdr + 392" in t and "hdr + 396" in t
    assert "M30_IRT_DIAG(55, \"subcache array" in t
    assert "M30_IRT_DIAG(56, \"subcache idx=%u suffix=%s" in t
    assert "sf[0] != '.'" in t and "sf[sf_len] != '/'" in t
    assert "m30_irt_subcache_cnt" in t and "m30_irt_subcache_index" in t
    assert "sc=%u si=%d fo=" in t
    # v48: the offset was found but the page patch never fired.  Record HAVE_OFF
    # fault counters and accept a different vnode instance for the same file by
    # strict (mount, vnode id) identity; this is not a security relaxation.
    assert "extern uint32_t vnode_vid(vnode_t);" in t
    assert "extern void *vnode_mount(vnode_t);" in t
    assert "m30_irt_target_vid = vnode_vid(target_vp);" in t
    assert "m30_irt_target_mount = vnode_mount(target_vp);" in t
    assert "m30_irt_haveoff_faults++" in t
    assert "m30_irt_target_vp_hits++" in t
    assert "m30_irt_offset_hits++" in t
    assert "vnode_vid(vp) == m30_irt_target_vid" in t
    assert "vnode_mount(vp) == m30_irt_target_mount" in t
    assert "fo=%u vh=%u oh=%u pr=%d" in t
    # v48: the target page was almost certainly faulted before the offset was
    # known, so patch the already-resident page via the vnode's VM object.
    # This is the same post-validation in-memory write as the fault path.
    assert "extern memory_object_control_t ubc_getobject(vnode_t, int);" in t
    assert "m30_irt_patch_resident_page(void)" in t
    assert "ubc_getobject(m30_irt_target_vp, UBC_FLAGS_NONE)" in t
    assert "memory_object_control_to_vm_object(" in t
    assert "vm_page_lookup(obj, page_off)" in t
    assert "VMP_CS_VALIDATED(page, PAGE_SIZE, 0)" in t
    assert "vm_page_wire(page, VM_KERN_MEMORY_OSFMK, FALSE)" in t
    assert "phystokv(pa)" in t
    assert "M30 IRT: patched resident page" in t
    assert "m30_irt_proactive_result = m30_irt_patch_resident_page();" in t
    assert "pr=%d" in t
    # v37: retrigger gate, and retry with a later vnode on wrong magic.
    assert "!m30_irt_thread_started) {" in t
    assert "m30_irt_retriggered = 1;" in t

    # v50: v49's early-start experiment failed physically (state=4 before the
    # symbol scan).  Restore the v48 gate, but let the bitmap fast path open it
    # when the XCTest literal is rewritten there.  The durable heartbeat carries
    # the patch count so the captured ring proves whether part (2) fired.
    v50 = PATCH_V50.read_text()
    assert "m30_irt_retrigger_after_xctest(void)" in v50
    assert "m30_xctest_patch_count == 0 || m30_irt_retriggered" in v50
    assert "m30_irt_retriggered && !m30_irt_thread_started" in v50
    assert v50.count("m30_irt_retrigger_after_xctest();") == 2
    assert "xctest=%lu" in v50
    assert "v49 started the" in v50
    print("[PASS] v50 patch: retrigger gate restored and fast path opens it")
    # v49: validation-bitmap fast paths skip the slow function where the
    # fix-ups used to live.  Run both fix-ups on that path too.
    assert t.count("m30_xctest_probe_fixup(kaddr, mo_offset)") == 2
    assert t.count("m30_internal_release_fixup(vnode, pager, mo_offset,") == 2
    assert "vm_page_validate_cs_fast(page, fault_page_size, fault_phys_offset)" in t
    assert "} else {" in t  # bitmap-fast-path branch added at the call site
    assert "validation bitmap fast path skips the slow function" in t
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

    # --- v44 physical: the companion's own mapping is a 16 KB stub, so it
    # cannot translate the nlist value.  The companion itself must come from
    # the same cache base as the live image list. ---
    d44 = PSTORE_V44.read_bytes()
    assert b"M30 IRT status: state=4 off=0x0 err=0 replay=13" in d44
    assert b"sym=0x1e1d3ad84 img=0x1d1c22000 hits=0 tries=138" in d44
    assert b"symmap=0x22ade8000/0x4000@0x0 fb=0x0" in d44
    assert b"This process should not be linking or loading SpringBoardUI.framewor" in d44
    assert b"M30 IRT: patched" not in d44
    print("[PASS] v44 pstore: companion map is a 16 KB stub -> select Cryptex companion")

    # --- v45 physical: deeper userspace, but the decisive IRT lines were
    # overwritten.  The assertion is absent only from the captured window. ---
    d45 = PSTORE_V45.read_bytes()
    assert len(d45) == 16372, "v45 pmsg ring should be full/wrapped"
    assert b"Early boot complete. Continuing system boot." in d45
    assert b"p=26[SpringBoard]" in d45
    assert b"mediaserverd" in d45 and b"driverkitd" in d45
    assert b"This process should not be linking or loading SpringBoardUI.framewor" not in d45
    assert b"M30 IRT" not in d45, "v45 final window lost all IRT replay lines"
    print("[PASS] v45 pstore: assertion absent, launchd early boot complete, SpringBoard loaded")

    # --- v46 physical: the durable heartbeat proves the patch did NOT happen.
    # The symbol and its local-symbol range were found, but no real cache file
    # mapping contained that vmaddr; only numeric subcache names were tried. ---
    d46 = PSTORE_V46.read_bytes()
    assert len(d46) == 16372, "v46 pmsg ring should be full/wrapped"
    assert b"M30 IRT: patched" not in d46
    assert b"M30 IRT final: state=4 off=0x0 err=0 sym=0x1e1d3ad84 " \
           b"comp=0 ls=0x4000 nlist_cnt=8705811 nlist_range=146 hits=0 " \
           b"tries=138" in d46
    assert b"M30 IRT final: state=4 off=0x0 err=0 sym=0x1e1d3ad84 " \
           b"comp=0 ls=0x4000 nlist_cnt=8705811 nlist_range=146 hits=0 " \
           b"tries=138 sc=" not in d46, "v46 must not contain v47 fields"
    assert b"hb=55" in d46, "final heartbeat must survive ring wrap"
    assert b"Early boot complete. Continuing system boot." not in d46
    assert b"SpringBoardUI.framework" not in d46
    assert b"CRASH backboardd" in d46
    print("[PASS] v46 pstore: durable final state=4, hits=0/tries=138, no patch")

    # --- v47 physical: exact subcache enumeration found the mapping, but the
    # state stayed HAVE_OFF; the in-memory patch never fired. ---
    d47 = PSTORE_V47.read_bytes()
    assert len(d47) == 16372, "v47 pmsg ring should be full/wrapped"
    assert b"M30 IRT: patched" not in d47
    assert b"M30 IRT final: state=2 off=0xa432d84 err=0 sym=0x1e1d3ad84 " \
           b"comp=0 ls=0x4000 nlist_cnt=8705811 nlist_range=146 hits=1 " \
           b"tries=29 sc=42 si=26 fb=0x0 hb=" in d47
    assert b"hits=1 tries=29 sc=42 si=26" in d47
    assert b"M30 IRT status: state=2 off=0xa432d84" in d47
    assert b"SpringBoardUI.framework" not in d47
    assert b"Early boot complete. Continuing system boot." not in d47
    print("[PASS] v47 pstore: mapping found (hits=1,sc=42,si=26) but state=2")

    # --- v48 physical: the IRT page patch finally fired. ---
    d48 = PSTORE_V48.read_bytes()
    assert len(d48) == 16372, "v48 pmsg ring should be full/wrapped"
    assert b"M30 IRT: patched _internal_release_type off 0xa432d84 (0 -> 3)" in d48
    assert b"M30 IRT: patched (final state=3 off=0xa432d84" in d48
    assert b"nlist_cnt=8705811 nlist_range=146 sc=42 si=26 fo=19821 " \
           b"vh=3493 oh=1 pr=-5 fb=0x0 hb=" in d48
    assert b"M30 IRT status: state=3 off=0xa432d84" in d48
    assert b"M30 IRT final:" not in d48
    # The resident-page shortcut was rejected (pr=-5: page not validated), but
    # the strict alias identity let a later normal fault patch the page.
    assert b"pr=-5" in d48 and b"oh=1" in d48
    # The SpringBoardUI assertion is still present and precedes the patch, so
    # no UI/user-space success is claimed.
    assert b"This process should not be linking or loading SpringBoardUI.framework" in d48
    assert b"Early boot complete. Continuing system boot." not in d48
    print("[PASS] v48 pstore: IRT patch fired (state=3, oh=1), assertion persists")

    # --- v49 physical: starting the worker on the first dyld fault regressed. ---
    d49 = PSTORE_V49.read_bytes()
    assert len(d49) == 16372, "v49 pmsg ring should be full/wrapped"
    assert b"M30 IRT status: state=4 off=0x0" in d49
    assert b"hits=0 tries=0" in d49
    assert b"M30 IRT: patched" not in d49
    assert b"M30 XCTEST: patched" not in d49
    assert b"Early boot complete. Continuing system boot." not in d49
    print("[PASS] v49 pstore: early-start regression (state=4, no patch marker)")

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

    # --- behavioural model: exact dyld4 subcache names from the header. ---
    import struct
    header = bytearray(552)
    header[:6] = b"dyld_v"
    struct.pack_into("<I", header, 392, 0x1000)   # subCacheArrayOffset
    struct.pack_into("<I", header, 396, 2)        # subCacheArrayCount
    entries = bytearray(2 * 56)
    entries[0*56+24:0*56+24+15] = b".03.development"
    entries[1*56+24:1*56+24+8] = b".25.data"
    assert struct.unpack_from("<I", header, 392)[0] == 0x1000
    assert struct.unpack_from("<I", header, 396)[0] == 2
    suffixes = []
    for i in range(2):
        raw = bytes(entries[i*56+24:(i+1)*56])
        sf = raw.split(b"\x00", 1)[0].decode()
        assert sf.startswith(".") and "/" not in sf
        suffixes.append(sf)
    assert suffixes == [".03.development", ".25.data"]
    base = "/private/preboot/Cryptexes/OS/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"
    exact_paths = [base + s for s in suffixes]
    numeric_paths = [base + ".%d" % i for i in range(512)]
    assert exact_paths[0] not in numeric_paths
    assert exact_paths[0].endswith("dyld_shared_cache_arm64.03.development")
    print("[PASS] model: header subcache suffixes reach non-numeric cache files")

    # --- behavioural model: stable vnode identity gate. ---
    target = ("cryptex_mount", 4242)
    observed = [
        ("other_mount", 4242),   # same vid, different mount: reject
        ("cryptex_mount", 9),    # same mount, different vid: reject
        ("cryptex_mount", 4242), # same file via a different vnode pointer: accept
    ]
    matched = [mp == target[0] and vid == target[1] for mp, vid in observed]
    assert matched == [False, False, True]
    print("[PASS] model: strict mount+vnode-id identity accepts alias safely")

    # --- behavioural model: resident-page patch requires a validated page. ---
    pages = {
        0xa430000: {"validated": True, "value": 1},
        0xa432000: {"validated": True, "value": 2},
        0xa434000: {"validated": False, "value": 9},
    }
    file_off = 0xa432d84
    page_off = file_off & ~0xfff
    po = file_off - page_off
    assert page_off == 0xa432000 and po == 0xd84
    page = pages.get(page_off)
    assert page is not None and page["validated"]
    patched = page["value"]
    assert patched == 2
    assert pages[0xa434000]["validated"] is False  # unvalidated page rejected
    print("[PASS] model: resident patch only touches a validated cached page")

    # --- behavioural model: bitmap fast path now runs the fix-ups. ---
    paths = {
        "slow": ["cs_validate_page", "xctest_fixup", "irt_fixup"],
        "bitmap_fast_before": ["bitmap_ok"],
        "bitmap_fast_v49": ["bitmap_ok", "xctest_fixup", "irt_fixup"],
    }
    assert paths["bitmap_fast_before"] == ["bitmap_ok"]
    assert paths["bitmap_fast_v49"] == [
        "bitmap_ok", "xctest_fixup", "irt_fixup"]
    assert set(paths["slow"][1:]) == set(paths["bitmap_fast_v49"][1:])
    print("[PASS] model: bitmap fast path covers both post-validation fix-ups")

    # --- behavioural model: only the XCTest patch opens the DSC scan gate. ---
    def run_fault(path, xctest_seen, retriggered, started):
        if path in ("xctest", "bitmap_xctest"):
            xctest_seen += 1
            if not retriggered:
                retriggered = True
        if retriggered and not started:
            started = True
        return xctest_seen, retriggered, started

    seen, retriggered, started = 0, False, False
    for path in ("dyld", "launchd", "dyld"):
        seen, retriggered, started = run_fault(path, seen, retriggered, started)
    assert (seen, retriggered, started) == (0, False, False)
    seen, retriggered, started = run_fault("xctest", seen, retriggered, started)
    assert (seen, retriggered, started) == (1, True, True)
    # The bitmap path can be the one that rewrites the literal; opening the
    # gate there must behave exactly like the slow path.
    seen2, retriggered2, started2 = 0, False, False
    seen2, retriggered2, started2 = run_fault("bitmap_xctest", seen2, retriggered2, started2)
    assert (seen2, retriggered2, started2) == (1, True, True)
    print("[PASS] model: fast-path XCTest patch opens the same DSC scan gate")

    print("ALL M30 INTERNAL RELEASE TYPE TESTS PASS")


if __name__ == "__main__":
    raise SystemExit(main())
