#!/usr/bin/env python3
"""Regression test for patch 0432 (v55: 16K code-directory block read-back).

Evidence chain
--------------
v45 physical pstore record [177]:
    CODE SIGNING: cs_invalid_page(0x1d5839000): p=26[SpringBoard]
    final status 0x22000000, allowing (remove VALID) page
immediately after launchd "Early boot complete" ([175]/[176]).  The willowios
project proved that this exact CS_VALID loss makes XNU refuse the
com.apple.springboard-ui.client entitlement and +[SpringBoardUI load] raises
NSInternalInconsistencyException.

Code cause
----------
vm_page_validate_cs_mapped_slow() (patch 0418) builds a 16K validation block
only from already-resident pages.  The FIRST fault of a 16K-hashed page has
just one resident 4K page, so validation was skipped, validated stayed 0, and
cs_invalid_page() stripped CS_VALID from the process.

v55 fix
-------
Read the exact 16K block from the code-signed vnode with UIO_READ/IO_NOCACHE
while the VM object lock is temporarily dropped (explicitly permitted by
vm_fault_cs_check_violation()).  After re-locking, overlay the actual bytes of
every still-resident page -- using kaddr for the busy faulting page -- before
cs_validate_page() hashes the whole block.  This proves the hash is checked
against what is really mapped, not merely against a trusted on-disk copy.
No signature, hash, AMFI, trust-cache or page-validation check is skipped;
the file is never written.  Counters are replayed in the durable IRT
heartbeat.
"""
from __future__ import annotations

from pathlib import Path
import os
import subprocess
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0432-m30-cs-16k-block-readback.patch"
PSTORE_V45 = ROOT / "validation/physical-boot-test/20261123-ios-v45-boot/raw/pmsg-ramoops-0"
PSTORE_V54 = ROOT / "validation/physical-boot-test/20261123-ios-v54-boot/raw/pmsg-ramoops-0"
V54_PATCH = ROOT / "xnu/patches-minimal/0431-m30-irt-retryable-early-scan.patch"
V54_BASE = ROOT / "milestone_artifacts/ci_45206251994/buildtree/unpacked/xnu/osfmk/vm/vm_fault.c"


def main():
    t = PATCH.read_text()

    # --- patch structure: read the whole 16K block, lock-safe ---------------
    assert "vm_object_unlock(object);" in t
    assert "vm_object_lock(object);" in t
    assert t.index("vm_object_unlock(object);") < t.index("vn_rdwr(UIO_READ")
    assert t.index("vn_rdwr(UIO_READ") < t.index("vm_object_lock(object);")
    assert "UIO_READ" in t
    assert "UIO_WRITE" not in t, "the backing file must never be written"
    assert "IO_NOCACHE" in t, "readback must not recurse via the UBC cache"
    assert "CS_16K_BLOCK_SIZE" in t
    assert "vsize = CS_16K_BLOCK_SIZE" in t
    assert "voff = block_mo" in t
    assert "cs_validate_page(vnode, pager, voff, vdata, vsize," in t
    # No false validation: overlay actual resident bytes after re-locking.
    assert "actual bytes of every still" in t
    assert t.index("vm_object_lock(object);") < t.index("vm_page_lookup(object,")
    assert "rpage == page" in t
    assert "(const void *)kaddr, PAGE_SIZE" in t
    assert "bpage[] was gathered before the lock drop" in t
    assert "object->alive &&" in t and "!object->terminating && object->pager != NULL" in t
    # Secure fallback stays intact: one mapped page, no validation claimed.
    assert "if (vdata == NULL) {" in t
    assert "vsize = PAGE_SIZE;" in t
    assert "fails closed" in t
    # No security weakening, no 0417, no other bypass.
    for bad in (
        "cs_enforcement_disable", "amfi_get_out_of_my_way",
        "launchd_unsecure_cache", "CSDebugDisable", "IO_NOAUTH",
        "VMP_CS_SET_VALIDATED", "tainted = 0;", "vmp_cs_tainted = 0",
    ):
        assert bad not in t, f"patch must not contain {bad!r}"
    # Durable evidence in the heartbeat.
    assert "csblk=%lu csfail=%lu" in t
    assert "csvok=%lu" in t
    assert t.count("m30_cs_block_reads, m30_cs_block_read_fail,") >= 2
    assert "M30_CS_DIAG(0," in t and "M30_CS_DIAG(1," in t and "M30_CS_DIAG(2," in t
    assert "m30_cs_diag_seen & (1ULL << (n))" in t
    # v54 IRT/CLASS behaviour must remain: none of the existing hooks may go.
    assert V54_BASE.exists(), "exact v54 CI buildtree base required for regression check"
    b = V54_BASE.read_text()
    removed = "\n".join(line for line in t.splitlines()
                        if line.startswith("-") and not line.startswith("---"))
    for hook in (
        "m30_xctest_probe_fixup(kaddr, mo_offset);",
        "m30_irt_retrigger_after_xctest();",
        "m30_internal_release_fixup(vnode, pager, mo_offset, kaddr);",
    ):
        assert hook in b, f"v54 base missing {hook}"
        assert hook not in removed, f"v55 must not remove {hook}"
    print("[PASS] patch 0432: lock-safe 16K readback, resident bytes overlaid, full-hash validation")

    # --- physical evidence: v45 CS_VALID loss, v54 IRT baseline -------------
    d45 = PSTORE_V45.read_bytes()
    assert b"p=26[SpringBoard]" in d45
    assert b"final status 0x22000000, allowing (remove VALID) page" in d45
    assert b"Early boot complete. Continuing system boot." in d45
    print("[PASS] v45 pstore: SpringBoard CS_VALID removed after early boot complete")

    d54 = PSTORE_V54.read_bytes()
    assert b"M30 IRT: patched (final state=3" in d54
    assert b"csblk=" not in d54, "v54 must not already carry v55 counters"
    assert V54_PATCH.exists(), "v54 retry baseline must stay in the chain"
    print("[PASS] v54 baseline preserved; v55 counters are new")

    # --- behavioural model -------------------------------------------------
    model = textwrap.dedent(r"""
        #include <stdio.h>
        #include <string.h>
        #include <stdint.h>
        #define PAGE_SIZE 4096
        #define BLOCK_SIZE 16384
        #define FAULT_INDEX 1
        static unsigned long reads = 0, fails = 0, validated = 0;
        static unsigned char file_block[BLOCK_SIZE];
        static unsigned char mapped_page[PAGE_SIZE];
        static unsigned char block[BLOCK_SIZE];

        /* Stand-in for cs_validate_hash over the full code-directory block. */
        static int hash_ok(const unsigned char *p) {
            unsigned int sum = 0;
            for (int i = 0; i < BLOCK_SIZE; i++) sum += p[i];
            return (sum & 0xff) == 0x78;
        }

        static int validate(int resident_count, int vnode_present,
                            int read_ok, int lock_held, int tampered) {
            memset(block, 0, sizeof(block));
            int vsize = PAGE_SIZE;

            if (resident_count == 4) {
                /* v54 all-resident path: hash the four mapped pages. */
                memcpy(block, file_block, BLOCK_SIZE);
                vsize = BLOCK_SIZE;
            } else if (vnode_present && !lock_held) {
                int resid = BLOCK_SIZE;
                reads++;
                if (!read_ok || resid != BLOCK_SIZE) {
                    fails++;
                } else {
                    memcpy(block, file_block, BLOCK_SIZE);
                    /* v55: overlay the real bytes of the busy faulting page. */
                    memcpy(block + (FAULT_INDEX * PAGE_SIZE), mapped_page, PAGE_SIZE);
                    if (tampered) {
                        block[(FAULT_INDEX * PAGE_SIZE) + 17] ^= 0xff;
                    }
                    vsize = BLOCK_SIZE;
                }
            }
            if (vsize != BLOCK_SIZE) {
                /* Old/fallback path: one 4K page cannot match a 16K hash. */
                memcpy(block, mapped_page, PAGE_SIZE);
                return 0;
            }
            if (!hash_ok(block)) {
                return 0;
            }
            validated++;
            return 1;
        }

        int main(void) {
            for (int i = 0; i < BLOCK_SIZE; i++) file_block[i] = (unsigned char)(i & 0xff);
            unsigned int target = 0;
            for (int i = 0; i < BLOCK_SIZE; i++) target += file_block[i];
            file_block[0] = (unsigned char)(file_block[0] + ((0x78u - (target & 0xffu)) & 0xffu));
            memcpy(mapped_page, file_block + (FAULT_INDEX * PAGE_SIZE), PAGE_SIZE);

            /* old v54 behaviour: one resident page, no readback -> violation */
            int rc = validate(1, 0, 1, 0, 0);
            if (rc != 0 || validated != 0) { printf("OLD=FAIL rc=%d\n", rc); return 1; }
            printf("OLD=OK validated=%lu\n", validated);

            /* v55: one resident page, lock dropped, read ok -> validated */
            rc = validate(1, 1, 1, 0, 0);
            if (rc != 1 || validated != 1 || reads != 1) {
                printf("READBACK=FAIL rc=%d v=%lu r=%lu\n", rc, validated, reads); return 2;
            }
            printf("READBACK=OK v=%lu r=%lu f=%lu\n", validated, reads, fails);

            /* all pages resident: no extra read */
            rc = validate(4, 1, 1, 0, 0);
            if (rc != 1 || validated != 2 || reads != 1) {
                printf("RESIDENT=FAIL rc=%d v=%lu r=%lu\n", rc, validated, reads); return 3;
            }
            printf("RESIDENT=OK v=%lu r=%lu\n", validated, reads);

            /* lock still held: refuse vnode I/O (v34 panic prevention) */
            rc = validate(1, 1, 1, 1, 0);
            if (rc != 0 || reads != 1) {
                printf("LOCK=FAIL rc=%d r=%lu\n", rc, reads); return 4;
            }
            printf("LOCK=OK r=%lu\n", reads);

            /* short/failed read: secure fallback, no false validation */
            rc = validate(1, 1, 0, 0, 0);
            if (rc != 0 || fails != 1 || validated != 2) {
                printf("FAILREAD=FAIL rc=%d f=%lu v=%lu\n", rc, fails, validated); return 5;
            }
            printf("FAILREAD=OK f=%lu v=%lu\n", fails, validated);

            /* tampered resident page: file read alone must NOT validate it */
            rc = validate(1, 1, 1, 0, 1);
            if (rc != 0 || validated != 2 || reads != 3) {
                printf("TAMPER=FAIL rc=%d v=%lu r=%lu\n", rc, validated, reads); return 6;
            }
            printf("TAMPER=OK v=%lu r=%lu\n", validated, reads);
            return 0;
        }
    """)
    # /tmp is a small tmpfs on this host; keep compiler scratch on the repo fs.
    scratch_root = ROOT / ".test-tmp"
    scratch_root.mkdir(exist_ok=True)
    env = dict(os.environ, TMPDIR=str(scratch_root))
    with tempfile.TemporaryDirectory(dir=str(scratch_root)) as td:
        c = Path(td) / "model.c"
        b = Path(td) / "model"
        c.write_text(model)
        subprocess.run(["cc", "-O0", "-Wall", "-Wextra", "-o", str(b), str(c)],
                       check=True, env=env)
        result = subprocess.run([str(b)], capture_output=True, text=True, env=env)
        if result.returncode != 0:
            raise AssertionError(f"model failed rc={result.returncode}\n"
                                 f"stdout={result.stdout}\nstderr={result.stderr}")
        out = result.stdout
    for marker in ("OLD=OK", "READBACK=OK", "RESIDENT=OK", "LOCK=OK",
                   "FAILREAD=OK", "TAMPER=OK"):
        assert marker in out, out
    print("[PASS] model: readback validates 16K; tampered page and short read fail closed; no I/O under held lock")

    print("ALL M30 16K CS BLOCK READBACK TESTS PASS")


if __name__ == "__main__":
    raise SystemExit(main())
