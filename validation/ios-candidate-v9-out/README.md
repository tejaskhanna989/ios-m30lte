# iOS candidate v9 — post-framebuffer deadlock fix

Isolated candidate. v6, v7, v8, all backups and physical evidence preserved.
No physical operations were performed for v9.

## Fix

Patch 0408: on M30LTE, `ml_wait_max_cpus()` returns `machine_info.max_cpus`
directly instead of waiting on `max_cpus_initialized`, which is never set on
this single-CPU build because `SweetCPU::startAll()` (the only relevant caller
of `ml_set_max_cpus()`) never starts. This wait in `kperf_init_early()` was
the concrete pre-`bsd_init()` deadlock that stalled every earlier candidate
at the framebuffer. Root cause:
`validation/post-framebuffer-stall-root-cause-20261121.md`.

Preserved: genuine iOS target, `maxmem=292` ramoops reservation, proven shim
region (`864370f6…d15211a`), 0406 pmsg mirror, 0407 root markers, and the
v8 cmdline `maxmem=292 rd=emmcroot0 emmcprobe=1`.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `ff9cd188ed3e0ac745c3d09bb79d71b33232c255a56174a80773cb8bc77cc9ad` |
| payload | `65ed007d71b91749be1ba02452db18a7dd17c346b0cd4a923dc8baf18da7a759` |
| combined.bin | `0be1a1a8d29c1aae7044d70e45521b37b05703e4cebaf8f12d629bf3e5550991` |
| shim-boot.img | `01fd8d436a062dea3a5a92e22426f1df5afd8ec352f15723022045a69a7dc07c` |
| ios-boot.img | `61e439ce0a8c3100b7e84869074309a25d7215e97f7bc8345324e1406189aae7` |

## Validation (offline)

CI `44886757576` success, iOS target confirmed, LSE=0. Buildtree PASS, kernel
PASS (6), platform 9/9, CPU 17/17, ADT 22/22, handoff 18/18, packaging PASS,
GIC 5/6 (known inapplicable DAIF check). `test_ml_wait_fix.py` PASS (M30LTE
returns immediately; other arm64 unchanged). `test_pmsg_mirror.py` ALL PASS.
`m30_bootlog.py selftest` PASS. Kernel contains 6 `M30 ROOT:` strings and
2 `_m30_pmsg_*` symbols.

## Expected evidence on a future authorized boot

The repaired pmsg mirror physically works (v8 proved 68 XNU records survive
XNU->TWRP). With 0408, the log should continue past the 30 Hz line into
`bsd_init()` and show `M30 ROOT:` / `A5XELTE eMMC:` / `BSD root:` markers if
those stages are reached. No such result is claimed until physically tested.

## Blockers

- No genuine iOS root filesystem; root mount/userspace cannot be claimed.
- v9 has NOT been physically tested; authorization required before any test.
