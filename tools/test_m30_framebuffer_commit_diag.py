#!/usr/bin/env python3
"""Regression test for patch 0442 (v65: framebuffer commit-path diagnostics).

v62/v64 reach IRT state=3 with SpringBoard and backboardd alive and a clean
Apple logo, but the 16 KB pstore ring cannot prove whether backboardd's staged
swap was ever copied to the panel. a5fb_noconsole=1 also mutes the console
path after the first GUI present, so ordinary IOLog lines cannot reach the
console->pmsg mirror. Patch 0442 adds a direct, bounded pstore sink and
M30LTE-only counters for staged swaps, present() calls, copied bytes and skip
reasons. No serial output, userland behaviour or security state is changed.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0442-m30-framebuffer-commit-diag.patch"
BASE = ROOT / "milestone_artifacts/ci_45356410574/buildtree/unpacked/xnu"
RESULT_SERIAL = "058f8ade47a0288b0ba474fa309309018d49bb0a70095379baeb766196da6dbc"
RESULT_FB = "b3cc2d07adeb8503ab60e66febb98fb073ff41ad62815cccfe257f44d396054c"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    t = PATCH.read_text()
    assert "diff --git a/pexpert/arm/pe_serial.c b/pexpert/arm/pe_serial.c" in t
    assert "diff --git a/iokit/Kernel/arm/SweetFramebuffer.cpp b/iokit/Kernel/arm/SweetFramebuffer.cpp" in t
    assert "m30_pmsg_diag_line" in t
    assert "M30 FB:" in t
    assert "fSwapCalls" in t and "fPresentCalls" in t and "fPresentBytes" in t
    assert "fLastSkip" in t and "fPresentSkips" in t
    assert "a5fb_noconsole" in t and "a5fb_keep_on" in t
    assert "M30 FB: staged" in t
    assert "M30 FB: present" in t
    assert "M30 FB: v=" in t
    assert "M30 FB: power" in t
    assert "a5fb_noconsole mutes" in t or "sweet_console_muted" in t
    for bad in ("cs_enforcement_disable", "amfi_get_out_of_my_way",
                "launchd_unsecure_cache", "disable_security",
                "PE_initialize_console", "serial=3", "sweetfb_noconsole=1"):
        assert bad not in t, bad
    print("[PASS] patch 0442: bounded direct-pstore diagnostic only")

    assert BASE.exists(), BASE
    scratch = ROOT / ".test-tmp"
    scratch.mkdir(exist_ok=True)
    env = dict(os.environ, TMPDIR=str(scratch))
    with tempfile.TemporaryDirectory(dir=str(scratch)) as td:
        work = Path(td)
        (work / "pexpert/arm").mkdir(parents=True)
        (work / "iokit/Kernel/arm").mkdir(parents=True)
        serial = work / "pexpert/arm/pe_serial.c"
        fb = work / "iokit/Kernel/arm/SweetFramebuffer.cpp"
        shutil.copy2(BASE / "pexpert/arm/pe_serial.c", serial)
        shutil.copy2(BASE / "iokit/Kernel/arm/SweetFramebuffer.cpp", fb)
        rel = work.relative_to(ROOT)
        subprocess.run(
            ["git", "apply", "--directory", str(rel), "-p1",
             str(PATCH.relative_to(ROOT))],
            cwd=str(ROOT), check=True, env=env,
            capture_output=True, text=True,
        )
        assert sha256(serial) == RESULT_SERIAL, sha256(serial)
        assert sha256(fb) == RESULT_FB, sha256(fb)
        text = fb.read_text()
        assert text.count("M30 FB:") >= 5
        assert "m30_pmsg_diag_line(m30_start_line);" in text
        assert "m30_pmsg_diag_line(line);" in text
    print("[PASS] patch 0442 applies to exact v62 CI source; hashes reproduced")
    print("ALL M30 FRAMEBUFFER COMMIT DIAGNOSTIC TESTS PASS")


if __name__ == "__main__":
    main()
