#!/usr/bin/env python3
"""Verify the native lock-screen candidate restores the exact v68 boot args."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "validation/ios-candidate-v68t-native-out/manifest.json"
EXPECTED = ("debug=0xc serial=3 cpus=6 keepsyms=1 maxmem=292 rd=emmcroot0 "
            "emmcroot=USERDATA emmcprobe=1 emmcwrite=1 a5fb_noconsole=1 "
            "a5fb_keep_on=1")


def main():
    d = json.loads(MANIFEST.read_text())
    cl = d["payload"]["cmdline"]
    assert cl == EXPECTED, cl
    for arg in ("m30touch", "m30touchhid", "m30uihb"):
        assert arg not in cl, arg
    for arg in ("serial=3", "a5fb_noconsole=1", "a5fb_keep_on=1"):
        assert arg in cl, arg
    kernel = (ROOT / "validation/ios-candidate-v68t-native-out/inputs/kernel.development.m30lte").read_bytes()
    assert b"M30 TOUCH:" in kernel and b"M30 UI HB:" in kernel
    print("[PASS] native candidate: exact v68 cmdline, no M30 debug/HID/heartbeat args")
    print("[PASS] native candidate: driver+heartbeat compiled but dormant by default")


if __name__ == "__main__":
    main()
