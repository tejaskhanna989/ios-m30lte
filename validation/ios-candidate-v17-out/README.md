# iOS candidate v17 — AMFI IOService for launchd_cache_loader

Isolated candidate. v6–v16, backups, all physical evidence preserved.
No physical operations performed for v17. Work on `main` @ `3ebdb14`.

## Exact cause and fix

Physical v16 (`65f39254…94829109`): genuine iOS 16.7.16 userspace booted
(UMD personas, launchd pid 1, dozens of boot tasks, `OS version: 20H392`).
Blocker: `launchd_cache_loader[23]: Unable to find AMFI`. Extracting the real
`launchd_cache_loader` from the local rootfs showed it opens
`IOServiceMatching("AppleMobileFileIntegrity")` and aborts if absent. Our
built-in AMFI is a kernel interface, not a kext, so no IOService existed.

**v17 fix (patch `0415-m30-amfi-ioservice-standin.patch`):** publish an
`AppleMobileFileIntegrity` IOService (IOResources provider) with an
`AppleMobileFileIntegrityUserClient` whose selector 6 returns the platform/trust
answer, following the existing SWEET AKS/WDT stand-in pattern. No security
weakening: signature validation stays in userspace SecCode + kernel AMFI
(`csblob_get_entitlements` checks entitlements against the code directory); the
stand-in grants no entitlements and matches the CS_PLATFORM_BINARY state our
kernel AMFI already asserts. Cmdline and all prior fixes unchanged.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `de8b895784b3a550e7649256bde8d1f28eedd85c9b41bd5284206b81ebb66482` |
| payload | `c78ee298ac81ac0ba9158472eca3948b240133b4facb8d9f63dc6fbf866dff0f` |
| combined.bin | `99fd59ef77d297e6a71a181af8b73ffa33265dd84515d75849dd43bf0d44f5c2` |
| shim-boot.img | `4f14d23c81279d47c86889f6efbe9c7cfa241b68affe11fdb86f114f0e5b30b0` |
| ios-boot.img | `68bda62add436d218b01e2baa200c2a07f7cc17033d2530429faba5ed7756c01` |

Cmdline: `debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292 rd=emmcroot0 emmcroot=USERDATA emmcprobe=1 emmcwrite=1`

## Validation (offline)

CI `44944125727` green (iOS target confirmed, LSE=0). AMFI IOService strings
and personality present in kernel. Buildtree PASS, kernel PASS, platform 9/9,
CPU 17/17, ADT 22/22, handoff 18/18, packaging PASS, GIC 5/6 (inapplicable).
All focused tests PASS including `test_m30_amfi_ioservice.py` (verifies the
stand-in, real loader requirement, and that validation is untouched). Shim
byte-identical to proven v6; `maxmem=292`, iOS 16 target preserved.

Note: kernel text grew with the new C++ service; entry VA, ADT PA and boot_args
PA shifted (0xfffffff00740d488 / 0x82450000 / 0x82454000); verifier updated.

## Status / next physical step

Not physically tested. Proposed: flash v17 BOOT only, preserve USERDATA/SYSTEM/
RECOVERY, one boot, capture pstore immediately. Expected: launchd_cache_loader
finds the AMFI service, validates/pushes the launchd cache signature, and the
boot proceeds further into iOS userspace. No full SpringBoard/UI claim until
device evidence proves it.
