#!/bin/bash
# M30 LTE QEMU boot test - Part 1: Build shim + generate ADT
# Usage: ./test-m30lte-qemu-simple.sh
#
# This builds the boot shim and generates the M30LTE Apple Device Tree.
# The kernel must be obtained separately (from CI build with MACHINE_CONFIG=M30LTE).

set -euo pipefail

REPO=~/Projects/m30lte-ios
cd "$REPO"

echo "=== M30 LTE QEMU Test: Build Shim + ADT ==="

# 1. Build the shim
echo "--- Building M30 shim ---"
cd "$REPO/shim"
bash build.sh 2>&1 | grep -E "error|Error|Image|shim-boot" || true
ls -la out/Image out/shim-boot.img

# 2. Generate the M30LTE ADT (QEMU mode)
echo "--- Generating M30LTE ADT ---"
cd "$REPO"
python3 tools/mkadt.py out/m30lte.adt --qemu
ls -la out/m30lte.adt

echo ""
echo "=== Build complete ==="
echo "Next: obtain the M30LTE kernel from CI (gh run download -n xnu-kernel)"
echo "Then: ./test-m30lte-qemu.sh <kernel>"
