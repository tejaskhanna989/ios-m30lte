# iOS candidate v46 — durable IRT heartbeat

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `3771d76b`.
No physical operations for v46 yet.

## What changed from v45

v45 physically reached deeper userspace: launchd printed `Early boot complete`,
SpringBoard was loaded, and later daemons appeared. The SpringBoardUI assertion
was absent from the captured final pstore window, but every `M30 IRT` line had
been overwritten, so `_internal_release_type` patching remained unconfirmed.

v46 keeps the Cryptex-first companion and all v45 lookup/mapping logic. It adds
a compact heartbeat after the existing 30 x 2 s full status replay:

- every 2 s for another 6 min;
- success: `M30 IRT: patched (final state=... off=... sym=... comp=... ls=... nlist_cnt=... nlist_range=... fb=... hb=...)`;
- failure: `M30 IRT final: state=... off=... err=... sym=... comp=... ls=... nlist_cnt=... nlist_range=... hits=... tries=... fb=... hb=...`.

This makes the final result, companion index, local-symbol count, symbol vmaddr,
and fallback state visible even after heavy daemon logging.

All file reads remain `UIO_READ`; the only write is to the already-faulted
in-memory page strictly after `cs_validate_page()`, gated on the target cache
vnode. No signature, hash, AMFI, trust-cache, or other security check is
weakened.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `9086e77ef607e3a722947373aa0028c15445ab4970942a9501cde06ed1d4ab55` |
| payload | `b5996a239fc04ef3807b220c44d044f5b060069b6b3fe6095f18be6b9eb409dd` |
| shim-boot.img | `831fb5141ef91e90a6b534779f897944bf883a224f4823b86f83cf47390cb826` |

The shim Image/ELF hashes remain byte-identical to v6/v30–v45, and the shim
region inside `shim-boot.img` matches the v31 reference byte-for-byte. Kernel
entry is unchanged at `0xfffffff007410488`.

## Validation

CI `45125633274` GREEN. Buildtree PASS, kernel PASS, platform 9/9, CPU 17/17,
ADT 22/22, packaging PASS, handoff 18/18, all applicable focused tests PASS
(`test_m30_16k_pages.py` intentionally inapplicable). Standalone syntax check
clean; patch dry-runs cleanly against pristine and the v45 buildtree.

## Next physical step

BOOT-only flash; capture pstore. Read the `M30 IRT: patched (final ...)` or
`M30 IRT final: ...` heartbeat, then inspect the next boot stage for evidence
that SpringBoard proceeds beyond loading. Do not equate a loaded SpringBoard
process with a visible UI.

No UI success claimed; BOOT readback skipped; USERDATA/SYSTEM/RECOVERY untouched.
