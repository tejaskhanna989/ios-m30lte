#!/usr/bin/env python3
"""Regression test for patch 0434 (v57: exclude busy pages from 16K CS readback).

Why v56 was stopped before any physical flash
----------------------------------------------
v56 fixed the sleeping allocation (`Z_WAITOK` under the VM object lock) but
still called `vn_rdwr(UIO_READ, ..., IO_NOCACHE, ...)` over the entire 16K
block.  On this buildtree, `cluster_read()` still creates a UPL even with
`IO_NOCACHE`, and `vm_object_upl_request()` does `PAGE_SLEEP()` on any page with
`vmp_busy` or `vmp_cleaning`.  The faulting page is deliberately kept busy by
`vm_page_map_and_validate_cs()` while `vm_page_validate_cs_mapped_slow()` runs,
and the 16K range necessarily contains it.  That is a self-deadlock, so the
v56 CI run was cancelled and v56 was never flashed.

v57 fix
-------
Read only absent 4K slots from the vnode, one page at a time with the object
lock dropped.  The busy faulting page is hashed from `kaddr`; other resident
pages are hashed from their real physical bytes.  Any other busy/cleaning page
fails closed.  Pager identity and object life are rechecked after every lock
drop/reacquire.  No signature, hash, AMFI, trust-cache or page-validation check
is weakened.
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
PATCH_V57 = ROOT / "xnu/patches-minimal/0434-m30-cs-16k-no-busy-upl.patch"
V55_BASE = ROOT / "milestone_artifacts/ci_45219943492/buildtree/unpacked/xnu/osfmk/vm/vm_fault.c"
V56_SHA = "2d9997b3f7b72d82576ccb404193a924ca147236c70ef667ee6f3edd52db2775"
V57_SHA = "a10ab98b0506e521090402674b5ce533f1edb6e901350b39ce8c36e42365aa77"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    v56 = PATCH_V56.read_text()
    v57 = PATCH_V57.read_text()

    # --- patch content: no UPL request may include the busy faulting page ---
    assert PATCH_V57.name.startswith("0434-")
    assert "diff --git a/osfmk/vm/vm_fault.c b/osfmk/vm/vm_fault.c" in v57
    assert "boolean_t need_read[4];" in v57
    assert "boolean_t read_ok = TRUE;" in v57
    assert "lp == page" in v57
    assert "need_read[slot] = FALSE; /* kaddr below */" in v57
    assert "lp == VM_PAGE_NULL" in v57
    assert "need_read[slot] = TRUE;  /* file bytes */" in v57
    assert "lp->vmp_busy || lp->vmp_cleaning" in v57
    assert "vm_object_upl_request() sleeps on vmp_busy" in v57
    assert "M30_CS_DIAG(5," in v57
    assert "readbuf + (slot << PAGE_SHIFT)" in v57
    assert "(int)PAGE_SIZE," in v57
    assert "object->pager == pager" in v57
    assert "UIO_READ" in v57 and "UIO_WRITE" not in v57
    assert "IO_NOCACHE" in v57
    for bad in (
        "cs_enforcement_disable", "amfi_get_out_of_my_way",
        "launchd_unsecure_cache", "CSDebugDisable", "IO_NOAUTH",
        "VMP_CS_SET_VALIDATED", "vmp_cs_tainted = 0",
    ):
        assert bad not in v57, f"v57 patch must not contain {bad!r}"
    # v56's non-sleeping allocation and pager recheck stay in the chain.
    assert "Z_NOWAIT" in v56 and "readbuf == NULL" in v56
    assert "object->pager == pager" in v56
    print("[PASS] patch 0434: busy faulting page excluded; only absent slots read")

    # --- exact patch chain to the exact v55 CI source ----------------------
    assert V55_BASE.exists(), "exact v55 CI buildtree is required"
    base_sha = hashlib.sha256(V55_BASE.read_bytes()).hexdigest()
    assert base_sha == "ab3cf37eac16a1dbf91472335153ce6b92ef8daa3e5565103b8a92b75afe62dd", base_sha

    scratch_root = ROOT / ".test-tmp"
    scratch_root.mkdir(exist_ok=True)
    env = dict(os.environ, TMPDIR=str(scratch_root))
    with tempfile.TemporaryDirectory(dir=str(scratch_root)) as td:
        work = Path(td)
        target = work / "osfmk/vm/vm_fault.c"
        target.parent.mkdir(parents=True)
        shutil.copy2(V55_BASE, target)
        rel = work.relative_to(ROOT)
        for patch in (PATCH_V56, PATCH_V57):
            subprocess.run(
                ["git", "apply", "--directory", str(rel), "-p1",
                 str(patch.relative_to(ROOT))],
                cwd=str(ROOT), check=True, env=env,
                capture_output=True, text=True,
            )
        assert sha256(target) == V57_SHA, sha256(target)

    # Verify the intermediate v56 source hash independently.
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
        assert sha256(target) == V56_SHA, sha256(target)
    print("[PASS] 0433+0434 apply to CI v55 source; SHA256 a10ab98b... reproduced")

    # --- behavioural model: never issue I/O for the busy faulting page -----
    model = textwrap.dedent(r"""
        #include <stdio.h>
        #include <string.h>
        #define PAGE_SIZE 4096
        /* slot states: 0 = busy faulting page, 1 = absent, 2 = clean resident,
         * 3 = other busy/cleaning page, 4 = short read */
        static int need_read[4];

        static int prepare(const int state[4], int *reads) {
            int ok = 1;
            *reads = 0;
            memset(need_read, 0, sizeof(need_read));
            for (int i = 0; i < 4; i++) {
                if (state[i] == 0) {
                    need_read[i] = 0;          /* use kaddr, never UPL */
                } else if (state[i] == 1 || state[i] == 4) {
                    need_read[i] = 1;          /* file bytes (4 = short) */
                } else if (state[i] == 3) {
                    return 0;                  /* fail before any I/O */
                } else {
                    need_read[i] = 0;          /* physical bytes */
                }
            }
            for (int i = 0; i < 4; i++) {
                if (!need_read[i]) continue;
                (*reads)++;
                if (state[i] == 4) ok = 0;     /* short/failed read */
            }
            return ok;
        }

        int main(void) {
            int reads = 0;
            int a[4] = {0, 1, 2, 1};
            if (prepare(a, &reads) != 1 || reads != 2 || need_read[0] != 0) {
                printf("MIXED=FAIL reads=%d need0=%d\n", reads, need_read[0]); return 1;
            }
            printf("MIXED=OK reads=%d\n", reads);

            int b[4] = {0, 3, 1, 1};
            if (prepare(b, &reads) != 0 || reads != 0) {
                printf("BUSY=FAIL reads=%d\n", reads); return 2;
            }
            printf("BUSY=OK reads=%d\n", reads);

            int c[4] = {0, 1, 4, 1};
            if (prepare(c, &reads) != 0 || reads != 3) {
                printf("SHORT=FAIL reads=%d\n", reads); return 3;
            }
            printf("SHORT=OK reads=%d\n", reads);

            int d[4] = {0, 2, 2, 2};
            if (prepare(d, &reads) != 1 || reads != 0) {
                printf("RESIDENT=FAIL reads=%d\n", reads); return 4;
            }
            printf("RESIDENT=OK reads=%d\n", reads);
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
    for marker in ("MIXED=OK", "BUSY=OK", "SHORT=OK", "RESIDENT=OK"):
        assert marker in out, out
    print("[PASS] model: busy faulting page gets no I/O; busy peer/short read fail closed")

    print("ALL M30 16K CS NO-BUSY-UPL TESTS PASS")


if __name__ == "__main__":
    main()
