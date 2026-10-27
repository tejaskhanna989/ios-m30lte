#!/bin/bash
# Full boot test for M30 LTE in QEMU
# This script builds all components and runs a QEMU test

set -euo pipefail

echo "=== Building M30 LTE QEMU test components ==="

# Build the shim for QEMU mode
echo "Building shim for QEMU mode..."
cd ~/Projects/m30lte-ios/shim
export SELECTED_DEVICE_M30LTE_QEMU=1
./build.sh qemu

echo "Building kernel and root image for M30..."
cd ~/Projects/m30lte-ios
# Build root image for M30
sudo tools/mkiosroot.sh OS.dmg SystemOS.dmg AppOS.dmg ios16-root-m30.img 16G

echo "Building boot image for QEMU..."
cd shim
./build.sh qemu

echo "=== Running QEMU test ==="
echo "Starting QEMU with M30 LTE configuration..."

# Run QEMU
qemu-system-aarch64 \
  -machine virt,gic-version=3 \
  -cpu cortex-a53 \
  -m 2048 \
  -kernel out/shim-boot-qemu.img \
  -initrd out/ramdisk.bin \
  -dtb ../dtb/boot_unpacked/dtb \
  -append "console=ttyAMA0 earlyprintk=serial,uart,0x9c000000,115200 earlyboot root=/dev/mmcblk0p2 ro" \
  -nographic \
  -s -S \
  -monitor stdio

echo "=== QEMU test completed ==="