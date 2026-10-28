#!/bin/bash
# flash-ios.sh - Flash iOS boot image to Galaxy M30 via Odin/Heimdall
# Usage: sudo ./flash-ios.sh [boot-image-path]
#
# Prerequisites:
#   - Phone in download mode (Power + Vol Down + USB)
#   - heimdall installed
#   - User confirmed they want to flash iOS

set -euo pipefail

IMG="${1:-/home/tejas/Projects/m30lte-ios/shim/out/shim-boot.img}"

if [ ! -f "$IMG" ]; then
    echo "Error: boot image not found: $IMG"
    echo "Build it first: cd shim && ./build.sh /path/to/payload.bin"
    exit 1
fi

echo "=== iOS Flash Script for Galaxy M30 (m30lte) ==="
echo "Boot image: $IMG"
echo "Size: $(du -h "$IMG" | cut -f1)"
echo ""

# Check if phone is in download mode
echo "Checking for device in download mode..."
if ! heimdall detect 2>/dev/null; then
    echo ""
    echo "ERROR: No device detected in download mode!"
    echo ""
    echo "To enter download mode on Galaxy M30:"
    echo "  1. Power off the phone completely"
    echo "  2. Hold Power + Volume Down"
    echo "  3. Connect USB cable to PC"
    echo "  4. Keep holding until the download mode screen appears"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "Device detected in download mode!"
echo ""

# Confirm with user
echo "WARNING: This will overwrite the boot partition!"
echo "Make sure you have a backup of your stock Android boot.img."
echo -n "Continue flashing iOS? [y/N]: "
read -r CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "Flashing iOS boot image..."
heimdall flash --BOOT "$IMG" --no-reboot 2>&1

echo ""
echo "Rebooting device..."
heimdall --resume 2>&1

echo ""
echo "=== Flash complete ==="
echo "The phone should now reboot into iOS."
echo "Watch the screen for the Apple logo!"
echo ""
echo "If it boot-loops:"
echo "  1. Re-enter download mode (Power + Vol Down + USB)"
echo "  2. Flash stock Android back: heimdall flash --BOOT stock-boot.img"
echo ""
