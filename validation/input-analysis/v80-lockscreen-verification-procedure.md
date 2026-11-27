# v80 — lock-screen regression: verification procedure (NOT executed)

This is the physical test that would confirm or refute the attribution in
`v80-lockscreen-regression-analysis.md`. It is written for a human with the
device; nothing here has been run by the agent.

## Hypothesis under test

The accepted lock screen (2026-11-25 06:07Z) was produced by

- BOOT `629843b597fd…` (v68 candidate) and
- USERDATA `5f2e2aa6…` (release `ios-root-20H392-44905109656`, written 2026-11-21),

observed for **≥ 15 minutes**. Every later combination changed BOOT, USERDATA or
the observation window.

Prediction: `v68 BOOT + 5f2e2aa6… USERDATA + ≥15 min` shows the lock screen
again. If it does, the regression is the USERDATA/BOOT pair, not SpringBoard.
If it does not, the 2026-11-25 success was not reproducible and the cause is
elsewhere (and must include device state that no partition image captures).

## Why a 15-minute window is mandatory

The accepted boot reached the lock screen ~10 minutes after resume, and the
`v68t-native` rebuild was abandoned at ~6 min with the Apple logo
(`v68t-native` analysis). A 5–10 minute check cannot distinguish "regressed"
from "not there yet".

## Preconditions (all read-only)

- TWRP with ADB; identity `SM-M305F` / `m30lte` / `M305FDDU8CVK1` / known serial.
- Original BOOT backup `m30-boot-original/boot.img` hash `469c12d2…` intact.
- BOOT source: `validation/ios-candidate-v68-out/ios-boot.img`
  (`629843b597fd665b7de6b6578a1605455ef5786ae9e06101b591d13a80bf8c50`).
  The file is committed; no rebuild is required.
- USERDATA source: release `ios-root-20H392-44905109656`, parts `part-aa…ad`
  (sizes and SHA-256 in `validation/ios-root-ci-build-20261121.md`).
  Reassemble with `cat parts | gunzip > ios-root.img` and verify
  `5f2e2aa6a80aea489946287d8cc32ef0ff6a1905a0d2923e8d4324163bb699b5`.

## Procedure

1. BOOT-only Heimdall flash of the v68 image, `--no-reboot`, Download Mode gate
   first. No BOOT readback required (v68 was already verified by hash).
2. **USERDATA**: re-write `5f2e2aa6…` only if the current image differs. Stream
   `cat parts | gunzip | adb shell dd of=/dev/block/by-name/USERDATA bs=4194304`,
   `sync`, bounded first-64-MiB readback hash check.
3. Boot with a stopwatch. Record the visual state at **2, 5, 10, 15, 20, 25 min**
   (Apple logo / console text / lock screen / black). A photo or a one-line note
   per checkpoint is enough.
4. Do **not** pull pstore before the 15-minute checkpoint: the pull requires
   returning to TWRP, which ends the test.
5. Only after the last checkpoint, return to TWRP and pull pstore read-only.

## Interpretation table

| Visual result | Meaning |
|---|---|
| Lock screen at ≥10 min | The accepted configuration reproduces. The regression is the USERDATA/BOOT pair; any fix must keep both. |
| Apple logo at 25 min | The 2026-11-25 success was a one-off or depends on device state not in either image. Report it as such; do not build another candidate on the assumption that images alone determine the outcome. |
| Lock screen, then lost when BOOT is later changed | Isolates the BOOT contribution exactly. |

## What NOT to conclude

- A visible Apple logo plus live `SpringBoard`/`backboardd` pids does not mean
  the UI is working.
- `copied=` counters in the first minutes of a boot do not measure whether a
  scene exists; the accepted boot also started there.
- Five separate USERDATA-era boot tests (v69, v70, v68t, v68t-native, v79)
  already failed with distinct BOOTs. Do not repeat any of them.

## Related lead (not a cause)

In the v73/v74 launchd logs, `datamigrator` runs **five** times
(16:02:24 → 16:05:41) and a 31-service XPC burst follows at 16:04:28, including
`com.apple.purplebuddy.budd`. In the first post-v68 boot (v68t, USERDATA
`dea9110c…`) migration ran **once** and exited 0. Repeated migration is
consistent with iOS deciding the data volume still needs Setup, which would
explain `budd` starting and the absence of a lock-screen scene — but no
surviving log shows why migration re-runs, so this stays a lead. If the
procedure above reproduces the lock screen, this lead is moot; if it does not,
capture `datamigrator` output next.
