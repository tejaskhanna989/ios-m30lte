# iOS candidate v51 — chunk-path XCTest fix-up

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `8ee1e3c5`.

## Why this candidate exists

v50 restored the v48 IRT gate and physically reached `state=3`, `oh=1`, with a
durable heartbeat carrying `xctest=1`. The SpringBoardUI
`NSInternalInconsistencyException` still appeared before the IRT patch marker,
so the single class-name rewrite was too late or on the wrong page/process.

v51 keeps all v50 behaviour and adds the last missing post-validation path:

- `m30_xctest_probe_fixup_range(kaddr, page_offset, len)` rewrites the
  `XCTestConfiguration` literal only inside the range that was just validated.
- The full-page wrapper still passes `PAGE_SIZE`.
- `vm_page_validate_cs_mapped_chunk()` (the `cs_validate_range()` path from
  `vm_fourk_pager.c:1027`) now calls the range scanner with `chunk_size` and
  `m30_irt_retrigger_after_xctest()` after `validated` is true.
- Bytes outside the validated chunk are never written.

All file reads remain `UIO_READ`. No signature, hash, AMFI, trust-cache or
page-validation check is weakened. No disk write is introduced.

## CI history

| Run | Result |
|---|---|
| `45169239555` | v50 GREEN; 0426 + 0427 applied; physically tested |
| `45173700250` | v51 GREEN; 0426 + 0427 + 0428 applied; buildtree matches intended source |

## Hashes

| File | SHA256 |
|---|---|
| kernel | `d857197355520846d82ba9bd4bcaf175f0d1ddf42677cf2f91a21e206db6a522` |
| payload | `0b75f9e0ef25615dd0e1c10e5699b9baaabf9c76b5a0762b7e7028c061ae2b0d` |
| shim-boot.img | `7bcaa7359081edb851a07bcb304b4bdf9dc64cb8cb4ecac23cd4f0e6cbf342be` |

## Layout change (verified, not assumed)

0428 grew `__TEXT_EXEC __text` by exactly `0x1000`, so:

- entry VA moved `0xfffffff007410488` -> `0xfffffff007411488`;
- `_start_first_cpu` moved `0xfffffff0074120ec` -> `0xfffffff0074130ec`;
- `__start` still branches to `_start_first_cpu`;
- ADT PA moved `0x82450000` -> `0x82454000`;
- boot_args PA moved `0x82454000` -> `0x82458000`.

`shim/loader.c` derives ADT and boot_args from the payload header, so the shift
is handled dynamically. See `entry-layout-check.txt` for the objdump and section
evidence. Shim Image/ELF and the shim region inside `shim-boot.img` remain
byte-identical to the v31 reference.

## Validation

CI `45173700250` GREEN. Buildtree PASS, kernel PASS, platform 9/9, CPU 17/17,
ADT 22/22, packaging PASS, handoff 18/18, all applicable focused tests PASS
(`test_m30_16k_pages.py` intentionally inapplicable). Patch order
`0426 -> 0427 -> 0428` was preflighted with `git apply --check` and verified to
reproduce the intended `vm_fault.c` byte-for-byte.

## Next physical step

BOOT-only flash, resume, one ~180 s boot window, return to TWRP, pull pstore.
Check for `xctest=<count>` greater than v50's `1`, the XCTest/retrigger markers,
IRT `state=3`, and whether the SpringBoardUI assertion still appears before the
IRT patch marker. Do not equate a loaded SpringBoard process with visible UI.

No UI success claimed; BOOT readback skipped; USERDATA/SYSTEM/RECOVERY untouched.
