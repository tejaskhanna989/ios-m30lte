#!/bin/bash
# Build + validate a genuine iOS HFSX root for the M30 (USERDATA target).
# USAGE: build_ios_root.sh OS.dmg SYSTEMOS.dmg APPOS.dmg OUT.img [SIZE]
# Example SIZE: 20G. Needs: apfs-fuse mkfs.hfsplus fsck.hfsplus rsync + sudo.
# Refuses to fabricate anything: all three genuine IPSW DMGs must be supplied.
set -euo pipefail
[[ $# -ge 4 ]] || { echo "usage: $0 OS.dmg SYSTEMOS.dmg APPOS.dmg OUT.img [SIZE]" >&2; exit 2; }
OS=$(realpath "$1"); SYS=$(realpath "$2"); APP=$(realpath "$3"); OUT=$(realpath -m "$4"); SIZE=${5:-20G}
for f in "$OS" "$SYS" "$APP"; do [[ -f "$f" ]] || { echo "MISSING DMG: $f" >&2; exit 2; }; done
[[ ! -e "$OUT" ]] || { echo "refusing to overwrite $OUT" >&2; exit 2; }
for t in apfs-fuse mkfs.hfsplus fsck.hfsplus rsync; do command -v "$t" >/dev/null || { echo "MISSING TOOL: $t" >&2; exit 2; }; done
command -v sudo >/dev/null && sudo -n true 2>/dev/null || { echo "passwordless sudo required (mount loop rw)" >&2; exit 2; }
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "Building HFSX root from genuine iOS DMGs ..."
"$ROOT/tools/mkiosroot.sh" "$OS" "$SYS" "$APP" "$OUT" "$SIZE"
echo "Applying M30 root tweaks ..."
MNT=$(mktemp -d /tmp/iosroot.XXXXXX)
sudo fsck.hfsplus -fy "$OUT" || true
sudo mount -t hfsplus -o loop,force,rw "$OUT" "$MNT"
sudo "$ROOT/tools/m30lte-root-tweaks.py" "$MNT"
sudo umount "$MNT"; rmdir "$MNT"
echo "Validating ..."
sudo fsck.hfsplus -n "$OUT"
SIG=$(sudo dd if="$OUT" bs=1 skip=1024 count=2 2>/dev/null | od -An -tx1 | tr -d ' \n')
[[ "$SIG" = "4858" ]] || { echo "FATAL: HFSX signature $SIG != 4858" >&2; exit 1; }
sudo mount -t hfsplus -o loop,force,ro "$OUT" "$MNT" || { mkdir -p "$MNT"; sudo mount -t hfsplus -o loop,force,ro "$OUT" "$MNT"; }
[[ -x "$MNT/sbin/launchd" ]] || { echo "FATAL: /sbin/launchd missing" >&2; sudo umount "$MNT"; exit 1; }
[[ -e "$MNT/System/Library/Caches/com.apple.dyld" ]] || echo "WARNING: dyld cache path missing"
sudo umount "$MNT"; rmdir "$MNT"
echo "RESULT: $OUT  size=$(stat -c %s "$OUT")  sha256=$(sha256sum "$OUT" | cut -d' ' -f1)  HFSX=0x4858  launchd=present"
