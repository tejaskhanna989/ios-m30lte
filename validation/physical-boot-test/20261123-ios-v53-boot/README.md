# v53 physical boot — early DSC gate failed

Device: Samsung Galaxy M30 SM-M305F (`m30lte`), serial `320081735bb166a3`,
TWRP recovery. Package: `validation/ios-candidate-v53-out/shim-boot.img`
SHA256 `7cf35ab74045307f69f752eb6f6c1cfc638c402116a91f3e30f3ec5c1046df00`.

Device was reconnected in TWRP and re-identified before flashing. BOOT-only
flash and `heimdall print-pit --resume` both exited 0. No BOOT readback.
USERDATA, SYSTEM, and RECOVERY were not rewritten.

The fixed window ran from `14:08:34Z` to `14:11:34Z`. The device was returned to
TWRP before pstore collection.

## Raw evidence

- `raw/pre-pmsg-ramoops-0`: pstore before v53, SHA256
  `409c2f25233750cc6e78b476c8e849207d8294e629b3a508d9e2c2f7e605de51` (same as
  the v52 result, confirming a fresh window).
- `raw/pmsg-ramoops-0`: v53 pstore, 16,372 B, SHA256
  `ade2f38b0262da9db0996b03bbc4f989235aa6f36ae27feb5c54a245ed893a1c`.
- `decoded-bootlog.txt`: decoded with `tools/m30_bootlog.py inspect`
  (118 records, 1 wrap issue).
- `heimdall-detect.log`, `heimdall-flash.log`, `heimdall-resume.log`.

## Result

v53 is a regression and is rejected:

```text
M30 IRT final: state=4 off=0x0 err=0 sym=0x0 ... hits=0 tries=0 sc=0 si=-1
  fo=0 vh=0 oh=0 pr=0 fb=0x0 hb=1 xctest=1 xctchunk=0
...
M30 IRT final: state=4 ... hb=38 xctest=1 xctchunk=0
```

There is no `M30 IRT: patched _internal_release_type`, no `state=3`, no
`M30 IRT: early scan started on DSC header`, no `M30 IRT: XCTEST patch after
early scan`, and no `M30 IRT: retrigger` marker in the captured ring. The
durable heartbeat is `state=4` through `hb=38`.

`xctest=1` shows the v50 XCTest path still fired once. `xctchunk=0` shows the
v52 chunk rewrite did not fire in this boot. Neither produced a usable IRT
scan.

The SpringBoardUI `NSInternalInconsistencyException` remains at record `[042]`.
No `Early boot complete`. No UI or lock-screen evidence. No UI success claimed.

## Interpretation

Observation: gating the worker on a `dyld_v` header at file offset 0 did not
produce a successful scan. The worker ended in `state=4`, the same terminal
failure class seen in v49, and the marker for the new early path was not
captured. The captured ring does not contain the one-shot diagnostics that
would identify which failure path was taken, so the exact reason is not proven.

Working hypothesis (not proven): the early DSC-header page is still too soon
for the companion symbol file selection used by the Cryptex-first logic, or the
vnode recovered from that early fault is not the one the worker can resolve.

v52 remains the last physically successful IRT candidate (`state=3`, `oh=1`,
durable status replay). v53 is not eligible for further flashing. No UI claim.
