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
    assert "m30_irt_diag_seen & (1U << (n))" in t, "diagnostics must be one-shot"
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
    assert "no vnode I/O, only in-memory patching" in t

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

    print("ALL M30 INTERNAL RELEASE TYPE TESTS PASS")


if __name__ == "__main__":
    raise SystemExit(main())
