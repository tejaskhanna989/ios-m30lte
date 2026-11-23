# iOS candidate v49 — post-validation fix-ups on the bitmap fast path

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `a1de1e3f`.

## Why this candidate exists

v48 physically proved the `_internal_release_type` patch:

```text
M30 IRT: patched _internal_release_type off 0xa432d84 (0 -> 3)
M30 IRT: patched (final state=3 ... sc=42 si=26 fo=19821 vh=3493 oh=1 pr=-5 ... hb=22)
```

but the SpringBoardUI assertion and `NSInternalInconsistencyException` still
appeared **before** the patch marker, and there is no `Early boot complete`.

Two narrow changes are made:

1. `vm_page_validate_cs_mapped()` can validate a page via the code-signing
   **bitmap fast path**, which skips `vm_page_validate_cs_mapped_slow()` where
   both post-validation fix-ups live. v49 runs `m30_xctest_probe_fixup()` and
   `m30_internal_release_fixup()` on the fast path too, with the page's object
   pager and `mo_offset`. Validation has already succeeded; the write remains
   in-memory only after validation.
2. The deferred IRT scan now starts on the **first dyld-pager fault** instead
   of waiting for the XCTEST retrigger, so the symbol patch can land before the
   SpringBoardUI probe. Wrong-magic vnodes still reset `NEED_DSC` for a later
   retry, and the retrigger still resets state for diagnostics.

All file reads remain `UIO_READ`. No signature, hash, AMFI, trust-cache or
page-validation check is weakened. The backing file is never written.

## CI history (important)

| Run | Result |
|---|---|
| `45156413249` | FAILED compile: `-U0` fast-path hunk landed at `vm_fault.c:9729` |
| `45159368112` | GREEN but 0426 was silently skipped by strict `git apply`; kernel had no IRT code, entry moved to `0xfffffff00740d488`. **Discarded, never packaged.** |
| `45162621882` | GREEN, 0426 applied, buildtree matches intended source, entry `0xfffffff007410488` |

## Hashes

| File | SHA256 |
|---|---|
| kernel | `f614daf731563f5ed34ed26e969e1a336e333b08fe2bc7ada4357ae7f87c0968` |
| payload | `aa7ad2f18c73b2719c873efad2ce8339d2ff509298d14c32eddb1321e140b6a3` |
| shim-boot.img | `81b4626da7c3fbc787ef824e8c7d73470e04f5fea5ee60a4ed3d605c9e812c79` |

Kernel entry remains `0xfffffff007410488`. Shim Image/ELF and the shim region
inside `shim-boot.img` remain byte-identical to the v31 reference.

## Validation

CI `45162621882` GREEN (17m3s). Buildtree PASS, kernel PASS, platform 9/9,
CPU 17/17, ADT 22/22, packaging PASS, handoff 18/18, all applicable focused
tests PASS (`test_m30_16k_pages.py` intentionally inapplicable). Patch
preflighted with `git apply --check` against the v48 CI base and verified to
reproduce `vm_fault.c` byte-for-byte.

## Next physical step

BOOT-only flash; capture pstore. Look for `M30 XCTEST: patched` markers, the
IRT patch marker and ordering relative to the SpringBoardUI assertion, and any
`Early boot complete` / SpringBoard progression. Do not equate a loaded
SpringBoard process with a visible UI.

No UI success claimed; BOOT readback skipped; USERDATA/SYSTEM/RECOVERY untouched.
