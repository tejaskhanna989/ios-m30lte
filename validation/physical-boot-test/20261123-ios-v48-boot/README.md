# v48 physical boot — `_internal_release_type` patch confirmed

Device: Samsung Galaxy M30 SM-M305F (`m30lte`), serial `320081735bb166a3`,
TWRP recovery. Package: `validation/ios-candidate-v48-out/shim-boot.img`
SHA256 `4b56a629e7c1359d98008208bec4e865152e5aff995e896e50dc36c93c07579c`.

BOOT-only flash succeeded. No BOOT readback. USERDATA, SYSTEM, and RECOVERY
were not rewritten. The device was returned to TWRP and pstore was pulled.

## Raw evidence

- `raw/pre-pmsg-ramoops-0`: pstore present before the v48 flash, SHA256
  `bdb1be4e0fa3655a113845447716c9a12a9f8749893872400e61a86078f2a493`.
- `raw/pmsg-ramoops-0`: v48 pstore, 16,372 B, SHA256
  `ea99ef076996bd636f19516f7a34d815119bbcfd913d3a952e1badffd6679b03`.
- `decoded-bootlog.txt`: decoded with `tools/m30_bootlog.py inspect`
  (116 records, 3 gap issues).

## Decisive result

The in-memory patch fired:

```text
M30 IRT: patched _internal_release_type off 0xa432d84 (0 -> 3)
```

The durable success heartbeat survived the wrapped ring:

```text
M30 IRT: patched (final state=3 off=0xa432d84 sym=0x1e1d3ad84 comp=0 ls=0x4000 nlist_cnt=8705811 nlist_range=146 sc=42 si=26 fo=19821 vh=3493 oh=1 pr=-5 fb=0x0 hb=0)
...
M30 IRT: patched (final state=3 off=0xa432d84 sym=0x1e1d3ad84 comp=0 ls=0x4000 nlist_cnt=8705811 nlist_range=146 sc=42 si=26 fo=19821 vh=3493 oh=1 pr=-5 fb=0x0 hb=22)
```

Periodic status lines confirm the transition:

```text
M30 IRT status: state=2 off=0xa432d84 ... fo=19324 vh=3350 oh=0 pr=-5 mo=0x24cd000 ...
M30 IRT status: state=3 off=0xa432d84 ... fo=19821 vh=3493 oh=1 pr=-5 mo=0xa432000 ...
```

Therefore:

- The authoritative subcache list still resolves the symbol (`sc=42`, `si=26`,
  `hits=1`) to file offset `0xa432d84`.
- The direct resident-page shortcut was **not** used: `pr=-5` means the page
  found through the vnode object was not code-signing validated at that moment.
  v48 correctly refused to write it.
- The strict `(mount, vnode id)` alias match plus the fault-path fallback did
  fire: `oh=1`, `mo=0xa432000`, and final state `3` (`DONE`).
- The write was in-memory only, after validation; no file write occurred.

## User-space status

The captured window still contains the SpringBoardUI assertion and exception:

```text
This process should not be linking or loading SpringBoardUI.framework
*** Terminating app due to uncaught exception 'NSInternalInconsistencyException' ...
```

That assertion appears **before** the IRT patch marker. There is no
`Early boot complete` and no evidence of a usable UI or lock screen. This boot
therefore confirms the IRT milestone only; it does not claim user-interface
success.

A likely next correction is to apply the already-validated post-validation
fix-ups on the code-signing bitmap fast path too. The current fix-ups run in
`vm_page_validate_cs_mapped_slow()`, so pages already covered by a validation
bitmap can skip both the class-name patch and the IRT fault hook. Starting the
IRT scan earlier may also place the patch before the SpringBoardUI probe.
