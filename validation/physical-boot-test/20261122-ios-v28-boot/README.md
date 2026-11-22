# iOS v28 physical boot — clean log, SpringBoardUI blocker isolated

Device: m30lte, serial 320081735bb166a3, TWRP 3.4.03.0.0-UNOFFICIAL.
Candidate: v28 (`602b13bb86a3db190c5c104ec8035435d0572fd8`), shim-boot.img
SHA256 `03fa2d70cdb5b169ce9d124199645594c96640f87ec3b6d1c0eb792d581434a6`.
BOOT flashed only via Heimdall (`--no-reboot`); USERDATA/SYSTEM/RECOVERY untouched.
No BOOT readback performed.

## Evidence

| File | SHA256 |
|---|---|
| `raw/pmsg-ramoops-0` | `edc4bf88ae53bcba231415345c96b80edb1865191865dbe5b0f1eb3cc3058089` |
| `raw/pre-pmsg-ramoops-0` | `5e5307a2cc61186784790fdac72fbed35dc94f40e71e0194c4b23f03cd930917` (v27 log) |

Decoded: 16372 bytes, 147 XNU records, 1 issue. The diagnostic flood from v22-v26
is gone — no `SWEET LDVAL`/`SWEET PLATQ`/`SWEET EXEC`/`SWEET CSOPS` records. The full
boot sequence is visible in the pstore ring.

## Confirmed milestones (physical)

- Deep genuine iOS 20H392 userspace: launchd boot tasks, dyld cache loader,
  HFSX root mount, and the full daemon set start (`keybagd`, `lockdownd`,
  `backboardd`, `mediaserverd`, `logd`, `configd`, `identityservices`, etc.).
- `SpringBoard[26]` starts (PID 26) and reaches Objective-C `+load` processing.
- No boot-task panic, no `Text page corruption`, no kernel panic, and the
  v18-era `lsd`/`securityd`/`backboardd` crash loop is gone.

## Current blocker

SpringBoard aborts during image initialization:

```
[056] CRASH SpringBoard[26] sig 6 ... slide 0x9ee8000 mh 0x10136c000
[060] STR *** Terminating app due to uncaught exception 'NSInternalInconsistencyException', reason: 'This process should not be linking or loading SpringBoardUI.framework (<rdar://problem/26143166>)'
```

This is the userspace `+[SpringBoardUI load]` assertion. LiveContainer's
`bypass_os_variant_has_internal_content()` works around the same iOS 16+ crash by
registering an `XCTestConfiguration` Objective-C class before the check runs
(`LiveContainer/Tweaks/Dyld.m`, commit `d2a329d`). The check is therefore a
class-presence probe, not a code-signing failure.

## Remaining non-fatal noise

- `CODE SIGNING: cs_invalid_page(...): p=N[...] final status 0x22000000, allowing
  (remove VALID) page` for daemons — still present but no longer fatal.
- `SWEET Sandbox: ... denied` / `privilege ... denied` events (expected with the
  permissive stand-in policy).
- `CRASH driverkitd[68] sig 9` — independent non-fatal crash.

## Next step

Kernel-side userspace compatibility shim: satisfy the `XCTestConfiguration`
class-presence probe without touching USERDATA, then reflash BOOT only and capture
pstore. No UI/lock-screen success is claimed by this evidence.
