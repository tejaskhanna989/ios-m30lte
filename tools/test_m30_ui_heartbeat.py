#!/usr/bin/env python3
"""Focused tests for patch 0453 (diagnostic-only UI heartbeat)."""
from __future__ import annotations

from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0453-m30-ui-heartbeat.patch"
BASE = ROOT / "milestone_artifacts/ci_45356410574/buildtree/unpacked/xnu"

LINE = ("M30 UI HB: sb=27 bb=57 reason=none irt=3 "
        "hid=unknown scene=unknown surface=unknown")


def main():
    t = PATCH.read_text()
    for token in (
        'PE_parse_boot_argn("m30uihb", &heartbeat, sizeof(heartbeat))',
        "int heartbeat = 0;",
        "for (int i = 0; i < 1800; i++)",
        '(void)tsleep(&chan, PZERO, "m30uihb", hz);',
        'printf("M30 UI HB: sb=%d bb=%d reason=%s irt=%d "',
        '"hid=unknown scene=unknown surface=unknown\\n"',
        "int m30_irt_state_snapshot(void) { return m30_irt_state; }",
        "stopped after 1800 samples",
    ):
        assert token in t, token
    print("[PASS] 0453: boot-arg disabled by default, 1s/1800-sample bound, fields")

    # No behavioral changes: no Melfas patch, no forbidden patches, no IRT writes.
    assert "m30lte_touch.c" not in t
    assert not [ln for ln in t.splitlines()
                if ln.startswith("+") and "m30_irt_state =" in ln]
    assert "sweet_hid_touch(" not in t
    for n in ("0446", "0447", "0448", "0449", "0450", "0452"):
        assert not list((ROOT / "xnu/patches-minimal").glob(f"{n}-*.patch")), n
    print("[PASS] 0453: no Melfas/IRT/HID behavior change; forbidden patches absent")

    # Heartbeat line format.
    m = re.fullmatch(
        r"M30 UI HB: sb=(\d+) bb=(\d+) reason=(\S+) irt=(\d+) "
        r"hid=(\S+) scene=(\S+) surface=(\S+)", LINE)
    assert m, LINE
    assert m.group(1) == "27" and m.group(2) == "57"
    assert m.group(4) == "3"
    assert m.group(5) == m.group(6) == m.group(7) == "unknown"
    print("[PASS] 0453: heartbeat format parses with measured/unknown fields")

    scratch = ROOT / ".test-tmp"
    scratch.mkdir(exist_ok=True)
    env = dict(os.environ, TMPDIR=str(scratch))
    with tempfile.TemporaryDirectory(dir=str(scratch)) as td:
        tree = Path(td) / "xnu"
        shutil.copytree(BASE, tree)
        subprocess.run(["patch", "-p1", "--dry-run", "-i", str(PATCH)], cwd=str(tree),
                       check=True, env=env, capture_output=True, text=True)
        tree2 = Path(td) / "xnu2"
        shutil.copytree(BASE, tree2)
        subprocess.run(["patch", "-p1", "-i", str(PATCH)], cwd=str(tree2),
                       check=True, env=env, capture_output=True, text=True)
        src = (tree2 / "bsd/dev/sweet_sample.c").read_text()
        assert "M30 UI HB:" in src and "m30uihb" in src
        fault = (tree2 / "osfmk/vm/vm_fault.c").read_text()
        assert "m30_irt_state_snapshot" in fault
    print("[PASS] 0453: patch applies to exact v68 buildtree")

    t4 = (ROOT / "xnu/patches-minimal/0454-m30-ui-hb-framebuffer.patch").read_text()
    for token in (
        'PE_parse_boot_argn("m30uihb", &hb_enabled, sizeof(hb_enabled))',
        "if ((++hb_ticks % 60) == 0)",
        "m30_ui_snapshot(&sb, &bb, &irt, &reason)",
        "M30 UI HB: sb=%d bb=%d reason=%s irt=%d",
        "hid=unknown scene=unknown surface=unknown",
    ):
        assert token in t4, token
    print("[PASS] 0454: framebuffer heartbeat gated, 1 Hz, measured/unknown fields")


if __name__ == "__main__":
    main()
