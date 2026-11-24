# v64 physical boot test — diagnostic in progress

MAIN only. Candidate: `validation/ios-candidate-v64-out/` (source commit
`49e8e046`, candidate commit `f1da00ac`). v64 keeps the v62 kernel policy and
`serial=3`, adding only the bounded `SBERR`/`BBERR` stderr capture to pstore.

## Identity and flash gate

- Positive identity verified in TWRP: model, device, bootloader and exact known
  device identity all matched; recovery/TWRP boot confirmed. Serial-bearing
  evidence is intentionally redacted in this repository.
- Download Mode detected by Heimdall before any write:
  `raw/heimdall-detect.txt`.
- BOOT-only flash `2026-11-24T15:09:08Z..15:09:13Z` with Heimdall
  `--no-reboot`; `BOOT upload successful`. Image SHA256
  `d396bb549000993a009f7febf2e879f42626d6c7b0af5b34d8fe127f452d8960`.
- Device resumed with `heimdall print-pit --resume`; the PIT confirms BOOT is
  partition entry 15. No USERDATA, SYSTEM or RECOVERY write; no Fastboot.

## Evidence hashes

| File | SHA256 |
|---|---|
| `raw/identity-gate.txt` | `0f4d6b347b742be9eae6afa3946341f0ca44370921aade800a258ef160bd4675` |
| `raw/identity-props-redacted.txt` | `363201e67f0e075f5cee18cecc028da0684ceaa88654dfddc0549855cdcb4542` |
| `raw/download-mode-gate.txt` | `fd704179b7d72dec2d90b6b6a3c04b371e77ce410195fa51a389e02c8c5a3f84` |
| `raw/heimdall-detect.txt` | `38ba9867ff6cf3d7c8d1e7c42152c956bb3580cba25ff6bb2d1dae80ba0b5891` |
| `raw/heimdall-flash.log` | `4bf2478fcc951372568ebaba583f3bf005df3bedf67a5f85337ccc1d817d2a4c` |
| `raw/resume.log` | `976bfbc1f24490c104e56b66df50dea00a09959115d921fb0e38b39e77f07b4a` |

## Visual result

Pending user observation. No lock-screen success is claimed at this stage.

## Pstore result

Pending: pull `pmsg-ramoops-0` read-only from TWRP after the visual observation
window, then decode and look specifically for `SBERR`/`BBERR` records.

## Acceptance

Apple logo, console text, process liveness, framebuffer activity, IRT state and
stderr capture are not lock-screen success. Only a persistent visible lock-screen
render plus supporting logs can close the objective.
