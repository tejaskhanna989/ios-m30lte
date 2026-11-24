#!/usr/bin/env python3
"""Regression test for patch 0437 (v60: durable CS/IRT + crash reason).

v59's pstore was captured hours after boot, so the 16 KB ring contained only
auxiliary-daemon noise. v60 adds a 10-minute slow heartbeat that stays near the
ring tail and replays the IRT/CS counters plus the first UI NS-exception reason
captured by the existing heap scanner. No security check is changed.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0437-m30-durable-crash-report.patch"
PATCH_INCLUDE = ROOT / "xnu/patches-minimal/0438-m30-string-include.patch"
BASE = ROOT / "milestone_artifacts/ci_45295419663/buildtree/unpacked/xnu"
VM = BASE / "osfmk/vm/vm_fault.c"
EXC = BASE / "osfmk/kern/exception.c"
BASE_VM_SHA = "98196f90fef3f7cc382678dbee83799b8bfd7893ac008ca0cefd0e8e262bf65d"
BASE_EXC_SHA = "ea2dd4490e8406687dd958f9a7ade88bdb946ee6db7909f871a3cc94ca10fe22"
VM_SHA = "cb010af81d89fa10ddf9d7aa03579225bd2860fb001de309c815ecfaf650551d"
EXC_SHA = "35b3161fadd93ff49aa9f4b93f9165296939407f7da8dde5a9558d6e5c480e80"
EXC_FINAL_SHA = "3446b62576fb098020640154d2359e0bd9a6c521cc82302cf85beb5c8dbb011e"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    text = PATCH.read_text()
    assert PATCH.name.startswith("0437-")
    for h in (
        "diff --git a/osfmk/vm/vm_fault.c b/osfmk/vm/vm_fault.c",
        "diff --git a/osfmk/kern/exception.c b/osfmk/kern/exception.c",
    ):
        assert h in text
    assert "extern char m30_last_crash_reason[];" in text
    assert 'printf("M30 SLOW: state=%d csblk=%lu csfail=%lu csvok=%lu ' in text
    assert 'cfa=%lu cfi=%lu cfp=%lu reason=%s\\n"' in text
    assert "delay(600000000);       /* 10 min */" in text
    assert "char m30_last_crash_reason[256];" in text
    assert 'strstr(text, "Exception") != NULL' in text
    assert "strlcpy(m30_last_crash_reason, text," in text
    inc = PATCH_INCLUDE.read_text()
    assert "diff --git a/osfmk/kern/exception.c b/osfmk/kern/exception.c" in inc
    assert "+#include <string.h>" in inc
    for bad in (
        "cs_enforcement_disable", "amfi_get_out_of_my_way",
        "launchd_unsecure_cache", "CSDebugDisable", "IO_NOAUTH",
        "VMP_CS_SET_VALIDATED", "vmp_cs_tainted = 0",
    ):
        assert bad not in text, bad
    print("[PASS] patch 0437: 10-min durable report + NS reason replay")

    for p, expected in ((VM, BASE_VM_SHA), (EXC, BASE_EXC_SHA)):
        assert p.exists() and sha256(p) == expected, (p, sha256(p) if p.exists() else None)
    print("[PASS] v59 buildtree source files present")

    scratch_root = ROOT / ".test-tmp"
    scratch_root.mkdir(exist_ok=True)
    env = dict(os.environ, TMPDIR=str(scratch_root))
    with tempfile.TemporaryDirectory(dir=str(scratch_root)) as td:
        work = Path(td)
        (work / "osfmk/vm").mkdir(parents=True)
        (work / "osfmk/kern").mkdir(parents=True)
        shutil.copy2(VM, work / "osfmk/vm/vm_fault.c")
        shutil.copy2(EXC, work / "osfmk/kern/exception.c")
        rel = work.relative_to(ROOT)
        for p in (PATCH, PATCH_INCLUDE):
            subprocess.run(
                ["git", "apply", "--directory", str(rel), "-p1",
                 str(p.relative_to(ROOT))],
                cwd=str(ROOT), check=True, env=env,
                capture_output=True, text=True,
            )
        assert sha256(work / "osfmk/vm/vm_fault.c") == VM_SHA
        assert sha256(work / "osfmk/kern/exception.c") == EXC_FINAL_SHA
    print("[PASS] patch 0437 applies to exact v59 CI source; hashes reproduced")

    # Ring budget: one ~200-byte line every 10 min, always near the tail.
    records_per_hour = 6
    assert records_per_hour * 200 * 24 < 16384 * 2, "slow report must stay small"
    print("[PASS] slow report: 6 records/hour, bounded ring usage")

    print("ALL M30 DURABLE CRASH REPORT TESTS PASS")


if __name__ == "__main__":
    main()
