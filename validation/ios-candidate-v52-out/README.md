# iOS candidate v52 — chunk rewrite with v50 gate timing

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `c4bbb74d`.

## Why this candidate exists

v50 was the last physically successful IRT candidate: `state=3`, `oh=1`,
durable heartbeat with `xctest=1`. The SpringBoardUI
`NSInternalInconsistencyException` still appeared before the IRT patch marker.

v51 added the 4K chunk-path rewrite but also called
`m30_irt_retrigger_after_xctest()` from that path. Physically it regressed to
`state=2`, `oh=0`, with no IRT patch marker. The working hypothesis is that the
chunk path opened the DSC scan gate too early.

v52 keeps the useful part of v51 and removes the suspected cause:

- Keep `m30_xctest_probe_fixup_range(kaddr, page_offset, len)` on
  `vm_page_validate_cs_mapped_chunk()` (the `cs_validate_range()` path). It
  rewrites the `XCTestConfiguration` literal only inside the just-validated
  chunk (`chunk_size`), using the exact `object->paging_offset + offset +
  offset_in_page` file offset.
- Remove `m30_irt_retrigger_after_xctest()` from the chunk path. Only the
  v48/v50-proven slow path and bitmap-fast path may open the DSC scan gate.
- Add `m30_xctest_chunk_count` and `xctchunk=<count>` to both durable heartbeat
  forms. A later pstore capture can therefore prove whether the extra chunk
  rewrite fired, independently of the v50-proven `xctest=<count>`.

All file reads remain `UIO_READ`. No signature, hash, AMFI, trust-cache,
page-validation or code-signing check is weakened. No disk write is introduced.

## CI history

| Run | Result |
|---|---|
| `45169239555` | v50 GREEN; 0426 + 0427 applied; physically tested (`state=3`) |
| `45173700250` | v51 GREEN; 0426 + 0427 + 0428; physically rejected (`state=2`) |
| `45179499798` | v52 GREEN; 0426 + 0427 + 0428 + 0429 applied |

CI `45179499798` completed in 14m22s for source commit `c4bbb74d`. The buildtree
`osfmk/vm/vm_fault.c` matches `/tmp/m30_v52/modified.c` byte-for-byte.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `6805139a62ccfc6992e421e0e7a8fad5b1a91f94c899fe12bcb368b54a10ea92` |
| payload | `58584cfeb606f15e218b82005d50ca342b40984fb70424d15b1f06a22f3c8d4d` |
| shim-boot.img | `d2e46bc18c161e9cd4c2c04f0c6eec96dc4166c479298f59285ac46bd2695cda` |
| ios-boot.img | `ae5bc3aa85b6627c9d3b1131e2ad5c854eb734af001c3ce1c585b5b60c16a8cb` |

## Layout (verified, not assumed)

Removing the chunk-path retrigger more than offsets the new counter/format
changes. v52 returns to the v50 layout:

- LC_UNIXTHREAD PC / entry VA: `0xfffffff007410488` (same as v50, not v51's
  `0xfffffff007411488`).
- `_start_first_cpu`: `0xfffffff0074120ec`; `__start` still branches to it.
- `__TEXT_EXEC __text`: vmaddr `0xfffffff007248000`, size `0x008ae9d8` — exactly
  the v50 values.
- ADT PA `0x82450000`; boot_args PA `0x82454000`.

`shim/loader.c` derives ADT and boot_args from the payload header, so no
hardcoded address change is needed. See `entry-layout-check.txt`. The shim
Image/ELF and the shim region inside `shim-boot.img` remain byte-identical to
the v31 reference.

## Validation

CI `45179499798` GREEN. Patch order `0426 -> 0427 -> 0428 -> 0429` was
preflighted with `git apply --check` against the exact v49 CI base and verified
to reproduce the intended v52 source byte-for-byte. Validators all PASS:
buildtree PASS, kernel PASS, platform 9/9, CPU 17/17, ADT 22/22, packaging PASS,
handoff 18/18, and all applicable focused tests (`test_m30_16k_pages.py`
intentionally inapplicable).

## Next physical step (requires explicit approval)

BOOT-only flash of `shim-boot.img`, resume, one ~180 s boot window, return to
TWRP, pull pstore. Check for:

- IRT `state=3`, `oh=1`, and the durable patched heartbeat;
- `xctest=<count>` and the new `xctchunk=<count>`;
- whether the SpringBoardUI assertion still appears before the IRT patch marker;
- any `Early boot complete` line.

Do not equate a loaded SpringBoard process with visible UI. No UI success is
claimed. BOOT readback is skipped; USERDATA/SYSTEM/RECOVERY are untouched.
