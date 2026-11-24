# v66 physical boot test — SwapWait handshake fix

MAIN only. Candidate: `validation/ios-candidate-v66-out/` (source commit
`b0d421bf`, candidate commit `049ca6bb`, GREEN CI `45451311913`). v66 keeps the
v62/v65 kernel policy and `serial=3`, adding a bounded `SwapWait` completion
handshake and swap-done notification for M30LTE.

## Identity and flash gate

- Positive identity verified in TWRP: `SM-M305F`, `m30lte`, bootloader
  `M305FDDU8CVK1`, exact known serial, `ro.twrp.boot=1`. Serial-bearing
  evidence is intentionally redacted in this repository.
- Download Mode detected by Heimdall before any write:
  `raw/heimdall-detect.txt` and `raw/download-mode-gate.txt`.
- BOOT-only flash `2026-11-24T18:11:45Z..18:11:50Z` with Heimdall
  `--no-reboot`; `BOOT upload successful`. Image SHA256
  `5c502123f49b6a4d126ead6b377bfbeca500855d5b37660dd9160af49a18d4e5`.
- Device resumed with `heimdall print-pit --resume`. No USERDATA, SYSTEM or
  RECOVERY write; no Fastboot.

## Result

REJECTED for the lock-screen objective. User reported console text with
SMP/SpringBoard lines, not a persistent lock screen. Read-only pstore pull and
decoded records are in `raw/` and `decoded-pmsg.*`; see `analysis.txt`. No
lock-screen claim is made from the flash, console text, process liveness, IRT
state, or logs alone.
