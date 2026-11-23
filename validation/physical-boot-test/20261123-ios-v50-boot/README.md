# v50 physical boot — IRT patch restored; XCTest patch still insufficient

Device: Samsung Galaxy M30 SM-M305F (`m30lte`), serial `320081735bb166a3`,
TWRP recovery. Package: `validation/ios-candidate-v50-out/shim-boot.img`
SHA256 `859b5d08dab9dd2f7a9aff80eb9c5f2c77ea6677969480f8ece332b7de74b07a`.

BOOT-only flash succeeded. No BOOT readback. USERDATA, SYSTEM, and RECOVERY
were not rewritten. The device was returned to TWRP and pstore was pulled.

## Raw evidence

- `raw/pre-pmsg-ramoops-0`: pstore before v50, SHA256
  `fd517375e9dbab5561cb9511808a33b96f6b35b3d32eaf79a348fc28a0370e0e`
  (same as the v49 result, confirming a fresh window).
- `raw/pmsg-ramoops-0`: v50 pstore, 16,372 B, SHA256
  `744b504a8552c1af9bfe5eb789f2ae85ee8c3e7216e9c3a50d0512eb0728ba2e`.
- `decoded-bootlog.txt`: decoded with `tools/m30_bootlog.py inspect`
  (97 records, 3 gap issues from ring wrap).

## Result

The v48 gate is restored and the IRT patch fired again:

```text
M30 IRT: patched _internal_release_type off 0xa432d84 (0 -> 3)
M30 IRT status: state=3 off=0xa432d84 ... hits=1 tries=29 sc=42 si=26
  fo=15017 vh=2483 oh=1 pr=-5 ...
M30 IRT: patched (final state=3 ... hb=24 xctest=1)
```

The new durable `xctest=` field proves the class-name fix-up ran **once**
(`xctest=1`) and the state machine stayed healthy through `hb=24`.

However, the SpringBoardUI assertion is still present, and it appears BEFORE
the IRT patch marker:

```text
[021] STR *** Terminating app due to uncaught exception
      'NSInternalInconsistencyException', reason: 'This process should not be
      linking or loading SpringBoardUI.framework ...
[039] STR aThis process should not be linking or loading SpringBoardUI.framework
[041] M30 IRT: patched _internal_release_type off 0xa432d84 (0 -> 3)
```

No `M30 XCTEST: patched` or `M30 IRT: retrigger` marker survives in the
captured ring, so the one patch cannot be placed relative to the assertion.
Because the assertion still fired, the single XCTest rewrite was either too
late or on the wrong process/page.

No `Early boot complete`. No UI or lock-screen evidence. No UI success claimed.

## Interpretation and next step

- Restoring the retrigger gate fixed the v49 regression; v50 is at least as
  good as v48 on the IRT milestone (`state=3`, `oh=1`, durable heartbeat).
- Retargeting the literal on the two `vm_page_validate_cs_mapped()` paths is
  not enough. The remaining unpatched code-signing validation path is
  `vm_page_validate_cs_mapped_chunk()` (called from `vm_fourk_pager.c:1027`),
  which calls `cs_validate_range()` directly. That is the likely path for the
  SpringBoardUI page.
- v51 should add the same post-validation `m30_xctest_probe_fixup()` and
  `m30_internal_release_fixup()` calls there, guarded by `validated`, with no
  0417 and no security check weakened.
