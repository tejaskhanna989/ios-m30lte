# Independent investigation: native lockscreen pipeline on M30LTE

Branch: `investigation/native-lockscreen-independent`. No device access used.
This document derives its claims from committed physical records, preserved
pstores, extracted launchd logs, the dyld/plist artifacts and repository git
history only. It does not adopt any prior agent's conclusion.

## 0. Controlling differential

| Boot | BOOT | USERDATA | Visual result |
|---|---|---|---|
| accepted v68 (`20261125-ios-v68-boot`) | `629843b5…` | `5f2e2aa6…` | native lockscreen at 06:07:50Z, still present 06:22:49Z |
| v81 compatibility (`20261127-v81-v68boot-compat-pstore`) | `629843b5…` (bit-identical) | `4f788a12…` | Apple logo at 3 min, still logo when observation ended ~12 min |

Because BOOT is bit-identical, the only controllable difference is USERDATA
(and whatever runtime state it produced). This is the strongest available
differential and it rules out a BOOT-only explanation for the latest failure.

## 1. Dependency map and evidence per stage

### Stage 1 — launchd service startup
Expected: launchd loads SpringBoard and backboardd jobs and advertises their
MachServices. Evidence: the SpringBoard launchd plist extracted from the image
declares 33 MachServices including `com.apple.frontboard.systemappservices`,
`com.apple.springboard.services`, `PurpleSystemAppPort`,
`com.apple.springboard.statusbarservices`; `RunAtLoad=true`, `KeepAlive=true`,
user `mobile`. The launchd logs available (`v68t` host-logs, `v73`, `v74`)
show `Successfully spawned SpringBoard[27]`, `backboardd[57]`, `keybagd[44]`,
`containermanagerd[65]`, `lsd`, `datamigrator`, `securityd`,
`mobileactivationd`.

Caveat: those launchd logs were extracted from the HFSX image (manifest
file IDs, e.g. `0004e76f_launchd.log`), not captured live; the v73 and v74
copies are byte-identical. They prove job loading in that image, not runtime
check-in. No launchd log exists for the accepted v68 boot.
Status: startup of the processes is supported; endpoint check-in is not.

### Stage 2 — backboardd display initialization
Expected: backboardd opens the framebuffer user client, gets display geometry,
creates an IOSurface, presents frames. Evidence: pstores for both the accepted
v68 boot and the failed v81 boot contain
`SWEET SURF: backboardd create id 2 1080x2340 fmt 0x42475241 bpe 4 bpr 4352 size 10186752 keys 11 -> 0x0`,
plus selector and trap records. This is a real, successful display-surface
creation in both cases.
Status: verified in both boots.

### Stage 3 — SpringBoard initialization
Expected: SpringBoard reaches a state where it can host scenes. Evidence:
`M30 UI: sb=27 bb=57 reason=none` in both pstores; SpringBoard and backboardd
PIDs stable; zero `CRASH`, zero `NSException`, zero `SBERR`/`BBERR` in the v81
capture. The v73/v74 captures also show no fatal SpringBoard record.
Status: process liveness and absence of a fatal exception are verified;
SpringBoard's internal initialization state is not.

### Stage 4 — FrontBoard / SystemAppServices availability
Expected: SpringBoard checks in as provider of
`com.apple.frontboard.systemappservices` and clients can look it up. Evidence:
the service is declared in the plist, but **no launchd log or pstore record in
the repository shows a client check-in or lookup for this service**. Searches
for "frontboard" in all three extracted launchd logs return zero lines.
Status: **not verified in any capture**. This is the earliest stage at which
the chain lacks positive evidence.

### Stage 5 — Scene/session creation and activation
Expected: SpringBoard creates an `SBWindowScene`/`FBSScene` and activates a
system application session. Evidence: none of the captures exposes scene
creation. The sweetsample sampler produced unusable `objc_msgSend` stub frames
and flooded the pstore ring in v74; the v68/v81 kernels have no sampler, so no
backtrace exists. `launchd.log` mentions `PassbookUISceneService` job loading,
which is not SpringBoard scene creation.
Status: not verified; no existing record can confirm or deny it.

### Stage 6 — Native lockscreen presentation
Expected: `SBCoverSheetPresentationManager` presents the cover sheet and the
wallpaper/clock/unlock controls are drawn. Evidence: visual observation only
for accepted v68. No failing boot has any record of this call.
Status: not verified in any failing boot.

## 2. What the framebuffer copies actually prove

`M30 FB: v=<n> sw=<s> pr=<p> copied=<bytes>` is emitted on the framebuffer
present path of the XNU patch chain. Comparing the two captures:

| Capture | FB records | v range | final `sw/pr` | final `copied` |
|---|---|---|---|---|
| v68 accepted | 138 | 15600..97800 | `11 / 8` | 70,761,600 |
| v81 failing (same BOOT) | 27 | 3000..18600 | `4 / 3` | 30,326,400 |

Both rings are full (16,372 bytes), so the tail is the newest retained record.
The v68 capture ends at v≈97800 (~27 min at 60 ticks/s); v81 ends at v≈18600
(~5 min). Therefore:

- A framebuffer surface was created and at least three frames were presented in
  the failing boot. The display path is not dead.
- After ~5 min, **no further present/heartbeat records were emitted** in the
  failing boot. That is consistent with "no new frames were presented", which
  is what one expects when no scene exists — but it does not prove that
  framebuffer presentation is the cause. It is a downstream symptom, or a
  capture-window artifact, not an established root cause.
- The accepted boot's higher counters are partly a capture-age difference: it
  was pulled after ~27 min, the failing one after ~12 min of wall time with
  only ~5 min of retained FB records. Counters alone cannot date a regression.

## 3. Earliest unverified transition

**Stage 4 — FrontBoard system-app-services check-in / availability**, followed
immediately by Stage 5 scene creation. This is the earliest point in the native
path for which no positive evidence exists in any boot, accepted or failing.
Stages 1–3 are supported to the extent described above. No capture in the
repository can currently distinguish "FrontBoard service never registered"
from "service registered but scene creation stalled".

## 4. Ranked possible blockers (unresolved, not established)

1. **Scene creation never starts (Stage 4/5).** No observation exists. This is
   the earliest unverified transition and is consistent with every capture:
   liveness, surface, no presented frame after ~5 min.
2. **USERDATA-derived runtime state prevents SpringBoard from considering the
   device ready for a lockscreen scene** — e.g. migration/Setup state
   (datamigrator runs once in the v68t-era launchd log vs five times in the
   v73 image log), activation state, or keybag/data-protection state. These are
   correlations from image-extracted logs, not live captures; they do not
   establish causation.
3. **Container path resolution changes caused by later MCM staging.** The
   original staging script at `7e029cd` has 153 lines and no MCM metadata code;
   the current script adds mobile-container skeletons, an allow-listed MCM
   build input and a SpringBoard system container. Any of these changes what
   BaseBoard resolves at runtime. No capture proves which path SpringBoard
   actually used in either boot.
4. **Framebuffer presentation stalls.** Supported only as a symptom:
   copies stop at 3 frames in the failing boot. Not accepted as root cause.
5. **A hardware/timing difference between the two physical sessions.** Not
   controllable from the repository; the compatibility experiment kept BOOT
   constant but not wall-clock environment.

## 5. Minimal repository-controlled fix

None is justified. The earliest failing operation is unobserved, and the
repository contains no source-level contract that identifies a missing call,
service or entitlement. Adding a SpringBoard/FrontBoard patch, another MCM
variant, or a display workaround would be speculative and is explicitly out of
scope. The correct next step is a bounded observation of Stage 4/5, not a code
change.

## 6. CI tests

No code change is proposed, so no new correctness gate is justified. A future
fix must add focused tests that assert the specific service/scene contract it
implements and must keep the existing lsd/MCM and boot-arg regression gates
green.

## 7. Safe physical verification plan (NOT executed)

Required to resolve Stage 4/5:
1. Keep the accepted v68 BOOT bit-identical (already installed) and, if the
   user authorizes a separate write, restore the original `5f2e2aa6…` USERDATA
   as the only variable.
2. Use a bounded, non-flooding observation of SpringBoard's scene path — a
   selector- or unwind-level trace limited to a handful of records written to a
   non-wrapping pstore sink, gated by an explicit boot arg and off by default.
   Do not reuse the v74 sampler: its frames were unusable stubs and it flooded
   the ring.
3. Observe for at least 20 minutes, recording XNU→Apple logo→lockscreen
   transitions with timestamps. Pull pstore immediately after returning to
   TWRP and note the boot age from the last `M30 FB: v=`.
4. Success requires a visibly rendered native lockscreen. SpringBoard PID,
   backboardd surface, framebuffer counters or absence of crashes are not
   success.

No physical step in this plan has been performed.
