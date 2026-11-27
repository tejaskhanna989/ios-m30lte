#!/usr/bin/env python3
"""Summarise a captured pmsg ring by boot phase (v82).

The ramoops pmsg zone is a RING: after it fills, the newest bytes overwrite the
oldest, so the byte order in a pull is circular and the decoded text order is
not the boot order.  This tool does the two things the earlier analyses did not:

1. Recover the monotonic boot phase of the captured window, using markers that
   only occur once and early (the IRT release-type patch, surf/framebuffer
   setup) versus markers that continue forever (the 10 s framebuffer heartbeat).
2. Report the swap/present/wait counters, which is where a backboardd stall is
   actually visible.

No device access, no writes; it only reads files under validation/.
"""
from __future__ import annotations

import argparse
import re
import struct
import sys
from pathlib import Path

REC_HDR = 19
REC_MAGIC = 0x6C
TAG = b"XNU"
VSYNC_US = 16667          # AppleCLCD fVsync period (M30Framebuffer.cpp)
FIRST_HB_V = 600          # first status line is the 600th vsync tick


def records(blob: bytes) -> list[str]:
    """Resynchronise on valid record boundaries (never trusts the length byte)."""
    out, i = [], 0
    while i < len(blob) - REC_HDR - 3:
        if (blob[i] == REC_MAGIC and REC_HDR <= blob[i + 1] <= 255
                and blob[i + REC_HDR:i + REC_HDR + 3] == TAG):
            end = i + blob[i + 1]
            out.append(blob[i + REC_HDR + 3:end - 1].decode("latin1"))
            i = end
        else:
            i += 1
    return out


def zone(blob: bytes) -> dict:
    start, size = struct.unpack_from("<II", blob, 4)
    cap = len(blob) - 12
    return {"start": start, "size": size, "capacity": cap,
            "full": size >= cap, "wrapped": size >= cap and start != 0}


def summarise(blob: bytes, label: str) -> dict:
    recs = records(blob)
    z = zone(blob)
    # Only the periodic status line carries the boot clock; the other M30 FB
    # lines also print sw/pr/copied but are not heartbeat samples.
    pairs = [(int(m.group(1)), tuple(map(int, m.groups()[1:])))
             for r in recs
             for m in [re.search(r"M30 FB: v=(\d+) sw=(\d+) pr=(\d+) copied=(\d+)", r)] if m]
    hb = [v for v, _ in pairs]
    stalled = [s for _, s in pairs]
    waits = [int(m.group(1)) for r in recs
             for m in [re.search(r"M30 FB: wait #(\d+)", r)] if m]
    dones = [int(m.group(1)) for r in recs
             for m in [re.search(r"M30 FB: done #(\d+)", r)] if m]
    present = [int(m.group(1)) for r in recs
               for m in [re.search(r"M30 FB: present #(\d+)", r)] if m]
    # IRT "patched" records only appear during early boot / release-type setup.
    early = any("M30 IRT" in r and "patched" in r for r in recs)
    # SWEET AKS lines appear from the first userland keystore client onwards;
    # a window with none is either pre-userland or a boot where no client asked.
    aks = sum(1 for r in recs if "SWEET AKS" in r)
    aks_lockfail = sum(1 for r in recs
                       if "SWEET AKS: securityd sel 10 " in r
                       and "0xe00002c7" in r)
    # A captured window that still shows the freeze heartbeat is a boot head.
    if hb:
        flat = max(stalled) if stalled else (0, 0, 0)
        flat_at = next((v for v, s in zip(hb, stalled) if s == flat), hb[0])
        # The ring covers from boot start to its newest sample, so the window
        # END is max_v.  flat_at is where the present counters stop moving.
        coverage = max(hb) * VSYNC_US / 1e6 / 60.0
        # the boot clock at which the present counter last moved
        present_stop = hb[-1]
        for (v0, prev), (v1, curr) in zip(pairs, pairs[1:]):
            if prev[1] != curr[1]:
                present_stop = v1
    else:
        flat, flat_at, coverage = (0, 0, 0), 0, 0.0
        present_stop = 0
    return {
        "label": label, "records": len(recs), "zone_full": z["full"],
        "hb_records": len(hb), "max_v": max(hb) if hb else 0,
        "coverage_min": round(coverage, 1),
        "flat_at_min": round(flat_at * VSYNC_US / 1e6 / 60.0, 1),
        "present_stop_min": round(present_stop * VSYNC_US / 1e6 / 60.0, 1),
        "window": "head" if early else "tail",
        "staged": len(present), "present": len(present),
        "done_max": max(dones) if dones else 0,
        "wait_max": max(waits) if waits else 0,
        "stalled_at": flat,
        "aks": aks,
        "aks_lockfail": aks_lockfail,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--csv", action="store_true")
    args = ap.parse_args()
    rows = [summarise(p.read_bytes(), p.parent.name) for p in args.paths]
    cols = ["label", "records", "zone_full", "window", "hb_records", "max_v",
            "coverage_min", "staged", "present", "done_max", "wait_max",
            "stalled_at", "aks", "aks_lockfail", "present_stop_min"]
    if args.csv:
        print(",".join(cols))
        for r in rows:
            print(",".join(str(r[c]) for c in cols))
        return 0
    w = max(len(r["label"]) for r in rows)
    print(f"{'boot':{w}}  {'window':4}  {'cov(min)':8}  {'done':4}  {'wait':4}  "
          f"{'sw/pr/copied (flat)':22}  {'AKS':4}  {'lockfail':8}  ok?")
    for r in rows:
        sw, pr, copied = r["stalled_at"]
        # A boot cannot have produced a UI frame if backboardd out-waited presents.
        suspect = "STALL" if r["wait_max"] > r["done_max"] else "-"
        print(f"{r['label']:{w}}  {r['window']:4}  {r['coverage_min']:8.1f}  "
              f"{r['done_max']:4d}  {r['wait_max']:4d}  "
              f"{sw}/{pr}/{copied:<14}  {r['aks']:4d}  {r['aks_lockfail']:8d}  {suspect}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
