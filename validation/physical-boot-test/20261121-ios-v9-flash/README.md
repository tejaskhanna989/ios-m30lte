# iOS candidate v9 — single BOOT flash + one boot attempt (objective record)

## Authorization

Exactly one BOOT-only flash of v9 and exactly one boot attempt. No other flash,
reboot, retry or partition write. No branches changed; `main` @ `3e5547c`.

## Pre-flight (all PASS)

- `main` @ `3e5547c`; v9 candidate SHA-256
  `01fd8d436a062dea3a5a92e22426f1df5afd8ec352f15723022045a69a7dc07c` verified
  at both pre-flight and the write boundary; 16,236,544 B.
- Device: serial `320081735bb166a3`, bootloader `M305FDDU8CVK1`,
  `ro.product.device=m30lte`, samsung, ADB root (SM-M305F family).
- BOOT -> `/dev/block/mmcblk0p12` (33,554,432 B); RECOVERY -> p13 untouched.
- Original BOOT backup hash `469c12d2…441e78` intact.
- `heimdall flash --BOOT <v9> --no-reboot` -> "BOOT upload successful".
- **BOOT readback gate PASS**: full 16,236,544 B read back with SHA-256
  `01fd8d43…a69a7dc` (exact candidate match) before the boot attempt.
- **BOOT still v9 after boot**: `boot-verify-afterboot.img` SHA-256
  `01fd8d43…a69a7dc` (exact match).

## Boot attempt

- One `adb reboot` issued at `2026-11-21T09:35:51Z`, rc=0. (An earlier
  boot-command waiter timed out with no device; no command was delivered.)
- Passive monitor `adb-monitor-postboot.txt`: no USB re-enumeration for the
  first 3 minutes (18/18 checks adb_online=0) — same hang pattern as v8.
- Device returned to PBRP recovery; user reported the screen stopped at the
  **same v8 point** (`SWEET FB: AppleCLCD ...` / `A5XELTE FB: 30 Hz ...`),
  with **no new `M30 ROOT:`, eMMC, `BSD root:` or panic line** visible.

## Evidence and its limitations

| File | SHA256 / size |
|---|---|
| `pmsg-preboot.bin` | `2da5f879…42cb2`, 7331 B (89 records, 68 XNU from v8) |
| `pmsg-postboot.bin` | `771ae87d…adf5e`, 3439 B (42 records, **1 XNU**) |
| `last_kmsg-postboot.txt` | `ec5fc66f…42394d`, 2 MiB |
| `boot-readback.img` / `boot-verify-afterboot.img` | `01fd8d43…a69a7dc` (exact) |

**Important capture limitation:** the evidence script spent the first 3 minutes
in passive monitoring before reading pstore. At recovery boot Linux reported
`persistent_ram: found existing buffer, size 8717, start 8717`, but by capture
time recovery's `adbd` had overwritten most of the circular pmsg zone: the
captured file is only 3439 B with a single surviving XNU record
(`Darwin Kernel Version 22.6.0 ... xnu-8796.141.3`). Raw scan confirms zero
occurrences of `M30 ROOT`, `Copyright`, `bsd`, `eMMC`, `30 Hz`, `AppleCLCD`.
No other pstore console file exists and `/dev/mem` is unavailable, so the
overwritten records cannot be recovered. No further boot is authorized.

`last_kmsg-postboot.txt` shows S-Boot loaded our BOOT image
(`kernel size = 0xf7b800` + 2048 B header = 16,236,544 B = v9) and
`Starting kernel at 0x80080000...`, then PINRST to recovery. No XNU text is
present in serial/pstore (framebuffer-only console).

## Outcome (strict)

- **S-Boot accepted and entered the v9 image exactly once**; the flashed image
  is byte-identical before and after the test.
- XNU began execution (the surviving `Darwin Kernel Version` record is genuine
  mirrored XNU output, proving the 0406 mirror still works).
- **No observable progress past the v8 stop point.** The screen showed the same
  framebuffer lines, and no root-stage marker was captured or seen.
- Therefore it is **NOT demonstrated** that patch 0408 let execution pass
  `ml_wait_max_cpus()` and enter `bsd_init()` / `IOFindBSDRoot()`. The screen
  and the surviving record are consistent with either (a) the stall persisting,
  or (b) the bootstrap thread advancing while console output stops being
  visible — the lost pmsg records prevent distinguishing these. The pre-BSD
  deadlock hypothesis is **not confirmed** by this test.
- No root mount, launchd, SpringBoard or iOS userspace boot is claimed.

## Next step

Requires fresh authorization. To avoid the capture loss, a future test should
read pstore **immediately** on recovery return (no 3-minute passive delay),
or use a non-overwritable capture path, before drawing conclusions from pmsg.
