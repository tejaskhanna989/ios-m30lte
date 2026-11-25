# v68 physical boot test — selector ABI diagnostic, lock screen observed

MAIN only. Candidate: `validation/ios-candidate-v68-out/` (implementation commit
`18322e15`, candidate commit `7c583deb`, GREEN kernel CI `45529035057`). v68
keeps the v67 framebuffer behavior unchanged and adds only the bounded
`M30 FB: ABI sel=` pstore trace from patch 0445. No selector response was
synthesized and no security or console policy was weakened.

## Identity and flash gate

- Positive identity verified in TWRP: `SM-M305F`, `m30lte`, bootloader
  `M305FDDU8CVK1`, exact known serial, `ro.twrp.boot=1`. Serial-bearing
  evidence is intentionally redacted in this repository.
- Download Mode detected by Heimdall before any write:
  `raw/heimdall-detect.txt`, `raw/heimdall-info.txt` and
  `raw/download-mode-gate.txt`.
- BOOT-only flash `2026-11-25T05:57:07Z..05:57:11Z`
  (`11:27:07..11:27:11 IST`) with Heimdall `--no-reboot`; `BOOT upload
  successful`. Image SHA256
  `629843b597fd665b7de6b6578a1605455ef5786ae9e06101b591d13a80bf8c50`.
- Device resumed with `heimdall print-pit --resume` at
  `05:57:28Z..05:57:33Z` (`11:27:28..11:27:33 IST`). No USERDATA, SYSTEM or
  RECOVERY write; no Fastboot; no rollback.

## Physical result

PHYSICAL LOCK-SCREEN OBSERVATION: **PASS**. See `observation.txt` for the exact
user-confirmed timeline. Early text was seen at ~2 minutes, then the user
reported a persistent iOS lock screen at ~10 minutes and confirmed it was the
iOS wallpaper/clock/unlock UI. It remained unchanged at the ~25-minute check.
No lock-screen claim is inferred from build logs, flash logs, Apple logo,
console text, framebuffer activity, process liveness, IRT counters or pstore
alone.

## Logs and deferred evidence

- `raw/` contains the exact identity, Download Mode, Heimdall flash and resume
  logs. `SHA256SUMS` hashes the committed evidence.
- The user explicitly chose to keep iOS running, so the device was not returned
  to TWRP and no pstore capture was attempted after this boot. The selector-79
  scalar inputs and block IDs therefore remain unobserved.
- NEXT: when the user permits a TWRP return, capture `pmsg-ramoops-0` read-only
  and decode it to identify the real block IDs. Only then implement an
  evidence-backed selector response with focused regression tests. Do not
  fabricate a response from the 1,580-byte output size or any other guess.
