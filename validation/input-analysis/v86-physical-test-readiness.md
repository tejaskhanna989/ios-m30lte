# v86 physical-test readiness assessment

Read-only investigation. **No device was touched**: no flash, no reboot, no
partition write. All evidence below is from this repository, its git history and
GitHub Actions metadata.

**Recommendation: NO-GO.** Three independent blockers, each sufficient on its
own. Details and evidence follow, then the precise fixes required before a
re-assessment.

---

## Q1 — v86 provenance

**There is no v86 candidate.** The name appears only in this session's report and
commit messages. `validation/` contains candidates up to `v78-ui-exact-touch`;
there is no `ios-candidate-v86-out`, no BOOT image, no package, no manifest.

What does exist is a **CI kernel build**, and its provenance is good:

| Item | Value |
|---|---|
| Run | `46125901817`, attempt 1, conclusion **success** |
| Source commit | `d2d8cac67a` |
| Patch count at that commit | **177** (176 original + `0456`) |
| Fail-closed pipeline | **Yes** — steps *Verify strict patch provenance*, *Every patch on disk is applied or allow-listed*, *No patch was silently skipped*, *Every applied patch exists on disk* all pass |
| Artifact | `xnu-kernel-macos-15-intel`, 9,761,357 bytes (zip) |
| Artifact availability | **Not retrievable.** `gh run download` fails `EOF` from `productionresultssa6.blob.core.windows.net` |
| Kernel SHA-256 | **UNKNOWN** — cannot be computed because the artifact cannot be downloaded |
| Patch order | Recorded in the run's `m30-patch-manifest.tsv`, shipped inside that unretrievable artifact |

So the provenance pipeline works and the build is trustworthy *as a CI build*.
It is **not a flashable artifact**, and the one identifier a physical test would
need — the kernel SHA-256 — is unavailable.

`HEAD` (`6517f6a`) differs from the built commit (`d2d8cac`) only in `README.md`
and the v86 report; `git diff` over `xnu/`, `tools/` and the workflow is empty,
so the committed patch set is exactly what CI built.

---

## Q2 — v68 comparison

The accepted v68 baseline, from `validation/ios-candidate-v68-out/manifest.json`:

| Item | Value |
|---|---|
| BOOT image (accepted) | `629843b597fd665b7de6b6578a1605455ef5786ae9e06101b591d13a80bf8c50` |
| Kernel | `b5e3b704a771fa7dc3e0afb23b7e2c99c7d251f7c8a4665ba0a0b5b16c163f83`, 16,807,480 bytes |
| XNU payload | `5a4fc4b790fcbd8fed24c41cbf6a7bf34d1861a4703e5325eca9b4a57db9…`, 16,179,712 bytes |
| ADT | `m30lte-corrected.adt`, 10,180 bytes |
| Stock cmdline | `debug=0xc serial=3 cpus=6 keepsyms=1 maxmem=292 rd=emmcroot0 emmcroot=USERDATA emmcprobe=1 emmcwrite=1 a5fb_noconsole=1 a5fb_keep_on=1` |

**v86 cannot be compared to this, because v86 does not exist as a boot image.**
Even hypothetically, the intended changes are not "only diagnostic":

1. **Toolchain/target difference.** v68's kernel is a `mach-o` at
   `/System/Library/Kernels/kernel.development.m30lte`, built through the legacy
   macOS path. The CI workflow defaults to `XNU_TARGET=iphoneos`, which builds
   `mach.development.m30lte` at the fakeroot root and adds
   `-DXNU_TARGET_OS_IOS`. Those are different preconditioning inputs, not
   cosmetic ones.
2. **Size.** v68 kernel is 16,807,480 bytes; the CI kernel is a 9,761,357-byte
   zip whose contents could not be measured. A 42% difference is not explained by
   `0456`, which adds ~70 lines.
3. **Unexplained pin history.** The `SweetFramebuffer.cpp` and
   `bsd/dev/sweet_sample.c` pins in CI never matched a buildable state until this
   session's correction, which itself was derived from CI observations. That
   means the relationship between the committed patch set and the produced binary
   has never been independently described. I corrected those pins with cited
   evidence, but the fact they were wrong for the project's whole history is an
   unresolved anomaly, not a closed item.

---

## Q3 — sampler fix (0456)

Verified by applying `0456` to a clean replay of the real patch chain onto
`xnu-8796.141.3` and reading the resulting source, not by trusting the tests.

**Correct:**

- Default is now `"-"` (off): `strlcpy(sweet_sample_names, "-", …)`, and
  `sweet_sample_thread` returns early on `sweet_sample_names[0] == '-'`. With no
  `sweetsample` boot-arg the sampler does **not** run.
- Budget default is 2 KiB with a `< 1` clamp to 1 KiB.
- Per-thread lines are accounted (`m30_sample_bytes += strlen(line)+1`) and the
  cap latches (`m30_sample_capped = true`) so the marker prints once.

**Defect found — the cap does not cover the header line.** The header is emitted
*before* any budget check:

```c
snprintf(hdr, sizeof(hdr), "SMP %s[%d] slide 0x%llx mh 0x%llx budget %d KiB", …);
if (m30_ls_diag_enabled) m30_ls_diag_line(hdr); else printf("%s\n", hdr);
m30_sample_bytes += (int)strlen(hdr) + 1;     /* counted, never enforced */
```

The `if (m30_sample_bytes > budget*1024)` test appears only inside the per-thread
loop. So if the sampler is enabled with `sweetsample=SpringBoard`, up to 80
header lines can still be emitted:

- `sweetsample=SpringBoard` → 80 × 65 B = **5,200 B = 32% of the 16 KiB ring**
- `sweetsample=SpringBoard,backboardd` → **10,320 B = 63% of the ring**

Both are unaffected by the 2 KiB cap. This does not affect the proposed test,
which uses the default (sampler off), but it means **"caps ring consumption at
2 KiB" is not true as written**, and the fix is incomplete for the case it was
designed for.

**Second, smaller issue:** `m30_sample_bytes` and `m30_sample_capped` are
function `static`s in a function callable from both the sampling thread and the
0455 diagnostic thread, with no synchronisation. Benign for `int`/`bool` on
AArch64 in practice, but it is shared mutable state in a diagnostic path and
should be per-sample locals or atomics.

---

## Q4 — would the proposed test produce discriminating evidence?

**No. This is the most important finding.**

The proposal is: boot with the stock v68 cmdline (no `sweetsample`), so the
sampler is dormant, then read `SWEET SURF` and `copied=` progression. The
question is whether those records can distinguish *scene-publication failure*
from *record eviction*.

They cannot, because the **accepted, working v68 capture already contains no
`SWEET SURF` records at all.** Measured from
`validation/physical-boot-test/20261125-ios-v68-boot/decoded-pmsg.json` (151
records, the boot on which the native lockscreen was observed):

| Record class | Count |
|---|---|
| `M30 FB:` framebuffer | 143 |
| other (AKS, IRT, HID) | 8 |
| **`SWEET SURF`** | **0** |

So "zero `SWEET SURF` records" is the signature of a **working** boot. The
acceptance criterion in the v86 report — "does a surface appear at all" — would
be satisfied by a completely healthy boot. It cannot falsify anything.

Worse, the framebuffer counter is also non-discriminating. The 143 records hold
only **three distinct `copied=` values**:

| ticks | sw | pr | copied | MiB |
|---|---|---|---|---|
| 15,600 – … | 6 | 4 | 30,326,400 | 30.3 |
| … | 10 | 7 | 50,544,000 | 50.5 |
| … | 11 | 8 | 70,761,600 | 70.8 |

`v` advances 15,600 → 97,800 (≈1,370 s at 60 Hz) while `copied=` moves through
just three values. It is the periodic heartbeat (every 60 s, `++ticks % 60`),
not a per-present counter — it samples a cumulative byte count at minute
granularity. Reading it cannot tell you whether frames were *presented* at a
particular moment; it only tells you how much had been copied when the last
heartbeat fired.

And the ring retention is only ~1.5 min of records (143 × ~109 B ≈ 15.6 KiB of a
16 KiB ring), so the earliest part of a boot is gone by the time anyone pulls it.

---

## Q5 — risk to the accepted v68 baseline

**The accepted artifacts are safe.** Nothing in this assessment writes to
`validation/ios-candidate-v68-out/`, and the proposal only changes which BOOT
image is flashed, which is reversible because:

- The original BOOT backup `m30-boot-original/boot.img` has hash `469c12d2…` and
  is intact per the v75 procedure.
- Prior tests (`v73`, `v74`) flashed BOOT only with
  `heimdall flash --BOOT … --no-reboot` and recorded "No USERDATA/SYSTEM/RECOVERY
  write".
- The USERDATA currently on device is `5f2e2e…` from release
  `ios-root-20H392-44905109656`, written 2026-11-21, and it is the same volume on
  which the parity failures occurred. v84 rated "USERDATA is not the controlling
  variable" as **moderate-high**, so using it for a comparison is acceptable.

The real risk is not damage to v68 — it is **spending the one physical test on an
experiment whose outcome is predetermined**, and being left with a capture that
says nothing either way.

**Second risk: the v68 boot behaviour itself is not reproducible from this
repository.** There is no local path to rebuild `kernel.development.m30lte`:
the only buildtree is `kb20278/xnu-buildtree/buildtree.tgz`, a stale `Sweet*`
generation, and the CI artifact that would supply a current tree is
unretrievable. So if a v86 boot regressed, the cause could not be bisected here.

---

## Q6 — safer or more informative alternative

**Yes, and it is strictly better.** The same question can be answered with
**zero physical risk** by mining captures already on disk, because the current
hypothesis makes a claim that existing data can test:

> "SpringBoard stalls before publishing a frontboard scene."

If a scene is never published, the framebuffer copy counter should **stop
advancing** early, and no `M30 UI`/surface activity should follow. Testing this
needs no new boot:

1. Across every existing capture with a known visual outcome (v68 lock screen
   present; v73/v74/v79 absent), extract the `M30 FB:` series and compare the
   `copied=` **plateau** — the tick at which it last changes — normalised against
   the record-retention window.
2. Compare the `sw`/`pr` fields at plateau. v68 reaches `sw=11 pr=8` with 70.8 MB
   copied. v79's captured values are already in the repository and can be read
   the same way.
3. If failing boots plateau at a materially lower `copied=`/`sw` than v68, the
   hypothesis gains support from existing data and the next physical test can be
   aimed at a *specific* threshold rather than a fishing trip. If they plateau
   indistinguishably, the hypothesis is weakened and the next test should target
   SpringBoard's start-up instead.

A better **diagnostic** also exists and needs no functional change: a monotonic
**per-present** record (one line per IOMedia/IOFramebuffer present, or a
`copied=` line emitted on change rather than on a 60 s heartbeat). That makes
"did frames reach the panel after time T" directly readable, which the current
heartbeat cannot answer. This is a diagnostic patch, not a UI change, and fits
the standing constraint that functional and diagnostic changes stay separate.

---

## Q7 — acceptance criteria that would actually discriminate

The v86 report's criteria are unworkable (see Q4). Replace them with conditions
that can fail:

**The test supports the scene-publication hypothesis if, with the sampler
dormant and the stock cmdline:**

1. A `M30 UI` heartbeat exists with both `sb=` and `bb=` non-zero (SpringBoard and
   backboardd alive — this is the control: it rules out "nothing started").
2. The `M30 FB:` `copied=` series **plateaus at a value below the v68 reference
   plateau** (v68: 70,761,600 B with `sw=11 pr=8`), and the plateau is reached
   early enough to be visible inside the retained ~1.5 min window.
3. No `CRASH` record for SpringBoard and no `SBERR`/`NSException` string appears.

**The test falsifies it if any of these hold:**

1. `copied=` reaches the v68 plateau and `sw`/`pr` reach `11`/`8` while the lock
   screen is still absent — frames were produced, so the defect is downstream of
   presentation and the hypothesis is wrong.
2. A `CRASH` record for SpringBoard exists — there is a real exception to chase,
   not a silent stall.
3. `sb=0` — SpringBoard never started, which is a different failure entirely.

**Explicitly NOT acceptance criteria:** the presence or absence of `SWEET SURF`
records (zero in the healthy v68 capture), and any absolute `copied=` value read
from a wrapped ring without knowing the record age.

---

## Required fixes before GO

1. **Produce a real candidate.** A v86 BOOT image must be built through the same
   packaging path as v68 (`mkpayload.py` → `m30lte-corrected.adt` →
   `combined.bin` → `ios-boot.img`) from a kernel whose SHA-256 is recorded, and
   published with a manifest carrying kernel SHA-256, payload SHA-256, BOOT
   SHA-256 and the full cmdline.
2. **Resolve the toolchain question explicitly.** State whether the candidate is
   `XNU_TARGET=macosx` (matching v68's lineage) or `iphoneos`, and justify it. A
   comparison against v68 requires the same preconditioning.
3. **Make the kernel retrievable and hash it.** Either fix artifact download in
   this environment or publish the kernel hash from CI (the workflow already
   computes it for `m30-patch-provenance.json`). **UNKNOWN kernel SHA-256 is a
   blocker**: nothing can be verified against it.
4. **Fix `0456`'s header bypass** so the 2 KiB claim is true, and make the
   counters per-sample rather than shared statics.
5. **Add a per-present or change-triggered framebuffer record** so presentation
   is measurable, otherwise even a correct candidate yields a non-discriminating
   capture.
6. **Do the zero-risk analysis in Q6 first.** It may make the physical test
   unnecessary, or aim it at a specific threshold.

## What is still uncertain

- Whether the CI kernel is even linkable into a bootable payload: it is built
  `iphoneos`-targeted, v68's is not, and the CI artifact cannot be inspected.
- Whether the 42% size difference from v68 reflects target/toolchain or an
  incomplete link.
- Why the `SweetFramebuffer.cpp` and `sweet_sample.c` pins were wrong for the
  project's entire history. I corrected them with cited evidence (CI run
  `46121357215` observed `ad6f8918…`, reproduced by an independent clean replay),
  but the anomaly itself is unexplained.
- Whether the v68 lock screen's appearance was repeatable at all, given the ring
  retains only ~1.5 min and no per-present evidence exists.

## Verdict

**NO-GO.** Not because v86 is dangerous — flashing BOOT is reversible and the
v68 backup is intact — but because the test as proposed **cannot answer its own
question**: its acceptance criterion (`SWEET SURF` records) is absent in the
working baseline, its framebuffer counter is a minute-granular heartbeat rather
than a present counter, and the candidate it would test does not exist as a
bootable artifact with a known hash. Running it would consume a physical test and
produce a null result that could be read either way.

The zero-risk analysis in Q6 should be done first. It is entirely repository
work and may materially change what the next physical test should be.
