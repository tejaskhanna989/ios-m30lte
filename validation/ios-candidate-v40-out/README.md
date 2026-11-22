# iOS candidate v40 — dyld4 subcache symbol path

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `ca344a7`.
No physical operations for v40 yet.

## What changed from v39

v39 physically proved the NUL-length fix: the faulted vnode path is
`/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.31`, with
`plen=65`, `strlen=64`. That is a dyld4 subcache, so appending `.symbols`
to the subcache path opens `dyld_shared_cache_arm64.31.symbols`, which does
not exist on this device.

v40 strips a trailing `.<digits>` subcache index and tries, in order:

1. `<base>.symbols` (main cache companion — expected here),
2. `<subcache>.symbols`,
3. `<base>` (main cache itself).

The first candidate whose header has a non-zero `localSymbolsOffset` wins.
If the symbol's vmaddr is not covered by the selected symbol file's mapping
table, the worker falls back to the faulted cache vnode's own mapping table
so subcache-resident symbols still produce a file offset relative to the
vnode that actually faults. All reads remain `UIO_READ`; the in-memory write
still happens strictly after `cs_validate_page()`; no security check is
weakened.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `fc68ed6ae0cbbc70e76bd795782d27e40478ab507500e0f18ce2f8657699b95e` |
| payload | `5b065a6462bdc5f9d1ed99943e9becc50d30f4d8fa0528a695a5f8f82bd51e40` |
| shim-boot.img | `611625babb5e3dc88bf272e1deadcb1c158cb1c9e115c5be3c334e459ca80391` |

The v40 linker placed the kernel entry at `0xfffffff00740f488` (one page
later than v39). The shim reads `entry_va` from the regenerated payload
header, so the boot handoff mechanism is unchanged. Shim Image/ELF hashes
are byte-identical to v6/v30-v39, and the shim region inside `shim-boot.img`
matches the v31 reference byte-for-byte.

## Validation

CI `45052304788` GREEN. Buildtree PASS, kernel PASS, platform 9/9,
CPU 17/17, ADT 22/22, packaging PASS, handoff 18/18, all applicable focused
tests PASS (`test_m30_16k_pages.py` intentionally inapplicable). Standalone
syntax check clean.

## Next physical step

BOOT-only flash; capture pstore. Expect `diag 31` (`plen=65`, `strlen=64`),
`diag 32` with the stripped base path, `diag 30` with `cand=0` and a non-zero
`ls_off`, `diag 28` with a distinct `.symbols` vnode, then `diag 10/13/16`
and either `M30 IRT: found ...` / `M30 IRT: patched ...` or a precise new
failure diagnostic. Check whether SpringBoard proceeds past
`+[SpringBoardUI load]`.

No UI success claimed; BOOT readback skipped; USERDATA/SYSTEM/RECOVERY untouched.
