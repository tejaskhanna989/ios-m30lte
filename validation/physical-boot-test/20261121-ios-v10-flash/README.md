# iOS candidate v10 — single BOOT flash + one boot attempt (objective record)

## Authorization / pre-flight (all PASS)

Exactly one BOOT-only flash, one boot attempt, no other device operations.
`main` @ `835c845`. Candidate SHA-256
`a6b93b47533c96f72ef443342299cc934cab857d5fbe2e9ca3e37242035d1e14`
verified at pre-flight and at the write boundary. Device: SM-M305F family
(`m30lte`, samsung, `M305FDDU8CVK1`, serial `320081735bb166a3`, ADB root).
BOOT -> `/dev/block/mmcblk0p12` (33,554,432 B), RECOVERY -> p13 untouched.
Backup `m30-boot-original/boot.img` hash `469c12d2…441e78` intact.
`heimdall flash --BOOT <v10> --no-reboot` -> "BOOT upload successful".
**BOOT readback gate PASS**: full 16,236,544 B, exact candidate hash, before boot.
One `adb reboot` at `2026-11-21T11:07:35Z`, rc=0. BOOT re-verified after boot:
exact candidate hash. No retries, no other flashes/reboots.

## Raw evidence (preserved before decoding)

| File | SHA-256 | Notes |
|---|---|---|
| `recovery-capture/pmsg-ramoops-0` | `1c0edaf82a924e57299b9f26e8d2701abe50aa44a9deb8bd02907f56a7cf2aa6` | Immediate recovery capture, 16,372 B, moved verbatim (hash verified before/after) |
| `recovery-capture/pmsg-decoded.txt` | `f48d75a6…67968fd` | Decoded companion (216 records, 2 seam issues) |
| `raw/pmsg-ramoops-0` | `552761c8...4932051d` | Delayed scripted capture (1,922 B, 1 XNU) — superseded by recovery-capture |
| `pmsg-preboot.bin` | `9ed6020f…08c5ca` | Pre-boot pstore (v9 recovered log) |
| `last_kmsg-postboot.txt`, `dmesg-postboot.txt`, `boot-readback.img`, `boot-verify-afterboot.img` | preserved | S-Boot evidence and full BOOT verification |

## Decoded XNU log — exact milestones

The immediate capture contains 216 records (208 `XNU`, 6 `adbd`, 1 `ArmToArm64Assembler`, 1 empty). In order:

1. `Darwin Kernel Version 22.6.0 ... xnu-8796.141.3`, VM/pmap bootstrap.
2. `iBoot version: m30lte-shim`, DT matching, vnguard, trust caches, keepsyms,
   `No POST boot-arg set.`
3. BSD copyright banner, `MAC Framework successfully initialized`,
   `using 1308 buffer headers and 1308 cluster IO buffer headers`.
4. **`M30 BSD: IOKitInitializeTime returned`** ← patch 0410 (IORTC wait skipped).
5. `M30 BSD: vfsinit returned`, `SWEET HFS: hfs-627.100.6 registered`,
   **`M30 BSD: sweet_hfs registered`**.
6. `mbinit: done`, `dlil_init` thread scheduling messages.
7. **`M30 BSD: calling bsd_autoconf`**, **`M30 BSD: bsd_autoconf returned`**.
8. ifnet_attach messages, then **`M30 ROOT: IOFindBSDRoot entered`**.
9. IOKit config thread output: platform expert, AKS, WDT, SURF, HID buttons/touch,
   AppleCLCD, 30 Hz framebuffer line.
10. **`M30 ROOT: waitForMatchingService(IOBSD) returned service`**.
11. **`M30 ROOT: A5XELTE keys/emmc stage (rdBootVar='emmcroot0')`**,
    `M30LTE KEYS: GPA1 ... (read only)`, `A5XELTE eMMC: host ctrl=10 status=8906 ...`,
    **`A5XELTE eMMC: GPT SYSTEM first=442368 sectors=7798784 read-only`**.
12. **`M30 ROOT: A5XELTE keys/emmc stage done`**,
    `A5XELTE eMMC: /dev/emmcroot0 ready, GPT SYSTEM read-only`,
    **`BSD root: emmcroot0, major 1, minor 0`**.
13. `hfs_ValidateHFSPlusVolumeHeader: unknown Volume Signature : 80b8`,
    `hfs_mount: hfs_mountfs returned error=22 for device unknown-dev`,
    `cannot mount root, errno = 19`.
14. Loop: `M30 ROOT: IOFindBSDRoot entered` again, `mount(2) failed`, then
    `mount(3)`, `mount(4)`, `mount(5)`, `mount(6) failed` — repeating root
    selection/attempt with the same HFS header failure. Key/GPIO HID events
    (power/volume) interleaved from the config thread.

## Exact last M30 BSD marker reached

**`M30 BSD: bsd_autoconf returned`** (record [086]) is the last `M30 BSD:` marker.
All five 0409 markers appeared in order, confirming `bsd_init()` progressed
through `IOKitInitializeTime`, `vfsinit`, `sweet_hfs_register` and
`bsd_autoconf`. The bootstrap thread then entered `IOFindBSDRoot()`.

## Confirmed vs not confirmed

- **Confirmed**: S-Boot entered the v10 image; XNU booted through BSD init and
  root-device discovery; `rd=emmcroot0` selected `/dev/emmcroot0` from a valid
  GPT (SYSTEM partition first=442368, 7,798,784 sectors, read-only);
  `BSD root: emmcroot0, major 1, minor 0` printed. The eMMC driver works.
- **Confirmed blocker**: root **mount** fails — HFS volume header signature
  `80b8` is not a valid HFS+ signature (0x482B/0x4858 expected); the Android
  SYSTEM partition is ext4, not HFS+, so `hfs_mountfs` returns 22 and mount
  loops (errno 19). No genuine iOS root filesystem exists.
- **Not claimed**: no launchd, SpringBoard, iOS userspace, or successful root
  mount. No further physical operations authorized.

No other partition touched; all prior candidates/backups/evidence preserved.
