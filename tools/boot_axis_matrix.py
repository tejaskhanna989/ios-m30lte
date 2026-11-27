#!/usr/bin/env python3
"""BOOT-axis revision comparison for Case #167 (offline, reproducible).

Builds a matrix of what each candidate boot actually changed on the BOOT axis,
using only records already in the repository.  Every cell is traceable to a
file; nothing here is inferred from a build log we do not have.

Columns are deliberately limited to what a capture can prove:
  * image hash           - from the boot record
  * heartbeats           - proves whether the 0446 cap was in the build
  * presents / done      - how much content the compositor ever produced
  * SBERR/NSException    - fatal-mode marker
  * M30 UI HB            - proves whether 0454's boot-arg path was armed

Usage:  python3 tools/boot_axis_matrix.py [--csv]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PT = ROOT / "validation/physical-boot-test"
sys.path.insert(0, str(ROOT / "tools"))

import summarize_pmsg_phase as sp  # noqa: E402

# (label, boot dir, outcome, patch set as recorded in the boot's own docs)
CANDIDATES = [
    ("v68", "20261125-ios-v68-boot", "PASS", "baseline"),
    ("v69", "20261125-ios-v69-boot", "A: fatal", "0446+0447+0448"),
    ("v70", "20261125-ios-v70-boot", "A: fatal", "0446 (cap)"),
    ("v68t", "20261125-ios-v68t-boot", "B: silent", "0446+touch"),
    ("v68t-native", "20261126-ios-v68t-native-boot", "B: silent", "0446+touch"),
    # The v81 capture is committed on origin/main but NOT on this branch; it is
    # reported as unavailable rather than silently omitted (see REPRODUCIBILITY).
    ("v81", "20261127-v81-v68boot-compat-pstore", "B: silent", "v68 BOOT"),
]


def first_hash(d: Path) -> str:
    for name in ("README.md", "analysis.txt"):
        p = d / name
        if p.exists():
            m = re.search(r"\b([a-f0-9]{64})\b", p.read_text(errors="ignore"))
            if m:
                return m.group(1)[:16]
    return "?"


def row(label: str, dirname: str, outcome: str, patches: str) -> dict:
    d = PT / dirname
    raw = d / "raw/pmsg-ramoops-0"
    if not raw.exists():
        raw = d / "pmsg-ramoops-0.bin"
    if not raw.exists():
        # v81 stored the pulled blob under its published name
        cands = sorted(d.glob("pmsg-ramoops-0*.bin"))
        raw = cands[0] if cands else raw
    if not raw.exists():
        return {"label": label, "err": "capture absent from this branch"}
    blob = raw.read_bytes()
    recs = sp.records(blob)
    s = sp.summarise(blob, label)
    sb = [r for r in recs if "SBERR" in r]
    fatal = any("libc++abi" in r or "NSException" in r for r in recs)
    return {
        "label": label,
        "outcome": outcome,
        "patches": patches,
        "image": first_hash(d),
        "heartbeats": s["hb_records"],
        "cap_0446": "yes" if s["hb_records"] <= 8 else "no",
        "presents": s["stalled_at"][1],
        "window_min": s["coverage_min"],
        "sberr": len(sb),
        "fatal": "YES" if fatal else "no",
        "uihb_armed": sum(1 for r in recs if "M30 UI HB" in r),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", action="store_true")
    args = ap.parse_args()
    rows = [row(*c) for c in CANDIDATES]
    cols = ["label", "outcome", "patches", "image", "heartbeats", "cap_0446",
            "presents", "window_min", "sberr", "fatal", "uihb_armed"]
    if args.csv:
        print(",".join(cols))
        for r in rows:
            print(",".join(str(r.get(c, "")) for c in cols))
        return 0
    w = max(len(r["label"]) for r in rows)
    print(f"{'boot':{w}}  {'outcome':9}  {'patches':12}  {'img':16}  "
          f"{'hb':4} {'cap':3} {'pres':4} {'win':5} {'SBERR':5} {'fatal':5} {'uihb'}")
    for r in rows:
        if r.get("err"):
            print(f"{r['label']:{w}}  {r['err']}")
            continue
        print(f"{r['label']:{w}}  {r['outcome']:9}  {r['patches']:12}  "
              f"{r['image']:16}  {r['heartbeats']:4d} {r['cap_0446']:3} "
              f"{r['presents']:4d} {r['window_min']:5.1f} {r['sberr']:5d} "
              f"{r['fatal']:5} {r['uihb_armed']}")
    print("\nKey: cap_0446=yes means the 0446 heartbeat cap is in the BOOT.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
