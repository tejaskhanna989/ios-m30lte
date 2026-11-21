# iOS candidate v16 — physical boot result (2026-11-22)

## Authorization / actions

Standing project authorization. Work on `main` @ `3a88c0b`.
Device `m30lte`, `320081735bb166a3`, `M305FDDU8CVK1`, TWRP.
v16 candidate hash verified `131459fa51afa5ef5e368a50121e4f1bab6e9887d9656ceb07778026bc8ef3d3`.

- Flash v16 `--BOOT --no-reboot` → "BOOT upload successful" (first attempt).
- BOOT readback skipped per standing instruction (not claimed).
- USERDATA / SYSTEM / RECOVERY untouched. One boot. Pstore captured immediately:
  `raw/pmsg-ramoops-0` SHA `65f392541f216db85128397a05188b878b0ad5eb4bf3963268c1c8fc94829109`
  (16,372 B, 204 records). Pre-boot baseline preserved.

## Result — MAJOR MILESTONE: genuine iOS 16.7.16 userspace booted

Patch 0414 worked — the `offset not aligned to cshash boundary` panic is GONE.
The phone booted into genuine iOS userspace (not just kernel/launchd load):
```
UMD_INIT: Created Default Persona Successfully / DONE EARLYBOOT SETUP
com.apple.xpc.launchd: launchd logging initialized. name: com.apple.xpc.launchd pid: 1
[System Event] launchd boot tasks: fsck, mount-phase-1/2, data-protection,
  finish-obliteration, detect-installed-roots, commit-boot-mode,
  restore-datapartition, init-with-data-volume, MSUEarlyBootTask, fips,
  keybag, usermanagerd, dirs_cleaner, xpcroleaccountd, init_featureflags,
  auearlyboot, tzinit, finish-restore, sysstatuscheck, prng_seedctl,
  launchd_cache_loader
auearlyboot: Starting Early Boot / No Early Boot Accessories / End Early Boot
OS version: 20H392   (genuine iOS 16.7.16)
```
This is the first time real iOS userspace runs on the M30. Many daemons
(dirs_cleaner, xpcroleaccountd, tzinit, etc.) executed. `cs_invalid_page`
messages (`allowing (remove VALID) page`) are the expected dyld-cache page
handling from 0414 — non-fatal, matching the design.

### New blocker — launchd_cache_loader needs an AMFI IOService
```
[139] Code: /System/Library/xpc/launchd.plist Sig: /System/Library/xpc/launchd.plist.sig
[140] abort: Unable to find AMFI
[143] panic: launchd_cache_loader[23] exited ... description: Unable to find AMFI
```
Analysis of the real `launchd_cache_loader` binary (extracted read-only from
the local rootfs): it does `IOServiceMatching("AppleMobileFileIntegrity")` +
`IOServiceGetMatchingService` and aborts if missing, then `IOServiceOpen` +
`IOConnectCallMethod(selector 6)` for a platform/trust query, after verifying
the launchd.plist signature with SecCode. Our built-in AMFI (sweet_amfi.c) is a
kernel interface, not a kext — no IOService exists.

### Fix (patch `0415-m30-amfi-ioservice-standin.patch`)
Publish an `AppleMobileFileIntegrity` IOService (IOResources provider) with an
`AppleMobileFileIntegrityUserClient` whose selector 6 returns trusted, following
the existing SWEET AKS/WDT stand-in pattern. Does NOT weaken security: signature
validation remains in userspace SecCode + kernel AMFI; the stand-in grants no
entitlements and matches the CS_PLATFORM_BINARY state our kernel AMFI already
asserts for rootfs binaries. Regression test `tools/test_m30_amfi_ioservice.py`
PASS.

## Honest status

- Genuine iOS 16.7.16 userspace (launchd + many daemons) runs on device ✓.
- New blocker: missing AMFI IOService for launchd_cache_loader — not a
  signature/validation bypass (signature checks pass).
- Next: CI build v17 with 0415, then physical test.
- No claim of full SpringBoard/UI boot yet.
