# Post-bsd_init stall analysis from recovered v9 pmsg (2026-11-21, offline)

## Evidence (raw preserved, unmodified)

`validation/physical-boot-test/20261121-ios-v9-flash/recovery-capture/pmsg-ramoops-0`
SHA-256 `9ed6020f9a52abbf1cc45da9edf9b5022175e7f4fb3a94af1440150a7d08c5ca`,
7633 B, decoded independently to 93 records (72 XNU, 0 issues).

Key XNU records:
- [079] `No POST boot-arg set.`
- [080-081] BSD copyright banner
- [082] `MAC Framework successfully initialized`
- [083] `using 1308 buffer headers and 1308 cluster IO buffer headers`
- [084-092] A5XELTE platform expert, AKS, WDT, SURF, HID buttons/touch,
  AppleCLCD, `A5XELTE FB: requested 30 Hz, effective 30 Hz, copy timing on`
- **end of log**

Absent (raw byte scan, 0 occurrences): `bsd_autoconf`, `kminit`, `vfsinit`,
`M30 ROOT`, `IOFindBSDRoot`, `SWEET HFS: hfs-627.100.6 registered`, `panic`,
`Failed to mount`.

## What the recovered messages prove

| Message | Source | Proves |
|---|---|---|
| BSD copyright | `bsd_init.c` `printf(copyright)` at top of `bsd_init()` | `bsd_init()` **entered** |
| `MAC Framework successfully initialized` | `mac_policy_initbsd()` called in `bsd_init()` | MAC BSD init reached |
| `using 1308 buffer headers...` | `bsd_bufferinit()` (`vfs_bio.c`) in `bsd_init()` | `bsd_bufferinit()` completed |

They do **not** prove root discovery, IOMedia registration, a root device, or
any mount. No `M30 ROOT:` / `IOFindBSDRoot` / `BSD root:` record exists.

## 0408 verdict

Patch 0408 (`ml_wait_max_cpus()` returns `machine_info.max_cpus` on M30LTE)
**worked**: the bootstrap thread reached `bsd_init()` — impossible if it were
still parked in `kperf_init_early()` before `bsd_init()`. This is source/control-
flow evidence plus the recovered log, not inference from framebuffer output.

## First expected milestone after buffer headers, and why absent

The bootstrap thread reached `bsd_bufferinit()` (bsd_init.c:682). The next
visible milestones in source order:
1. `IOKitInitializeTime()` (bsd_init.c:688) — calls
   `IOService::waitForService(resourceMatching("IORTC"), 30s)`. **No IORTC
   service exists on this target** (no node in ADT, no publisher in M30 build;
   source even comments "RTC is not present on this target", yet only BCM2837
   is excluded). A 30s sleep with no producer.
2. `vfsinit()` (bsd_init.c:694) — no visible log.
3. `sweet_hfs_register()` (bsd_init.c:703) — logs
   `SWEET HFS: hfs-627.100.6 registered` — **compiled in but absent from log**.
4. `bsd_autoconf()` (bsd_init.c:801) — logs `bsd_autoconf: calling kminit` —
   **absent**.

Since (3) and (4) are absent, the bootstrap thread is stuck in (1) or (2).
`vfsinit()` contains only in-memory table setup (no waits), so the evidence-supported
blocker is the **30s IORTC wait in `IOKitInitializeTime()`** — a wait on a service
that never registers. This is a bootstrap-thread stall; it is distinct from the
IOKit config thread, which independently produced records [084-092] (platform
expert, AKS, WDT, SURF, HID, AppleCLCD). Config-thread output after the 30 Hz
line is **not** proof the bootstrap thread progressed.

## Fix (smallest, evidence-supported)

- **0410**: in `iokit/Kernel/IOStartIOKit.cpp`, skip the IORTC wait for M30LTE
  (`#if !defined(BCM2837) && !defined(ARM64_BOARD_CONFIG_M30LTE)`), add the
  board_config include. Non-M30LTE arm64 and BCM2837 keep original behavior.
- **0409**: five narrowly scoped, newline-terminated M30LTE `printf()` markers
  around `IOKitInitializeTime`, `vfsinit`, `sweet_hfs_register`, and
  `bsd_autoconf` in `bsd/kern/bsd_init.c`, to pinpoint any remaining stall on
  the next authorized boot.

## Tests

`tools/test_bsd_progress.py` PASS: patch structure assertions; faithful model
compiled three ways — M30LTE skips wait (0 calls), generic arm64 retains it
(1 call), BCM2837 retains original skip (0 calls).

## Preserved / constraints

iOS 16 target, `maxmem=292`, verified shim region, all prior candidates and
evidence unchanged. No physical operations. No root-mount/launchd/SpringBoard
claim.

## Next required physical verification (needs fresh authorization)

Boot a candidate built with 0409+0410 and read pstore **immediately** on
recovery return. Expected: `M30 BSD: IOKitInitializeTime returned`,
`M30 BSD: vfsinit returned`, `M30 BSD: sweet_hfs registered`, then
`bsd_autoconf: calling kminit` and the `M30 ROOT:` markers. If the markers stop
at a specific point, that names the next blocker exactly.
