#!/usr/bin/env python3
"""Report the exact external inputs required to build a genuine iOS 16 root.

The M30 kernel already contains HFS+ / HFSX support (bsd/sweet_hfs) and the
eMMC driver accepts rd=emmcroot0 emmcroot=USERDATA. No APFS filesystem exists
in XNU open source (only kern_apfs_reflock, a lock primitive). Therefore the
proven path (see ios-m20lte-donor) is: download the genuine iOS IPSW, extract
its APFS DMGs, and convert them to a case-sensitive HFSX image with
tools/mkiosroot.sh + tools/m30lte-root-tweaks.py, then flash that image to the
device's USERDATA partition (requires physical authorization).

This tool checks, read-only, what is present and what is missing. It does not
download anything, fabricate images, or bypass personalization.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# iPhone X (iPhone10,3 / D22AP), iOS 16.7.16 (20H392) -- the donor-proven set.
IPSW_BUILD = "16.7.16 (20H392)"
IPSW_MODEL = "iPhone10,3 / D22AP"
DMGS = {
    "OS (rootfs)": "087-86698-044.dmg",
    "SystemOS (cryptex)": "087-86593-047.dmg",
    "AppOS (cryptex)": "087-86715-047.dmg",
}
HOST_TOOLS = ["apfs-fuse", "mkfs.hfsplus", "fsck.hfsplus", "rsync"]
ROOT_ASSETS = ["tools/mkiosroot.sh", "tools/m30lte-root-tweaks.py"]


def check() -> int:
    print("=== iOS root asset audit (read-only) ===")
    print(f"Required IPSW: {IPSW_MODEL}, iOS {IPSW_BUILD}")
    print("Filesystem format on device: HFSX (case-sensitive HFS+), NOT APFS")
    print("Kernel support: sweet_hfs HFS+/HFSX present; APFS filesystem absent\n")

    missing = 0
    print("--- local IPSW / DMG assets ---")
    found = []
    for base in (ROOT, Path("/home/tejas")):
        found += list(base.rglob("*.dmg")) + list(base.rglob("*.ipsw"))
    found = sorted(set(str(p) for p in found))
    if found:
        for p in found[:20]:
            print("  FOUND:", p)
    else:
        print("  NONE FOUND (no IPSW or DMG anywhere under repo or /home/tejas)")
        missing += 1

    print("\n--- required DMGs from the IPSW ---")
    for role, name in DMGS.items():
        print(f"  {role:22s}: {name}  (MISSING unless inside an IPSW above)")

    print("\n--- host tools needed by tools/mkiosroot.sh ---")
    for tool in HOST_TOOLS:
        ok = shutil.which(tool)
        print(f"  {tool:16s}: {ok or 'MISSING'}")
        if not ok:
            missing += 1

    print("\n--- root-image build scripts in repo ---")
    for rel in ROOT_ASSETS:
        p = ROOT / rel
        print(f"  {rel:32s}: {'present' if p.is_file() else 'MISSING'}")
        if not p.is_file():
            missing += 1

    print("\n--- genuine root image on device (requires physical check, not done) ---")
    print("  USERDATA must hold a genuine HFSX image containing /sbin/launchd.")
    print("  Current v10 boot selected SYSTEM (ext4) -> HFS signature 0x80b8 -> mount fail.")
    print("  Next candidate cmdline uses rd=emmcroot0 emmcroot=USERDATA.")

    print("\n=== RESULT ===")
    if missing:
        print(f"NOT READY: {missing} category/categories missing. USER ACTION REQUIRED:")
        print("  1. Download the genuine IPSW (iPhone10,3 / 16.7.16 / 20H392) from Apple.")
        print("  2. Provide the three DMGs above (or the IPSW) inside this repo.")
        print("  3. Install apfs-fuse, hfsprogs (mkfs.hfsplus/fsck.hfsplus), rsync on the host.")
        print("  4. Authorize building + flashing the HFSX image to USERDATA (physical).")
        return 1
    print("READY: all local inputs present (physical flash still needs authorization).")
    return 0


if __name__ == "__main__":
    raise SystemExit(check())
