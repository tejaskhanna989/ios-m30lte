# iOS candidate v21 — physical boot result (2026-11-22)

## Authorization / actions

Standing project authorization. Work on `main` @ `72a64d3`.
Device `m30lte`, `320081735bb166a3`, TWRP.
v21 candidate hash verified `9db28ba44e213d44541943da520cb3f07decb7ca8b07a9abd6b2595bb9e35d10`.

- Flash v21 `--BOOT --no-reboot` → "BOOT upload successful" (first attempt).
- BOOT readback skipped per standing instruction (not claimed).
- USERDATA / SYSTEM / RECOVERY untouched. One boot. Pstore captured immediately:
  `raw/pmsg-ramoops-0` SHA `8f9fa9050c56b5dc03b7aa315bac6cd2ce35d9d9d106798745be28eaba3b33ca`
  (16,372 B, 191 records). Pre-boot baseline preserved.

## Result — diagnostic: platform flag IS set, but launchd still panics

The v21 diagnostic in `sweet_amfi_vnode_check_signature` shows EVERY signature is
marked platform with rootfs=1 and `csflags 0x24000003` (includes CS_PLATFORM_BINARY
0x04000000 | CS_SIGNED 0x20000000 | CS_VALID 0x1 | CS_ADHOC 0x2):
```
[024] SWEET AMFI: plat com.apple.xpc.launchd rootfs=1 csflags 0x24000003
[025] SWEET AMFI: plat com.apple.darwin.ignition rootfs=1 csflags 0x24000003
[072-120] SWEET AMFI: plat com.apple.dyld.cache.arm64.universal ... 0x24000003
[130] SWEET AMFI: plat com.apple.fsck rootfs=1 csflags 0x24000003
```
So the kernel-side CS_PLATFORM_BINARY marking works — patch 0419 is effective.
The dyld cache signatures (previously the crash-loop source) are all marked
platform and validates cleanly (no cs_invalid_page / Text page corruption).

But launchd STILL panics:
```
[126] assertion failed: 99Z999: launchd + 71896 [5C15DB07...]: 0xffffffffffffffff
[129] (fsck) Doing boot task
[131] panic: userspace panic: boot task is not a platform binary (fsck, /sbin/fsck)
```
`0xffffffffffffffff` (-1) is a failed `csops` lookup (code signing identity).
The failure is at the PROCESS level: `csops(CS_OPS_STATUS)` calls
`csproc_get_platform_binary` -> `csproc_get_blob(p)` which requires
`p->p_textvp != NULL`, `proc_getcsflags(p) & CS_SIGNED`, and
`ubc_cs_blob_get(p->p_textvp, -1, -1, p->p_textoff)` to return the platform blob.
launchd may use `csops(CS_OPS_CDHASH)`/`CS_OPS_IDENTITY` and compare cdhash to an
expected value ("code signing identity mismatch" string in launchd). The vnode
blob is platform; need to find which process-level query returns -1/wrong value.

## Honest status

- Primary v18 objective (daemon crash loop) FIXED and stable across v20, v21 ✓.
- Fully genuine iOS userspace runs launchd + dyld boot tasks ✓.
- New blocker is launchd's boot-task identity/platform check at process level,
  not signature validation. No SpringBoard/UI claim.
- Next: instrument csops (CS_OPS_STATUS/CDHASH/IDENTITY) and fix process-level
  platform/cdhash reporting, then rebuild and test.
