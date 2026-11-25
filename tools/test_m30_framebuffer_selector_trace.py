#!/usr/bin/env python3
"""Regression test for patch 0445 (v68: bounded selector-input diagnostics).

The v68 ABI work proved from genuine iOS 16.7 IOMobileFramebuffer binaries
that selector 79 is a chunked byte-array read whose scalar inputs include a
block ID and byte offset.  The v67 pstore records only counts and sizes, so
the block IDs behind the 1580-byte and 40-byte reads are still unknown.
This patch logs those scalar inputs without changing any returned byte.
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
PATCHES = (
    "0441-m30-stderr-capture.patch",
    "0442-m30-framebuffer-commit-diag.patch",
    "0443-m30-framebuffer-swapwait-handshake.patch",
    "0444-m30-framebuffer-notify-push.patch",
    "0445-m30-framebuffer-selector-trace.patch",
)
PATCH = ROOT / "xnu/patches-minimal" / PATCHES[-1]
PATCH_0451 = "0451-m30-melfas-touch.patch"
BASE = ROOT / "milestone_artifacts/ci_45356410574/buildtree/unpacked/xnu"
RESULT_SERIAL = "0567414c2f004778bba71a01b2723202af5bde98bf1ca6ec035856b086c2a772"
RESULT_SYS = "438bc8468900285491f4bd71be1cf89aa5f40874f0c7ff3ec37e7828138df94f"
RESULT_FB = "695fd229053168433a2aec5b55af4d40d09d8f3a6508d3e02b7ffa7f131436e3"
TRACE_SELECTORS = (79, 74, 84, 50, 68, 55)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    t = PATCH.read_text()
    assert "diff --git a/iokit/Kernel/arm/SweetFramebuffer.cpp b/iokit/Kernel/arm/SweetFramebuffer.cpp" in t
    assert "M30 FB: ABI sel=" in t
    assert "sweet_fb_abi_trace_count[sel] < 4" in t
    for sel in TRACE_SELECTORS:
        assert f"sel == {sel}" in t, sel
        assert f"case {sel}:" not in t, f"selector {sel} must not gain a synthetic response"
    for bad in (
        "cs_enforcement_disable", "amfi_get_out_of_my_way",
        "launchd_unsecure_cache", "disable_security",
        "PE_initialize_console", "serial=3", "sweetfb_noconsole=1",
        "IOSleep(5000)", "notify-all",
    ):
        assert bad not in t, bad
    print("[PASS] patch 0445: bounded diagnostic only, no selector response")

    assert BASE.exists(), BASE
    scratch = ROOT / ".test-tmp"
    scratch.mkdir(exist_ok=True)
    env = dict(os.environ, TMPDIR=str(scratch))
    with tempfile.TemporaryDirectory(dir=str(scratch)) as td:
        work = Path(td)
        tree = work / "xnu"
        shutil.copytree(BASE, tree)
        for patch in PATCHES + (PATCH_0451,):
            subprocess.run(
                ["patch", "-p1", "-i", str(ROOT / "xnu/patches-minimal" / patch)],
                cwd=str(tree), check=True, env=env,
                capture_output=True, text=True,
            )
        assert sha256(tree / "pexpert/arm/pe_serial.c") == RESULT_SERIAL
        assert sha256(tree / "bsd/kern/sys_generic.c") == RESULT_SYS
        assert sha256(tree / "iokit/Kernel/arm/SweetFramebuffer.cpp") == RESULT_FB
        text = (tree / "iokit/Kernel/arm/SweetFramebuffer.cpp").read_text()
        assert "M30 FB: ABI sel=" in text
        assert "M30 FB: notify mask=" in text
        assert "for (int i = 0; i < 20" not in text
        # The zero-fill success path for these selectors is untouched.
        zero = text.index("for (uint32_t i = 0; i < args->scalarOutputCount; i++)")
        bzero = text.index("bzero(args->structureOutput, args->structureOutputSize);", zero)
        assert "args->scalarOutput[i] = i < outCount ? out[i] : 0;" in text[zero:bzero + 200]
        report = subprocess.run(
            ["python3", str(ROOT / "tools/verify_m30_buildtree.py"),
             "--tree", str(tree), "--patch-dir", str(ROOT / "xnu/patches-minimal")],
            cwd=str(ROOT), check=True, env=env,
            capture_output=True, text=True,
        )
        verify = json.loads(report.stdout)
        assert verify["result"] == "PASS", verify
        assert len(verify["critical_patch_provenance"]) == 5
    print("[PASS] 0441+0442+0443+0444+0445 apply in CI order; hashes and provenance reproduced")
    print("ALL M30 SELECTOR TRACE TESTS PASS")


if __name__ == "__main__":
    main()
