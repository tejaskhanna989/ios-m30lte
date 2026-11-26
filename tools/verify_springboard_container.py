#!/usr/bin/env python3
"""CI gate: the staged rootfs must contain SpringBoard's native MCM container."""
from __future__ import annotations

import argparse
import importlib.util
import plistlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "m30lte_root_tweaks", ROOT / "tools" / "m30lte-root-tweaks.py")
tweaks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tweaks)
MCM_META = tweaks.MCM_META
UI_DAEMON_CONTAINERS = tweaks.UI_DAEMON_CONTAINERS


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", type=Path)
    args = ap.parse_args()
    ident, uuid = next(iter(UI_DAEMON_CONTAINERS.items()))
    d = args.root / "private/var/containers/Data/System" / uuid
    if not d.is_dir():
        print(f"FAIL missing SpringBoard container {uuid}")
        return 1
    if not (d / "Library/Caches").is_dir():
        print("FAIL SpringBoard container has no Library/Caches")
        return 1
    meta = d / MCM_META
    if not meta.is_file():
        print("FAIL SpringBoard container has no MCM metadata")
        return 1
    try:
        data = plistlib.loads(meta.read_bytes())
    except Exception as exc:
        print(f"FAIL SpringBoard metadata is malformed: {exc}")
        return 1
    if data.get("MCMMetadataIdentifier") != ident or data.get("MCMMetadataUUID") != uuid:
        print("FAIL SpringBoard metadata values do not match")
        return 1
    print(f"PASS SpringBoard container {ident} {uuid} present with metadata")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
