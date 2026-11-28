# Priorities 2–6: target reconciliation, provenance, capture analysis, diagnostic design

Date: 2026-11-27. Branch `arena/f8de43b7-ios-m30lte`.
Status: analysis complete; **no candidate assembled, no device touched**.

This document supersedes two claims in `v86-physical-test-readiness.md`. Where it
contradicts that file, this file wins, because it is based on the binaries
themselves rather than on build logs.

---

## 1. Priority 1 — 0456 header-budget bypass: FIXED and verified

The 2 KiB cap previously applied only to sampler body lines. The per-present
header was emitted with a bare `printf` before any budget check, so a 2 KiB cap
could not stop 80 header lines (5,200–10,320 bytes, 32–63% of a 16 KiB ring).
That is why 0456 did not bound output as intended.

Fix: a single hard-budget emitter, `m30_smp_emit()`, now gates **every** line
including headers. The budget covers headers, full lines, partial lines and the
truncation marker.

Two real defects were found by compiling the emitter and measuring the bytes
that actually reach the sink, and both are now pinned by tests:

| Defect | Symptom | Fix |
|---|---|---|
| Reserve used `sizeof(MARKER)` | Reserved 1 byte too many (the NUL is never emitted) | `strlen(M30_SMP_MARKER) + 1` |
| Clamp used `len = room` | Charged `len + 1` after emitting `len`, so every truncated line overshot by exactly 1 byte | `len = room - 1`, guarded by `if (len + 1 > room)` |

Silent shortening at 256 bytes was also removed: an over-long line is now cut at
`sizeof(buf) - 1` and ends in `...`, so a clipped line is never mistaken for a
complete one.

Verified behaviour, measured on generated output (not by reading source):

| Budget | Lines supplied | Bytes emitted | Last line |
|---|---|---|---|
| 2 KiB | 30 × 65 B | 1,980 | complete (65 B) |
| 2 KiB | 31 × 65 B | 2,007 | **clipped to 26 B, ends `...`** |
| 2 KiB | 32 × 65 B | **2,048 exactly** | marker `M30 SMP budget reached, output truncated` |

Invariant holds across 14 shapes (budgets 1–4 KiB, 0–10,000 lines, lines up to
8,191 B): emitted bytes never exceed the budget, and the marker is the last line.

Tests: `tools/test_m30_smp_budget_boundary.py` — 10 tests, all pass. Six execute
the patched C through a host-compiled harness; four assert source invariants.
The patch applies cleanly on the chain through 0455 and touches exactly two
files (`bsd/dev/sweet_sample.c`, `osfmk/kern/exception.c`).

---

## 2. Priority 2 — the v68 vs CI target discrepancy: RESOLVED, and v68 is iOS

**The earlier claim that v68 was built on the legacy `macosx` path is wrong.**
That conclusion came from the absence of `SDKROOT=iphoneos` in the eight v68
build logs, which is weak negative evidence. The kernel binary itself settles it:

```
$ read LC_BUILD_VERSION from validation/ios-candidate-v68-out/inputs/kernel.development.m30lte
magic=0xfeedfacf  cputype=0x0100000c (arm64)  filetype=2 (MH_EXECUTE)
LC_BUILD_VERSION: platform=2 (iOS)  minos=0x120000 (18.0)  sdk=0x120000
__TEXT vmaddr=0xfffffff007004000  vmsize=0x164000  fileoff=0
```

The accepted v68 kernel is **tagged iOS**, built with `-miphoneos-version-min`.
So CI's default `XNU_TARGET=iphoneos` matches the v68 lineage; the target is not
a deviation.

Independently confirmed in `xnu-8796.141.3` sources:

- `makedefs/MakeInc.def:87` — embedded platforms get
  `-miphoneos-version-min=$(SDKVERSION) -DXNU_TARGET_OS_IOS`; macOS gets nothing.
  The presence of a nonzero iOS `LC_BUILD_VERSION` therefore proves the iOS path.
- `makedefs/MakeInc.def:328,334` — `ARM64_LINK_ADDR = 0xfffffff007004000` for all
  non-MacOSX platforms, and `0xfffffe0007004000` only under
  `ifneq ($(filter $(PLATFORM),MacOSX),)`. v68's `__TEXT` is exactly
  `0xfffffff007004000`, which is the embedded value. A macOS build would have
  linked at `0xfffffe0007004000` — a 32 MB-aligned base of `0xfffffe0006000000`,
  not the `0xfffffff006000000` the packager derived.

**Packaging compatibility is therefore established on the two quantities that
actually matter to `mkpayload.py`:**

- `virt_base` comes from `text['vmaddr'] & ~(0x2000000-1)`. Both v68 and the CI
  kernel link at `0xfffffff007004000`, giving `virt_base = 0xfffffff006000000`.
- `kernel_end` is `max(vmaddr + vmsize)` over segments; it is a function of the
  linked image, not of the SDK.

`mkpayload.py` reads `cputype`, segments, `LC_UNIXTHREAD` pc and
`LC_DYLD_CHAINED_FIXUPS` and applies chained fixups at `image_base`. None of
those depend on `SDKROOT`. An iOS-targeted CI kernel at the same link address
feeds the existing M30 payload pipeline unchanged.

**What this does *not* establish.** Matching platform tags and link addresses
prove the packaging pipeline accepts the artefact. They do **not** prove the CI
kernel behaves like v68: the patch set differs (177 patches vs the v68 set), and
behaviour is exactly what failed before. Per the standing instruction not to
treat matching filenames or configurations as proof of compatibility, this is
treated as *packaging compatibility only*; behavioural equivalence must be
demonstrated by a measured boot, not inferred.

---

## 3. Priority 3 — provenance reconciliation

Two different records had been conflated. They answer different questions and
neither substitutes for the other.

| | Patch provenance manifest | Candidate packaging manifest |
|---|---|---|
| Path | `m30-patch-manifest.tsv` + `m30-patch-provenance.json` | `validation/ios-candidate-v68-out/manifest.json` |
| Produced by | `verify_patch_provenance.py` in CI | `mkpayload.py` at packaging time |
| Answers | which patches, in what order, with which hashes, were applied to the tree | what bytes went into the flashable image, and where they sit |
| Artifact | `m30-patch-evidence` (2,762 B) | not an artifact; committed with the candidate |
| Keys | order, name, sha256, status | `kernel_source`, `shim`, `payload`, `raw_combined`, `runtime_layout`, `android_boot_components`, `images` |

**Defect found and fixed.** The kernel hash recorded by CI was taken from
`dxb/build/$(ls dxb/build | head -1)`. That is a *build directory*, not the
kernel that gets packaged, so the provenance record's `kernel_sha256` did not
describe the shipped image — which is why the v86 kernel SHA read as UNKNOWN and
could not be trusted even when present. CI now hashes the file that the
"Verify exact M30 kernel binary" step verifies:

```
dxb/fakeroot/System/Library/Kernels/kernel.<kc>.m30lte
dxb/fakeroot/mach.<kc>.m30lte            (iOS layout)
```

and fails loudly if neither exists. A new **Publish kernel identity** step writes
`m30-kernel-identity.json` (kernel config, machine config, target, macOS version,
dxb sha, commit, run id, kernel path, sha256, size) to the step summary and as an
artifact, so a kernel can never again be consumed without a retrievable identity.
Logs are not reliably fetchable; summaries and small artifacts are.

---

## 4. Priority 4 — zero-risk analysis of the existing captures

`tools/analyse_fb_progression.py` reads the 25 decoded pstore captures already on
disk. No device access. Per instruction, **missing `SWEET SURF` records are not
treated as failure** — and the data confirms that would have been actively
misleading: the one boot where the lock screen appeared has **zero** SWEET SURF
records, while several failed boots have 7–9.

### The measurement that does discriminate

`M30 FB: done #N copied=<bytes>` is emitted when a framebuffer copy completes.
A full-frame copy on the M30 is ~10.1 MB (the v66 step size). Presence of a
completed copy separates the classes cleanly:

| Capture | `done #` records | max `copied=` | Lock screen |
|---|---|---|---|
| **v68 (accepted)** | **5** | **70,761,600** | **seen** |
| v73 | 5 | 50,544,000 | absent |
| v68t | 5 | 50,544,000 | unknown |
| v68t-native | 3 | 30,326,400 | absent |
| v67 | 4 | 40,435,200 | absent |
| v66 | 1 | 10,108,800 | absent |
| v55–v64 | 0 | 0 | absent |
| **v74** | **0** | **0** | absent |
| **v79** | **0** | **0** | absent |

Discrimination test over all 25 captures:

```
sweet_surf    seen=[0]          absent=[0,1,7]        -> NOT DISCRIMINATING
sb_alive      seen=[False]      absent=[False,True]   -> NOT DISCRIMINATING
crash_records seen=[0]          absent=[0,1,2]        -> NOT DISCRIMINATING
done/fb/size  seen=[138 recs]   absent=[0,4,5]        -> separates
copied_max    seen=[70761600]   absent=[0,10108800,…] -> separates
sw_max        seen=[11]         absent=[0,1,3]        -> separates
```

Read this carefully: `copied_max` **separates** the classes, but separation is
not sufficiency. Several failed boots also reach 20–50 MB. A completed copy is
necessary for a visible frame but not sufficient, so it is a *gate*, not a
pass/fail oracle. The correct use is negative: **`copied = 0` with a live
backboardd proves nothing was ever presented**, which is a cheap, high-confidence
rejection signal. `sw`/`pr` rising is meaningless on its own — v74/v79 show
`sw=0 pr=0` while v65 shows `sw=6` and still no lock screen.

### The v74 anomaly

v74 is the only post-0445 capture where backboardd reached selector **79** but
never reached 50, 55, 68 or 84:

```
v73 (progressed): ABI sel=79 in=2/0 s0=0x40 (64)   out=0/40
v74 (stalled):    ABI sel=79 in=2/0 s0=0x4d (77)   out=0/1580
```

Both return `out=0`, i.e. the synthetic response supplies no output bytes; only
the requested block ID and size differ, and v74 asks for a much larger block
(1,580 B). v74 then stops, `copied` never leaves 0, and no frame is ever
presented. This is consistent with the standing hypothesis that SpringBoard
fails before publishing a scene, with the stall occurring at the first
IOMobileFramebuffer block read rather than later.

**Limits of this analysis, stated plainly.** There is exactly **one** capture
labelled "lock screen seen", and 20 labelled absent; the discrimination result
rests on a single positive example and cannot be generalised statistically. The
outcome labels for v68t, uihb, uihb2 and sweetsample are "unknown" in the
project record, so they contribute no class information. Nothing here identifies
the root cause of the SpringBoard failure; it narrows where to look.

---

## 5. Priority 5 — low-overhead framebuffer diagnostic

Current cost is the real problem: the v68 capture holds 143 framebuffer records
at ~109 B, about 15.6 KiB of a 16 KiB ring, giving roughly **1.5 minutes** of
retention. The ring wraps before the interesting failure, which is the diagnostic
defect the v86 review identified.

**Design: transition logging, not event logging.** Emit a line only when the
observable state tuple changes:

```
state = (sw, pr, copied > 0, copied_bucket, done_count)
```

plus one heartbeat every 60 s and on any `done #` event. `copied_bucket` is
`copied >> 20` (MiB), so a monotonically growing copy counter cannot itself
drive output.

Worst-case quantification using the accepted v68 capture:

| Quantity | v68 observed | Transition-logged |
|---|---|---|
| `copied` distinct values | 3 | 3 |
| `sw` distinct values | 6 (6→11) | 6 |
| `pr` distinct values | 5 (4→8) | 5 |
| `done #` events | 5 | 5 |
| Heartbeats over ~1,370 s | — | 23 |
| **Total lines** | **143** | **≈ 42** |
| **Bytes at ~110 B** | **~15,600** | **≈ 4,600 (28% of ring)** |

Ring consumption drops from ~100% to ~28%, extending retention from ~1.5 min to
~5.3 min at identical information about *state changes*. Because it is driven by
a bounded tuple, growth is bounded by distinct states rather than by event rate:
the pathological case (a caller toggling `sw` every frame) is capped by the same
2 KiB hard budget verified in priority 1, after which the marker is the last line.

This is a design. It is **not implemented and not in v86**; it requires a new
patch and a rebuild, and is therefore part of the next candidate, not this one.

---

## 6. Priority 6 — revised experiment design and GO/NO-GO criteria

### What changed in our understanding

1. The v68 kernel is iOS-targeted, so the CI target is not the discrepancy it was
   reported to be. Packaging compatibility is established; behavioural
   equivalence is not, and must be measured.
2. The kernel hash in CI provenance was recorded from the wrong path. Fixed, and
   kernel identity is now published per run.
3. The acceptance criterion used by v86 (`SWEET SURF`) does not appear in the one
   healthy boot, so it could never have certified success. It must be replaced.
4. `copied = 0` with a live backboardd is a reliable *negative* signal; a
   completed copy is necessary but not sufficient.

### Acceptance criteria for the next candidate

**Prerequisites (all must hold before any device is touched):**

- P1. `git apply --check` of the full patch chain on a clean tree at the pinned
  XNU tag: 0 failures outside the allowlist. *(0456 now verified.)*
- P2. `test_patch_provenance.py` and `test_m30_smp_budget_boundary.py` pass.
- P3. `m30-kernel-identity.json` exists for the run and its `kernel_sha256`
  matches the kernel inside the packaged payload, recomputed locally. **A run
  without a retrievable kernel SHA is not a candidate.**
- P4. The payload is rebuilt from that kernel with `mkpayload.py`; resulting
  `ios-boot.img` size is under the 33,554,432 B partition limit.
- P5. `mkpayload.py` refuses a kernel whose `LC_BUILD_VERSION` platform is not
  iOS, so a target mix-up cannot reach the device.

**GO criteria (measured on the device):**

- G1. Boot reaches the pstore ring: records are recovered after the attempt.
- G2. `copied` becomes non-zero and a `done #` record appears. *(Necessary. If
  absent, stop — nothing was presented and no visual judgement is possible.)*
- G3. The native lock screen is observed on the panel.
- G4. The capture is decoded and committed with its records, so the next
  analysis is again zero-risk.

**NO-GO criteria (any one stops the attempt or fails it):**

- N1. Any prerequisite P1–P5 unmet.
- N2. Kernel SHA cannot be verified against the packaged payload. *(This alone
  blocked v86 and remains blocking.)*
- N3. `copied` stays 0 while `backboardd` is observed alive — per priority 4 this
  means no frame was presented; do not re-flash variations of the same image.
- N4. A regression in `done #` records relative to the accepted v68 baseline
  (5 records, 70.7 MB). Any candidate that presents less than v68 is strictly
  worse and must not be adopted.
- N5. The pstore ring is exhausted before the failure point, i.e. the diagnostic
  cannot observe the failure. If transition logging is not in the image, treat a
  full ring as NO-GO on *observability*, not on the kernel.

### Explicit non-goals for this round

- No physical flash, reboot or partition write has been performed.
- No candidate has been assembled, per the standing instruction that assembly
  waits on resolving the target discrepancy and the diagnostic defect.
- The target discrepancy is now resolved; the diagnostic defect is resolved in
  design (priority 5) but requires implementation and a rebuild.

### Single highest-value next action

Implement transition logging from priority 5 as patch 0457, rebuild, and require
P1–P5 including a published kernel SHA. That converts the next boot from an
unobservable attempt into one that either shows the lock screen or provably
presents nothing.
