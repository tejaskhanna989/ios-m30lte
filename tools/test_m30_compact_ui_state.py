#!/usr/bin/env python3
"""Regression test for patch 0440 (v62: compact frequent UI liveness line).

v61 showed backboardd rendering surfaces but no lock screen; the ring wrapped
before SpringBoard's final state could be seen. v62 prints `M30 UI: sb=.. bb=..
reason=..` every 30 s and keeps full backtraces only every fourth tick, so a
late pstore pull always contains UI liveness and the last NS reason.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0440-m30-compact-ui-state.patch"
BASE = ROOT / "milestone_artifacts/ci_45334020730/buildtree/unpacked/xnu/bsd/dev/sweet_sample.c"
BASE_SHA = "2af97866f307677d2feb11548cc2fcd469a77c66d3ceb5a5428cbc5ab09bdfde"
RESULT_SHA = "c7e92cc467a5c0fe062d8f4cd77dbe99c10a3909a4287dcd78c517963489fcf0"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    t = PATCH.read_text()
    assert "diff --git a/bsd/dev/sweet_sample.c b/bsd/dev/sweet_sample.c" in t
    assert "M30 UI: sb=%d bb=%d reason=%s" in t
    assert "tsleep(&chan, PZERO, \"sweetsmp\", 30 * hz)" in t
    assert "(i % 4) == 0" in t
    assert "extern char m30_last_crash_reason[]" in t
    for bad in ("cs_enforcement_disable", "amfi_get_out_of_my_way", "launchd_unsecure_cache"):
        assert bad not in t
    print("[PASS] patch 0440: compact UI liveness every 30s, full trace every 2min")

    assert BASE.exists() and sha256(BASE) == BASE_SHA, sha256(BASE)
    scratch = ROOT / ".test-tmp"
    scratch.mkdir(exist_ok=True)
    env = dict(os.environ, TMPDIR=str(scratch))
    with tempfile.TemporaryDirectory(dir=str(scratch)) as td:
        work = Path(td)
        (work / "bsd/dev").mkdir(parents=True)
        target = work / "bsd/dev/sweet_sample.c"
        shutil.copy2(BASE, target)
        rel = work.relative_to(ROOT)
        subprocess.run(
            ["git", "apply", "--directory", str(rel), "-p1",
             str(PATCH.relative_to(ROOT))],
            cwd=str(ROOT), check=True, env=env,
            capture_output=True, text=True,
        )
        assert sha256(target) == RESULT_SHA, sha256(target)
    print("[PASS] patch 0440 applies to exact v60 CI source; hash reproduced")
    print("ALL M30 COMPACT UI STATE TESTS PASS")


if __name__ == "__main__":
    main()
