#!/usr/bin/env python3
"""Correlate framebuffer progression with known visual outcomes across captures.

Zero-risk analysis: reads only captures already on disk. No device access.

The question this answers: can any quantity observed in an existing pstore
capture distinguish a boot where the native lock screen appeared from one where
it did not?

It deliberately does NOT treat "no SWEET SURF records" as failure. The accepted
v68 capture - the boot where the lock screen DID appear - contains zero SWEET
SURF records, so their absence carries no information.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PB = ROOT / "validation/physical-boot-test"

# Visual outcome labels, from the project record. "seen" = native lock screen
# observed; "absent" = booted but no lock screen; "unknown" = not recorded.
OUTCOME = {
    "20261125-ios-v68-boot": "seen",
    "20261123-ios-v55-boot": "absent",
    "20261123-ios-v57-boot": "absent",
    "20261124-ios-v58-boot": "absent",
    "20261124-ios-v59-boot": "absent",
    "20261124-ios-v60-boot": "absent",
    "20261124-ios-v60-boot-long": "absent",
    "20261124-ios-v61-boot": "absent",
    "20261124-ios-v62-boot": "absent",
    "20261124-ios-v63-boot": "absent",
    "20261124-ios-v64-boot": "absent",
    "20261124-ios-v65-boot": "absent",
    "20261124-ios-v66-boot": "absent",
    "20261125-ios-v67-boot": "absent",
    "20261125-ios-v67-direct-boot": "absent",
    "20261125-ios-v68t-boot": "unknown",
    "20261125-ios-v69-boot": "absent",
    "20261125-ios-v70-boot": "absent",
    "20261126-ios-v68t-native-boot": "absent",
    "20261126-ios-v68t-uihb-boot": "unknown",
    "20261126-ios-v68t-uihb2-boot": "unknown",
    "20261126-v68t-sweetsample-boot": "unknown",
    "20261126-v73-rootfs-boot": "absent",
    "20261126-v74-lockdiag-boot": "absent",
    "20261127-v79-pstore": "absent",
}

FB_RE = re.compile(r"M30 FB: v=(\d+) sw=(\d+) pr=(\d+) copied=(\d+)")
UI_RE = re.compile(r"M30 UI: sb=(\d+) bb=(\d+)")
CRASH_RE = re.compile(r"CRASH (\w+)\[(\d+)\]")


def load_messages(path: Path) -> list[str]:
    """Return decoded record messages, handling both .json and .txt formats."""
    msgs: list[str] = []
    if path.suffix == ".json":
        try:
            data = json.loads(path.read_text(errors="ignore"))
        except json.JSONDecodeError:
            return msgs
        recs = data if isinstance(data, list) else data.get("records", [])
        for r in recs:
            if isinstance(r, dict):
                msgs.append(r.get("message", "") or "")
            elif isinstance(r, str):
                msgs.append(r)
    else:
        for line in path.read_text(errors="ignore").splitlines():
            if line.startswith("#") or not line.strip():
                continue
            if "XNU: " in line:
                msgs.append(line.split("XNU: ", 1)[1])
            elif ": " in line:
                msgs.append(line.split(": ", 1)[1])
    return msgs


def analyse(d: Path) -> dict:
    src = next((p for p in (d / "decoded-pmsg.json", d / "decoded-pmsg.txt") if p.is_file()), None)
    out: dict = {"capture": d.name, "outcome": OUTCOME.get(d.name, "unlabelled"),
                 "source": src.name if src else None}
    if src is None:
        out["error"] = "no decoded pmsg"
        return out
    msgs = load_messages(src)
    out["records"] = len(msgs)

    fb = []
    for m in msgs:
        g = FB_RE.search(m)
        if g:
            fb.append(tuple(int(x) for x in g.groups()))
    out["fb_records"] = len(fb)
    if fb:
        out["v_first"], out["v_last"] = fb[0][0], fb[-1][0]
        out["sw_max"] = max(f[1] for f in fb)
        out["pr_max"] = max(f[2] for f in fb)
        out["copied_max"] = max(f[3] for f in fb)
        out["copied_min"] = min(f[3] for f in fb)
        out["copied_distinct"] = len({f[3] for f in fb})
        # plateau: index of first record achieving copied_max
        out["copied_max_at"] = next(i for i, f in enumerate(fb) if f[3] == out["copied_max"])
        out["ticks_span"] = fb[-1][0] - fb[0][0]
    else:
        for k in ("v_first", "v_last", "sw_max", "pr_max", "copied_max",
                  "copied_min", "copied_distinct", "copied_max_at", "ticks_span"):
            out[k] = None

    out["sweet_surf"] = sum(1 for m in msgs if "SWEET SURF" in m)
    out["sampler_lines"] = sum(1 for m in msgs if m.startswith("SMP ") or " SMP " in m[:6])
    ui = [UI_RE.search(m) for m in msgs]
    ui = [u for u in ui if u]
    out["ui_records"] = len(ui)
    out["sb_alive"] = bool(ui) and any(int(u.group(1)) > 0 for u in ui)
    out["bb_alive"] = bool(ui) and any(int(u.group(2)) > 0 for u in ui)
    crashes = [CRASH_RE.search(m) for m in msgs]
    out["crash_records"] = len([c for c in crashes if c])
    out["crash_names"] = sorted({c.group(1) for c in crashes if c})
    return out


def main() -> int:
    rows = [analyse(d) for d in sorted(p for p in PB.iterdir() if p.is_dir())]
    rows = [r for r in rows if r.get("source")]
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)

    hdr = ("capture", "outcome", "recs", "fb", "sw", "pr", "copied_max",
           "dist", "surf", "smp", "sb", "bb", "crash")
    print(f"{'capture':34s} {'outc':8s} {'recs':>4s} {'fb':>4s} {'sw':>3s} {'pr':>3s} "
          f"{'copied_max':>12s} {'d':>2s} {'surf':>4s} {'smp':>4s} {'sb':>3s} {'bb':>3s} {'crash':>5s}")
    print("-" * 112)
    for r in rows:
        def f(k, w, dflt="-"):
            v = r.get(k)
            return f"{v:>{w}}" if v is not None else f"{dflt:>{w}}"
        print(f"{r['capture'][:34]:34s} {r['outcome'][:8]:8s} {f('records',4)} {f('fb_records',4)} "
              f"{f('sw_max',3)} {f('pr_max',3)} {f('copied_max',12)} {f('copied_distinct',2)} "
              f"{f('sweet_surf',4)} {f('sampler_lines',4)} {str(r.get('sb_alive'))[:3]:>3s} "
              f"{str(r.get('bb_alive'))[:3]:>3s} {f('crash_records',5)}")

    seen = [r for r in rows if r["outcome"] == "seen"]
    absent = [r for r in rows if r["outcome"] == "absent"]
    print()
    print(f"captures analysed: {len(rows)}   seen={len(seen)}  absent={len(absent)}")
    if seen:
        s = seen[0]
        print(f"\nBASELINE (lock screen seen): {s['capture']}")
        print(f"  framebuffer records : {s['fb_records']}")
        print(f"  SWEET SURF records  : {s['sweet_surf']}  <- zero in a WORKING boot")
        print(f"  copied= max         : {s['copied_max']:,} bytes, {s['copied_distinct']} distinct values")
        print(f"  sw/pr max           : {s['sw_max']}/{s['pr_max']}")
        print(f"  sampler lines       : {s['sampler_lines']}")
    if absent:
        print("\nABSENT-LOCKSCREEN captures, same fields:")
        for r in absent:
            cm = f"{r['copied_max']:,}" if r["copied_max"] is not None else "none"
            print(f"  {r['capture'][:34]:34s} fb={r['fb_records']:3d} copied_max={cm:>12s} "
                  f"sw={r['sw_max']} surf={r['sweet_surf']} sb={r['sb_alive']}")

    # Discriminating check: does any single field separate seen from absent?
    print("\nDISCRIMINATION TEST (does the field separate the classes?)")
    fields = ["sweet_surf", "fb_records", "copied_max", "sw_max", "sb_alive", "crash_records"]
    for fld in fields:
        sv = {r.get(fld) for r in seen}
        av = {r.get(fld) for r in absent}
        if fld == "copied_max":
            overlap = any(a is not None and a >= (min(x for x in sv if x) if any(sv) else 0) for a in av)
        else:
            overlap = bool(sv & av)
        verdict = "NOT DISCRIMINATING (classes overlap)" if overlap else "separates"
        print(f"  {fld:14s} seen={sorted(x for x in sv if x is not None)[:3]} "
              f"absent={sorted(x for x in av if x is not None)[:3]}  -> {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
