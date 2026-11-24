# v62 known-good BOOT restore after v65 rejection

MAIN only. v65 was rejected after a final visual of Apple logo only and
durable pstore evidence that framebuffer presents stopped after five copies.

## Gate and flash

- Positive identity verified in TWRP immediately before the write:
  `SM-M305F`, `m30lte`, bootloader `M305FDDU8CVK1`, exact known serial,
  `ro.twrp.boot=1`. Serial-bearing evidence is redacted in this repository.
- Samsung Download Mode detected by Heimdall before any write.
- BOOT-only flash of known-good v62 image
  `7798b211ebc9773df3225732e572dc18d091d2805cc1f7be72f967fbdd0913c7`
  at `2026-11-24T17:28:19Z..17:28:24Z` with `--no-reboot`;
  `BOOT upload successful`. Device resumed with `heimdall print-pit --resume`.
- No USERDATA, SYSTEM or RECOVERY write; no Fastboot. No security change.
