#!/usr/bin/env python3
"""CI gate: read purplebuddy preferences from a mounted staged rootfs.

    sudo python3 tools/verify_setup_prefs.py MOUNTED_ROOT EXPECT_DONE

EXPECT_DONE is 'true' or 'false'. Fails closed on missing/malformed plists or
unexpected values. Prints only the two boolean values, never binary content.
"""
from __future__ import annotations

import argparse
import plistlib
import sys
from pathlib import Path

REL = "private/var/mobile/Library/Preferences/com.apple.purplebuddy.plist"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", type=Path)
    ap.add_argument("expect_done", choices=("true", "false"))
    args = ap.parse_args()
    path = args.root / REL
    if not path.is_file():
        print(f"FAIL missing {REL}")
        return 1
    try:
        data = plistlib.loads(path.read_bytes())
    except Exception as exc:
        print(f"FAIL malformed plist: {exc}")
        return 1
    for key in ("SetupDone", "SetupFinishedAllSteps"):
        if key not in data:
            print(f"FAIL missing key {key}")
            return 1
        if not isinstance(data[key], bool):
            print(f"FAIL {key} is not bool")
            return 1
    want = args.expect_done == "true"
    got_done = data["SetupDone"]
    got_finished = data["SetupFinishedAllSteps"]
    print(f"SetupDone={got_done} SetupFinishedAllSteps={got_finished}")
    if got_done != want or got_finished != want:
        print(f"FAIL expected both to be {want}")
        return 1
    print(f"PASS setup prefs match EXPECT_DONE={args.expect_done}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
