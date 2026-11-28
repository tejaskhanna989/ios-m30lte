#!/bin/sh
# Build a minimal HFSX ramdisk root from the VERIFIED v68 rootfs release.
#
# Host-only. No device access, no partition write, no USERDATA touch.
# Deterministic: every input is pinned by SHA-256 in minimal-jobs.json.
#
# Usage:
#   build_minimal_ramdisk.sh --check        # verify inputs/tools, no download
#   build_minimal_ramdisk.sh --build        # download, verify, extract, pack
#
# Output directory (outside git): $WORK (default /home/tejas/opencode-work/minimal-lockscreen-build)

set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO=$(CDPATH= cd -- "$HERE/../.." && pwd)
WORK=${WORK:-/home/tejas/opencode-work/minimal-lockscreen-build}
RELEASE=ios-root-20H392-44905109656
IMAGE_SHA=5f2e2aa6a80aea489946287d8cc32ef0ff6a1905a0d2923e8d4324163bb699b5

die() { echo "ERROR: $*" >&2; exit 1; }
info() { echo "[minimal] $*"; }

check_inputs() {
    python3 "$HERE/check_manifest.py" || die "manifest validation failed"
    for t in gh curl sha256sum gzip; do
        command -v "$t" >/dev/null 2>&1 || die "missing tool: $t"
    done
    for t in mkfs.hfsplus fsck.hfsplus; do
        command -v "$t" >/dev/null 2>&1 || \
            info "NOTE: $t missing (needed only for actual --build)"
    done
    [ -f "$REPO/tools/mkpayload.py" ] || die "mkpayload.py missing"
    info "stage 0 inputs OK; workdir=$WORK"
}

fetch_rootfs() {
    mkdir -p "$WORK/rootfs-parts"
    cd "$WORK/rootfs-parts"
    for p in aa ab ac ad; do
        f="ios-root-20H392.img.gz.part-$p"
        if [ ! -f "$f" ]; then
            info "downloading $f"
            gh release download "$RELEASE" -p "$f" --clobber
        fi
    done
    gh release download "$RELEASE" -p parts-sha256.txt -O parts-sha256.txt --clobber
    sha256sum -c parts-sha256.txt || die "part hashes do not match release"
    if [ ! -f "$WORK/ios-root-20H392.img" ]; then
        info "decompressing 4 parts to $WORK/ios-root-20H392.img"
        cat ios-root-20H392.img.gz.part-?? | gzip -dc > "$WORK/ios-root-20H392.img"
    fi
    got=$(sha256sum "$WORK/ios-root-20H392.img" | awk '{print $1}')
    [ "$got" = "$IMAGE_SHA" ] || die "rootfs image hash $got != $IMAGE_SHA"
    info "rootfs verified: $IMAGE_SHA"
}

case "${1:---check}" in
    --check) check_inputs ;;
    --build)
        check_inputs
        fetch_rootfs
        info "Stage 1 input ready. Mounting/extraction and ramdisk packing are"
        info "implemented in tools/make_ramdisk.py (next commit); this script"
        info "deliberately stops here so no partial artifact can be flashed."
        ;;
    *) die "usage: $0 [--check|--build]" ;;
esac
