# iOS candidate v8 — single BOOT flash + one boot attempt (objective record)

## Authorization / deviations

Exactly one BOOT flash was performed with the v8 image; exactly one boot of the
flashed image occurred. No other flash, reboot, retry or partition write.

**Deviation to report honestly:** the intended pre-boot BOOT readback gate was
**not completed** — the readback command was interrupted (no readback file was
produced) and the device exited Download Mode directly into the flashed v8
image. No boot command was issued by the harness. The flash itself passed the
candidate hash gate at the write boundary and Heimdall reported
"BOOT upload successful". A post-boot BOOT readback was attempted but the ADB
connection dropped mid-transfer (`boot-readback-postboot.img` is a partial
2,605,056-byte capture, not a valid full readback).

## Pre-flight (PASS)

- `main` @ `1a6bc38`; v8 candidate SHA-256
  `c9f6d20de46ef1681ea98184e93c50614062666636f2faeb88aeb90fb9901c2c` matched.
- Device: serial `320081735bb166a3`, bootloader `M305FDDU8CVK1`,
  `ro.product.device=m30lte`, manufacturer samsung (SM-M305F family), ADB root.
- BOOT -> `/dev/block/mmcblk0p12` (33554432 B), RECOVERY -> p13 untouched.
- Original BOOT backup `m30-boot-original/boot.img` hash
  `469c12d2d304ff4b2f07ea89ff1bc329a77f8f73037420aa260c9e68db441e78` intact.
- BOOT before write contained the prior v7 image (`6e1fcfab…f998dd`).

## Key result: first genuine XNU log recovered

`pmsg-postboot.bin` (7331 B) decodes to 89 records, 0 issues: 68 `XNU`, 16
`adbd`, 4 `ArmToArm64Assembler`, 1 `cutils-trace`. The `XNU` records contain a
verbatim boot log: `Darwin Kernel Version 22.6.0 ... xnu-8796.141.3`, VM/pmap
bootstrap, vnguard, platform expert, AppleKeyStore, IOWatchdog,
IOCoreSurfaceRoot, HID buttons/touch, AppleCLCD and the 30 Hz line. This
**physically proves** the repaired 0406 pmsg mirror works and its records
survive XNU->TWRP. (Raw user screen transcription preserved in
`screen-observation.txt`.)

**No** `M30 ROOT:`, `A5XELTE eMMC:`, or `BSD root:` record exists. The last XNU
record is `A5XELTE FB: requested 30 Hz, effective 30 Hz, copy timing on`.
`last_kmsg-postboot.txt` confirms S-Boot loaded our BOOT image
(`kernel size = 0xf7b800` + 2048 B header = 16,236,544 B = v8) and
`Starting kernel at 0x80080000...`, followed by PINRST and recovery.

## Conclusion

S-Boot accepted and entered our image once. XNU executed through VM bootstrap,
IOKit service matching (including touch registration) and framebuffer startup.
It did **not** emit any BSD/root-stage marker. Offline tracing in
`validation/post-framebuffer-stall-root-cause-20261121.md` identifies the
cause: `kperf_init_early()` -> `ml_wait_max_cpus()` blocks forever just before
`bsd_init()` because no caller sets `max_cpus_initialized` on this single-CPU
build. Fixed by patch 0408 (candidate v9, no physical test performed).

No launchd, SpringBoard, root mount, or iOS userspace boot is claimed.
