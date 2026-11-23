#!/usr/bin/env python3
"""Regression test for patch 0433 (v56: non-sleeping 16K CS readback).

Evidence
--------
v55 physical pstore decoded 154/154 records cleanly: the kernel reached
`load_init_program` and then stopped.  There was no IRT heartbeat, no CS diag,
no launchd progress and no ring wrap.  The v55 patch allocates the 16K readback
buffer with `kalloc_data(..., Z_WAITOK)` while the VM object lock is still
held; that can sleep under the lock.  v56 uses `Z_NOWAIT`, fails closed on
allocation failure, and rechecks the pager after the lock drop/reacquire.

This is the historical gate for 0433 only.  v56 was cancelled before any
physical flash because 0433 still lets `vn_rdwr()` create a UPL containing the
busy faulting page; the final gate is `tools/test_m30_cs_16k_no_busy_upl.py`
for 0434.  All v55 validation semantics remain: the vnode is read only, the
resident bytes are overlaid before hashing, short reads fail closed, and no
security check is weakened.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import os
import shutil
import subprocess
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parent.parent
PATCH_V55 = ROOT / "xnu/patches-minimal/0432-m30-cs-16k-block-readback.patch"
PATCH_V56 = ROOT / "xnu/patches-minimal/0433-m30-cs-16k-nowait-pager-recheck.patch"
V55_BASE = ROOT / "milestone_artifacts/ci_45219943492/buildtree/unpacked/xnu/osfmk/vm/vm_fault.c"
V55_BASE_SHA = "ab3cf37eac16a1dbf91472335153ce6b92ef8daa3e5565103b8a92b75afe62dd"
V56_RESULT_SHA = "2d9997b3f7b72d82576ccb404193a924ca147236c70ef667ee6f3edd52db2775"
V55_PSTORE = ROOT / "validation/physical-boot-test/20261123-ios-v55-boot/raw/pmsg-ramoops-0"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    # --- patch content: exact v55 failure mode is removed -------------------
    v55 = PATCH_V55.read_text()
    v56 = PATCH_V56.read_text()

    assert PATCH_V56.name.startswith("0433-")
    assert "diff --git a/osfmk/vm/vm_fault.c b/osfmk/vm/vm_fault.c" in v56
    assert "-char *readbuf = kalloc_data(CS_16K_BLOCK_SIZE, Z_WAITOK);" not in v56
    assert "-			char *readbuf = kalloc_data(CS_16K_BLOCK_SIZE, Z_WAITOK);" in v56
    assert "+			readbuf = kalloc_data(CS_16K_BLOCK_SIZE, Z_NOWAIT);" in v56
    assert "The object lock is still held here: Z_WAITOK can sleep." in v56
    assert "+			if (readbuf == NULL) {" in v56
    assert "+				m30_cs_block_read_fail++;" in v56
    assert '+				M30_CS_DIAG(3, "16K readback allocation failed\\n");' in v56
    assert "object->pager == pager" in v56
    assert "pager_same=%d" in v56
    assert 'M30_CS_DIAG(4, "16K readback rejected err=%d resid=%d pager_same=%d\\n",' in v56
    assert "UIO_READ" in v56 and "UIO_WRITE" not in v56
    assert "IO_NOCACHE" in v56
    for bad in (
        "cs_enforcement_disable", "amfi_get_out_of_my_way",
        "launchd_unsecure_cache", "CSDebugDisable", "IO_NOAUTH",
        "VMP_CS_SET_VALIDATED", "vmp_cs_tainted = 0",
    ):
        assert bad not in v56, f"v56 patch must not contain {bad!r}"
    # v55's readback, resident-byte overlay and counters remain in the chain.
    for marker in (
        "vn_rdwr(UIO_READ", "vm_object_unlock(object);", "vm_object_lock(object);",
        "rpage == page", "(const void *)kaddr, PAGE_SIZE",
        "vsize = CS_16K_BLOCK_SIZE", "csblk=%lu csfail=%lu", "csvok=%lu",
    ):
        assert marker in v55, f"v55 patch lost {marker!r}"
    print("[PASS] patch 0433: Z_NOWAIT, allocation fail-closed, pager identity recheck")

    # --- physical evidence: v55 hang, not a wrapped-log artifact -----------
    p55 = V55_PSTORE.read_bytes()
    assert b"load_init_program" in p55
    assert b"M30 IRT:" not in p55
    assert b"csblk=" not in p55
    assert b"M30 CS diag" not in p55
    print("[PASS] v55 pstore: clean early stop after load_init_program, no IRT/CS telemetry")

    # --- patch applies to the exact v55 CI buildtree -----------------------
    assert V55_BASE.exists(), "exact v55 CI buildtree is required"
    assert sha256(V55_BASE) == V55_BASE_SHA, sha256(V55_BASE)

    scratch_root = ROOT / ".test-tmp"
    scratch_root.mkdir(exist_ok=True)
    env = dict(os.environ, TMPDIR=str(scratch_root))
    with tempfile.TemporaryDirectory(dir=str(scratch_root)) as td:
        work = Path(td)
        target = work / "osfmk/vm/vm_fault.c"
        target.parent.mkdir(parents=True)
        shutil.copy2(V55_BASE, target)
        rel = work.relative_to(ROOT)
        subprocess.run(
            ["git", "apply", "--directory", str(rel), "-p1",
             str(PATCH_V56.relative_to(ROOT))],
            cwd=str(ROOT), check=True, env=env,
            capture_output=True, text=True,
        )
        assert sha256(target) == V56_RESULT_SHA, sha256(target)
    print("[PASS] patch 0433 applies to CI v55 source and reproduces expected SHA256")

    # --- behavioural model: never sleep, never validate a failed block -----
    model = textwrap.dedent(r"""
        #include <stdio.h>
        #include <string.h>
        #include <stdint.h>
        #define PAGE_SIZE 4096
        #define BLOCK_SIZE 16384
        #define FAULT_INDEX 1
        static unsigned long reads, fails, validated;
        static unsigned char file_block[BLOCK_SIZE];
        static unsigned char mapped_page[PAGE_SIZE];
        static unsigned char block[BLOCK_SIZE];

        static int hash_ok(const unsigned char *p) {
            unsigned int sum = 0;
            for (int i = 0; i < BLOCK_SIZE; i++) sum += p[i];
            return (sum & 0xff) == 0x78;
        }

        /* v56: allocation happens under the object lock, so it must not wait. */
        static int validate(int alloc_ok, int read_ok, int pager_same, int tampered) {
            memset(block, 0, sizeof(block));
            if (!alloc_ok) {
                fails++;
                return 0;                 /* secure one-page fallback */
            }
            reads++;
            if (!read_ok || !pager_same) {
                fails++;
                return 0;                 /* free buffer, fail closed */
            }
            memcpy(block, file_block, BLOCK_SIZE);
            memcpy(block + (FAULT_INDEX * PAGE_SIZE), mapped_page, PAGE_SIZE);
            if (tampered) block[(FAULT_INDEX * PAGE_SIZE) + 17] ^= 0xff;
            if (!hash_ok(block)) return 0;
            validated++;
            return 1;
        }

        int main(void) {
            for (int i = 0; i < BLOCK_SIZE; i++) file_block[i] = (unsigned char)(i & 0xff);
            unsigned int target = 0;
            for (int i = 0; i < BLOCK_SIZE; i++) target += file_block[i];
            file_block[0] = (unsigned char)(file_block[0] + ((0x78u - (target & 0xffu)) & 0xffu));
            memcpy(mapped_page, file_block + (FAULT_INDEX * PAGE_SIZE), PAGE_SIZE);

            if (validate(0, 1, 1, 0) != 0 || reads != 0 || fails != 1 || validated != 0) {
                printf("ALLOCFAIL=FAIL r=%lu f=%lu v=%lu\n", reads, fails, validated); return 1;
            }
            printf("ALLOCFAIL=OK r=%lu f=%lu\n", reads, fails);

            if (validate(1, 1, 1, 0) != 1 || reads != 1 || fails != 1 || validated != 1) {
                printf("READBACK=FAIL r=%lu f=%lu v=%lu\n", reads, fails, validated); return 2;
            }
            printf("READBACK=OK v=%lu\n", validated);

            if (validate(1, 1, 0, 0) != 0 || reads != 2 || fails != 2 || validated != 1) {
                printf("PAGER=FAIL r=%lu f=%lu v=%lu\n", reads, fails, validated); return 3;
            }
            printf("PAGER=OK f=%lu\n", fails);

            if (validate(1, 1, 1, 1) != 0 || validated != 1) {
                printf("TAMPER=FAIL v=%lu\n", validated); return 4;
            }
            printf("TAMPER=OK f=%lu\n", fails);
            return 0;
        }
    """)
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
    for marker in ("ALLOCFAIL=OK", "READBACK=OK", "PAGER=OK", "TAMPER=OK"):
        assert marker in out, out
    print("[PASS] model: no allocation wait; failed read/pager/tamper all fail closed")

    print("ALL M30 16K CS NOWAIT TESTS PASS")


if __name__ == "__main__":
    main()
