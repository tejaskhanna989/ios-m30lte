#!/usr/bin/env python3
"""Decode `sweetsample` kernel backtrace records from a decoded pmsg text file.

The XNU sampler prints, from `sweet_sample_thread()`/`sweet_sample_task()`:

    SMP --- sample 0
    SMP SpringBoard[27] slide 0x... mh 0x...
    SMP SpringBoard t0 pc 0x... lr 0x... sp 0x... bt 0x... 0x...
    ...

Frames are raw userspace addresses. Subtract the reported shared-cache slide
and symbolicate with the matching iOS 16.7.16 binary/dyld shared cache. This
tool only parses; it does not fabricate symbols.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HDR = re.compile(r"^SMP\s+(\S+)\[(\d+)\]\s+slide\s+(0x[0-9a-f]+)\s+mh\s+(0x[0-9a-f]+)")
THR = re.compile(r"^SMP\s+(\S+)\s+t(\d+)\s+pc\s+(0x[0-9a-f]+)\s+lr\s+(0x[0-9a-f]+)\s+sp\s+(0x[0-9a-f]+)\s+bt(.*)$")
SAMPLE = re.compile(r"^SMP\s+---\s+sample\s+(\d+)")


def decode(text: str) -> dict:
    samples: list[dict] = []
    current = None
    proc = None
    for line in text.splitlines():
        m = SAMPLE.match(line)
        if m:
            current = {"sample": int(m.group(1)), "processes": []}
            samples.append(current)
            proc = None
            continue
        if current is None:
            continue
        m = HDR.match(line)
        if m:
            proc = {"name": m.group(1), "pid": int(m.group(2)),
                    "slide": m.group(3), "mh": m.group(4), "threads": []}
            current["processes"].append(proc)
            continue
        m = THR.match(line)
        if m and proc is not None:
            frames = re.findall(r"0x[0-9a-f]+", m.group(6))
            proc["threads"].append({
                "index": int(m.group(2)), "pc": m.group(3), "lr": m.group(4),
                "sp": m.group(5), "frames": frames,
            })
    return {"samples": samples}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path, help="decoded pmsg text file")
    ap.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()
    result = decode(args.input.read_text(errors="replace"))
    out = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(out)
    else:
        print(out, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
