#!/usr/bin/env python3
"""Tests for the sweetsample diagnostic candidate and backtrace decoder."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys_path = ROOT / "tools"
import sys
sys.path.insert(0, str(sys_path))
import decode_sweet_sample as dec  # noqa: E402

MANIFEST = ROOT / "validation/ios-candidate-v68t-sweetsample-out/manifest.json"
EXPECTED_BASE = ("debug=0xc serial=3 cpus=6 keepsyms=1 maxmem=292 rd=emmcroot0 "
                 "emmcroot=USERDATA emmcprobe=1 emmcwrite=1 a5fb_noconsole=1 "
                 "a5fb_keep_on=1")


def main():
    d = json.loads(MANIFEST.read_text())
    cl = d["payload"]["cmdline"]
    assert cl == EXPECTED_BASE + " sweetsample=SpringBoard,backboardd", cl
    print("[PASS] candidate cmdline = exact v68 + sweetsample=SpringBoard,backboardd")

    sample = """SMP --- sample 0
SMP SpringBoard[27] slide 0x12340000 mh 0x100000000
SMP SpringBoard t0 pc 0x12345678 lr 0x12345999 sp 0x16f0000000 bt 0x12346000 0x12346100
"""
    out = dec.decode(sample)
    s = out["samples"][0]
    p = s["processes"][0]
    assert s["sample"] == 0 and p["name"] == "SpringBoard" and p["pid"] == 27
    assert p["threads"][0]["frames"] == ["0x12346000", "0x12346100"]
    print("[PASS] decoder extracts sample/process/thread/frames without inventing symbols")


if __name__ == "__main__":
    main()
