# iOS candidate v43 — DSC mapping evidence and Cryptex cache fallback

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `8c99e27`.
No physical operations for v43 yet.

## What changed from v42

v42 physically proved the image-scoped nlist lookup: `diag 42` found image
nlist `6047093/146`, `diag 43` read `strx=318698902`, and `diag 13` resolved
`sym_vmaddr=0x1e1d3ad84`. However, `diag 18` showed that no tried real cache
mapping contained that vmaddr, so the in-memory page could not be patched.

v43 adds observable mapping evidence and a broader real-cache search:

- `diag 50` prints the base cache mapping table (count, first and last range).
- `diag 49` prints the target image's unslid address and `pathFileOffset`.
- Periodic `M30 IRT status:` now includes `sym`, `img`, mapping-hit count, and
  the base mapping range, so the decisive values survive the 16 KB pmsg wrap.
- Real-cache lookup also tries `/private/preboot/Cryptexes/OS/System/Library/
  Caches/com.apple.dyld` and its numbered subcaches.

The `.symbols` companion is still used only for nlist/string data. All file
reads are `UIO_READ`; the only write is to the already-faulted in-memory page
strictly after `cs_validate_page()`, gated on the target cache vnode. No
signature, hash, AMFI, trust-cache, or other security check is weakened.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `1a2290a37abe15ad40fdb6738e48ca6f35831650c522dd832f1ba3805f72ef6f` |
| payload | `b3348e9f1afd21f1754e6a84e5c99bcbf158d60fc8c48238e033828b6f8f189d` |
| shim-boot.img | `f605a5d46ca4e9a7e2421c53ccaf1a8254c043c5b9ae226a4ebc1f76d8283b09` |

The shim Image/ELF hashes remain byte-identical to v6/v30–v42, and the shim
region inside `shim-boot.img` matches the v31 reference byte-for-byte.

## Validation

CI `45115267398` GREEN. Buildtree PASS, kernel PASS, platform 9/9, CPU 17/17,
ADT 22/22, packaging PASS, handoff 18/18, all applicable focused tests PASS
(`test_m30_16k_pages.py` intentionally inapplicable). Standalone syntax check
clean; patch dry-runs cleanly against pristine and the v42 buildtree.

## Next physical step

BOOT-only flash; capture pstore. Read `diag 49/50` and the periodic status
fields (`sym`, `img`, `hits`, `basecnt`, `base0`). Expect either
`M30 IRT: patched ...` or a new precise failure diagnostic. Check whether
SpringBoard proceeds past `+[SpringBoardUI load]`.

No UI success claimed; BOOT readback skipped; USERDATA/SYSTEM/RECOVERY untouched.
