#!/usr/bin/env python3
"""Regression test for patch 0444 (v67: nonblocking SwapWait + notify push).

v66 proved a blocking SwapWait regresses the UI transaction stream from five
presents to one. v67 removes the block and, after each present(), pushes a
completion notification to every registered IOMobileFramebuffer notification
type rather than only type 6. This is a behavioral fix attempt for the
backboardd transaction stall; it keeps the v62 security state, serial=3, and
USERDATA untouched.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
PATCH_0441 = ROOT / "xnu/patches-minimal/0441-m30-stderr-capture.patch"
PATCH_0442 = ROOT / "xnu/patches-minimal/0442-m30-framebuffer-commit-diag.patch"
PATCH_0443 = ROOT / "xnu/patches-minimal/0443-m30-framebuffer-swapwait-handshake.patch"
PATCH = ROOT / "xnu/patches-minimal/0444-m30-framebuffer-notify-push.patch"
PATCH_0451 = ROOT / "xnu/patches-minimal/0451-m30-melfas-touch.patch"
BASE = ROOT / "milestone_artifacts/ci_45356410574/buildtree/unpacked/xnu"
RESULT_SERIAL = "0567414c2f004778bba71a01b2723202af5bde98bf1ca6ec035856b086c2a772"
RESULT_SYS = "438bc8468900285491f4bd71be1cf89aa5f40874f0c7ff3ec37e7828138df94f"
RESULT_FB = "6d0c9f8820d71c62d0baa4112f2c5cf3015ce5329a23a697969607f86bfc0e39"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    t = PATCH.read_text()
    assert "diff --git a/iokit/Kernel/arm/SweetFramebuffer.cpp b/iokit/Kernel/arm/SweetFramebuffer.cpp" in t
    assert "never block the backboardd user-client thread" in t
    assert "-\t\t\tIOSleep(5000);" in t  # removed by this patch
    assert "for (uint32_t type = 0; type < SWEET_FB_NOTIFY_TYPES; type++)" in t
    assert "M30 FB: notify mask=" in t
    for bad in ("cs_enforcement_disable", "amfi_get_out_of_my_way",
                "launchd_unsecure_cache", "disable_security",
                "PE_initialize_console", "serial=3", "sweetfb_noconsole=1"):
        assert bad not in t, bad
    print("[PASS] patch 0444: nonblocking SwapWait and all-registered notify push")

    assert BASE.exists(), BASE
    scratch = ROOT / ".test-tmp"
    scratch.mkdir(exist_ok=True)
    env = dict(os.environ, TMPDIR=str(scratch))
    with tempfile.TemporaryDirectory(dir=str(scratch)) as td:
        work = Path(td)
        tree = work / "xnu"
        shutil.copytree(BASE, tree)
        rel = tree.relative_to(ROOT)
        for patch in (PATCH_0441, PATCH_0442, PATCH_0443, PATCH, PATCH_0451):
            subprocess.run(
                ["git", "apply", "--directory", str(rel), "-p1",
                 str(patch.relative_to(ROOT))],
                cwd=str(ROOT), check=True, env=env,
                capture_output=True, text=True,
            )
        assert sha256(tree / "pexpert/arm/pe_serial.c") == RESULT_SERIAL
        assert sha256(tree / "bsd/kern/sys_generic.c") == RESULT_SYS
        assert sha256(tree / "iokit/Kernel/arm/SweetFramebuffer.cpp") == RESULT_FB
        text = (tree / "iokit/Kernel/arm/SweetFramebuffer.cpp").read_text()
        assert "M30 FB: staged" in text and "M30 FB: done" in text
        assert "M30 FB: wait" in text and "M30 FB: notify mask" in text
        assert "for (int i = 0; i < 20" not in text
        report = subprocess.run(
            ["python3", str(ROOT / "tools/verify_m30_buildtree.py"),
             "--tree", str(tree), "--patch-dir", str(ROOT / "xnu/patches-minimal")],
            cwd=str(ROOT), check=True, env=env,
            capture_output=True, text=True,
        )
        verify = json.loads(report.stdout)
        assert verify["result"] == "PASS", verify
        assert len(verify["critical_patch_provenance"]) == 5
    print("[PASS] 0441+0442+0443+0444 apply in CI order; hashes and 0403 provenance reproduced")
    print("ALL M30 NOTIFY PUSH TESTS PASS")


if __name__ == "__main__":
    main()
