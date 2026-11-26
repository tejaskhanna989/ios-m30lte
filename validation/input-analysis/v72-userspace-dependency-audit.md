# v72 userspace dependency audit — consolidated

Read-only audits of `main` (commits through `50147c7b`). No device operations.

## P0 — confirmed defect and fix

**LaunchServices crash loop.** Fresh pstore `77f3a5e5…` contains 32 decoded
records with `CRASH`: 7 `lsd` SIGABRT quadruples (PIDs 97, 101–104, 106, 108;
identical `pc 0x1d1daf198`, `lr 0x1e133e5f8`) and
`Process[…] crashed: lsd. Too many corpses being created.`. A recovered
`lsd-*.ips` shows `__31-[_LSDefaults userContainerURL]_block_invoke`,
`-[_LSDefaults userContainerURL]`, `historicalSecurePreferencesFileURL`,
`_LSServerMain`. All 29 cached MCM metadata records declare UUIDs matching no
directory (e.g. lsd `AAD4FDC5-…` in `6561B268-…`, lsd `58B7EA8C-…` in
`3EA10E23-…`); 0 UUID directories exist in the cached catalog. Nil container
path → Foundation `+[NSURL fileURLWithPath:]` raises → SIGABRT.

Fix: `tools/m30lte-root-tweaks.py::ensure_metadata_uuid_dirs()` creates
UUID-named content copies (with preserved ownership/mode/symlinks) before the
metadata rewrite; idempotent, traversal-safe. Regression tests in
`tools/test_ios_container_metadata.py`. CI gate in `ios-root-build.yml` uses
`tools/verify_rootfs_containers.py`. No device write, no auth/UI bypass.

## Confirmed present / healthy prerequisites

- SpringBoard and backboardd spawn and stay running; activation `Activated`;
  SetupDone / migration / SpringBoard preference values correct.
- Required binaries/frameworks/dyld cache exist (`SpringBoard`, `backboardd`,
  `lsd`, `BackBoardServices`, `FrontBoardServices`, `SpringBoardHome`,
  `UIKit`, `IOMobileFramebuffer`, dyld shared cache).
- HID path: `sweet_hid_touch()` → `SweetHIDTouch::touch()` →
  `IOHIDEventServiceUserClient` → user client. `backboardd` contains the
  required `com.apple.hid.system.user-access-service` entitlement; the button
  path previously reached `1 clients`. No missing rootfs HID entitlement or
  service found.
- Melfas patch 0451 builds/links and its boot-arg gates are verified; patch
  applies to the exact v68 buildtree.

## Missing evidence / components by priority

1. **P0 — prove corrected rootfs in CI and on hardware.** Current CI run
   `45806225340` must produce a new release with UUID dirs present; no physical
   test until reviewed. No USERDATA backup exists — one must be made read-only
   before any rootfs write (`v72-rootfs-physical-procedure.md`).
2. **P0 — lsd health after fix.** Fresh pstore must show 0 `CRASH lsd` and no
   "Too many corpses" before attributing anything else to SpringBoard.
3. **P1 — lock-screen scene transition.** No `SBCoverSheetPresentationManager`
   / `SBWindowScene` creation observed; `sweetsample=SpringBoard,backboardd`
   boot produced 0 `SMP` samples. This remains unobserved, not disproven.
4. **P1 — Melfas runtime telemetry.** No `M30 TOUCH` producer record survives;
   0451 uses the console mirror, which is muted after GUI present and ring-
   wrapped. Add durable early telemetry only with explicit approval; hardware
   I2C power/clock and IRQ 243 routing remain unproven.
5. **P1 — complete asset audit.** `CoverSheet.framework`, wallpaper assets,
   icon-layout DBs were not in the host cache; the corrected rootfs image must
   be inspected in CI to close this gap.
6. **P2 — secondary configuration defects.** `/private/var/containers/Temp`
   absent from cached catalog (script creates it, but cached device snapshot
   lacks it). `tools/verify_ios_root_assets.py` is stale and must not be used
   as a readiness gate. `com.apple.oscard` provider absent (not proven causal).
   Several hardware-variant launchd failures (wifid, checkerboard,
   biometrickitd.pearl, etc.) are expected on M30 and not lock-screen blockers.

## Do not do
No fake lock screen, no auth bypass, no speculative service additions, no
SpringBoard/framework patch, no touch success claim without physical contact
evidence.
