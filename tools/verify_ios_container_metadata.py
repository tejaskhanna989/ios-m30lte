#!/usr/bin/env python3
"""Verify container metadata UUIDs and expected caches paths in a staged iOS root.

Read-only host verifier.  Returns non-zero when any container metadata UUID
does not match its directory name, or when a daemon's expected container
Library/Caches path is absent.
"""
from __future__ import annotations

import argparse
import os
import plistlib
import sys
from pathlib import Path

MCM_META = ".com.apple.mobile_container_manager.metadata.plist"
BASES = ("private/var/containers", "private/var/mobile/Containers")


def check(root: Path) -> list[str]:
    issues: list[str] = []
    for base in BASES:
        top = root / base
        if not top.is_dir():
            continue
        for path, _dirs, files in os.walk(top):
            if MCM_META not in files:
                continue
            meta = Path(path) / MCM_META
            try:
                with meta.open("rb") as fh:
                    data = plistlib.load(fh)
            except Exception as exc:
                issues.append(f"unreadable metadata {meta}: {exc}")
                continue
            want = Path(path).name
            got = data.get("MCMMetadataUUID")
            if got != want:
                issues.append(
                    f"{meta}: MCMMetadataUUID={got} but directory={want} "
                    f"identifier={data.get('MCMMetadataIdentifier')}"
                )
            if not (Path(path) / "Library/Caches").is_dir():
                issues.append(
                    f"{path}: missing Library/Caches for "
                    f"{data.get('MCMMetadataIdentifier')}"
                )
    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", type=Path, help="staged rootfs directory")
    args = ap.parse_args()
    issues = check(args.root)
    # A silent empty inventory must never pass the gate.
    found = sum(1 for base in ("private/var/containers", "private/var/mobile/Containers")
                for _p, _d, files in os.walk(args.root / base)
                if MCM_META in files)
    if found == 0:
        print("FAIL no MCM metadata records found (wrong user, path, or image)")
        return 1
    print(f"metadata records found: {found}")
    if issues:
        for line in issues[:50]:
            print("FAIL", line)
        print(f"RESULT: {len(issues)} container metadata issue(s)")
        return 1
    print("RESULT: container metadata UUIDs all match directory names")
    return 0


if __name__ == "__main__":
    sys.exit(main())
