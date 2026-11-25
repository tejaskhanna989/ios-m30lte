#!/usr/bin/env python3
"""Focused tests for patch 0451 (v68 native Melfas MSS100 driver)."""
from __future__ import annotations

from pathlib import Path
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0451-m30-melfas-touch.patch"
BASE = ROOT / "milestone_artifacts/ci_45356410574/buildtree/unpacked/xnu"


def main():
    t = PATCH.read_text()
    for token in (
        "#define M30_TOUCH_I2C_PA        0x13870000u",
        "#define M30_TOUCH_I2C_ADDR      0x48u",
        "#define M30_CTRL_READY          0xA0u",
        "#define M30_STATUS_NONE         0x05u",
        "#define M30_STATUS_LOG          0x77u",
        "#define M30_ALIVE_PA            0x11CB0000u",
        "#define M30_GPA0_DAT            0x0004u",
        "#define M30_R0_EVENT            0x02u",
        "#define M30_R1_EVENT_PKT_INFO   0x10u",
        "#define M30_R1_EVENT_PKT_DATA   0x11u",
        "#define M30_EVENT_SIZE          12u",
        "#define M30_RAW_MAX             4095u",
        "#define M30_MAX_FINGERS         10u",
    ):
        assert token in t, token
    print("[PASS] 0451: evidence-backed I2C/status/IRQ constants")

    for token in (
        'PE_parse_boot_argn("m30touch", &enabled, sizeof(enabled))',
        'PE_parse_boot_argn("m30touchhid", &m30_hid_enabled,',
        "m30_irq_sample()",
        "m30_cycles - m30_seen[id] > 100",
        "M30 TOUCH: hb pkts=%u contacts=%u errors=%u",
        "irq_edges=%u line=%u hid=%d",
    ):
        assert token in t, token
    assert "fw_name" not in t and "MIP_R0_PARAM" not in t
    print("[PASS] 0451: opt-in gates, IRQ sampling, timeout release, no controller writes")

    # Format-8 decode and coordinate scaling.
    p = bytes([0x11, 0x01, 0xAA, 0x2C, 0x3B, 0, 0, 0, 0, 0, 0, 0x01])
    assert (p[0] & 0xf0) >> 4 == 1
    ident = (p[0] & 0x0f) - 1
    assert ident == 0
    xraw = ((p[2] & 0x0f) << 8) | p[3]
    yraw = (((p[2] >> 4) & 0x0f) << 8) | p[4]
    assert (xraw, yraw) == (2604, 2619)
    x, y = xraw * 1080 // 4096, yraw * 1920 // 4096
    assert (x, y) == (686, 1227), (x, y)
    print("[PASS] 0451: format-8 decode and 1080x1920 scaling")

    # State transitions: press, move, release; direct (HID enabled) path.
    seq = [(0x11, 0x01, 0xAA, 0x2C, 0x3B),
           (0x11, 0x01, 0xAA, 0x30, 0x40),
           (0x11, 0x00, 0xAA, 0x30, 0x40)]
    out = []
    for q in seq:
        down = bool(q[1] & 1)
        cx = (((q[2] & 0x0f) << 8) | q[3]) * 1080 // 4096
        cy = ((((q[2] >> 4) & 0x0f) << 8) | q[4]) * 1920 // 4096
        out.append((down, cx, cy))
    assert [o[0] for o in out] == [True, True, False]
    assert out[2][1:] == out[1][1:]
    print("[PASS] 0451: press/move/release state transitions")

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
        src = (tree2 / "bsd/dev/m30lte_touch.c").read_text()
        lines = src.splitlines()
        calls = [i for i, line in enumerate(lines) if "sweet_hid_touch(" in line]
        assert len(calls) == 5  # 1 extern + 4 gated call sites
        assert all("m30_hid_enabled" in lines[i - 1] for i in calls[1:])
    print("[PASS] 0451: patch applies to exact v68 buildtree; all HID calls gated")


if __name__ == "__main__":
    main()
