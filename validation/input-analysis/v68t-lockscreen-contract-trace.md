# Native iOS lock-screen startup path — evidence trace and blocker

Status: **blocked** — no defensible source fix can be implemented from the
evidence permitted by this task. This document records the exact traced path
and the specific missing observation; it is not another cause list.

## Traced native path (from the shipped iOS 16.7.16 binaries)
1. `launchd` starts `com.SpringBoard` (`ProgramArguments =
   /System/Library/CoreServices/SpringBoard.app/SpringBoard`, `RunAtLoad=true`).
   Evidence: extracted `com.apple.SpringBoard.plist`.
2. `backboardd` starts and creates the main display surface. Evidence:
   `SWEET SURF: backboardd create id 2 1080x2340 ... keys 11 -> 0x0`.
3. SpringBoard's lock-screen presentation is implemented by
   `-[SBCoverSheetPresentationManager setCoverSheetPresented:animated:options:withCompletion:]`
   and `SBLockScreenManager`; both symbols exist in the shipped SpringBoard
   binary. `llvm-nm` on the extracted binary shows:
   - `0xe0f8 t -[SBCoverSheetPresentationManagerAccessibility setCoverSheetPresented:animated:options:withCompletion:]`
   - `0x1a7d4 t +[SBLockScreenManagerAccessibility ...]`
   - `0x19fa4 t +[SBWindowSceneAccessibility ...]`
4. Presenting the cover sheet requires a `SBWindowScene`/`UIWindowScene`
   created inside SpringBoard through FrontBoard (`com.apple.frontboard.systemappservices`
   is declared as a SpringBoard MachService in the launchd plist).

## What is proven on hardware
- `M30 UI: sb=27 bb=57 reason=none` (native-candidate pstore `d05b1b41…`).
- With heartbeat enabled: 140 records of `sb=27 bb=57 reason=none irt=3` (pstore
  `83c8cca8…`).
- IRT reaches state 3; framebuffer swaps/copies active; no fatal crash.
- Exact v68 cmdline produces the same Apple-logo-only result (evidence commit
  `31e71eb4`).

## Exact failing contract / blocker
There is **no observation** of step 3 or 4 actually executing: neither
`setCoverSheetPresented:` invocation nor `SBWindowScene` creation is exposed by
any enabled kernel hook. The only existing mechanism that can show where
SpringBoard is blocked is `sweet_sample_task()` in
`bsd/dev/sweet_sample.c`, which prints auser-space PC/LR/frame-pointer
backtrace for processes named in the `sweetsample` boot arg. That hook is
disabled by default and requires a physical boot with `sweetsample=1`;
the current task forbids physical flash/reboot. The persistent console ring
requires `a5log=1` and likewise needs another physical boot.

Therefore the exact failing call cannot be named from the permitted evidence.
Any XNU-side change (IRT, AMFI, framebuffer, code signing) would be speculative
and is explicitly forbidden. No SpringBoard/framework patch is permitted.

## Conclusion
Blocked at the userspace scene-creation boundary. Required next evidence (only
with a separately approved physical test): boot the current v68t kernel with
`sweetsample=1` (and optionally `a5log=1`) and decode the SpringBoard user
backtrace from pstore/console ring. That will identify the first failing call
inside step 3/4. Until then, no functional patch is justified.
