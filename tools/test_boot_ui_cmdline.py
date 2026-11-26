#!/usr/bin/env python3
"""Boot-arg invariants for native UI presentation with dormant-safe touch.

The M30 lockscreen path requires the kernel console to stop drawing when the
GUI presents. Keeping console on top (a5fb_keep_on=1 without
a5fb_noconsole=1) leaves the XNU log screen covering the UI. Touch is enabled
by its own boot args and must not affect the framebuffer/UI path.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATE = ROOT / "validation/ios-candidate-v77-ui-touch-out/cmdline.txt"
BASE = ("debug=0xc serial=3 cpus=6 keepsyms=1 maxmem=292 rd=emmcroot0 "
        "emmcroot=USERDATA emmcprobe=1 emmcwrite=1")


def main() -> None:
    assert CANDIDATE.is_file(), "v77 cmdline missing"
    cmdline = CANDIDATE.read_text().strip()
    assert cmdline.startswith(BASE), cmdline
    assert "a5fb_noconsole=1" in cmdline, "console must mute at GUI handoff"
    assert "a5fb_keep_on=1" in cmdline, "keep_on required by v68 baseline"
    assert "m30touch=1" in cmdline and "m30touchhid=1" in cmdline
    assert "m30sblockdiag" not in cmdline, "diagnostic sampler must stay off"
    assert "m30uihb" not in cmdline, "ui heartbeat must stay off"
    print("[PASS] UI cmdline: console mutes at handoff, touch enabled, sampler off")
    print("[PASS] cmdline:", cmdline)


if __name__ == "__main__":
    main()
