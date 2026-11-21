# iOS candidate v10 — post-bsd_init IORTC fix + progress markers

Isolated candidate. v6-v9, backups and all physical evidence preserved.
No physical operations performed.

## Fix

- **0410**: skip `IOKitInitializeTime()`'s 30s `waitForService(IORTC)` on
  M30LTE (no IORTC service exists on this target; source already notes
  "RTC is not present"). BCM2837 and generic arm64 unchanged.
- **0409**: five narrowly scoped newline-terminated M30LTE `printf()` markers
  bracketing `IOKitInitializeTime`, `vfsinit`, `sweet_hfs_register`, and
  `bsd_autoconf` to pinpoint any remaining bootstrap-thread stall.

Root cause evidence: `validation/bsd-progress-analysis-20261121.md` and
`validation/physical-boot-test/20261121-ios-v9-flash/pmsg-recovered-raw.bin`.

Preserved: iOS 16 target, `maxmem=292`, ramoops reservation, proven shim
(`864370f6…d15211a`), 0406 mirror, 0407 root markers, 0408 cpu fix, and the
v9 cmdline (`maxmem=292 rd=emmcroot0 emmcprobe=1`).

## Hashes

| File | SHA256 |
|---|---|
| kernel | `afbb2fd8d1d9e3401376ee6dbf3f74b540a3f15303c733333b7f5dcc73ee552b` |
| payload | `f0378099ba6141ee5594d668f662fc593f554723fc72c4799615ebf6e5af4d04` |
| combined.bin | `f4cae0bb238ff1ac4342ffe57018d93b2a369f81fa8ce564558315a76c262350` |
| shim-boot.img | `a6b93b47533c96f72ef443342299cc934cab857d5fbe2e9ca3e37242035d1e14` |
| ios-boot.img | `338429c18568198a494a31af06a5c33f5726925d0b6de1315f6cd08b880cc19c` |

## Validation (offline)

CI `44893471750` success, iOS target confirmed, LSE=0. Buildtree PASS, kernel
PASS (6), platform 9/9, CPU 17/17, ADT 22/22, handoff 18/18, packaging PASS,
GIC 5/6 (documented inapplicable DAIF check). `test_bsd_progress.py` PASS
(M30LTE skips IORTC wait; generic arm64 and BCM2837 retain original behavior).
`test_pmsg_mirror.py` ALL PASS, `test_ml_wait_fix.py` PASS, bootlog selftest
PASS. Kernel contains 5 `M30 BSD:` and 6 `M30 ROOT:` markers.

## Next required physical verification (fresh authorization)

Boot v10 and read pstore **immediately** on recovery return. Expected markers:
`M30 BSD: IOKitInitializeTime returned`, `M30 BSD: vfsinit returned`,
`M30 BSD: sweet_hfs registered`, `M30 BSD: calling bsd_autoconf`,
`M30 BSD: bsd_autoconf returned`, then `M30 ROOT: IOFindBSDRoot entered`.
The last marker seen pinpoints the exact remaining blocker.

No root-mount/launchd/SpringBoard claim. No physical test yet.
