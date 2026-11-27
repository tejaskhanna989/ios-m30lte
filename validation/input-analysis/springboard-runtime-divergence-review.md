# SpringBoard runtime divergence review — Case #167 Round 3

Addressed to Mr. Craig Fedehri. Branch `investigation/native-lockscreen-independent`.
No device access, no flash, no speculative functional patch.

## 1. Evidence timeline (facts only)

| Boot | Observed result | Captured runtime evidence |
|---|---|---|
| v68 accepted | lockscreen at 06:07:50Z, still present 06:22:49Z | pstore `7918d7b8…`: 138 FB records v=15600..97800, `sw=11 pr=8 copied=70761600`; 3 benign `SBERR` duplicate-class warnings; **no `M30 UI:` record, no SMP sample** |
| v69 | Apple logo; rebooted by user | pstore `f029f1f2…`: `SBERR terminating due to uncaught exception of type NSException`, 3 `SBERR`, 1 `M30 UI:`, FB v=3000..4800 |
| v70 | Apple logo | pstore: `NSException`, 3 `SBERR`, 1 `M30 UI:`, FB v=2400..4800 |
| v68t / v68t-native / sweetsample / v73 | Apple logo, no fatal record | each has 1 `M30 UI: sb=27 bb=57 reason=none`, IRT final-state lines, no `CRASH`/`NSException`/`SBERR` in the surviving window |
| v74 lockdiag | Apple logo | pstore `3d4c1717…`: 2 SMP SpringBoard samples, 2 SMP backboardd samples, 2 `M30 UI:`, 4 `CRASH driverkitd` (JETSAM, unrelated), FB v=1800..3600 |
| v81 (v68 BOOT + v79 USERDATA) | Apple logo at 3 min, still logo at 12 min | pstore `952a0484…`: 1 `M30 UI:`, surface created, 3 FB copies, 0 CRASH/NSException/SBERR, FB v=3000..18600 |

### What is common and what diverges

Common to accepted and failing boots in the surviving captures: SpringBoard PID 27,
backboardd PID 57, `reason=none`, IRT reaching its final-state lines, a
`1080x2340` backboardd surface. **All of these are liveness/display facts, not
scene facts.**

The accepted v68 capture has **no SMP backtrace and no `M30 UI:` record at all**.
Therefore there is no captured execution path from the accepted boot to compare
against the failing boots. Any claim that v74's sampled path is "the same as v68"
or "different from v68" is unsupported — there is no v68 sample.

## 2. Thread / runtime comparison from the two v74 samples

SpringBoard:

| Sample | Header | Threads emitted | t0 PC / LR / SP |
|---|---|---|---|
| 1 (record 010) | slide 0x49eb0000, mh 0x100b28000 | t0–t4 (5) | 0x20c4c1030 / 0x20c4d2b18 / 0x16f2d6b80 |
| 2 (record 063) | same slide/mh | t0–t2 (3) | **identical PC/LR/SP/BT** |

Backboardd:

| Sample | Threads emitted | t0 PC |
|---|---|---|
| 1 (record 003) | t0–t5 (6) | 0x20c4c1030 |
| 2 (record 052) | t0–t9 (10) | **0x20c4c14ac (different)** |

Facts:
- SpringBoard's main-thread register set and frame-pointer list are byte-identical
  at the two sample times.
- SpringBoard's sampled thread count changed 5 -> 3; backboardd's grew 6 -> 10.
- Backboardd's t0 PC changed between samples.
- Record 067 follows immediately after the second SpringBoard sample, so the
  shorter list is not pstore truncation — the second sample genuinely emitted 3
  threads.

Inferences permitted: both processes were changing state between samples;
backboardd was doing work. **Not permitted:** declaring SpringBoard deadlocked
because its registers are identical. A process waiting at the same IPC call site
produces exactly this pattern on each sample.

Corroboration: v60-long (3 samples) and v79 pstore (3 samples) also show
byte-identical SpringBoard t0 PC/LR/SP/frame chain at every sample. That is a
stable wait-site pattern across multiple boots, not a v74 anomaly. It cannot
distinguish a normal event-loop wait from a stalled wait without symbolication
or a state transition — neither of which the samples provide.

## 3. The v74 objc_msgSend / stub observation

`sweet_sample_task()` reads user PC/LR/SP and walks the frame-pointer chain from
saved user state (`osfmk/kern/exception.c`, lines 1039-1080 in the CI tree). It
does not unwind; it reads `[fp]` and `[fp+8]` pairs. iOS release userspace is not
built with reliable frame pointers, so frames after the first one or two are
frequently stale stack words.

Nearest-symbol lookup of `0x20c4c1030` against the cached dyld symbols resolved
to `objc_msgSend$setWithObjects:` in a stub section — a nearest-preceding match,
not a verified symbol. Downstream frames resolved to data/stub symbols
(`__OBJC_$_PROTOCOL_METHOD_TYPES_NSObject`, `swift_memcpy`, ObjC class RO data).
None of that is reliable attribution.

What can be inferred: the common PC/LR pattern across both processes and multiple
threads is consistent with a **libsystem IPC/trap wait site**, which is the normal
idle state of a UI application's main thread. What cannot be inferred: any
SpringBoard method name, whether the wait is a deadlock, or whether a scene call
was attempted.

## 4. Stage 3 lockscreen infrastructure

The cached SpringBoard binary (`validation/.../springboard-artifacts/00007695_SpringBoard`)
contains symbols including `-[SBCoverSheetPresentationManagerAccessibility
setCoverSheetPresented:animated:options:withCompletion:]`,
`+[SBLockScreenManagerAccessibility ...]`, `-[SBLockScreenManagerAccessibility
_setUILocked:]`, and `-[SBLockScreenManagerAccessibility
_finishUIUnlockFromSource:withOptions:]`.

This proves the **capability exists in the binary**. It is not evidence that any
of these methods ran. No pstore record, launchd log or crash report in the
repository contains a call to, or a failure from, any of them. Absence from logs
is not absence at runtime — it is absence of observation.

## 5. FrontBoard hypothesis — reassessment

Weakened from "earliest unverified dependency" to "one of two unverified
transitions." The evidence still shows:
- `com.apple.frontboard.systemappservices` is declared in SpringBoard's launchd
  plist (33 MachServices, `RunAtLoad`, user `mobile`).
- **Zero** "frontboard" lines in all three launchd logs; no check-in or lookup
  record.
- No service-port creation or message-send record in any capture.
- A declaration is not a registration; a textual port label is not a successful
  lookup; an outgoing message is not a handled request.

Patch 0456 is designed to observe port creation with a text name and sends to a
named port. It still cannot observe `mach_service_lookup` by name, scene
creation, or MIG success. The FrontBoard hypothesis remains **unproven**, and
must not be promoted on the strength of a declaration.

## 6. Patch 0456 audit (independently checked)

- File exists: `xnu/patches-minimal/0456-m30-mach-service-trace.patch`.
- `git apply --check` against the current CI build tree: PASS.
- Focused test `tools/test_m30_mach_service_trace.py`: PASS (gating, caps,
  durable-sink only, no return/lock/allocation changes).
- CI gate exists once in `.github/workflows/xnu.yml`.
- CI `46054644182` **failed** at `Verify effective M30 source tree`: an earlier
  revision changed `config/MASTER.arm64.m30lte`, breaking replay of critical
  patch `0400-m30lte-board-target.patch` on the same file.
- Revised patch removes the config change; name storage/getter are
  M30LTE-conditional in `ipc_service_port.h/.c`; the send hook sits outside the
  `CONFIG_SERVICE_PORT_INFO` block.
- Current CI `46056839806` (head `b861d1f6`) is **in progress**; no result yet.
  The later documentation commits are not in that run but do not affect the build.

Therefore: the patch exists, applies, is test-covered, and has source-proven
name attribution; it has **not yet produced a successful CI build**.

## 7. IRT evidence

Not revived. The state=2/state=3 discrepancy is accepted as a sampling-order
artifact. IRT lines are used only as weak temporal markers, not as a blocker
claim.

## 8. Ranked hypotheses

1. **Scene creation never starts** (Stage 5). Consistent with every capture;
   wholly unobserved. Ranked first only because it is the earliest unverified
   transition after service availability, not because it is proven.
2. **FrontBoard service unavailable or SpringBoard cannot access it** (Stage 4).
   Declaration exists; no runtime evidence either way.
3. **USERDATA-derived readiness state** (activation, migration, keybag, Setup).
   Supported only by image-extracted launchd logs; no live capture.
4. **Downstream presentation problem.** Contradicted in part by the matched-window
   result: at v=15600..18600 both v68 and v81 copied exactly 30,332,800 bytes.
   Early framebuffer presentation worked in both. The later cessation in v81 is
   a symptom, not an established cause.

## 9. Falsification criteria

- Byte-identical SpringBoard t0 registers across samples do **not** prove a
  deadlock; a transition to a different call site would falsify a deadlock
  reading but not the "no scene" finding.
- A captured call to `setCoverSheetPresented:` with a visible lockscreen would
  falsify hypothesis 1.
- 0456 showing both launchd REG for the frontboard name and SpringBoard SEND to
  it would falsify hypothesis 2 (as a *complete* blocker; partial failure remains
  possible).
- A visible lockscreen on current USERDATA would falsify the USERDATA-readiness
  hypothesis.

## 10. Low-volume diagnostic design that preserves framebuffer evidence

- Keep `a5fb_noconsole=1` and the v68 framebuffer patch chain unchanged.
- Add no heartbeat/sampler that writes to the pstore on every frame. The v74
  sampler flooded the ring with 253-byte records; the v81/v68 comparison shows
  only 27 FB records survived.
- Use 0456's two 24/48-record hooks, gated by `m30svctrace=1`, writing only short
  `M30 SVC REG/SEND` lines to the durable sink.
- Add a **single** Stage-5 marker with a bounded counter and no stack dump, at a
  point that can be observed from the kernel without touching Apple binaries —
  no such point currently exists; this is why 0456 is the maximum safe diagnostic
  available now.
- Observe ≥20 minutes, pull pstore immediately after returning to recovery, and
  correlate framebuffer counters by matched `v`, not by final totals.

## 11. Smallest offline analysis that distinguishes the four states

Already executed: matched-window pstore comparison. Result: identical copied
bytes at matched `v`; divergent swap/present counts and later cessation. It
rules out "framebuffer never worked" and cannot distinguish blocked execution
from normal waiting — that requires symbolication or a state transition, which
existing captures do not provide.

## Exact references

- Commits: `81cfb9bd` (independent investigation), `97a52cd9`, `69832fa0`,
  `5640c712`, `b861d1f6`, `0b72c6d2`, `c824aea5` (0456 work and docs).
- Paths: `validation/physical-boot-test/20261125-ios-v68-boot/`,
  `.../20261126-v74-lockdiag-boot/`,
  `.../20261127-v81-v68boot-compat-pstore/`,
  `validation/input-analysis/springboard-runtime-divergence-review.md` (this file),
  `validation/input-analysis/mach-service-name-mapping.md`,
  `xnu/patches-minimal/0456-m30-mach-service-trace.patch`.
- Test result: `tools/test_m30_mach_service_trace.py` PASS locally; CI pending.
