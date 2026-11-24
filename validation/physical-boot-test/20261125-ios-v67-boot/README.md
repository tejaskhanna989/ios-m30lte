# v67 physical boot test — nonblocking SwapWait + notify push

MAIN only. Candidate: `validation/ios-candidate-v67-out/` (implementation commit
`03acae4f`, candidate commit `97264eae`, GREEN CI `45459907542`). v67 keeps the
v62/v65 kernel policy and `serial=3`, but removes the v66 blocking `SwapWait`
loop and pushes present-completion notifications to all registered framebuffer
notification types.

## Identity and flash gate

- Positive identity verified in TWRP: `SM-M305F`, `m30lte`, bootloader
  `M305FDDU8CVK1`, exact known serial, `ro.twrp.boot=1`. Serial-bearing
  evidence is intentionally redacted in this repository.
- Download Mode detected by Heimdall before any write:
  `raw/heimdall-detect.txt` and `raw/download-mode-gate.txt`.
- BOOT-only flash `2026-11-24T19:09:49Z..19:09:54Z`
  (`00:39:49..00:39:54 IST`) with Heimdall `--no-reboot`; `BOOT upload
  successful`. Image SHA256
  `afc7cac13eac9d56686d701d97afd65aa40e9a3e2fed98ed05ba7fd995ca4209`.
- Device resumed with `heimdall print-pit --resume`. No USERDATA, SYSTEM or
  RECOVERY write; no Fastboot.

## Result

REJECTED for the lock-screen objective. User confirmed at ~00:55 IST that the
screen stayed on the Apple logo indefinitely. Per explicit user instruction,
**no rollback was performed**; v67 BOOT remains installed and the device is in
TWRP. Read-only pstore pull and decoded records are in `raw/` and
`decoded-pmsg.*`; see `analysis.txt`. No lock-screen claim is made from the
flash, Apple logo, process liveness, IRT state, or logs alone.
