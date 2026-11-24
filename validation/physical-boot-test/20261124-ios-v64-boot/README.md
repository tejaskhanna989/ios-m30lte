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
| `raw/pmsg-ramoops-0` | `5331c2f90da194587d4f803fcef16cbdabef3b0241f55a25cb53a07751c8f1af` |
| `decoded-pmsg.txt` | `0c178a1c45270c73ab63d4025feaebd633f1642349af08b537993fcae4dff98e` |
| `decoded-pmsg.json` | `bde3a6c5195ed5ce00697a9eebd9dbfd77e7ba300d0333e6ed626c718187fa0f` |
| `stderr-extract.txt` | `7c2e8344193a25120ab9b4462bb3a3889c732a59bf4fca013d1114aaff4afbe7` |

## Visual result

User-confirmed: **no lock screen**. The final frame was a **clean Apple logo**
(same presentation as v62), not console text and not blank. v64 is definitively
rejected for the lock-screen objective.

## Pstore result

Pulled read-only from TWRP at ~`15:15Z`, identity re-verified before the read.

- Raw `pmsg-ramoops-0`: 16372 bytes, SHA256
  `5331c2f90da194587d4f803fcef16cbdabef3b0241f55a25cb53a07751c8f1af`.
- Decode: 156 records, 131 `XNU:`-tagged, `clean=False` (ring wrapped; expected
  for this long run).
- `SBERR`: **0** records survived in the captured ring. Because the ring
  wrapped, a very early SpringBoard fd-2 write could have been overwritten, but
  the diagnostic captured no evidence of one.
- `BBERR`: 13 writes, only three unique benign Objective-C duplicate-class
  warnings from `DualSenseHIDServicePlugin` / GameController in backboardd.
- `M30 UI: sb=26 bb=57 reason=none`: SpringBoard and backboardd both alive, no
  NS exception reason. No `NSInternalInconsistencyException`, no SpringBoard
  crash, no `SMP SpringBoard` telemetry survived the wrap.
- `M30 IRT` reached final `state=3`; counters include
  `csblk=3937 csfail=8 csvok=36903 cfa=3 cfi=5 cfp=0`. These are liveness
  telemetry, not lock-screen evidence.
- Crashes: `containermanager` sig 10 and `driverkitd` sig 9, both previously
  seen and unrelated to SpringBoard.

Conclusion: the earlier stderr/`write(2)` hypothesis is not supported by the
captured evidence. No surviving SpringBoard error record exists; the blocker is
most likely elsewhere in the UI presentation path.

## Acceptance

Apple logo, console text, process liveness, framebuffer activity, IRT state and
stderr capture are not lock-screen success. Only a persistent visible lock-screen
render plus supporting logs can close the objective.
