# iOS candidate v7 — single BOOT flash + single boot attempt (objective record)

## Authorization scope (strictly honored)

Exactly ONE BOOT-partition flash of `validation/ios-candidate-v7-out/shim-boot.img`,
exactly ONE subsequent boot attempt. No other flash, reboot, retry, or partition
write. No physical operations beyond the authorized scope. All work on `main`.

## Pre-flight (all PASS)

- Branch `main` @ `f898449`; v7 README read; candidate full SHA-256
  `6e1fcfabc2110ebc4c4d3a3802cf718882a9b343d68bdcacc38c57f0a7f998dd` matched
  README and was rechecked at the write boundary.
- Device identity: serial `320081735bb166a3`, bootloader `M305FDDU8CVK1`,
  `ro.product.device=m30lte`, `manufacturer=samsung` (SM-M305F family), ADB root,
  PBRP recovery. USB flapped several times; each re-entry was re-verified.
- BOOT -> `/dev/block/mmcblk0p12` (via `/dev/block/platform/13500000.dwmmc0/by-name/BOOT`),
  size `33554432`, RECOVERY -> p13. Recovery path present throughout.
- Original BOOT backup `m30-boot-original/boot.img` intact:
  SHA `469c12d2d304ff4b2f07ea89ff1bc329a77f8f73037420aa260c9e68db441e78`,
  `33554432` bytes (matches the recorded value).
- Pre-flash BOOT contained the prior authorized v6 candidate
  (`5bb27fb3…f83c7f`) — expected, authorized overwrite.
- Packaging validator re-run: **PASS**; 6 `M30 ROOT:` strings + 2 `_m30_pmsg_*`
  symbols confirmed in the kernel.
- Ramoops params live: `mem_address=0x92400000`, `mem_size=0x8000`,
  `pmsg_size=0x4000`, `record_size=0x4000` — matching the mirror design.

## Actions performed

1. `adb reboot download` -> `heimdall detect` = "Device detected".
2. `heimdall flash --BOOT <v7 image> --no-reboot` -> "BOOT upload successful";
   only BOOT written; no reboot issued by the harness. (`heimdall-flash.log`)
3. User returned the device from Download Mode to PBRP recovery (hardware keys;
   boots the unchanged RECOVERY partition, not v7).
4. BOOT readback (`dd bs=2048 count=7928`, 16,236,544 B) SHA
   `6e1fcfab…f998dd` — **exact match** with the candidate. Readback gate PASS.
5. `adb reboot` issued ONCE at `2026-11-20T07:16:14Z`, `rc=0`. (Earlier two
   `adb reboot` attempts returned "no devices/emulators found" and were never
   delivered to the device.) Passive monitoring 07:16:21–07:19:06 (`adb-online=0`
   on all 12 checks) — device did **not** re-enumerate.
6. User reported the screen hung at the same text as v6 and returned the device
   to PBRP recovery manually. No retry.
7. Post-boot evidence captured automatically on ADB return; BOOT re-verified
   after the test: SHA still `6e1fcfab…f998dd`.

## Evidence (raw, preserved before interpretation)

| File | SHA256 / size |
|---|---|
| `pmsg-preboot-final.bin` | `8f3da8b3…efe3ef1c`, 2683 B, 33 records (all PBRP adbd) |
| `pmsg-postboot.bin` | `7ac7ca55…adb50027f3`, 3116 B, 39 records |
| `last_kmsg-postboot.txt` | `2d11dbde…3cdab7f9c3`, 2 MiB |
| `boot-readback.img` | `6e1fcfab…f998dd` (exact candidate) |
| `boot-verify-afterboot.img` | `6e1fcfab…f998dd` (BOOT unchanged by the test) |
| `heimdall-flash.log`, `boot-attempt.log`, `adb-monitor-postboot.txt`, `capture-trigger.log`, `dmesg-postboot.txt`, `ramoops-params-postboot.txt` | preserved |

## Findings

### 1. Did XNU's mirrored pmsg records survive XNU→TWRP? **NO.**

`pmsg-postboot.bin` decodes cleanly (39 records, 0 issues) but the tag histogram is
`adbd: 34`, `ArmToArm64Assembler: 4`, `cutils-trace: 1`. There are **zero** records
with tag `XNU`, and no `M30 ROOT:`, `SWEET FB`, `AppleCLCD`, `A5XELTE FB`, or `touch`
strings anywhere in the raw zone. The 6 additional records vs pre-boot are ordinary
PBRP adbd transport cycles from the recovery re-entries. The pre-boot records are
still present at the head of the zone, so recovery did not wholesale-erase it.

**Conclusion:** no XNU-written record survived — and given the evidence below, the
mirror most likely never activated. No persistence claim can be made.

### 2. Root cause identified from Linux source (offline)

Linux pstore sets a zone header signature of
`PERSISTENT_RAM_SIG ^ zone_type` (`fs/pstore/ram_core.c`), with
`PSTORE_TYPE_PMSG = 7` (`include/linux/pstore.h`). The pmsg zone signature is
therefore `0x43474244 ^ 0x07 = 0x43474243`. The 0406 patch checks for
`M30_PMSG_SIG = 0x43474244` and returns without writing on mismatch. So on real
hardware `m30_pmsg_init()` rejects the genuine pmsg zone and the mirror is inert.
Prior offline validation used a synthetic header of `0x43474244` and therefore
could not catch this. **Fix for a future round:** use `0x43474243` (or accept both
`0x43474244` and `0x43474243`). No fix was built or flashed here.

### 3. Last root-stage marker / eMMC findings

No `M30 ROOT:` marker was recovered by any channel. No `A5XELTE eMMC:` or
`BSD root:` line was recovered. Therefore **nothing can be concluded about how far
`IOFindBSDRoot()` progressed**; the 0407 markers produced no physical evidence.

### 4. Confirmed vs framebuffer-only conclusions

- **Confirmed (objective):** `last_kmsg-postboot.txt` shows S-Boot loading our BOOT
  image — `load_kernel: loading boot image from 153600..`, `kernel size = 0xf7b800`
  (16,234,496 B kernel payload + 2048 B header = 16,236,544 B = v7 image) and
  `Starting kernel at 0x80080000...`, followed by PINRST and the recovery kernel.
  The BOOT partition still holds the exact v7 candidate after the test.
- **User observation (framebuffer only):** screen hung at the same text as v6
  (`SWEET FB: AppleCLCD ...`, `A5XELTE FB: requested 30 Hz ... copy timing on`).
  No `SWEET HID: touch registered` and no `M30 ROOT:` line was seen. This is
  consistent with — but does not independently prove — XNU reaching framebuffer
  startup and stopping around/after `AppleCLCD::start()`.
- **Not established:** no evidence of `IOFindBSDRoot()` entry, root-device
  selection, eMMC probe, or any later stage. No panic text was recovered in
  serial/pstore (XNU console is framebuffer-only, and the pmsg mirror was inert).

## Bottom line

S-Boot accepted and entered the v7 image exactly once; the device hung at the same
visible point as v6. The pmsg mirror did not activate because of a wrong zone
signature constant, so it yielded no XNU log records. No iOS userspace or
SpringBoard boot is claimed. Stopping here — no retry, no rebuild, no flash.
