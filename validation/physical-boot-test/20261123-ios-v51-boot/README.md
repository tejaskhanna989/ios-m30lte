# v51 physical boot — chunk-path hook regressed the IRT patch

Device: Samsung Galaxy M30 SM-M305F (`m30lte`), serial `320081735bb166a3`,
TWRP recovery. Package: `validation/ios-candidate-v51-out/shim-boot.img`
SHA256 `7bcaa7359081edb851a07bcb304b4bdf9dc64cb8cb4ecac23cd4f0e6cbf342be`.

BOOT-only flash and resume succeeded. No BOOT readback. USERDATA, SYSTEM, and
RECOVERY were not rewritten. The device was returned to TWRP and pstore pulled.

## Raw evidence

- `raw/pre-pmsg-ramoops-0`: pstore before v51, SHA256
  `744b504a8552c1af9bfe5eb789f2ae85ee8c3e7216e9c3a50d0512eb0728ba2e`
  (same as the v50 result, confirming a fresh window).
- `raw/pmsg-ramoops-0`: v51 pstore, 16,372 B, SHA256
  `ecf0c2ed5289be600e956a014ee4bd1b01fd8aec2391124b57b426a649efdebd`.
- `decoded-bootlog.txt`: decoded with `tools/m30_bootlog.py inspect`
  (101 records, 1 wrap issue).

## Result

v51 is a regression against v50:

```text
M30 IRT status: state=2 off=0xa432d84 ... hits=1 tries=29 sc=42 si=26
  fo=15460 vh=2804 oh=0 pr=-5 ...
M30 IRT final: state=2 off=0xa432d84 ... hits=1 tries=29 sc=42 si=26
  fo=15649 vh=2826 oh=0 pr=-5 ... hb=11 xctest=1
```

There is **no** `M30 IRT: patched _internal_release_type`, no
`M30 IRT: patched (final state=3 ...)`, no `M30 XCTEST: patched`, and no
`M30 IRT: retrigger` marker in the captured ring. `xctest=1` matches v50's
count, so the extra chunk-path rewrite cannot be shown to have fired a second
time. The durable heartbeat is `M30 IRT final: state=2` rather than v50's
`M30 IRT: patched (final state=3 ...)`.

The SpringBoardUI `NSInternalInconsistencyException` and the literal reason
string are still present. No `Early boot complete`. No UI or lock-screen
evidence. No UI success claimed.

## Interpretation

Observation: the IRT worker reached the companion symbols file (`hits=1`,
`tries=29`, `sc=42`, `si=26`) but never reached the v50 patch state (`oh=0`,
`mo` never settled at `0xa432000`). This is closer to an early/incorrect gate
than to a complete scan.

Working hypothesis (not proven by this capture): adding
`m30_irt_retrigger_after_xctest()` to the 4K chunk path can open the DSC scan
gate on a different, earlier validated page than the v48/v50-proven slow or
bitmap-fast path. The worker then starts with pager/vnode state that is not yet
ready for the header scan.

v50 remains the last physically successful IRT candidate (`state=3`, `oh=1`,
durable heartbeat through `hb=24`). v51 is rejected as a candidate for flashing.
