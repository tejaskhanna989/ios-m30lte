# iOS candidate v6 — BOOT-only flash (readback pending)

## Authorization
Explicit user authorization: ONE controlled BOOT-only flash + ONE boot test of iOS candidate v6.

## Preconditions (all PASS)
- Branch main @ 6affd53 (verified before any action)
- Device identity: SM-M305F / M305FDDU8CVK1 / m30lte, ADB root, recovery 3.4.03.0.0-UNOFFICIAL
- BOOT -> /dev/block/mmcblk0p12, size 33554432
- Original BOOT backup SHA256 469c12d2d304ff4b2f07ea89ff1bc329a77f8f73037420aa260c9e68db441e78 (from git history), 33554432 B
- Candidate: validation/ios-candidate-v6-out/shim-boot.img
  SHA256 5bb27fb3d340ffe01e5667e2f136927a331a1752b7030fd31c2c84ab10f83c7f, 16236544 B
  (verified at write boundary immediately before flash)
- Current BOOT before write (read-only): header ANDROID!, image-region sha e24927982e578032aef367799571849bb8601666b0bfb063c46ad3fcdfafdc71 (different image, authorized overwrite)

## Actions performed
1. adb reboot download (exit 0)
2. heimdall detect -> "Device detected"
3. heimdall flash --BOOT /home/tejas/Projects/m30lte-ios/validation/ios-candidate-v6-out/shim-boot.img --no-reboot
   -> "BOOT upload successful", exit 0. Only BOOT written, no reboot by harness.

## State after flash
Device in Download Mode (heimdall detect OK, no ADB). No reboot issued.

## PENDING — readback gate (condition 4)
Readback requires the device back in recovery (Heimdall cannot read partitions in Download Mode):
  adb exec-out 'dd if=/dev/block/mmcblk0p12 bs=2048 count=7928 2>/dev/null' | sha256sum
Expected: 5bb27fb3d340ffe01e5667e2f136927a331a1752b7030fd31c2c84ab10f83c7f
(7928 * 2048 = 16,236,544 = exact candidate length)
BOOT TEST IS WITHHELD UNTIL EXACT READBACK MATCH IS CONFIRMED.
