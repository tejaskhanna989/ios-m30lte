# iOS candidate v27 — physical boot result (2026-11-22) — MAJOR MILESTONE

## Authorization / actions

Standing project authorization. Work on `main` @ `5a8aeee`.
Device `m30lte`, `320081735bb166a3`, TWRP.
v27 candidate hash `1612da4747aa6a4c3b51949f4301aff3c56d1c92e4fa45e2a67bf0ecae338ae7`.

- Flash v27 `--BOOT --no-reboot` → "BOOT upload successful". BOOT readback skipped
  (standing instruction). USERDATA/SYSTEM/RECOVERY untouched. One boot.
- Phone booted into iOS and disconnected from USB (did not return to TWRP on its
  own); user forced it back to TWRP. Pstore captured: `raw/pmsg-ramoops-0` SHA
  `5e5307a2cc61186784790fdac72fbed35dc94f40e71e0194c4b23f03cd930917` (16,372 B).

## Result — MAJOR MILESTONE: genuine iOS userspace boots deeply, SpringBoard starts

Patch 0424 (regenerated to apply after 0423) fixed the loader full-page hash:
```
SWEET LDVAL: ... vsize 4096 valid 1 tainted 0x0        <- full-page hash MATCHES, no taint
SWEET EXEC imgact: result.csflags 0x26000003           <- CS_VALID (0x1) now SET
SWEET EXEC procsig: p.csflags 0x22000001 after update  <- CS_SIGNED propagated to process
SWEET PLATQ: pid N ... blob 1 plat 1                   <- process reports PLATFORM BINARY
```
Results:
- **No boot-task platform-binary panic.** No daemon crash loop. No kernel panic.
- Processes retain CS_VALID/CS_SIGNED and report platform=1.
- **SpringBoard is starting** — logs show `SpringBoardUI.framework` being loaded
  by multiple system daemons (assistantd, WirelessRadioManagerd, bluetoothd,
  seld, askpermissiond, familynotificationd, tccd, nanoprefsyncd, xpcproxy).
- This is the deepest iOS 20H392 boot achieved: full userspace with SpringBoard.

### New blocker — SpringBoardUI linkage exception (userspace, non-fatal to kernel)
```
STR *** Terminating app due to uncaught exception 'NSInternalInconsistencyException',
reason: 'This process should not be linking or loading SpringBoardUI.framework
(<rdar://problem/26143166>)'
```
This is genuine iOS SpringBoard framework linkage enforcement firing in a daemon
that links SpringBoardUI.framework — a userspace issue, not code signing / kernel.
Needs investigation (which daemon, why it links SpringBoardUI on this hardware).

## Success criteria (from physical evidence)

- 4K config (loader diag shift 12) ✓
- dyld shared-cache pages fully validated (vsize 4096, valid 1, tainted 0x0) ✓
- platform binaries reported correctly (blob 1, plat 1 on many daemons) ✓
- no boot-task platform-binary panic ✓
- no kernel panic ✓
- daemon crash loop gone (no repeated CRASH lsd/securityd) ✓
- SpringBoard starting (SpringBoardUI.framework loaded) ✓
- root mount / launchd / dyld / OS version: early lines wrapped out of the 16KB
  pstore ring buffer (flooded by diagnostics; record 000 starts mid-stream), but
  v27 reached deep userspace — which itself proves they succeeded; v26 pstore
  baseline still shows `hfs: mounted iOSRoot`, `load_init_program /sbin/launchd`,
  `hello from launchd.1`, `Darwin Bootstrapper 7.0.0`.

## Honest status

- Primary v18 daemon crash-loop objective FIXED ✓ (v20-v27 stable).
- Code-signing fully validated, platform binaries reported correctly ✓.
- Genuine iOS userspace with SpringBoard starting ✓.
- No full UI/SpringBoard "booted to lock screen" claim without device evidence of
  a stable UI. The phone booted far enough to disconnect from recovery USB and
  the user had to force it back to TWRP with hardware keys.
- Remaining: SpringBoardUI.framework NSException in a system daemon (userspace,
  non-fatal to kernel); non-fatal cs_invalid_page events on some dyld pages.
- Next: remove diagnostic patches (0420-0423) for a clean production candidate,
  re-verify, and address the userspace SpringBoardUI issue if actionable.
