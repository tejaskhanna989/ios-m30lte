#!/usr/bin/env python3
"""Focused tests for the bounded, disabled-by-default lock-screen diagnostic."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0455-m30-lockscreen-diag.patch"
CI_TREE = Path("/home/tejas/opencode-work/v74-ci-buildtree/extracted/xnu")
BUILDTREE = CI_TREE if (CI_TREE / "bsd/dev/sweet_sample.c").is_file() else Path("/home/tejas/opencode-work/v68t-buildtree/xnu")


def main() -> None:
    assert PATCH.is_file(), "0455 lock-screen diagnostic patch missing"
    text = PATCH.read_text()
    # Gated by an explicit boot arg; no automatic activation.
    assert 'PE_parse_boot_argn("m30sblockdiag", &lsdiag' in text
    assert "if (lsdiag) {" in text
    # Bounded: 6 samples, then stops and clears the flag.
    assert "for (int i = 0; i < 6; i++)" in text
    assert "m30_ls_diag_enabled = 0;" in text
    assert "stopped after 6 samples" in text
    # Durable sink; never uses printf for SMP lines when enabled.
    assert "m30_pmsg_diag_line" in text
    assert "if (m30_ls_diag_enabled) m30_ls_diag_line(hdr); else printf" in text
    # Read-only: no SpringBoard/UI code, no input injection, no auth change.
    for banned in ("SBCoverSheet", "SBLockScreenManager", "sweet_hid_touch", "m30touch="):
        assert banned not in text, banned
    # Applies cleanly to the exact v68 buildtree with 0451/0453/0454 already applied.
    if (BUILDTREE / "bsd/dev/sweet_sample.c").is_file():
        r = subprocess.run(["git", "apply", "--check", str(PATCH)], cwd=BUILDTREE,
                           capture_output=True)
        assert r.returncode == 0, (r.stderr + r.stdout).decode()
        print("[PASS] 0455 applies to buildtree, gated, bounded, durable-only")
    else:
        print("[PASS] 0455 source checks (buildtree not present locally)")


if __name__ == "__main__":
    main()
