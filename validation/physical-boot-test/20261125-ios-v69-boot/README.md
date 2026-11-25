# v69 physical boot test — buttons reached HID, Apple logo persisted

MAIN only. Candidate: `validation/ios-candidate-v69-out/` (source commits
`30badb2a`, `7be16020`, candidate commit `f34c48a8`, GREEN CI `45575704483`).
v69 is logging-only: quiet framebuffer heartbeat, bounded M30 key diagnostics,
bounded HID diagnostics. No touch driver was added and no security policy was
weakened.

## Identity and flash gate

- Fresh identity PASS in TWRP: `SM-M305F`, `m30lte`, bootloader
  `M305FDDU8CVK1`, exact known serial (redacted in committed evidence).
  Download Mode detected by Heimdall before the write.
- BOOT-only flash `2026-11-25T09:17:20Z..09:17:25Z`
  (`14:47:20..14:47:25 IST`) with `--no-reboot`; `BOOT upload successful`.
  Image SHA256
  `3d63bae2b709fad2d58a973158ff9d87bed1403ab64cdfc30b461879477d6835`.
- Resume attempt started `09:17:32Z` (`14:47:32 IST`) and failed with
  `Failed to send file part size packet!`, but the device left Download Mode
  and booted XNU. No USERDATA, SYSTEM or RECOVERY write; no Fastboot; no
  rollback.

## Result

- PHYSICAL LOCK-SCREEN: **NOT OBSERVED**. The user reported the device stuck at
  the Apple logo and restarted it. v68 remains the accepted lock-screen
  baseline.
- BUTTONS -> HID: **RUNTIME PASS at producer/HID boundary**. 66 GPIO transition
  records and 67 HID dispatch records with `1 clients` survived in pstore.
  This is stronger than compile-only evidence but does not prove UI response.
- TOUCH: **NOT OBSERVED / NOT IMPLEMENTED**. No Melfas producer exists.
- Pstore heartbeat reduction worked: 4 `M30 FB: v=` records versus 138 in v68;
  7 selector ABI records survived for the first time. See `analysis.txt`.

## Pstore capture

- Device returned to TWRP; identity recheck PASS at `09:48:54Z`
  (`15:18:54 IST`); read-only pull immediately after.
- Raw 16372 bytes, SHA256
  `f029f1f266c335256414ce4801dfac5ad78a25db5dc1c193c07aea13b9a4e8fe`.
  Decoder: 225 records, `clean=False` (wrapped-ring leading bad_magic).
- The user's restart overwrote the early bounded `M30 KEY:` / `M30 HID:` lines;
  surviving pre-existing key/HID lines still establish GPIO-to-HID delivery.
- Serial-bearing evidence is intentionally redacted in this directory.

## Decision

Do not claim input support or a display regression cause from this run. Do not
restore or reflash anything without explicit instruction. v68 remains the
rollback baseline. Future work should either capture pstore earlier after a
boot or add an even lower-volume key/HID trace before further physical tests.
