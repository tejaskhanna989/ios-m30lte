# iOS candidate v45 — Cryptex-first DSC companion

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `ea8202c`.
No physical operations for v45 yet.

## What changed from v44

v44 physically showed that the `/System` `.symbols` companion maps only 16 KB
(`symmap=0x22ade8000/0x4000@0x0`) at a virtual base unrelated to the live cache
mapping (`base0=0x1ecc80000/0x62ac000@0x0`). Its nlist value could not be
translated, and the SpringBoardUI assertion persisted.

v45 makes the companion and the image list describe the same cache generation:

- Companion selection now tries the Cryptex `.symbols` file and Cryptex main
  cache first, then the previous `/System` candidates.
- The selected companion's base path drives the image-list reopen, the subcache
  search, the mapping-fallback target path, and `diag 18`.
- Periodic `M30 IRT status:` now reports `comp=<candidate>` and `ls=0x...` so
  the chosen companion is visible even after the 16 KB pmsg ring wraps.

All reads remain `UIO_READ`; the only write is to the already-faulted in-memory
page strictly after `cs_validate_page()`, gated on the target cache vnode. No
signature, hash, AMFI, trust-cache, or other security check is weakened.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `2c641272b7ad70435987c28eff6ff5cf2326c5bf35b8ef1d7568de55e26c777d` |
| payload | `617917ee01b2b9df7f1112b63080dedf1d0031c4094e93200c3c1298c474bd75` |
| shim-boot.img | `382db454eb9b0c74ca9957aea8b841f988d1e589406eb0e1a3b3b3210e37c689` |

The shim Image/ELF hashes remain byte-identical to v6/v30–v44, and the shim
region inside `shim-boot.img` matches the v31 reference byte-for-byte. Kernel
entry is `0xfffffff007410488`, matching v44; handoff is 18/18 PASS.

## Validation

CI `45121370706` GREEN. Buildtree PASS, kernel PASS, platform 9/9, CPU 17/17,
ADT 22/22, packaging PASS, handoff 18/18, all applicable focused tests PASS
(`test_m30_16k_pages.py` intentionally inapplicable). Standalone syntax check
clean; patch dry-runs cleanly against pristine and the v44 buildtree.

## Next physical step

BOOT-only flash; capture pstore. Read `comp=`, `ls=`, `symmap=`, and `fb=` from
the status replay, plus `diag 30/28/36/49/13/33`. Expect either
`M30 IRT: patched ...` or a new precise failure diagnostic. Check whether
SpringBoard proceeds past `+[SpringBoardUI load]`.

No UI success claimed; BOOT readback skipped; USERDATA/SYSTEM/RECOVERY untouched.
