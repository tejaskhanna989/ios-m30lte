# iOS candidate v36 — .symbols companion file scan

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `ef168b7`.
No physical operations for v36 yet.

## What changed from v35

v35 physically confirmed the deferred kernel-thread scan works with no
recursive-lock panic, but the main dyld shared cache header has
`localSymbolsOffset == 0`: symbols are split into a `<cache>.symbols`
companion file. Patch `0426` now has the worker call `vn_getpath()` on the
main DSC vnode, append `.symbols`, open it with `vnode_open()` under
`vfs_context_kernel()`, re-read its DSC header and continue the symbol scan
there. All reads are `UIO_READ`; the in-memory page patch stays after
`cs_validate_page()`; no security check is weakened.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `c3914e69eb2d6a5bc2c11c00d2e202848487a1b88609abf496a390b6bd0caea5` |
| payload | `4fd22d4458015d3bdf3cbfe6df0022f01d04a69f3dea5d08eb3b8151586109d7` |
| shim-boot.img | `2d629c034d114ff88b3dab71d75bea80088fee5868e804c55ef0bffc81c0817f` |

Entry VA `0xfffffff00740e488`. Shim byte-identical to v6/v30-v35.

## Validation

CI `45040004275` GREEN (iphoneos, LSE=0). Buildtree PASS, kernel PASS,
platform 9/9, CPU 17/17, ADT 22/22, packaging PASS, handoff 18/18, all
applicable focused tests PASS (0417 inapplicable by design). Standalone C
syntax check of the fix-up block is clean.

## Next physical step

BOOT-only flash, one boot, force back to TWRP, capture pstore. Expected after
`diag 8`: `diag 28 opened symbols file`, `diag 30 symbols map_off ...`,
`diag 13 symbol name found`, `diag 16 symbol vmaddr`, `M30 IRT: found ...`.
Then a fault on the `_internal_release_type` page should log
`M30 IRT: patched ...` and SpringBoard should proceed past `+[SpringBoardUI load]`.

No UI success claimed; BOOT readback skipped; USERDATA/SYSTEM/RECOVERY untouched.
