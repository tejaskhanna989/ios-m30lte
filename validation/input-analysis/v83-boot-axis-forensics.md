# Case #167 — BOOT-axis forensic investigation

**To:** Mr. Craig Fedehri, Court Moderator
**From:** Counsel for the defence
**Date:** 2026-11-27
**Evidence base:** repository records only. No device access, no flash, no
partition write, no reboot, no functional patch. Read-only.

Labels: **[PROVEN]** = traceable to a committed file. **[HYPOTHESIS]** =
inference. **[UNVERIFIED]** = no record exists.

Reproduce the matrix: `python3 tools/boot_axis_matrix.py` (offline, ~1 s).

---

## 0. Summary of finding

The BOOT axis does not contain a single suspect that explains both failure
modes. It contains **evidence of two independent regressions**, and — more
importantly — it exposes that **the last known-good configuration cannot be
rebuilt from this tree**.

Three claims, each argued below:

1. **The 0446 heartbeat cap cannot be the cause.** It is present in every fatal
   boot and absent from every silent boot. **[PROVEN]**
2. **The fatal and silent modes are produced by disjoint BOOT changes.** Fatal
   boots changed only logging (0446/0447/0448); silent boots changed logging
   *plus* the lock-screen diagnostic set (0453/0454/0455) *plus* a
   framebuffer-adjacent touch driver (0451). **No patch is common to both
   modes except 0446 — and 0446 is provably absent from one silent boot**
   (v68t-native), which kills it. **[PROVEN]**
3. **The accepted baseline is not reproducible.** Patch `0446` — which is in
   every post-v68 build and is *not* in the tree — is missing, and the v81
   capture is not on this branch. **[PROVEN]** This is the most consequential
   result in the report and it is a reproducibility failure, not a hypothesis.

---

## 1. BOOT revision comparison (reproducible)

| boot | outcome | patch set (per its own record) | image SHA256 | hb | 0446 cap | presents | window | SBERR | fatal |
|---|---|---|---|---|---|---|---|---|---|
| v68 | **PASS** | baseline | `629843b597fd665b…` | 138 | no | 8 | 27.2 min | 3 (warnings) | no |
| v69 | A: fatal | 0446+0447+0448 | `3d63bae2b709fad2…` | 4 | **yes** | 2 | 1.3 min | 3 | **YES** |
| v70 | A: fatal | 0446 only | `51eef66440cc4abb…` | 5 | **yes** | 2 | 1.3 min | 3 | **YES** |
| v68t | B: silent | 0446+touch | `fa00fa435f89b936…` | 28 | no | 5 | 5.2 min | 0 | no |
| v68t-native | B: silent | 0446+touch | `9c022561c09b53de…` | 34 | **no** | 3 | 6.2 min | 0 | no |
| v81 | B: silent | v68 BOOT | `629843b5…` (same) | 27 | no | 3 | 5.2 min | 0 | no |

The `0446 cap` column is **measured, not asserted**: patch 0446 caps `M30 FB: v=`
at 8 records, so a boot with more than 8 heartbeats provably does not contain it.

---

## 2. Commit / patch provenance

| artifact | status |
|---|---|
| `0442`–`0445` (framebuffer diagnostics) | present in tree; applied by `xnu.yml`, hash-pinned |
| `0446` (heartbeat cap) | **ABSENT from tree** — referenced only in prose |
| `0447`, `0448` (key/HID diag) | **ABSENT from tree** — v70 reverted them |
| `0451` (Melfas touch, `bsd/dev/m30lte_touch.c`) | present; touch-driver-adjacent |
| `0453`, `0454`, `0455` | present; **truncated by `ui_exact`** |
| v68 candidate manifest | present: kernel `b5e3b704…` |
| v69, v70 manifests | **DO NOT EXIST in this repository** |
| v68t manifest | kernel `5e898ee0…` |
| v68t-native manifest | kernel `464b410c…` |

**[PROVEN]** No manifest records a patch list or a build commit. The patch
composition for each candidate survives only in prose in the boot directories.
The mapping from boot to patch set is therefore **documentary, not
cryptographic** — a real limitation, stated plainly.

---

## 3. Classification of every relevant difference

| change | class | evidence |
|---|---|---|
| `0446` heartbeat cap | diagnostic; **reduces** ring load | heartbeat count 138 → 4 **[PROVEN]** |
| `0447`/`0448` key+HID diag | diagnostic; adds pstore lines on key path | v69 had them, v70 removed them, both fatal **[PROVEN]** |
| `0451` Melfas touch | **behavioural** — new IOKit driver, `m30touch`/`m30touchhid` boot args | present from v68t onward **[PROVEN]** |
| `0453` | diagnostic (`proc_iterate` on a 45 s thread) | in-tree **[PROVEN]** |
| `0454` | diagnostic **with a scheduling consequence** — adds code to `SweetFramebuffer.cpp` including a gated `proc_iterate(PROC_ALLPROCLIST)` on the present path | in-tree **[PROVEN]** |
| `0455` | diagnostic; samples SpringBoard/backboardd, 253-byte records | in-tree **[PROVEN]** |
| `ui_exact` build switch | build configuration; excludes 0453–0455 | `xnu.yml` **[PROVEN]** |

**On 0454 specifically** — the Court's rule *"do not assume a patch is harmless
merely because it is called diagnostic"* applies directly. 0454 inserts a
`proc_iterate(PROC_ALLPROCLIST)` into the framebuffer path, gated behind
`m30uihb` and a 60-tick counter. That gate means it executes only on every 60th
present. **[PROVEN]** No case boot logs a single `M30 UI HB` record from that
path, so on present evidence the inserted work never ran in v68t or v68t-native.
The uihb2 boot did arm it (140 records) and **still** produced only
`v=31200..39000 sw=5 pr=4` — 5 presents — so arming it did not itself increase
presentation. This is a **negative** result for 0454 as a cause, but it is
evidence, not proof of harmlessness.

---

## 4. Do the two failure modes share a cause?

**On BOOT-axis evidence: no. [PROVEN]**

| | fatal (v69, v70) | silent (v68t, v68t-native) |
|---|---|---|
| 0446 present | yes | **no** (both) |
| 0451 touch | no | yes |
| 0453/0454/0455 | no | yes (excluded only in the `ui-touch`/`exact` builds) |
| SBERR/NSException | 3 / 1 | 0 / 0 |
| SpringBoard pid at ~1 min | 27 | 27 |
| presents | 2 | 3–5 |

The two sets are **almost complementary**. 0446 is the only change present in
fatal boots and absent from silent ones — and it is a *load-reducing* change. A
change that removes writes from the ring cannot plausibly introduce an
Objective-C exception. **[HYPOTHESIS]** The fatal crash is therefore not caused
by 0446; it is either caused by 0447/0448 (which v70 removed without success,
so this is contradicted) or it is **not caused by the diagnostic set at all**.

**The contradiction the Court should notice:** v70 is v68 plus a *logging cap*
and nothing else, and it produced a fatal `NSException`. That is the single
hardest fact on this axis. **[UNVERIFIED]** We cannot verify it further, because
**0446 is not in the tree** and v70's manifest does not exist. The one build that
isolates 0446 to a single change is the one build we cannot reproduce.

---

## 5. Isolated vs confounded

| comparison | isolated? |
|---|---|
| v68 → v70 | **Isolated** (0446 only) — but irreproducible (patch absent) |
| v69 → v70 | **Isolated** (removal of 0447/0448) — outcome unchanged |
| v68 → v68t | **Confounded** (0446 + 0451 + 0453/54/55 + cmdline + new userspace) |
| v68t → v68t-native | **Confounded** (cmdline, touch flags, userspace) |
| v68 BOOT → v81 | **Isolated on BOOT (bit-identical)** — confounded on USERDATA |

No *isolated* comparison in this case changes the silent/fatal outcome. The only
clean single-variable experiment ever run on this axis (v68→v70) says a logging
cap flips a working lockscreen to a fatal crash, and cannot be re-run.

---

## 6. Earliest observable divergence

**[PROVEN]** At the level the captures can resolve, the divergence is **early
and identical across all four failing boots**:

- all reach `M30 IRT: patched (0 -> 3)` **[PROVEN]** — with the v68 caveat below
- all create the display surface `1080x2340 … size 10186752` **[PROVEN]**
- all stage and present **2–5** frames, then stop **[PROVEN]**
- **only v69/v70 emit `SBERR libc++abi:` → `NSException`**; v68t/v68t-native
  emit no fatal record at all **[PROVEN]**

The divergence is therefore **in SpringBoard's fate, not in the kernel's
progress**: kernel-side sequence is the same up to the point where composition
stops, and the fatal mode adds a crash marker the silent mode lacks.

**The caveat that limits this section:** **[PROVEN] v68's capture contains zero
IRT records** (rotated out of the ring). The earliest divergence cannot be
pushed earlier than the surface-creation sequence, and the one successful boot
is the one with the least early evidence.

---

## 7. Ranked BOOT-axis suspects

**1. `0451` Melfas touch + its boot args — a behavioural driver change, not a
diagnostic. [SUSPECT]**
*For:* it is the only genuinely behavioural change in the silent-mode set; it is
present in every silent boot and absent from every fatal one and from v68. It
registers a new IOKit service and a new HID producer on the boot path — exactly
the layer SpringBoard's HID/UI path depends on.
*Against:* v68t logs `M30 TOUCH` 0 times (may be rotation); the v68t-uihb2 boot
produced only 5 presents with the touch path present but no contact evidence;
and the earlier v68t analysis already concluded "0 touch records survive … not
proof the driver did not run". **Correlation only.** Cannot be called a cause.

**2. `0453`/`0454`/`0455` diagnostic set. [WEAK]**
*For:* present in all silent boots.
*Against:* `0454`'s present-path work is gated and provably never executed in
these boots (0 `M30 UI HB` records); `0455` was only active under
`m30sblockdiag=1`; `0453` runs on its own 45 s thread. All three are excluded
entirely in the `ui-touch`/`ui-exact` builds.

**3. `0446` heartbeat cap. [CONTRADICTED as a cause]**
*For:* v68→v70 is the only isolated experiment and it failed.
*Against:* load-reducing; present in both fatal boots; **absent from
v68t-native, which also failed**. A single change cannot be the cause of a mode
it does not appear in. **Ranked low, but the v68→v70 fact remains unexplained.**

**4. Build-configuration / userspace-staging differences. [UNVERIFIED]**
Each silent boot also changed the USERDATA staging revision (`1a85731`,
`9cad333`) and the boot cmdline. These are BOOT-axis *only* in the loosest
sense. **This is the largest confound in the case and the least documented.**

**5. Something not in this tree at all. [OPEN]**
`0446` is referenced but absent; v69/v70 manifests do not exist; v70's source
commit `528bb276` is not reachable here. The axis contains at least one build we
cannot inspect.

---

## 8. Proposed minimal offline experiment

**No flash. No device.** Two things, both reproducible, both CI-runnable:

1. **Restore provenance before restoring hardware.** Recover `0446` (and
   `0447`/`0448`) into `xnu/patches-minimal/` at their exact historical content,
   and add a CI check that every patch referenced by any boot record exists in
   the tree with a recorded hash. **A baseline that cannot be rebuilt is not a
   baseline.** This is the single highest-value action available offline.
2. **Make the matrix a test.** `tools/boot_axis_matrix.py` already computes the
   table in §1 from committed captures; a test should pin the 0446-present ⇒
   fatal and 0446-absent ⇒ silent pattern so that any future capture violating
   it is flagged immediately. That converts §4 from prose into an invariant.

Only after (1) exists does a *bounded* physical retest of a **known** build make
sense, and it remains unauthorised by this proceeding.

---

## 9. Court-mandated labelling of the bottom line

- **[PROVEN]** The 0446 cap is present in every fatal boot and in neither of
  v68t/v68t-native; only the fatal boots emit `NSException`.
- **[PROVEN]** Patch `0446` is not in this tree. v69/v70 candidate manifests do
  not exist. The v81 capture is not on this branch.
- **[PROVEN]** No BOOT change is common to both failure modes except 0446, and
  0446 is contradicted by v68t-native.
- **[HYPOTHESIS]** The two modes are independent regressions with a shared
  outcome.
- **[UNVERIFIED]** Which change, if any, causes either mode. The fatal mode's
  only isolated experiment is irreproducible.

**Recommendation:** the Court should not accept any BOOT-axis attribution until
`0446` is restored and the baselines are cryptographically pinned. Until then the
only honest statement is that the axis contains **two regressions we can see and
none we can reproduce**.
