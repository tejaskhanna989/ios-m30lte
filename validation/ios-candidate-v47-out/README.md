# iOS candidate v47 — authoritative dyld4 subcache names

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `3a98f3a6`.

## Why this candidate exists

v46 physically proved that `_internal_release_type` was **not** patched:

```text
M30 IRT final: state=4 off=0x0 err=0 sym=0x1e1d3ad84 comp=0 ls=0x4000 nlist_cnt=8705811 nlist_range=146 hits=0 tries=138 fb=0x0 hb=55
```

The Cryptex `.symbols` companion and image-scoped local-symbol lookup worked;
the symbol vmaddr was found. The failure was in real-cache mapping: only
numeric `.0`-`.511` subcache names were searched, while dyld4 records exact
`fileSuffix` values such as `.03.development` and `.25.data` in the main cache
header's `subCacheArrayOffset`/`subCacheArrayCount` table.

v47 keeps all v46 companion, symbol, mapping-fallback, and heartbeat logic and
adds one narrow correction: before the numeric fallback, read the main cache
header, enumerate each `dyld_subcache_entry.fileSuffix`, reject unsafe suffixes
(non-leading `.` or embedded `/`), and try the exact `<basepath><suffix>` file.

Status and heartbeat lines now carry `sc=<subcache count>` and
`si=<matched index>` so the next physical result shows whether the authoritative
subcache list was found and used.

All file reads remain `UIO_READ`; the only write remains the in-memory page
patch after `cs_validate_page()`, gated on the target vnode. No signature, hash,
AMFI, trust-cache, or page-validation check is weakened.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `c2862edd5fba0993ede34876ee7776561fcb982c35a1a34fad9a5133cdda7d27` |
| payload | `26f769b6bccee46df8b04d5122919cc19aa7441ac98b216fe1051f0cad13fa93` |
| shim-boot.img | `23e131d59da50441967018d523b6b1888db1168f6eaaa339847c2108cbd7374c` |

Kernel entry remains `0xfffffff007410488`. Shim Image/ELF and the shim region
inside `shim-boot.img` remain byte-identical to the v31 reference.

## Validation

CI `45135148861` GREEN. Buildtree PASS, kernel PASS, platform 9/9, CPU 17/17,
ADT 22/22, packaging PASS, handoff 18/18, all applicable focused tests PASS
(`test_m30_16k_pages.py` intentionally inapplicable). Standalone syntax check
and patch dry-runs against pristine and the v46 buildtree PASS.

## Next physical step

BOOT-only flash; capture pstore. Read the updated heartbeat for either
`M30 IRT: patched (final ... sc=... si=...)` or `M30 IRT final: ... sc=... si=...`,
then inspect the next boot stage. Do not equate a loaded SpringBoard process
with a visible UI.

No UI success claimed; BOOT readback skipped; USERDATA/SYSTEM/RECOVERY untouched.
