#!/bin/bash
# Simple test script for M30 LTE QEMU build

echo "Building M30 LTE shim for QEMU..."

# Build the shim for QEMU mode
cd ~/Projects/m30lte-ios/shim
./build.sh qemu

echo "Build complete!"