# iOS candidate v20 — physical boot result (2026-11-22)

## Authorization / actions

Standing project authorization. Work on `main` @ `048c800`.
Device `m30lte`, `320081735bb166a3`, `M305FDDU8CVK1`, TWRP.
v20 candidate hash verified `3fdd4246d78d830ebdd9147cf7f8b01538e60f2e8ee5703275d661fe4e363e78`.

- Flash v20 `--BOOT --no-reboot` → "BOOT upload successful" (first attempt).
- BOOT readback skipped per standing instruction (not claimed).
- USERDATA / SYSTEM / RECOVERY untouched. One boot. Pstore captured immediately:
  `raw/pmsg-ramoops-0` SHA `74a8ab976c3c15242ef992d431d02bec22d2c22c403301023100d01d1a0518cc`
  (16,372 B, 207 records). Pre-boot baseline preserved.

## Result — MAJOR MILESTONE: daemon crash loop FIXED, real launchd boot tasks

Patch 0418 (full 16K code-directory block validation) WORKED:
- ZERO `cs_invalid_page` messages, ZERO "Text page corruption", ZERO daemon crashes.
- Root mounted (`hfs: mounted iOSRoot`), AMFI registrations OK, launchd running.
- **Real launchd notices**: `com.apple.xpc.launchd: hello`, Darwin Bootstrapper
  Version 7.0.0, boot-args echoed, `entering ondemand mode`, `created`.
- Boot tasks executing: `(fsck) Doing boot task`, `system` service created.

This is the first boot where the v18 userspace daemon crash loop is gone.

### New blocker — launchd boot-task platform binary check
```
[143] assertion failed: 99Z999: launchd + 71896 ...
[147] panic: userspace panic: boot task is not a platform binary (fsck, /sbin/fsck)
```
launchd called `reboot()` with a panic message because its boot task `/sbin/fsck`
was reported as not a platform binary. Note this is a **userspace** decision, not
a kernel code-signing failure — the 16K block validation itself succeeded (no
cs_invalid_page / taint / crash).

Investigation: `sweet_amfi_vnode_check_signature` sets `CS_PLATFORM_BINARY` when
`vfs_flags(vnode_mount(vp)) & MNT_ROOTFS`; root mounted with flags `0x480d001`
(MNT_ROOTFS 0x4000 set). `csproc_get_platform_binary` reads
`blob->csb_platform_binary` set in `ubc_cs_blob_add` from `cs_flags`. Need to
determine why fsck's process reports non-platform (possibly a different check
in launchd, e.g. AMFI user client selector, or csb flag propagation).

## Honest status

- Daemon crash loop fixed ✓; genuine iOS userspace runs real launchd boot tasks ✓.
- New blocker is launchd's platform-binary gate for fsck — not signature validation.
- No SpringBoard/UI claim. Next: fix platform-binary reporting, rebuild, test.
