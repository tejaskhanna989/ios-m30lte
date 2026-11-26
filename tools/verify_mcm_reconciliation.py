#!/usr/bin/env python3
"""Strict post-build CI gate for the explicit MCM build input.

    sudo python3 tools/verify_mcm_reconciliation.py MOUNTED_ROOT INPUT.json

Prints only identifiers, UUIDs and status; never raw metadata bytes.  Exits
non-zero on any missing, changed or unexpected metadata mapping.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mcm_reconcile as mr  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('root', type=Path)
    ap.add_argument('input', type=Path)
    args = ap.parse_args()
    try:
        entries = mr.load_input(args.input)
        lines = mr.verify(args.root, entries)
    except mr.InputError as exc:
        print('FAIL', exc)
        return 1
    print(f'MCM reconciliation verified: {len(lines)}/{len(entries)} containers')
    for line in lines:
        print(line)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
