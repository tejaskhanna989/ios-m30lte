# v65 physical boot test — diagnostic in progress

MAIN only. Candidate: `validation/ios-candidate-v65-out/` (source commit
`17948e4a`, candidate commit `b187a598`, GREEN CI `45439734351`). v65 adds
bounded direct-pstore framebuffer commit telemetry and keeps the v62/v64
kernel policy and `serial=3`.

## Identity and flash gate

- Positive identity verified in TWRP: `SM-M305F`, `m30lte`, bootloader
  `M305FDDU8CVK1`, exact known serial, `ro.twrp.boot=1`. Serial-bearing
  evidence is intentionally redacted in this repository.
- Download Mode detected by Heimdall before any write:
  `raw/heimdall-detect.txt` and `raw/download-mode-gate.txt`.
- BOOT-only flash `2026-11-24T17:07:34Z..17:07:38Z` with Heimdall
  `--no-reboot`; `BOOT upload successful`. Image SHA256
  `97f4f4044722ef4f9375f56685381e5889d9c75494bedd3d7d7d04f369956ac3`.
- Device resumed with `heimdall print-pit --resume`; the PIT confirms BOOT is
  a partition entry. No USERDATA, SYSTEM or RECOVERY write; no Fastboot.

Visual result and read-only pstore pull are pending. No lock-screen claim is
made from the flash, Apple logo, process liveness, IRT state, or logs alone.
