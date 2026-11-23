# v54 physical boot — early-retry candidate restored the IRT patch

Device: Samsung Galaxy M30 SM-M305F (`m30lte`), serial `320081735bb166a3`,
TWRP recovery (`ro.twrp.boot=1`). Package:
`validation/ios-candidate-v54-out/shim-boot.img` SHA256
`1da365a3b352575a366d2d8e898e0a8585afc56fd917ca95c5e122af0aeb4d5c`.

Explicit user approval was given for this BOOT-only test. The device was
positively re-identified in TWRP before flashing. `heimdall flash --BOOT ...
--no-reboot` and `heimdall print-pit --resume` both exited 0. No BOOT readback.
USERDATA, SYSTEM, and RECOVERY were not rewritten.

The fixed window began at `16:02:46Z` and ended at `16:05:46Z` (180 s). The
device disconnected from USB during the iOS boot, as in earlier runs; the user
forced it back to TWRP with hardware keys after the window, and pstore was then
pulled.

## Raw evidence

| File | SHA256 |
|---|---|
| `raw/pre-pmsg-ramoops-0` | `ade2f38b0262da9db0996b03bbc4f989235aa6f36ae27feb5c54a245ed893a1c` |
| `raw/pmsg-ramoops-0` | `a146572fe77038d4fd0c22a5e1c9b94fc66da4c4222b54a5b78bcb0981c554b9` |
| `decoded-bootlog.txt` | `37de17f53b7da03e49390ac262a9ddfd667d462df8acf2144a425547c075048e` |

The pre-flash pstore matches the v53 result, confirming a fresh window.
`raw/pmsg-ramoops-0` is 16,372 bytes. `tools/m30_bootlog.py inspect` decoded 87
records with 4 wrap/gap issues; the record stream starts mid-message.

## Result

v54 restored the successful IRT state that v53 lost:

```text
M30 IRT: patched (final state=3 off=0xa432d84 sym=0x1e1d3ad84 comp=0
  ls=0x4000 nlist_cnt=0 nlist_range=146 sc=42 si=26 fo=18612 vh=3330
  oh=1 pr=-5 fb=0x0 hb=15 xctest=1 xctchunk=0)
...
M30 IRT: patched (final state=3 ... hb=39 xctest=1 xctchunk=0)
```

- Durable `state=3` and `oh=1` from `hb=3` through `hb=39`; 75 full status
  replay lines containing `state=3 off=0xa432d84` and `xctest=1 xctchunk=0`.
- No `state=4` record in the captured ring (v53 had 30+).
- `xctest=1` and `xctchunk=0`: the v50 XCTEST path fired once; the v52 chunk
  rewrite did not fire in this window.
- The IRT symbol/offset resolution is consistent with v45–v52: `sym=0x1e1d3ad84`,
  `sc=42`, `si=26`, `fo=18612`, `oh=1`, `pr=-5`.

The captured ring does **not** contain the one-shot `early scan started`,
`early scan attempt`, `rearming NEED_DSC`, or `patched _internal_release_type
off ...` markers. Because the stream starts mid-message and has 4 gaps, those
records wrapped out. Therefore this boot cannot prove which path (early retry
or XCTEST fallback) started the successful worker; it only proves the worker
reached `state=3` and patched the in-memory page.

The SpringBoardUI `NSInternalInconsistencyException` is also absent from this
captured ring. That is **not** evidence that it is fixed, because the same
early records wrapped out. There is no `Early boot complete` and no lock-screen
evidence. No UI/lock-screen success is claimed.

## Interpretation and status

v54 is an improvement over v53 at the IRT-state level: the bounded retry change
did not regress the scan to terminal `state=4`, and the durable heartbeat again
shows the in-memory `_internal_release_type` patch (`state=3`, `oh=1`,
`off=0xa432d84`). It joins v52 as a physically successful IRT candidate, with
the distinction that v54 keeps the early DSC-header gate and adds retryability.

The decisive one-shot evidence was lost to the 16 KB pmsg ring wrap. A shorter
post-resume capture window would be needed to order the early-start/retry
markers relative to the SpringBoardUI assertion. No further flash is queued;
any additional physical test needs explicit user approval.

BOOT readback skipped; USERDATA/SYSTEM/RECOVERY untouched. No UI claim.
