# v86 — Overnight mission report

Status: **Priority 1 complete and CI-enforced.** Priority 3 produced one
confirmed, measured defect with a fix; causation of the missing lock screen
remains **UNRESOLVED**. No device was touched: read-only throughout, no flash,
no reboot, no BOOT/USERDATA/SYSTEM/RECOVERY write.

---

## 1. Defects confirmed

**D1 — The build could not prove what it contained.** `patch_build_sh.py`
replaced upstream's loop with one that printed `Skipping patch …` and continued.
A patch that did not apply was invisible twice over: not in the kernel, and not
in the record. CI checked applied-ness for four patches (`0442`–`0445`) and none
of `0446`–`0455`. This is the mechanism that let v70 ship eleven patches
documented as six.

**D2 — Nine patches were being skipped on every build, silently.**
`9999d`, `iobuffermemd_monterey`, `kas_info`, `machine_routines`,
`skywalk_sonoma`, `skywalk_ventura`, `syntax_checker_sonoma`,
`syntax_checker_ventura`, `TrustCache`. Each is now individually explained in
`SKIP-ALLOWLIST.txt` in one of three classes: repo-side target, shadowed by our
earlier hunks, or upstream revision mismatch. **None was found by inspection;
all nine were found by making the build fail.**

**D3 — My own verifier was wrong in four ways** (found by CI, in order):
it compared the manifest against one patch directory while the build stages two;
it hard-failed on stale allow-list entries belonging to *upstream*; it parsed
`build.log` without stripping the build script's ANSI colouring; and it globbed
every `patches/*/` subdirectory when `MACOS_VERSION=13.5` iterates only the top
level. Each is now covered by a test, and the last two by tests that run the
**real embedded CI script as a subprocess**.

**D4 (Priority 3) — Our own diagnostics were evicting the evidence.**
`0054` defaults the process sampler to `"SpringBoard,backboardd"` when the
`sweetsample` boot-arg is absent. `tools/test_m30_native_bootargs.py` asserts
that no accepted candidate (v68, v68t, v78) ever carried that boot-arg, so the
default has run on **every boot including the accepted baseline**. The ring it
writes into is `pmsg`, 16384 bytes ≈ 100 records.

Measured, not inferred:

| capture | sampler lines | bytes | share of ring | SWEET SURF records |
|---|---|---|---|---|
| `20261127-v79-pstore` | 57 | 8190 | **50%** | **0** |
| `20261126-v74-lockdiag-boot` | 29 (one sample) | 3771 | 23% | **0** |

v74 also shows the rest of the ring spent on AKS access logging (46 lines), which
is why a single sample still left only four framebuffer records.

The consequence is concrete: the surface-creation records and framebuffer
counters needed to answer "did SpringBoard ever publish a scene" were being
pushed out by backtraces of threads that were merely blocked.

---

## 2. Fixes implemented

| commit | change |
|---|---|
| `f625c4d`…`a47cfd5` | strict provenance (below) |
| `31ee1b6` | verifier models both patch sources; upstream stale entries warn |
| `1d07165` | strip ANSI before parsing `build.log` |
| `ab5e4c8` | glob only the iterated patch directory; diagnosis printed on failure |
| `890f65f` | accept the strict loop's own skip wording (`Allowed skip of <name>`) |
| `25ad8b6` | one named CI assertion per failure class |
| `46c31bc` | `OUT-OF-TREE:` allow-list prefix; 0456 budget patch |
| `a47cfd5` | 0456: sampler dormant by default + 2 KiB ring budget |

**Strict provenance, as enforced now.** `patch_build_sh.py` writes a TSV
manifest `order⇥name⇥sha256⇥status` with statuses `applied | allowed-skip |
FAILED`, and writes a `FAILED` sentinel row *before* exiting so the failure
survives even if shell `set -e` semantics swallow the subshell exit.
`verify_patch_provenance.py` fails on: missing/empty manifest, `FAILED` row,
undocumented patch, phantom row, SHA-256 drift, duplicate name, apply-order
drift, unjustified skip, stale allow-list entry (ours), and now a reason with
no checkable evidence in it. CI additionally asserts, as four separately named
steps, that every patch on disk is applied or allow-listed, that no patch of
ours is skipped unless marked `OUT-OF-TREE:`, that no skip is unjustified, and
that no applied patch is absent from the tree.

**`0456-m30-uihb-ring-budget.patch`** — two changes, both confined to the
sampler: the default is now `"-"` (off, `sweetsample=SpringBoard` still
enables it; the 0455 lock-screen diagnostic sets its own names and is
unaffected), and total sampler output is capped at 2 KiB per boot
(`m30samplebudget`) with a single latched marker line on exhaustion. No state
change, no injection, no timer or scheduling change.

---

## 3. Commits and CI runs

| run | result |
|---|---|
| `46062155779` | **kernel built**, 9,705,559 bytes; my verifier failed |
| `46063870150` | kernel built, 9,662,315 bytes; assertion failed on ANSI |
| `46066038733` | assertion failed on patch-directory scope |
| `46068304031` | assertion failed on skip wording |
| `46073400417` | **steps 10, 11, 12, 14 PASSED**; step 13 failed on `9999d` |
| `46119076115` | `ios-root-tests` **success** |

---

## 4. Test results

- `tools/test_patch_provenance.py` — **41 PASS**. Executes the generated bash
  against a scratch git repo (not a Python re-implementation), and runs the real
  embedded CI scripts as subprocesses against synthetic workspaces: consistent
  build, colourised log, upstream skip wording, missing patch, our-patch-skipped,
  unjustified skip, phantom application, and a guard that greps the patcher for
  its actual message text.
- `tools/test_m30_sample_budget.py` — **9 PASS** (new).
- `test_v82_dependency_map.py`, `test_v80_lockscreen_regression.py`,
  `test_m30_native_bootargs.py`, `test_mcm_build_input.py`,
  `test_ios_container_metadata.py` — PASS.
- `py_compile` over `tools/*.py` — clean.

**Latent defect found while testing, worth recording:** three patches
(`0031`, `0041`, `0401`) target HFS files that do not exist at the pinned
revision. Replaying all 176 patches onto a real `xnu-8796.141.3` checkout gives
167 applied, 0 unexplained skips, 3 failures — all `bsd/sweet_hfs/core/*`. They
are not allow-listed, which means CI must be applying them via a path this
replay does not model (the build applies patches from `dxb/patches/` after
upstream's own edits), so this is recorded as **UNVERIFIED**, not as a failure.

---

## 5. Is strict provenance enforced?

**Yes.** Every patch in the tree either applies and is recorded with order,
SHA-256 and status, or is named in `SKIP-ALLOWLIST.txt` with a reason containing
something checkable. A patch that fails to apply fails the build. The manifest,
its JSON report and `build.log` ship inside the kernel artifact, so a kernel
cannot be consumed without its provenance.

---

## 6. Are v68/v69/v70 reproducible?

**v68 — yes**, and its identity is pinned in `test_m30_native_bootargs.py`
(kernel `629843b5…`, boot image hash). **v69 and v70 — no.** Their artifacts
return `total_count: 0`; the binaries are gone and cannot be rebuilt, because
reproducing them requires the exact skipped-patch state of a tolerant build that
kept no record. The patches are recovered but the inputs to the build are not.
This is a permanent limit, not a pending task.

---

## 7. What we learned about the missing lock screen

**Confirmed by measurement:** the lock-screen investigation was destroying its
own evidence. Half the capture ring went to sampler output on a stock boot, and
the records that would show whether a scene was ever created — `SWEET SURF`
surface creation and the framebuffer `copied=` counters — were the first things
evicted. v74 and v79 both end with **zero** `SWEET SURF` records. Every
conclusion previously drawn about "no surface presented" from those captures is
therefore drawn from a ring in which the surfaces may simply have been
overwritten. This does not prove a scene was created; it proves the captures
could not tell us either way.

**Still unobserved:** whether SpringBoard publishes the frontboard service,
requests a scene, or raises an exception. That boundary is where the failure is
and it has never been inside the instrumented window.

---

## 8. Strongest remaining hypothesis

> The lock screen does not appear because SpringBoard stalls or fails **before
> publishing a frontboard scene**, and we have never had a capture wide enough
> to see it — because our own sampler consumed the ring.

**HYPOTHESIS, not proven.** It is ranked first because it is the only one that
explains the zero `SWEET SURF` records without requiring a new userspace
failure, and because the fix is already built.

Explicitly *not* supported: that USERDATA is causal (parity failures ran the
accepted volume), that the framebuffer commit path deadlocks (final wait closed
by the following present), or that `0446` caused the fatal exceptions (its
recovered body is a print cap; `2ee2c8d8…`).

---

## 9. Exact next physical experiment (proposed, not performed)

**Candidate v86.** Same kernel configuration as the accepted v68 baseline with
`0456` included, which means: sampler dormant, 2 KiB cap if enabled, and the
lock-screen diagnostic available behind `m30sblockdiag=1`.

Boot with **no** `sweetsample` boot-arg — the stock cmdline, unchanged from the
pinned v68 one. Pull pstore plus the durable pmsg sink after the first screen
update, and read, in this order:

1. **`SWEET SURF` records** — does a surface with nonzero dimensions appear at
   all? This is the question the previous captures could not answer.
2. **`copied=` counter movement** — does the framebuffer copy counter advance
   past the initial few, or stop?
3. **`M30 UI` heartbeat** — do `sb`/`bb` pids stay alive?
4. Only if 1 and 2 are silent, re-run with `m30sblockdiag=1` and the sampler
   forced to `SpringBoard`, now safe because of the 2 KiB cap.

Success criterion: a capture that either shows a scene being created (and the
lock screen still absent, which moves the defect downstream) or shows the ring
containing no surface activity *at all* even with the sampler silent (which
moves it upstream into SpringBoard's own start-up). Either result is new
information; the present record cannot distinguish them.

**No functional patch is justified until that capture exists.** Restoring the
default-on sampler, or patching SpringBoard or UIKit, would be guessing.
