# v74 — lock-screen blocker determination and bounded diagnostic

## Evidence reviewed (all read-only)

- `validation/physical-boot-test/20261126-v73-rootfs-boot/`: pstore
  (`412052f6…`, 168 records), decoded pmsg, `launchd.log` (`051a4b0a…`),
  analysis.
- v68 accepted lock-screen capture (`7918d7b8…`) for differential.
- `validation/input-analysis/v68t-lockscreen-contract-trace.md`,
  `v72-userspace-dependency-audit.md`.

## What v73 proved and what it did not

v73 removed the `lsd` SIGABRT loop: one `Successfully spawned lsd[103]`, no
exit/crash lines through 16:11:19, 0 pstore `CRASH` records, no `.ips` reports.
The user then confirmed visually that **the native lock screen did not appear**.

SpringBoard[27] and backboardd[57] are alive; IRT final state 3; backboardd
created a 1080×2340 BGRA surface (`SWEET SURF create id 2 … -> 0x0`). The
framebuffer records show only 5 surface copies (`copied=50544000`) before the
counter stops changing — identical in shape to the early copies in the v68
accepted capture. Framebuffer activity is therefore backboardd/kernel surface
work plus heartbeat, **not proof of SpringBoard content presentation**.

## Exact blocker

The first failing dependency is still **unobserved**, not a proven crash:
there is no record of `SBWindowScene`/`UIWindowScene` creation or
`-[SBCoverSheetPresentationManager setCoverSheetPresented:…]` execution.
With `lsd` stable and no crash/exception/SBERR/BBERR record, the stall is inside
SpringBoard's userspace scene-creation path.

Why no observation exists:
- v73 boot-args contain `sweetsample=SpringBoard,backboardd`, but the sampler
  patch (`0054`) is not in the current kernel source tree (removed with the
  v71 exact-v68 restoration). The arg is therefore inert — 0 `SMP` records.
- The 16 KiB pstore ring wrapped during the ~29 min iOS run; only one
  `M30 UI: sb=27 bb=57 reason=none` line survived.

No SpringBoard/framework patch, no authentication bypass and no speculative
XNU change is justified by this evidence.

## Implemented correction (diagnostic, not a functional UI patch)

`xnu/patches-minimal/0455-m30-lockscreen-diag.patch`:
- reuses the existing `sweet_sample_task()` read-only backtrace mechanism;
- routes its lines through the durable `m30_pmsg_diag_line()` sink when
  `m30sblockdiag=1` so samples survive the ring wrap;
- bounded: first sample 45 s after start, then every 60 s, at most 6 samples,
  then clears the flag; disabled by default;
- touches no SpringBoard/UIKit code, no AMFI/code-signing state, no input path.

`tools/test_m30_lockscreen_diag.py` verifies gating, bounds, durable-only
output, absence of touch/UI/auth changes, and clean application to the exact
v68 buildtree with 0451/0453/0454 already applied.

## Touchscreen safety review (no change made)

Source: `bsd/dev/m30lte_touch.c` in the v68t buildtree, patch 0451.
- `m30lte_touch_probe()` returns immediately unless `m30touch=1`; all HID calls
  are additionally gated by `m30touchhid=1`. **Dormant by default.**
- Bounded polling loops (`delay(1)` with fixed maxima 20000/5000), no XNU IRQ
  handler, no dynamic allocation, fixed finger array — no interrupt storm or
  memory-corruption path when disabled.
- Risks if enabled: unproven I2C4 power/clock and IRQ 243 routing; no durable
  contact telemetry; and a concrete coordinate mismatch — the driver scales to
  **1080×1920**, while backboardd presents a **1080×2340** surface. Touch is
  therefore NOT enabled in this candidate and no touch claim is made.

Touch remains compiled in (as in the accepted native candidate) but inactive;
it can be switched on independently in a later, separately authorized boot.

## Conclusion / next evidence required

Native lock-screen rendering and physical touch are both **unproven**. The next
authorized physical boot must use `m30sblockdiag=1` with the v73 USERDATA in
place, let it settle, then pull pstore promptly and decode `SMP` lines with
`tools/decode_sweet_sample.py`. That backtrace is the first evidence capable of
naming the failing SpringBoard call; only then can a functional patch be
justified.
