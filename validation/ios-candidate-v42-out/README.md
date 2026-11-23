# iOS candidate v42 — absolute DSC image path offsets

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `533fca1`.
No physical operations for v42 yet.

## What changed from v41

v41 physically proved that the image list is readable (`diag 36`:
`images off=0x270 cnt=2710`), but every image was rejected before its path was
read. `dyld_cache_image_info.pathFileOffset` is an absolute offset in the main
cache file; the v41 guard `po >= chunk` incorrectly treated it as an offset into
the 4 KiB scratch buffer, yielding `diag 38 libsystem_darwin image not found`.

v42 removes that guard and reads each path directly at its absolute
`pathFileOffset` with `vn_rdwr(UIO_READ)`. It adds one-shot `diag 47` (first
image path) and `diag 48` (libsystem-prefixed candidate) so the next pstore
proves the comparison data before the image-scoped nlist lookup runs.

The rest of the LiveContainer-style lookup is unchanged: find
`/usr/lib/system/libsystem_darwin.dylib` in the main DSC image list, read its
`dyld_cache_local_symbols_entry_64` from the companion, scan only that image's
nlist range, and resolve the vmaddr through a real cache file before patching.
The `.symbols` companion is used only for nlist/string data. All file reads are
`UIO_READ`; the only write is to the already-faulted in-memory page strictly
after `cs_validate_page()`. No signature, hash, AMFI, trust-cache, or other
security check is weakened.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `35178aa6f83d22060e4fa5d0d7edb3170572c33ca97d52a6830c9160d3034de4` |
| payload | `5ac8105713b4bb5556b76bbdb7c847cf8552f9b4ddc2cb856f4af1fc41856e66` |
| shim-boot.img | `f451f7e8f7786c837d2544bce5c7de717fe43c54e7f57e1892028880586b4709` |

The shim Image/ELF hashes remain byte-identical to v6/v30–v41, and the shim
region inside `shim-boot.img` matches the v31 reference byte-for-byte.

## Validation

CI `45102718208` GREEN. Buildtree PASS, kernel PASS, platform 9/9, CPU 17/17,
ADT 22/22, packaging PASS, handoff 18/18, all applicable focused tests PASS
(`test_m30_16k_pages.py` intentionally inapplicable). Standalone syntax check
clean; patch dry-runs cleanly against pristine and the v41 buildtree.

## Next physical step

BOOT-only flash; capture pstore. Expect `diag 47/48`, `diag 39`, `diag 42`,
`diag 13`, `diag 33`, then either `M30 IRT: patched ...` or a new precise
failure diagnostic. Check whether SpringBoard proceeds past
`+[SpringBoardUI load]`.

No UI success claimed; BOOT readback skipped; USERDATA/SYSTEM/RECOVERY untouched.
