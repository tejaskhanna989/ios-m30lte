#!/usr/bin/env python3
"""Verify the native lock-screen candidate restores the exact v68 boot args.

v80 adds the accepted-kernel identity checks: the BOOT that physically showed
the lock screen (v68) and the later "native" rebuild must be distinguishable,
so a candidate can never claim v68 equivalence while carrying a different
kernel or a different patch set.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "validation/ios-candidate-v68t-native-out/manifest.json"
EXPECTED = ("debug=0xc serial=3 cpus=6 keepsyms=1 maxmem=292 rd=emmcroot0 "
            "emmcroot=USERDATA emmcprobe=1 emmcwrite=1 a5fb_noconsole=1 "
            "a5fb_keep_on=1")

# Accepted physical configuration (2026-11-25 lock-screen PASS).
V68_MANIFEST = ROOT / "validation/ios-candidate-v68-out/manifest.json"
V68_KERNEL_SHA256 = "b5e3b704a771fa7dc3e0afb23b7e2c99c7d251f7c8a4665ba0a0b5b16c163f83"
V68_BOOT_SHA256 = "629843b597fd665b7de6b6578a1605455ef5786ae9e06101b591d13a80bf8c50"
# Later rebuilds that were physically tested and did NOT show the lock screen.
LATER_REJECTED = (
    "validation/ios-candidate-v68t-out/manifest.json",
    "validation/ios-candidate-v68t-native-out/manifest.json",
    "validation/ios-candidate-v78-ui-exact-touch-out/manifest.json",
)


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

    # v80: the accepted BOOT identity is fixed and must not drift.
    v68 = json.loads(V68_MANIFEST.read_text())
    assert v68["kernel_source"]["sha256"] == V68_KERNEL_SHA256
    assert v68["images"]["ios-boot.img"]["sha256"] == V68_BOOT_SHA256
    for arg in ("m30touch", "m30touchhid", "m30uihb", "m30sblockdiag", "sweetsample"):
        assert arg not in v68["payload"]["cmdline"], arg
    print("[PASS] accepted v68 BOOT identity pinned (kernel + boot image)")

    # A rebuild that adds source patches cannot be byte-identical to v68 and
    # must not be reported as the accepted configuration.
    for rel in LATER_REJECTED:
        later = json.loads((ROOT / rel).read_text())
        assert later["kernel_source"]["sha256"] != V68_KERNEL_SHA256, rel
        assert later["images"]["ios-boot.img"]["sha256"] != V68_BOOT_SHA256, rel
    print("[PASS] every post-v68 rebuild is distinguishable from the accepted BOOT")


if __name__ == "__main__":
    main()
