#!/bin/bash
# M30 LTE QEMU boot test - Part 2: Full boot test with kernel
# Usage: ./test-m30lte-qemu.sh <kernel.macho>
#
# Boots the M30LTE XNU kernel in QEMU with the M30LTE ADT.
# Requires: kernel (from CI build with MACHINE_CONFIG=M30LTE)
#
# Example:
#   gh run download <run-id> -R tejaskhanna989/ios-m30lte -n xnu-kernel -D /tmp/kernel
#   ./test-m30lte-qemu.sh /tmp/kernel/kernel.development.m30lte

set -euo pipefail

REPO=~/Projects/m30lte-ios
KERNEL="${1:-}"

if [ -z "$KERNEL" ]; then
    echo "Usage: $0 <kernel.macho>"
    echo ""
    echo "Obtain the kernel from CI:"
    echo "  gh run download <run-id> -R tejaskhanna989/ios-m30lte -n xnu-kernel -D /tmp/kernel"
    echo "  $0 /tmp/kernel/kernel.development.m30lte"
    exit 1
fi

if [ ! -f "$KERNEL" ]; then
    echo "ERROR: Kernel not found: $KERNEL"
    exit 1
fi

cd "$REPO"

echo "=== M30 LTE QEMU Full Boot Test ==="
echo "Kernel: $KERNEL"

OUTDIR="out/qemu-test"
mkdir -p "$OUTDIR"

# 1. Generate the M30LTE ADT (QEMU mode)
echo "--- Generating M30LTE ADT ---"
python3 tools/mkadt.py "$OUTDIR/m30lte.adt" --qemu

# 2. Pack the payload (kernel + ADT + cmdline)
echo "--- Packing M30LTXNU payload ---"
python3 tools/mkpayload.py "$KERNEL" "$OUTDIR/m30lte.adt" "$OUTDIR/payload.bin" \
    --cmdline 'debug=0xc serial=3 cpus=1 keepsyms=1 -enable_kprintf_spam rd=md0'

# 3. Run QEMU boot test
echo "--- Booting M30LTE in QEMU ---"
python3 tools/qemu-m30lte.py "$OUTDIR/payload.bin" "$OUTDIR" \
    --secs 40 \
    --kernel "$KERNEL" \
    --fail-on-panic

RC=$?
echo ""
echo "=== QEMU test exit code: $RC ==="
case $RC in
    0) echo "RESULT: QEMU boot completed, no panic observed" ;;
    1) echo "RESULT: QEMU exited early (possible boot failure)" ;;
    2) echo "RESULT: PANIC detected in QEMU boot" ;;
    3) echo "RESULT: Incomplete/blank framebuffer decode" ;;
    *) echo "RESULT: Unexpected exit code" ;;
esac

exit $RC
