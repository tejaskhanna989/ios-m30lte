# v70 physical boot test — Apple logo persisted, NSException remained

MAIN only. Candidate `validation/ios-candidate-v70-out/` (source `528bb276`,
candidate `6e3296ee`, GREEN CI `45592281185`). v70 kept the 0446 heartbeat cap
and reverted the v69 key/HID diagnostic patches 0447/0448 to their v68 source
state. No touch driver, security change or selector synthesis was included.

## Identity and flash gate

- Fresh exact identity PASS in TWRP at `2026-11-25T10:32:50Z`
  (`16:02:50 IST`): `SM-M305F`, `m30lte`, bootloader `M305FDDU8CVK1`, exact
  known serial (redacted in committed evidence), `ro.twrp.boot=1`.
- Heimdall Download Mode detect PASS at `10:33:05Z` (`16:03:05 IST`),
  immediately before the write.
- BOOT-only flash `2026-11-25T10:33:17Z..10:33:22Z`
  (`16:03:17..16:03:22 IST`) with `--no-reboot`; `BOOT upload successful`.
  Image SHA256
  `51eef66440cc4abb0fe99db6a28628e440ee2406813929e587f3b5d5fce4a6e9`.
- Resume `10:33:28Z..10:33:32Z` (`16:03:28..16:03:32 IST`) succeeded and
  rebooted the device. No USERDATA, SYSTEM or RECOVERY write; no Fastboot; no
  rollback.

## Result

- PHYSICAL LOCK-SCREEN: **NOT OBSERVED**. The user reported `Apple logo only`
  at `16:10:28 IST`, about 6.9 minutes after resume. v68 remains the accepted
  lock-screen baseline.
- SpringBoard: **FATAL**. Pstore ends with
  `SBERR terminating due to uncaught exception of type NSException`, the same
  fatal record as v69. No reason, thread or backtrace survived.
- Correction assessment: reverting 0447/0448 did not restore the lock screen.
  The only remaining source difference from v68 is the logging-only 0446
  heartbeat cap; it is not proven causal. No broad investigation was started.
- GPIO -> HID: **NOT RETESTED**. The user confirmed no physical button was
  pressed after boot. HID touch/button user clients opened with one client each,
  but no transition records exist. The v69 runtime proof remains valid.
- TOUCH: **NOT OBSERVED / NOT IMPLEMENTED**.

## Pstore capture

- Device returned to TWRP; identity recheck PASS at `10:42:39Z`
  (`16:12:39 IST`); read-only pull immediately after.
- Raw 16372 bytes, SHA256
  `f380b9abb7463e7a83e77f274a559143d7da0ed5676732fbd3d26c375cebc77a`.
  Decoder: 169 records, `clean=False` (expected wrapped-ring leading
  `bad_magic`).
- Heartbeat cap worked: 5 `M30 FB: v=` records versus 138 in v68.
  9 `M30 FB: ABI sel=` records survive, including selector 79 twice; no
  selector response was synthesized.
- Serial-bearing evidence is intentionally redacted in this directory.

## Decision

Do not claim a restored lock screen, input support or touch support from this
run. Do not restore or reflash anything without explicit user direction. v68
remains the rollback baseline.
