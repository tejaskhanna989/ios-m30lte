# iOS candidate v41 — image-scoped DSC symbol lookup

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `2977581`.
No physical operations for v41 yet.

## What changed from v40

v40 physically proved that stripping the dyld4 subcache suffix finds the real
`.symbols` companion: `diag 30` reported `ls_off=0x4000` and `diag 28` showed a
distinct vnode. However, a global first-match scan of the companion string pool
produced `strx=318698973`, which no nlist in the target dylib used.

v41 follows LiveContainer's `litehook_find_dsc_symbol()` algorithm:

1. Read the image list from the main cache and find
   `/usr/lib/system/libsystem_darwin.dylib`.
2. Read `local_symbols_info` and the image's
   `dyld_cache_local_symbols_entry_64` from the companion.
3. Scan only that image's nlist range, reading each nlist's own string.
4. Map the resulting vmaddr through a REAL cache file: the faulted vnode, the
   base cache, then numbered subcaches. The `.symbols` companion is used only
   for nlist/string data; its file offsets are never used for patching.
5. Retain the target cache vnode and require it in the fault-path patch gate.

All file reads remain `UIO_READ`. The only write is to the already-faulted
in-memory page, strictly after `cs_validate_page()`. No signature, hash, AMFI,
trust-cache, or other security check is weakened.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `2e46c41c4d727c11efdfc7aab611bef39cf2efc4f9811f185432e173c0e2037a` |
| payload | `f90feb5b7210c7a080efe882c9400b64081ae8d8eb2c2153c6f8f08d85af88d2` |
| shim-boot.img | `274e39b49d883abd392a1e626a14daab4e146e1b1d3f36e15344ac96539b0ca5` |

The shim Image/ELF hashes are byte-identical to v6/v30-v40, and the shim region
inside `shim-boot.img` matches the v31 reference byte-for-byte.

## Validation

CI `45060087612` GREEN. Buildtree PASS, kernel PASS, platform 9/9, CPU 17/17,
ADT 22/22, packaging PASS, handoff 18/18, all applicable focused tests PASS
(`test_m30_16k_pages.py` intentionally inapplicable). Standalone syntax check
clean; patch dry-runs cleanly against pristine and the v40 buildtree.

## Next physical step

BOOT-only flash; capture pstore. Expect `diag 39` (image index), `diag 42`
(image nlist start/count), `diag 13` (symbol vmaddr), `diag 33` (real target
cache vnode and file offset), then either `M30 IRT: patched ...` or a new
precise failure diagnostic. Check whether SpringBoard proceeds past
`+[SpringBoardUI load]`.

No UI success claimed; BOOT readback skipped; USERDATA/SYSTEM/RECOVERY untouched.
