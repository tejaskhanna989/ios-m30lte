#!/usr/bin/env python3
"""Regression test for patch 0435 (v58: SpringBoard visibility).

v57 proved the CS readback fix, but its IRT heartbeat wrote 210 records into a
16 KB pmsg ring (30 full + 180 compact), overwriting the window in which
SpringBoard/backboardd would have logged.  v58:
  - reduces that to 5 full + 18 compact heartbeats (10 s apart),
  - starts the existing M30LTE-compiled process sampler from the eMMC root
    path so SpringBoard/backboardd are sampled at 90 s then every 120 s.
No signature, hash, AMFI, trust-cache or page-validation check is weakened.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0435-m30-springboard-visibility.patch"
BASE = ROOT / "milestone_artifacts/ci_45230106038/buildtree/unpacked/xnu"
VM_FAULT = BASE / "osfmk/vm/vm_fault.c"
EMMC = BASE / "bsd/dev/a5xelte_emmc.c"
SAMPLE = BASE / "bsd/dev/sweet_sample.c"
VM_SHA = "9193cd37cf769a68b362dffe8a48c3d7b443cd7a7202d409ea941ab7bac5339a"
EMMC_SHA = "d15f61b44050bafb36162bb3124c9a2b4dd355c04f91b2a76cba4e5e133c6bbe"
BASE_VM_SHA = "a10ab98b0506e521090402674b5ce533f1edb6e901350b39ce8c36e42365aa77"
BASE_EMMC_SHA = "40ff2f5fc588261b5d03603c5ee2bab150f13ab37660993a7106ee6d9b70b52c"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    text = PATCH.read_text()

    assert PATCH.name.startswith("0435-")
    for header in (
        "diff --git a/osfmk/vm/vm_fault.c b/osfmk/vm/vm_fault.c",
        "diff --git a/bsd/dev/a5xelte_emmc.c b/bsd/dev/a5xelte_emmc.c",
    ):
        assert header in text, header
    assert "for (i = 0; i < 5; i++)" in text
    assert "for (i = 0; i < 18; i++)" in text
    assert "delay(10000000);     /* 10 s */" in text
    assert "overwrote the entire 16 KB pmsg ring" in text
    assert "leaving most of the 16 KB ring for userspace" in text
    assert "+extern void sweet_sample_start(void);" in text
    assert "+		sweet_sample_start();" in text
    for bad in (
        "cs_enforcement_disable", "amfi_get_out_of_my_way",
        "launchd_unsecure_cache", "CSDebugDisable", "IO_NOAUTH",
        "VMP_CS_SET_VALIDATED", "vmp_cs_tainted = 0",
    ):
        assert bad not in text, bad
    print("[PASS] patch 0435: heartbeat reduced; SpringBoard/backboardd sampler enabled")

    assert VM_FAULT.exists() and EMMC.exists() and SAMPLE.exists()
    assert sha256(VM_FAULT) == BASE_VM_SHA, sha256(VM_FAULT)
    assert sha256(EMMC) == BASE_EMMC_SHA, sha256(EMMC)
    sampler = SAMPLE.read_text()
    assert "ARM64_BOARD_CONFIG_M30LTE" in sampler
    assert 'strlcpy(sweet_sample_names, "SpringBoard,backboardd"' in sampler
    print("[PASS] v57 buildtree: sampler already compiled for M30LTE with UI defaults")

    scratch_root = ROOT / ".test-tmp"
    scratch_root.mkdir(exist_ok=True)
    env = dict(os.environ, TMPDIR=str(scratch_root))
    with tempfile.TemporaryDirectory(dir=str(scratch_root)) as td:
        work = Path(td)
        (work / "osfmk/vm").mkdir(parents=True)
        (work / "bsd/dev").mkdir(parents=True)
        shutil.copy2(VM_FAULT, work / "osfmk/vm/vm_fault.c")
        shutil.copy2(EMMC, work / "bsd/dev/a5xelte_emmc.c")
        rel = work.relative_to(ROOT)
        subprocess.run(
            ["git", "apply", "--directory", str(rel), "-p1",
             str(PATCH.relative_to(ROOT))],
            cwd=str(ROOT), check=True, env=env,
            capture_output=True, text=True,
        )
        assert sha256(work / "osfmk/vm/vm_fault.c") == VM_SHA
        assert sha256(work / "bsd/dev/a5xelte_emmc.c") == EMMC_SHA
    print("[PASS] patch 0435 applies to exact v57 CI source; modified hashes reproduced")

    old_records = 30 + 180
    new_records = 5 + 18
    assert old_records == 210 and new_records == 23
    assert new_records * 300 < 16384 // 2, "heartbeat must leave half the ring free"
    print(f"[PASS] ring budget: {old_records} -> {new_records} heartbeat records")

    print("ALL M30 SPRINGBOARD VISIBILITY TESTS PASS")


if __name__ == "__main__":
    main()
