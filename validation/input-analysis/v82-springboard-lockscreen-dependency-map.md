# v82 — SpringBoard → lockscreen dependency map (independent investigation)

Scope: repository evidence and physical captures only. No device access, no
flash, no partition write, no Apple binary modification. Every claim below
carries the file it came from; anything not backed by a record is marked
**unverified**.

Read with `validation/physical-boot-test/20261127-v81-v68boot-compat-pstore/`
(v81) and `validation/physical-boot-test/20261125-ios-v68-boot/` (the accepted
boot). Reproduction: `python3 tools/summarize_pmsg_phase.py <pmsg files>`.

---

## 1. Dependency map: what each stage needs, and what we can see

Stage definitions follow the task. "Proof" means a record in this repository,
not an inference from a counter or a live pid.

### Stage 1 — launchd starts the services

| Needs | Evidence | Status |
|---|---|---|
| launchd runs from the HFSX root | `…20261126-v73-rootfs-boot/launchd.log` line 2 (`Darwin Bootstrapper Version 7.0.0`) | **proven** |
| SpringBoard job spawns | `Successfully spawned SpringBoard[27] because system support` (16:00:14.568) | **proven** |
| backboardd job spawns | `Successfully spawned backboardd[57] because speculative` (16:00:17.006) | **proven** |
| runningboardd (the process owner SpringBoard must register with) | `Successfully spawned runningboardd[26] because speculative` (16:00:35.476) | **proven** |
| lsd (LaunchServices front-end for scene/app registration) | `Successfully spawned lsd[103] because ipc (mach)` (16:02:31.268) | **proven** |
| No fatal exit for any of the four | 0 exit/crash lines for pids 26/27/57/103 in the v73/v74 logs | **proven** |

Ordering note: runningboardd starts **21 s after** SpringBoard. That is legal
(XPC-launch ordering is lazy) but it means SpringBoard's first assertion
requests are made against a bootstrapping domain.

### Stage 2 — backboardd initialises the display and framebuffer

| Needs | Evidence | Status |
|---|---|---|
| IOMobileFramebuffer published | `SWEET FB: display on`; selector traffic from `backboardd` | **proven** |
| Main display surface created | `SWEET SURF: backboardd create id 2 1080x2340 fmt 0x42475241 bpe 4 bpr 4352 planes 0 size 10186752 keys 11 -> 0x0` (v81 rec 102) | **proven** |
| Framebuffer ABI answers selectors 79/84/50/68/55 | `M30 FB: ABI sel=…` records, all `-> 0x0` | **proven** (return codes only; the *contents* of the selector-79 40-byte output are unverified — 0445 logs shape, not payload) |
| Layer staging reaches the driver | `M30 FB: staged #1..#4` | **proven** |
| Pixels copied to the panel | `present #1..#3 copied=10108800`, `done #1..#3` | **proven** |
| Driver keeps its vsync clock while idle | 138 heartbeats to `v=97800` with `dirty=0` | **proven** (see §3.1-3.2) |
| Composition continues past the boot logo | 8 frames in v68 vs 3 in v81 | **v68 only** — see §3.5 |

The v81 sequence is self-consistent to `done #3`. The final swap-wait
(`wait #7 token=3 before=2 done=2`) is satisfied by the `present #3` that follows
it, so **no wait is left outstanding**; the driver goes idle with `dirty=0`
because no further layer is staged. See §3.3.

### Stage 3 — SpringBoard initialises its app + lockscreen infrastructure

| Needs | Evidence | Status |
|---|---|---|
| Process alive **at the moment of the record** | `M30 UI: sb=27 bb=57 reason=none` (v81 rec 26) | **proven for one instant only** — v74's durable sampler showed this; it does not establish continued health, and §3.5 shows mode-B boots stop composing ~90 s later |
| Reads its preferences | `com.apple.springboard` plist with `BKNoWatchdogs=True`, `MCForceShowCloudConfigurationUI=False`, `FBLaunchWatchdogExceptions={com.apple.purplebuddy:100.0}` (extracted, `…20261125-ios-v68t-boot/host-logs/0004e807_…plist`) | **proven** |
| Activation gate satisfied | `mobileactivationd.log.0`: `Hactivation is enabled, short circuiting activation state to Activated` | **proven** |
| Setup gate satisfied | `SetupDone=True SetupFinishedAllSteps=True SetupVersion=11` (`0004e761_…purplebuddy.plist`) | **proven** (but see §5 — migration still re-runs) |
| Lock-screen manager / cover-sheet objects exist | nothing. No record names `SBLockScreenManager` or `SBCoverSheetPresentationManager` in any capture | **unverified** |
| SpringBoard resolved its own system container | indirect only: backboardd and lsd resolve theirs without crashing | **unverified** for SpringBoard |

### Stage 4 — FrontBoard / SystemAppServices provides scene infrastructure

| Needs | Evidence | Status |
|---|---|---|
| `com.apple.frontboard.systemappservices` declared by the SpringBoard job | present in the job's `MachServices` dict (`00029e50_com.apple.SpringBoard.plist`) | **proven (declared)** |
| SpringBoard actually **checked in** and published that service | nothing. There is no record of a successful `bootstrap_check_in` from pid 27 | **UNVERIFIED — earliest gap** |
| A SpringBoard scene request reaches FrontBoard | nothing | **unverified** |
| FrontBoard creates the scene | nothing | **unverified** |

`grep -ic frontboard` over every saved `launchd.log` (v68t, v73, v74) returns
**0**. FrontBoard is not a separate daemon on this system — it is a framework
inside SpringBoard — so the absence of a daemon is expected, but it also means
the repository has **never** observed this stage in any form.

*Correction to an earlier reading:* launchd's `Service stub created for …`
lines are issued for **outgoing lookups** by the process that requests a
service, and they are emitted for `backboardd[57]` (40 lines) but **never** for
`SpringBoard[27]` (0 lines). Those lines therefore do **not** prove that
SpringBoard failed to publish anything; they only confirm SpringBoard is not
doing lookups at that time. Publication cannot be read from them.

### Stage 5 — SpringBoard requests and receives the scene

No record exists in any capture. To reach this stage SpringBoard must first have
completed Stage 4.

### Stage 6 — lockscreen visible

Proven exactly once, by human observation:
`…20261125-ios-v68-boot/observation.txt` — lock screen at
`2026-11-25T06:07:50Z`, still present `06:22:49Z`.

---

## 2. The earliest unverified transition

**Stage 4: SpringBoard's `bootstrap_check_in` of
`com.apple.frontboard.systemappservices` (and of `com.apple.springboard.services`,
`PurpleSystemAppPort`, `com.apple.springboard.blockableservices`).**

Why this and not "scene creation": scene creation cannot be attempted until the
service is published, and stage 3 (process init) is proven only to the point of
"pid alive + preferences read". Everything from publication onwards is
unobserved in every one of the six captures.

Why it is not visible today: the kernel has no hook on `bootstrap_check_in`,
so nothing is recorded. This is a **visibility** gap, not proof of failure.

---

## 3. Is the framebuffer presenting? No — and that is not a fault

This section corrects the central misreading that every earlier pass made,
including the first draft of this document. The counter that looked like a
health check is a **composition** counter, and the vsync timer can be verified
alive independently of it.

**3.1 The timer never stops.** `M30 FB: v=` is emitted from
`(++fDiagTick % 600)`, i.e. once per 600 vsyncs, unconditionally from the timer
callback (`0442`, line 107). v68 emits **138** consecutive heartbeat records to
`v=97800`, spanning ~27 min — 5,800 vsync firings after its last present. A wedged
or deadlocked timer cannot do that. The timer fires, the reschedule works, and
`present()` simply finds nothing to copy.

**3.2 `dirty=0` says why.** Every heartbeat in **every** capture carries
`dirty=0`. In `SweetFramebuffer.cpp` the panel copy is gated on `fDirty`, which is
set only when a new layer is staged. Zero dirty means **nobody submitted a new
frame**. The driver is idle, not stuck.

**3.3 The one apparent deadlock is not one.** v81's last swap-wait reads
`wait #7 token=3 before=2 done=2`, which looks like backboardd waiting forever for
present #3. The very next records are `staged #4` then `present #3` — the wait for
token 3 **is** satisfied, and `fSwapDone` catches up. No wait is left outstanding.
The `wait #` records are bounded to `fPresentCalls <= 4`, so in v68 they were
rotated out of the ring; their absence there is a logging artifact, not a
difference.

**3.4 A static screen produces zero presents — by design.** v68 composed 8 frames
across boot and stopped at **7.0 min**, and its lock screen was static on screen
for the following ~20 min. That is the expected behaviour of an idle display
pipeline. Reading "presents stopped" as "the display broke" is therefore invalid
in principle, not just in this instance.

**3.5 What actually separates the boots is how many frames were ever composed.**

| boot | frames composed | composition stopped | log stopped |
|---|---|---|---|
| v68 (lock screen) | **8** | 7.0 min | never (27 min) |
| v68t | 5 | 1.5 min | 5.2 min |
| v81 | 3 | 1.5 min | 5.2 min |
| v68t-native | 3 | 1.7 min | 6.2 min |

v68 composed roughly **double** the frames of any failure before going idle, and
the extra frames are exactly the ones that paint a lock screen on top of the boot
logo. Nothing in this table is a hardware or driver fault; it is a count of how
much content the userspace compositor was ever given.

**3.6 Consequence for attribution.** The framebuffer driver is not** the
blocker, and it is not sitting in a deadlock either. It is an idle display waiting
for content. Every earlier conclusion of the form "the framebuffer stopped, so the
framebuffer is the bug" is refuted by the passing boot, where it did exactly the
same thing while showing a working lock screen. The blocker is upstream: whatever
should have produced the lock-screen content never did.

That is precisely the Stage 4/5 gap in §2 — and it is now supported by a positive
measurement (content starvation) rather than by absence of records.

## 4. Two distinct failure modes (this is the ranking's backbone)

The six captures are **not** six attempts at one failure. Sorting by surviving
evidence splits them cleanly, and the split survives the "is logging cut short or
just full?" objection because every zone is a full ring of identical size:

| mode | boots | SpringBoard fatal? | content composed | lock screen |
|---|---|---|---|---|
| **A — fatal** | v69, v70 | **yes**: `SBERR libc++abi:` / `terminating due to uncaught exception of type NSException` | 2-5 frames | no |
| **B — silent** | v68t, v68t-native, v81 | no: `M30 UI: sb=27 bb=57 reason=none` | 3-5 frames | no |
| **PASS** | v68 | no | **8 frames** | **yes, ~10 min** |

Mode A is a SpringBoard crash: the process dies on an uncaught Objective-C
exception whose reason was never captured. Mode B is a *silent* starvation:
SpringBoard stays alive, nothing fatal is recorded, the driver sits idle with
`dirty=0`, and the compositor never produces the frames that would paint a lock
screen. Different mechanisms, one shared outcome — the lock screen is never
composed.

**Corollary that removes two candidate blockers:** v69/v70 are the only boots with
the NSException, and **v69 has zero `sel 10` keystore rejections**. Neither the
keystore rejection nor the container metadata can be the cause of the *first*
regression. Any explanation covering only v70 onwards explains a secondary
symptom.

**Corollary about the BOOT axis:** v69/v70 changed only logging patches (0446
heartbeat cap; 0447/0448 reverted). A logging-only delta producing a fatal
NSException is a strong statement — either the reverted diagnostics were
load-bearing, or the exception is independent of the patch delta. The v70
`README` already reaches this conclusion and it stands.

**A decoder caveat that does not change the ranking.** `sp.records()` scans for
valid record boundaries instead of parsing from the header's `start` offset. That
is safe for *counting tags* (every surviving record is found exactly once) but
not for *time ordering*. Every timing claim in §3 rests on the ring-full argument
(identical 16,372 B zones, newest records last) and on the heartbeat's known
period, not on decoder ordering — so the ranking is unaffected. It should still
be replaced by a `start`-offset decoder before anyone builds a timeline from
interleaving.

## 5. Ranked blockers

| # | Blocker | Evidence | Confidence |
|---|---|---|---|
| 1 | **Lock-screen content is never composed (Mode B).** SpringBoard stays alive, the driver is idle and not dirty, and only 3-5 frames ever reach the panel. | §3.3-3.5; `dirty=0` in every heartbeat; 8 frames in the passing boot | **high** (that content is missing) |
| 2 | **SpringBoard dies on an uncaught NSException (Mode A).** Reproducible across two builds whose only delta from v68 is logging. | `SBERR libc++abi:` ×2 captures; reason never captured | **high** (that it is fatal), **none** on cause |
| 3 | SpringBoard never publishes FrontBoard / scene services (Stage 4), so no scene can be requested | no publication record in any capture; `frontboard` never appears | **medium** — the earliest *unobserved* step, and the most direct explanation of #1 |
| 4 | The device keeps re-running first-boot migration, so the UI never reaches a settled state | `datamigrator` 5× in v73/v74 vs 1×; `budd` spawn at 16:04:28 | **low** (no cause for the re-runs is recorded) |
| 5 | Keystore `sel 10` rejections | see §7 | **rejected as a cause** — v69 has none |

Blocker 1 and blocker 3 are the same failure seen from two ends: the driver can
only report that it was never given content, and Stage 4 is the stage that would
have produced it. Neither is provable with the current instrumentation, which is
what §6 addresses.

## 6. Minimal testable correction

Because the driver is idle rather than broken, **no framebuffer change is
justified as a fix.** What is justified is making the idle state and the missing
content observable, so the next boot answers the question instead of re-raising
it. Two repository-controlled changes, both bounded:

1. **Report idle-vs-starved explicitly.** Today a heartbeat with `sw=pr` frozen
   looks identical whether the panel is showing a static lock screen (v68) or
   nothing at all (v81). Emitting the last staged timestamp and the number of
   staged frames *since the last copy* turns "no presents" into either
   "static content, expected" or "starved, nobody ever staged". This is a
   logging change in `0442`, not a behavioural one.
2. **Name Stage 4 instead of inferring it.** Patch `0441` already mirrors tagged
   `stderr`; extending its tag list to SpringBoard's own bootstrap/`bootstrap_check_in`
   failure text (bounded to the first 32 lines, as today) would show whether
   `com.apple.frontboard.systemappservices` is published. Until that exists, §2's
   "earliest unverified transition" stays unverified by construction.

Neither touches an Apple binary, and neither changes an accepted artifact.

## 7. Why the keystore reading cannot be used either way

`SWEET AKS: securityd sel 10 … -> 0xe00002c7` appears 32x in v68t, v68t-native and
v81, 24x in v70, **0x in v69**, and 0x in the accepted v68 window. The natural
reading — "the keybag path is broken and blocks SpringBoard" — fails three ways:

1. **v69 is the first failure and has none.** A blocker cannot be absent from the
   first boot that fails while later boots with identical physical symptoms have
   it (§4 corollary).
2. **Every window is a rotated ring.** A surviving window contains only the most
   recent records, so "0 rejections" does not mean "no rejections happened"; it
   means none survived. That reading is only sound if the surviving window also
   contains successful calls, and **no capture contains a single successful
   `sel 10`**. The measurement cannot distinguish "all calls fail" from "no calls
   survived", so it cannot be compared across boots.
3. **It is an error return, not a crash.** `0xe00002c7` is
   `kIOReturnNotPermitted`-class; the client is told "no", which is a normal
   Apple response for an unentitled caller, and nothing observable follows it.

The same reasoning applies to the `SBERR objc[27]: Class MSDPreferencesFile is
implemented in both…` lines in **v68**: duplicate-class warnings are present in
the passing boot too, so they are noise, not signal. They were previously
recorded as "v68 has 3 SBERR" without noting they are warnings.

**What would settle it:** any capture containing a *successful* `sel 10` in the
same window as the failure, or a build whose 0038 log also prints the calling
pid. Neither exists, so this remains an open contradiction rather than a finding.

## 8. Independent assessment of the other investigation

As of this writing **no written report from the parallel USERDATA forensic
comparison exists in this repository** (`git log --all`, `git ls-tree` over
`main` and this branch: the only new evidence is
`20261127-v68-boot-compat-flash/` and `…v81-v68boot-compat-pstore/`). The
points below are therefore an assessment of the *experiment* and of the
reasoning recorded in those two directories, not of a document.

1. **Is the comparison complete?** No, and it cannot be from repository
   contents. Only three USERDATA identities are recorded (`5f2e2aa6…` works,
   `dea9110c…`, `b0f5dba6…`, `4f788a12…`), and **no image is in the tree** — the
   parts live in release assets. Any statement about *what differs inside* the
   images is unverifiable here until one is rebuilt in CI and diffed. Claims
   about the contents should be treated as unproven until such a diff exists.
2. **Do the differences explain the UI failure?** The one v81 data point shows
   v68 BOOT + v79 USERDATA fails with a BOOT that is bit-identical to the
   accepted one. That is consistent with the USERDATA mattering — but the v69
   result shows a *logging-only kernel delta on the accepted USERDATA* also
   fails, and fails **differently** (fatal NSException vs silent stop). So the
   two axes are not competing explanations of one failure; they are two
   independent ways to break the same missing stage. A USERDATA-only account
   leaves v69 unexplained.
3. **Does the proposed correction address the missing prerequisite?** Unknown —
   no correction is recorded. If a correction targets container metadata, note
   that v79 already applied the most complete variant and the lockscreen did not
   return.
4. **Correlation vs causation.** The largest risk in the record — and one this
   document itself fell into on first pass — is "framebuffer stopped copying
   ⇒ framebuffer is broken ⇒ that is the blocker". §3 refutes it twice over:
   the vsync timer keeps firing for 5,800 ticks after the last copy, and
   `dirty=0` shows the driver was never asked to copy anything. Any conclusion
   written before that check should be re-read with suspicion.
5. **Does the v81 experiment isolate the right variable?** Partly. It isolates
   USERDATA (BOOT bit-identical) — good. But it does **not** control time: it
   observed to ~12 min and pulled a window that covers boot head → 5.2 min,
   while the accepted lockscreen appeared at ~10 min *of uptime*. It is a fair
   test of "does this USERDATA ever show a UI", and the answer was no; it is not
   a test of "does the accepted configuration still reproduce", because the
   accepted USERDATA was not present.

**Verdict:** the v81 result is real and useful (it kills "the v68 BOOT alone was
the magic"), but it must not be reported as a root cause. The decisive
experiment remains the accepted pair.

---

## 9. Boot -> USERDATA provenance (the load-bearing assumption)

The whole ranking depends on **which data volume each boot actually ran**, and
that is recorded only indirectly, through the staging revision in CI:

| boot | outcome | staging rev (rootfs builder) | USERDATA identity per staging rev |
|---|---|---|---|
| v68 | PASS | `7e029cdd` (153 lines) | `5f2e2aa6…` |
| v69 | A: NSException | `7e029cdd` + logging patches | `5f2e2aa6…` (no USERDATA write) |
| v70 | A: NSException | same | `5f2e2aa6…` |
| v68t | B: silent | `1042340…` (+`fix_container_metadata`) | `dea9110c…` |
| v68t-native | B: silent | `1a85731…` (+mobile skeleton) | `b0f5dba6…` |
| v81 | B: silent | `9cad333…` (+`ensure_ui_daemon_containers`) | `4f788a12…` |

If this table is right, the two failure modes line up exactly with the two axes:

- **v69/v70 fail on the BOOT axis with the accepted data volume** — so a
  logging-only kernel delta is sufficient to break the UI into a fatal exception.
- **v68t and later fail on the USERDATA axis with a kernel that no longer
  contains 0447/0448** — silent mode instead of fatal.

That is the most important structural finding in this document, and it is also
the most fragile: the USERDATA column is inferred from CI staging revisions, not
from a hash recorded at flash time. **A capture that records the USERDATA hash
in pstore (or a read-only `/mnt/vendor/...` checksum at boot) would convert this
whole table from inference to fact** and is worth more than any further
diagnostic build.

## 10. Recommended next physical test (single variable, cheap)

Two candidate next tests, and the choice depends on which mode is more useful:

1. **Re-test the accepted pair** (v68 BOOT staging + USERDATA `5f2e2aa6…`) to
   ≥15 min. This tells us whether the 06:07 success is reproducible at all. If
   it reproduces, mode B is a USERDATA regression and the block is data-shaped.
   If it does not reproduce, the original success was a one-off and every later
   analysis has been chasing a configuration that never worked again.
2. **Re-test v69 BOOT with USERDATA `dea9110c…`** to see whether mode A persists
   on a different data volume. This distinguishes "the logging delta breaks
   SpringBoard" from "the 11-25 data volume was already marginal".

Test 1 is strictly more informative and is the one to run.

Whichever is run, capture **must** include the `wait/done` pair and the last
`SBERR`/`NSException` record. Those two measurements decide between blockers 1
and 2 with no further diagnostic build.
