#!/usr/bin/env python3
"""Regression test for patch 0436 (v59: busy-peer CS overlay + fail reasons).

v58 proved SpringBoard launches but then aborts; CS_VALID is still stripped
from SpringBoard/backboardd. The v57 readback rejected a whole 16K block when
a non-faulting peer page was busy/cleaning, so those pages fell back to a
single 4K page and failed validation. v59 copies busy peers through phystokv()
instead of rejecting them; a torn read can only fail the full hash, never
bypass it. Per-reason counters cfa/cfi/cfp are replayed in the IRT heartbeat.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0436-m30-cs-busy-peer-overlay.patch"
BASE = ROOT / "milestone_artifacts/ci_45245697689/buildtree/unpacked/xnu/osfmk/vm/vm_fault.c"
BASE_SHA = "9193cd37cf769a68b362dffe8a48c3d7b443cd7a7202d409ea941ab7bac5339a"
RESULT_SHA = "98196f90fef3f7cc382678dbee83799b8bfd7893ac008ca0cefd0e8e262bf65d"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    text = PATCH.read_text()
    assert PATCH.name.startswith("0436-")
    assert "diff --git a/osfmk/vm/vm_fault.c b/osfmk/vm/vm_fault.c" in text
    assert "m30_cs_fail_alloc++" in text
    assert "m30_cs_fail_io++" in text
    assert "m30_cs_fail_pager++" in text
    assert 'csvok=%lu cfa=%lu cfi=%lu cfp=%lu' in text
    assert "Busy/cleaning peers are safe to copy through" in text
    assert "A torn read can only fail the full hash" in text
    # The old rejection paths must be gone from the added source.
    added = "\n".join(l[1:] for l in text.splitlines()
                      if l.startswith("+") and not l.startswith("+++"))
    assert "rpage->vmp_busy ||" not in added
    assert "lp->vmp_busy || lp->vmp_cleaning" not in added
    # Security invariants remain.
    assert "UIO_WRITE" not in text
    for bad in (
        "cs_enforcement_disable", "amfi_get_out_of_my_way",
        "launchd_unsecure_cache", "CSDebugDisable", "IO_NOAUTH",
        "VMP_CS_SET_VALIDATED", "vmp_cs_tainted = 0",
    ):
        assert bad not in text, bad
    print("[PASS] patch 0436: busy peers overlaid physically, fail reasons durable")

    assert BASE.exists() and sha256(BASE) == BASE_SHA, sha256(BASE)
    base_text = BASE.read_text()
    assert "vn_rdwr(UIO_READ" in base_text and "IO_NOCACHE" in base_text
    scratch_root = ROOT / ".test-tmp"
    scratch_root.mkdir(exist_ok=True)
    env = dict(os.environ, TMPDIR=str(scratch_root))
    with tempfile.TemporaryDirectory(dir=str(scratch_root)) as td:
        work = Path(td)
        (work / "osfmk/vm").mkdir(parents=True)
        target = work / "osfmk/vm/vm_fault.c"
        shutil.copy2(BASE, target)
        rel = work.relative_to(ROOT)
        subprocess.run(
            ["git", "apply", "--directory", str(rel), "-p1",
             str(PATCH.relative_to(ROOT))],
            cwd=str(ROOT), check=True, env=env,
            capture_output=True, text=True,
        )
        assert sha256(target) == RESULT_SHA, sha256(target)
    print("[PASS] patch 0436 applies to exact v58 CI source; hash reproduced")

    # Behavioural model: busy peer is still hashed from real bytes; tamper fails.
    model = r'''
        #include <stdio.h>
        #include <string.h>
        static unsigned char file[16384], mapped[16384], block[16384];
        static int full_hash_ok(const unsigned char *p) {
            unsigned sum = 0;
            for (int i = 0; i < 16384; i++) sum += p[i];
            return (sum & 0xff) == 0x5a;
        }
        static int validate(int busy_peer, int tampered) {
            memcpy(block, file, sizeof(block));
            memcpy(block + 4096, mapped + 4096, 4096);   /* kaddr/fault page */
            if (busy_peer) {
                /* v59: copy the peer's real physical bytes anyway */
                memcpy(block + 8192, mapped + 8192, 4096);
            }
            if (tampered) block[8192 + 17] ^= 0xff;
            return full_hash_ok(block);
        }
        int main(void) {
            for (int i = 0; i < 16384; i++) { file[i] = i & 0xff; mapped[i] = file[i]; }
            unsigned target = 0;
            for (int i = 0; i < 16384; i++) target += file[i];
            file[0] = (file[0] + ((0x5a - (target & 0xff)) & 0xff)) & 0xff;
            memcpy(mapped, file, sizeof(file));
            if (!validate(1, 0)) { printf("BUSY=FAIL\n"); return 1; }
            printf("BUSY=OK\n");
            if (validate(1, 1)) { printf("TAMPER=FAIL\n"); return 2; }
            printf("TAMPER=OK\n");
            return 0;
        }
    '''
    with tempfile.TemporaryDirectory(dir=str(scratch_root)) as td:
        c = Path(td) / "m.c"
        b = Path(td) / "m"
        c.write_text(model)
        subprocess.run(["cc", "-O0", "-Wall", "-Wextra", "-o", str(b), str(c)],
                       check=True, env=env)
        r = subprocess.run([str(b)], capture_output=True, text=True, env=env)
        assert r.returncode == 0 and "BUSY=OK" in r.stdout and "TAMPER=OK" in r.stdout, r.stdout
    print("[PASS] model: busy peer validated from real bytes; tamper still fails")

    print("ALL M30 CS BUSY-PEER OVERLAY TESTS PASS")


if __name__ == "__main__":
    main()
