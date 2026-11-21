# iOS candidate v19 — 16K pages to match genuine iOS 16 rootfs

Isolated candidate. v6–v18, backups, all physical evidence preserved.
No physical operations performed for v19. Work on `main` @ `2c1b87d`.

## Exact cause and fix

Physical v16–v18: genuine iOS 16.7.16 userspace booted deep (launchd + many
daemons), but a daemon crash loop (lsd, securityd, backboardd, identityservices;
sig 5/6 with `Text page corruption`) persisted through the 4K workarounds.
Root cause: the M30 kernel is 4K (`PAGE_SHIFT=12`) while the iOS rootfs and dyld
shared cache are 16K. The TCR translation granule and `ARM_PGSHIFT` are
compile-time (`__ARM_16K_PG__`); SWEET.h already defines it.

**v19 fix (patch `0417-m30-16k-pages.patch`):** define `__ARM_16K_PG__ 1` in
`M30LTE.h` so the kernel uses 16K pages natively. The dyld cache 16K code
directory now validates and maps natively; patches 0413/0414/0416 become
harmless no-ops. Code signing is STRONGER (native 16K page hash granularity),
not weakened. Genuine iOS target, `maxmem=292`, cmdline, and all prior fixes
preserved. `verify_m30_buildtree.py` updated to include 0417 in critical-patch
provenance (reverse-applied before 0402, which created M30LTE.h).

## Hashes

| File | SHA256 |
|---|---|
| kernel | `1af2a1210a57d258dde92a0dba56da7ce21d0143b60b0578b2c6bc0b0bbb40e5` |
| payload | `4f675949bd6a968e005db8a13fadc2f0172184c2354b660ba6230fe2a6cc7de1` |
| combined.bin | `18413b6a0dc5509e69c1aea3f159ed783cc9af5fd31112056025a4c2312b4aaf` |
| shim-boot.img | `55f66a95648c2dbd23e81d9e7226ee06f3058f4d724f8d92957d49087097a57f` |
| ios-boot.img | `ad2ec8616e1fb10fe68fcfd57d07a20a451a91063b42101cd863d82f528ba423` |

Cmdline: `debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292 rd=emmcroot0 emmcroot=USERDATA emmcprobe=1 emmcwrite=1`

## Validation (offline)

CI `44950568628` green (iOS target confirmed, LSE=0). Buildtree PASS, kernel
PASS, platform 9/9, CPU 17/17, ADT 22/22, handoff 18/18, packaging PASS, GIC
5/6 (inapplicable). All focused tests PASS including `test_m30_16k_pages.py`
(verifies compile-time 4K->16K transition). Shim byte-identical to proven v6.
Kernel layout shifted with 16K build; entry VA / ADT PA / boot_args PA
(0xfffffff00741e488 / 0x8245c000 / 0x82460000) verifier updated.

## Status / next physical step

Not physically tested. Proposed: flash v19 BOOT only, preserve USERDATA/SYSTEM/
RECOVERY, one boot, capture pstore immediately. Expected: native 16K dyld cache
validation, no daemon text-page crash loop, boot progresses further (SpringBoard
may start). No SpringBoard/UI success claim until device evidence proves it.

**Risk note:** 16K pages is a fundamental memory-model change. If the kernel
fails to boot on the M30 hardware (Cortex-A53 supports 16K granule), v18 remains
the best deep-userspace candidate and this change can be reverted.
