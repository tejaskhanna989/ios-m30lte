# v52 physical boot — IRT patch restored; assertion persists

Device: Samsung Galaxy M30 SM-M305F (`m30lte`), serial `320081735bb166a3`,
TWRP recovery. Package: `validation/ios-candidate-v52-out/shim-boot.img`
SHA256 `d2e46bc18c161e9cd4c2c04f0c6eec96dc4166c479298f59285ac46bd2695cda`.

The first Heimdall attempt found no download-mode device and performed no write
(`heimdall-flash-failed-download-detect.log`). The device was then put into
download mode with `adb reboot download`; `heimdall detect` succeeded
(`heimdall-detect.log`). The BOOT-only flash and resume then both exited 0.
No BOOT readback. USERDATA, SYSTEM, and RECOVERY were not rewritten.

The 180 s window ran from `13:27:04Z` to `13:30:04Z`. The device was returned
to TWRP before pstore collection.

## Raw evidence

- `raw/pre-pmsg-ramoops-0`: pstore before v51/v52, SHA256
  `ecf0c2ed5289be600e956a014ee4bd1b01fd8aec2391124b57b426a649efdebd` (same as
  the v51 post-boot result, confirming a fresh window).
- `raw/pmsg-ramoops-0`: v52 pstore, 16,372 B, SHA256
  `409c2f25233750cc6e78b476c8e849207d8294e629b3a508d9e2c2f7e605de51`.
- `decoded-bootlog.txt`: decoded with `tools/m30_bootlog.py inspect`
  (124 records, 1 wrap issue).
- `heimdall-flash.log`, `heimdall-resume.log`, `heimdall-detect.log`, and
  `heimdall-flash-failed-download-detect.log` preserve the physical sequence.

## Result

v52 restores the v50 IRT patch state after the v51 regression:

```text
M30 IRT: patched _internal_release_type off 0xa432d84 (0 -> 3)
M30 IRT status: state=3 off=0xa432d84 ... hits=1 tries=29 sc=42 si=26
  fo=14843 vh=2782 oh=1 pr=-5 mo=0xa432000 ... replay=10
...
M30 IRT status: state=3 ... oh=1 ... replay=19
```

There are 10 `state=3` status lines with `oh=1` and `mo=0xa432000`, covering
`replay=10` through `replay=19` (~20 s of repeated post-patch status). This is
verifiable evidence that the IRT patch fired and remained visible in the ring.

The capture ends during the 30-iteration status loop; it does **not** contain
`M30 IRT: patched (final state=3 ...)`, `M30 IRT final: ...`, `xctest=`, or
`xctchunk=`. Therefore the new chunk counter cannot be evaluated from this
window. Absence of the final heartbeat here is a capture-timing limitation, not
a `state=2` failure: v51 ended with `M30 IRT final: state=2`, while v52 has no
failure heartbeat and has 10 post-patch `state=3` status lines.

The SpringBoardUI `NSInternalInconsistencyException` and its reason string are
still present, including at records `[024]`, `[027]`, and `[089]`, all before
the IRT patch marker at `[092]`. No `Early boot complete`. No UI or lock-screen
evidence. No UI success claimed.

## Interpretation

Observation: v52 removed the v51 regression and restored the v50 patch result
(`state=3`, `oh=1`, `mo=0xa432000`). The SpringBoardUI assertion still occurs
before the patch, exactly as in v50.

Working hypothesis (not proven by this capture): moving the retrigger back to
the v50-proven paths fixed gate timing, but the deferred gate starts the worker
later than v50, so the fixed 180 s capture ends before the compact heartbeat
loop. The chunk-path literal rewrite may not have fired at all; the absent
`xctchunk` field cannot decide this.

v50 remains the last candidate with a full compact final heartbeat
(`hb=24`, `xctest=1`). v52 is not rejected on IRT correctness, but it shows no
UI improvement. Any next candidate should first make the chunk rewrite
observable inside the status loop before changing behaviour again.
