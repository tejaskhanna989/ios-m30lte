#!/usr/bin/env python3
"""Regression test for patch 0441 (v64: bounded SpringBoard stderr capture).

v63 proved that removing the serial console kills both console output and the
console->pmsg mirror, so the stderr/serial-stall hypothesis was wrong. The
remaining question is what SpringBoard is actually writing to fd 2 while its
main thread repeatedly samples in fprintf_stderr. This diagnostic copies at
most 190 bytes of the first 32 fd-2 writes from SpringBoard/backboardd into
the existing XNU pmsg ring. It changes no security state and no userland
behaviour.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0441-m30-stderr-capture.patch"
BASE = ROOT / "milestone_artifacts/ci_45356410574/buildtree/unpacked/xnu"
RESULT_SERIAL = "3a85e204a5a90639b8a60ee52be27e7ab40e0b959e4e191e35b1614d2263aa03"
RESULT_WRITE = "438bc8468900285491f4bd71be1cf89aa5f40874f0c7ff3ec37e7828138df94f"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    t = PATCH.read_text()
    assert "diff --git a/pexpert/arm/pe_serial.c b/pexpert/arm/pe_serial.c" in t
    assert "diff --git a/bsd/kern/sys_generic.c b/bsd/kern/sys_generic.c" in t
    assert "m30_stderr_capture" in t
    assert '"SBERR"' in t and '"BBERR"' in t
    assert "uap->fd == 2" in t
    assert "m30_stderr_seen < 32" in t
    assert "uint8_t line[190]" in t
    for bad in ("cs_enforcement_disable", "amfi_get_out_of_my_way",
                "launchd_unsecure_cache", "disable_security", "serial=3"):
        assert bad not in t, bad
    print("[PASS] patch 0441: bounded diagnostic only, no security change")

    assert BASE.exists(), BASE
    scratch = ROOT / ".test-tmp"
    scratch.mkdir(exist_ok=True)
    env = dict(os.environ, TMPDIR=str(scratch))
    with tempfile.TemporaryDirectory(dir=str(scratch)) as td:
        work = Path(td)
        (work / "pexpert/arm").mkdir(parents=True)
        (work / "bsd/kern").mkdir(parents=True)
        serial = work / "pexpert/arm/pe_serial.c"
        writefile = work / "bsd/kern/sys_generic.c"
        shutil.copy2(BASE / "pexpert/arm/pe_serial.c", serial)
        shutil.copy2(BASE / "bsd/kern/sys_generic.c", writefile)
        rel = work.relative_to(ROOT)
        subprocess.run(
            ["git", "apply", "--directory", str(rel), "-p1",
             str(PATCH.relative_to(ROOT))],
            cwd=str(ROOT), check=True, env=env,
            capture_output=True, text=True,
        )
        assert sha256(serial) == RESULT_SERIAL, sha256(serial)
        assert sha256(writefile) == RESULT_WRITE, sha256(writefile)
    print("[PASS] patch 0441 applies to exact v62 CI source; hashes reproduced")
    print("ALL M30 STDERR CAPTURE TESTS PASS")


if __name__ == "__main__":
    main()
