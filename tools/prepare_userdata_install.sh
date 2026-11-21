#!/bin/bash
# PRINT-ONLY preparation for installing a validated HFSX iOS root to USERDATA.
# EXECUTES NO WRITES. Run only with fresh explicit authorization for USERDATA.
set -euo pipefail
[[ $# -ge 1 ]] || { echo "usage: $0 VALIDATED_HFSX.img" >&2; exit 2; }
IMG=$(realpath "$1"); [[ -f "$IMG" ]] || { echo "MISSING: $IMG" >&2; exit 2; }
SIG=$(dd if="$IMG" bs=1 skip=1024 count=2 2>/dev/null | od -An -tx1 | tr -d ' \n')
[[ "$SIG" = "4858" ]] || { echo "REFUSING: image signature $SIG is not HFSX (4858)" >&2; exit 1; }
echo "Image: $IMG  $(stat -c %s "$IMG") bytes  sha256=$(sha256sum "$IMG"|cut -d' ' -f1)"
cat <<'EOF'
-- On the device in recovery (AUTH REQUIRED; nothing executed here): --
adb shell 'ls -l /dev/block/platform/13500000.dwmmc0/by-name/USERDATA'   # resolve mapping
adb shell 'blockdev --getsize64 /dev/block/<USERDATA>'                   # must exceed image size
adb push VALIDATED_HFSX.img /sdcard/ios-root.img
adb shell 'sha256sum /sdcard/ios-root.img'                               # compare to host hash
adb shell 'dd if=/sdcard/ios-root.img of=/dev/block/<USERDATA> bs=4M status=progress'
adb shell 'sync'
adb shell 'dd if=/dev/block/<USERDATA> bs=4M count=64 2>/dev/null | sha256sum'  # readback gate
-- Then flash ONLY BOOT with v11 (shim-boot.img) and boot once (separate auth). --
EOF
echo "NOTE: verify the verified USERDATA/personal-data backup before any write."
