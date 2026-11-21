# Genuine iOS root filesystem installation — first physical boot (2026-11-21)

## Authorization and scope

Full installation (USERDATA write) + one BOOT flash + one boot, explicitly authorized.
All work on `main` @ `7970ce9`. No retries, no second boot, no other partition writes.

## Actions performed

1. Re-confirmed device: `m30lte`, samsung, `M305FDDU8CVK1`, serial `320081735bb166a3`,
   TWRP `3.4.03.0.0-UNOFFICIAL`, ADB root. USERDATA = `/dev/block/mmcblk0p28`,
   capacity 57,038,340,096 B. BOOT = p12, RECOVERY = p13, SYSTEM = p20 (untouched).
2. Verified local image SHA-256 `5f2e2aa6…b699b5`, size 21,474,836,480 B.
3. Unmounted `/data` and `/sdcard`; confirmed USERDATA not mounted.
4. Wrote image host->device via `adb shell dd of=/dev/block/mmcblk0p28 bs=4194304`
   (plain toybox dd + `sync`): 5,120 records, 21,474,836,480 bytes copied, synced
   at 15:54:15Z. **`userdata-write.log`**.
5. **Full 20 GiB readback was started but stopped by user request after ~22 min;
   it never completed. USERDATA readback hash is NOT verified — do not claim it is.**
6. Verified v11 BOOT SHA-256 `6bdb25d9…d1740c`; `heimdall flash --BOOT ... --no-reboot`
   -> "BOOT upload successful". **No BOOT readback** (explicitly waived by user).
7. User performed the single boot; device returned to TWRP. Raw pstore captured
   immediately on ADB return (16:29:18Z): `raw/pmsg-ramoops-0` SHA
   `129b9f8c…e335bb5f` (16,372 B, 215 XNU records), `raw/pstore-listing.txt`,
   `last_kmsg-postboot.txt`, `dmesg-postboot.txt`. Original raw files preserved.

## Boot outcome — evidence (raw pmsg)

- S-Boot loaded our image: `kernel size = 0xf7b800` + 2048 B header = v11 size;
  `Starting kernel at 0x80080000...`.
- XNU reached BSD init: MAC Framework, buffer headers, all five `M30 BSD:` markers,
  `bsd_autoconf returned`, `IOFindBSDRoot entered`.
- eMMC path works: `A5XELTE eMMC: /dev/emmcroot0 ready, GPT USERDATA read-only`,
  `BSD root: emmcroot0, major 1, minor 0`.
- **The genuine HFSX volume was recognized** — `hfs: Initializing the journal
  (joffset 0xa2000 sz 0x800000)...`. This is far past the old `unknown Volume
  Signature 80b8` (ext4) failure: the iOS image is on the device and its HFSX
  volume header validates.
- **Exact new blocker:** the root is mounted **read-only** (`GPT USERDATA read-only`)
  and journal creation needs a write:
  ```
  jnl: b(1, 0): do_jnl_io: strategy err 0x1e       (EROFS)
  jnl: b(1, 0): write_journal_header: error writing the journal header!
  jnl: b(1, 0): journal_create: failed to write journal header.
  hfs: late jnl init: failed to open/create the journal (retval 0)
  hfs_mounthfsplus: hfs_late_journal_init returned (22)
  cannot mount root, errno = 19
  ```
  Loop of `mount(2)…mount(6) failed` follows. No launchd, no SpringBoard.

## Honest status

- Genuine iOS HFSX root filesystem **physically present and recognized**.
- Root **mount failed** on read-only journal initialization — NOT a filesystem
  format problem. No launchd/SpringBoard/userspace boot occurred.
- USERDATA readback hash unverified (stopped by user).
- The local rootfs image was preserved per instruction (not deleted).
- No retry, no reflash, no second boot. SYSTEM/RECOVERY untouched.

## Smallest next fix (not implemented — requires fresh authorization)

The donor's working cmdline included `emmcroot=USERDATA emmcwrite=1 rootrw=1`;
ours has `emmcroot=USERDATA` but not `emmcwrite=1`/`rootrw=1`. Adding those to the
payload cmdline (a config-only candidate rebuild, no kernel change) should let the
HFS journal initialize and the root mount read-write. Then re-flash BOOT and boot
once under fresh authorization. Alternatively, build the root image unjournaled.
