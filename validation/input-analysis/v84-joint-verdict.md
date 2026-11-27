# Case #167 — Joint Verdict

**To:** Mr. Craig Fedehri, Presiding Judge · **Authorised by:** Mr. Tejas Khanna,
Court Moderator
**From:** both investigators, reporting jointly
**Date:** 2026-11-27 · Read-only. No device access, no flash, no partition write,
no functional patch, no fabricated artifact. v68 preserved as the accepted
observed baseline.

Labels: **[PROVEN]** traceable to a committed file or a resolved commit;
**[HYPOTHESIS]** inference; **[UNVERIFIED]** no record exists.

Reproduce: `python3 tools/boot_axis_matrix.py`.

---

## 1. Established facts

1. **[PROVEN]** The display pipeline is not broken. Every heartbeat in every
   capture reports `dirty=0`; the vsync clock keeps firing ~5,800 times after the
   last present (v68: 138 samples to `v=97800`). A stopped present count is a
   *static screen*, not a fault — v68 stopped composing at 7.0 min and showed a
   lock screen at ~10 min.
2. **[PROVEN]** Two distinct failure modes exist:
   **A (fatal)** v69, v70 — `SBERR libc++abi:` → `NSException`;
   **B (silent)** v68t, v68t-native, v81 — no fatal record, composition stops at
   1.5–1.7 min, logging ends 5.2–6.2 min.
3. **[PROVEN]** The parity failures ran the **accepted** USERDATA volume. Every
   boot from v68 to v68t-native records *"No USERDATA, SYSTEM or RECOVERY
   write"*. Only two USERDATA writes exist: release `45651107666` (11-25) and
   `45949747024` (11-27). The images `dea9110c…`/`b0f5dba6…` were **never
   booted**.
4. **[PROVEN]** No volume identity has ever been recorded at boot; candidate
   manifests are BOOT-only. `5f2e2aa6…` is a release image hash, not a device
   reading.
5. **[PROVEN]** The IRT `state=2` vs `state=3` contradiction is a **sampling-window
   artifact**. Order is always `status(state=2)` → `patched (0->3)` →
   `patched (final state=3)`. v74 was pulled before the patch landed. **v68 has
   zero IRT records**, so IRT cannot separate success from failure.
6. **[PROVEN]** SpringBoard is present without observed progress in Mode B
   (v74: same pid, byte-identical registers across ~60 s, no crash record). Its
   own analysis assigns the shared first frames to an `objc_msgSend` stub wait.
7. **[PROVEN]** Recovered this round: patches `0446`–`0450` were absent from the
   tree but are intact at commit `528bb2760e`. They are now restored with a
   `sha256sum` manifest. **0446 is verbatim a print cap** — `++fb->fDiagTick;`
   plus a `<= 4800` guard. It changes no counter, staging, notification or power
   behaviour.
8. **[PROVEN]** The 0446-cap ↔ fatal-NSException correlation is **perfect across
   all five observable boots** (yes/yes, yes/yes, no/no, no/no, no/no).

---

## 2. Disproved or weakened theories

| theory | status |
|---|---|
| Framebuffer driver is the blocker | **DISPROVED** — `dirty=0`; v68 shows a UI on a stalled pipeline |
| SwapWait deadlock wedged the display | **DISPROVED** — final wait is closed by the following present; v68's wait records rotated out |
| Keystore `sel 10` rejection is causal | **DISPROVED** — v69, the first failure, has zero |
| USERDATA is the controlling variable | **WEAKENED to unsupported** — parity failures ran the accepted volume |
| IRT state is unstable across boots | **WITHDRAWN** — sampling artifact |
| 0446 causes the fatal exception | **DISPROVED as mechanism** — a print guard cannot raise an Objective-C exception |
| 0454 injects work into the present path | **WEAKENED** — gated on `m30uihb` + every 60th present; 0 `M30 UI HB` records in any case boot; the armed uihb2 boot still produced only 5 presents |
| 0451 Melfas touch causes Mode B | **UNSUPPORTED** — present in Mode B, absent from Mode A, but no `M30 TOUCH` records survive and no contact was observed. Correlation only |

---

## 3. Disagreements, and how they resolve

**D1 — Is 0446 a suspect?** One investigator ranked it contradicted (absent from
v68t-native); the other treated v68→v70 as an unexplained hard fact.
**Resolution:** both are right about different things. 0446 is **not a
mechanism** (its recovered body proves it only guards a `printf`), but the
correlation is genuine and perfect. It must therefore be read as a **marker of
build lineage**, not a cause. The mechanism it marks is the change below.

**D2 — What changed for v70?** The prose summary said "v68 + 0446 only".
**[PROVEN] false.** Commit `528bb276` contains **eleven** patches; `18322e15`
(v68) contains six. v70 adds `0446, 0447, 0448, 0449, 0450` — that is, the
diagnostics **and their revert patches, in the same build**. The composition was
confounded, and the record said otherwise.

**D3 — Can the missing artifacts be recovered?** **Yes, partially, and this
round did it.** Both source commits resolve on GitHub; `0446`–`0450` are
recovered verbatim and hash-pinned. **Not recoverable:** the v69/v70 *binary*
manifests (never created) and the v69/v70 **build artifacts** — both runs
(`45575704483`, `45592281185`) report `total_count: 0` artifacts. The patches
are recoverable; the exact binaries are not.

---

## 4. Most likely explanation

**[HYPOTHESIS — ranked first]** Mode A and Mode B are **separate regressions
sharing one outcome** (no lock-screen content is ever composed), and the
strongest remaining BOOT-axis explanation for the *pattern* is **patch-set
composition drift in a tolerant build pipeline**, not any single patch.

Supporting, in order of strength:
1. **[PROVEN]** The build script skips patches that fail to apply ("already
   upstream, previously applied, or malformed") and continues. A build can
   therefore differ from its documented patch list **without failing CI**.
2. **[PROVEN]** CI verifies applied-ness for only `0442`–`0445`. Patches
   `0446`–`0455` are **never** checked for application.
3. **[PROVEN]** v70's real composition (11 patches, including both 0447/0448 and
   their reverts) differs from its documented composition (6 patches + 0446).
   This is a **demonstrated instance** of the documentation diverging from the
   build.
4. **[PROVEN]** The one patch correlated with Mode A (0446) provably cannot
   cause it — so whatever did cause it was **not on the documented list**.

**[HYPOTHESIS — ranked second]** Mode B is dominated by `0451` (a genuinely
behavioural IOKit driver plus new boot args), confounded with the diagnostic set
and with USERDATA staging revisions. Insufficient evidence to rank higher.

---

## 5. Confidence

- That the display driver is not the cause: **high**.
- That the two modes are distinct: **high**.
- That USERDATA is not the controlling variable: **moderate-high**.
- That patch-composition drift explains Mode A: **low-moderate** — it is a
  demonstrated defect, but no record proves it produced a *bad* build.
- Which change causes Mode B: **low**.
- Any root cause: **not established**.

---

## 6. Remaining unknowns

1. Whether v70's build actually applied `0447`/`0448` before `0449`/`0450`
   reverted them, or skipped one or more. The build log is gone.
2. The exception **reason** for Mode A. Never captured, on either build.
3. Whether Mode B is a hang or a steady-state wait (§1.6 is consistent with both).
4. Whether SpringBoard ever publishes `com.apple.frontboard.systemappservices`.
   Still unobserved in all captures.
5. Which volume any given boot ran. Never recorded on the device.

---

## 7. Single recommended next experiment

**Make the build provenance auditable, then re-derive the baselines. Offline.**

**Action:** extend the existing `verify_m30_buildtree.py` gate so that **every**
patch present in `xnu/patches-minimal/` must either appear as
`Applying patch: …<name>` in `build.log` **or** be explicitly listed in an
allow-list of intentionally-unapplied patches. Fail the build otherwise. Extend
the CI "patch chain applied" loop from `0442`–`0445` to the full set, and record
each patch's `sha256` alongside the built `kernel.development.macho` hash.

**Success criterion:** a build where the set of applied patches is
mechanically enumerated and hash-pinned, so any future boot can be tied to exact
source. Concretely: `applied_patches == expected_patches` with zero silent skips,
and the kernel hash reproducible from the recorded patch set.

**Failure criterion:** any patch applied that is not in the documented set, any
silent skip, or a kernel hash that cannot be reproduced from the recorded
patches — each of which falsifies the assumption that our builds match their
documentation.

**Why this and not a new probe:** every remaining hypothesis needs a *known*
build. We now know the documentation and the build can diverge, and we cannot
tell which historical boots were affected. A new diagnostic on an unverified
build inherits the same defect.

---

## 8. Device requirement and authorisation

**Does it require a physical device? No.** It is entirely offline: patch
enumeration, build-log parsing, hash pinning and CI enforcement.

**Would it need separate authorisation? It needs none from this proceeding.**
It requires only CI compute. A *subsequent* physical retest of a now-auditable
build would require separate, explicit authorisation — and is not proposed here.

---

## 9. Final verdict

# ROOT CAUSE UNRESOLVED

**Precisely why.**

The cause cannot be established from the available evidence for three
independent reasons, each sufficient on its own:

1. **The decisive build is not reproducible.** v70 is the only isolated
   comparison on the BOOT axis, and its build artifacts no longer exist
   (`total_count: 0`). Its patches are recoverable — this round recovered them —
   but the binary they produced is gone.
2. **The mechanism cannot be inferred from the record.** The one patch
   correlated with Mode A is provably a print cap. Whatever caused a fatal
   Objective-C exception is **not on the documented patch list**, and the
   tolerant build makes it impossible to know what actually ran.
3. **The critical stage is unobserved in every capture.** Whether SpringBoard
   publishes the frontboard service, requests a scene, and what exception it
   raised are all recorded nowhere. Mode B is present-without-progress; the
   transition that fails is still outside the instrumented boundary.

We do not have evidence that identifies the failing transition, and we decline
to name one. What this proceeding *has* established is a large set of negative
results — the framebuffer, the deadlock, the keystore, the IRT state and the
USERDATA story are each ruled out or weakened with records — and one positive
finding of lasting value: **our builds are not guaranteed to match their own
documentation, and nothing in CI detects that.**

**Recommendation to the Court:** rule that the case remains open on causation,
and that the first act of any continuation is to make build provenance
auditable. Attribution attempted on unaudited builds is what produced three
wrong root causes earlier in this record.
