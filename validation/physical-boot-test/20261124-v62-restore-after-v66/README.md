# Known-good v62 BOOT restored after v66 rejection

MAIN only. v66 was rejected after a read-only pstore pull showed the SwapWait
handshake ran but commit activity regressed to 1 swap/1 present and the final
visual was console text, not a lock screen.

## Gates and BOOT-only write

- Positive identity re-verified in TWRP: `SM-M305F`, `m30lte`, bootloader
  `M305FDDU8CVK1`, exact known serial, `ro.twrp.boot=1`. Serial-bearing
  evidence is intentionally redacted in this repository.
- Samsung Download Mode detected by Heimdall before any write:
  `raw/heimdall-detect.txt` and `raw/download-mode-gate.txt`.
- Known-good v62 BOOT image SHA256
  `7798b211ebc9773df3225732e572dc18d091d2805cc1f7be72f967fbdd0913c7`
  flashed BOOT-only with Heimdall `--no-reboot` at
  `2026-11-24T18:25:24Z..18:25:29Z`; `BOOT upload successful`.
- Device resumed with `heimdall print-pit --resume`. No USERDATA, SYSTEM or
  RECOVERY write; no Fastboot.
