# iOS candidate v54 — bounded retry for the early IRT scan

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `25b905f8`
(patch source commit `d2a4854d`).

## Why this candidate exists

v53 started the read-only IRT scan on the first genuine dyld shared-cache header
(`dyld_v`, file offset 0), but the physical boot ended with durable `state=4`,
`comp=0`, `ls=0x4000`, `img=0`, `sym=0`, `hits=0`, `tries=0`, `nlist_cnt=0`, and
`err=0`. The worker selected the Cryptex `.symbols` companion but failed before
resolving an image or symbol. The exact failing branch is still unproven.

v54 keeps that early DSC-header gate, but makes early failures retryable:

- A worker started from a genuine DSC-header fault records failures through
  `m30_irt_mark_failure()`. For up to `M30_IRT_MAX_EARLY_ATTEMPTS=4` attempts it
  rewinds to `M30_IRT_STATE_NEED_DSC`, clears the one-shot diag bits, and lets a
  later DSC-header fault start a fresh scan.
- Failed early attempts with a retry armed skip the long heartbeat replay, so
  they cannot overwrite the next attempt's pstore diagnostics.
- Attempt numbers (`attempt=N`) and early-scan markers are printed for evidence.
- After the budget is exhausted, the failure is terminal but leaves the v50
  XCTEST fallback able to restart. A worker started only by XCTEST remains
  terminal on failure (v50 behaviour preserved).
- Wrong-magic vnodes seen by an early worker take the same retryable path.

All file reads remain `UIO_READ`. The only write is the post-validation,
in-memory uint32 patch at `_internal_release_type`. No signature, hash, AMFI,
trust-cache, page-validation or other security check is weakened. No disk write
is introduced. No 0417; v18 baseline and 4K config unchanged.

## CI history

| Run | Result |
|---|---|
| `45179499798` | v52 GREEN; IRT restored, assertion still early |
| `45185667251` | v53 GREEN; physically rejected (`state=4`, no patch) |
| `45206251994` | v54 GREEN; 0426 + 0427 + 0428 + 0429 + 0430 + 0431 applied |

CI `45206251994` completed for source commit `25b905f8`. The buildtree
`osfmk/vm/vm_fault.c` matches `/tmp/m30_v54/modified.c` byte-for-byte.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `4327c4c9fda0f3c6d50c5d65beaab74ab42af985e7569f4a5b93ffac3d3610e5` |
| payload | `a69480ebee4a7b90108f4b63c96e33a8f9c3168e8bd7ae738ea210947c743543` |
| shim-boot.img | `1da365a3b352575a366d2d8e898e0a8585afc56fd917ca95c5e122af0aeb4d5c` |
| ios-boot.img | `0f5af834c16bcac89c28da139340f28c10987e485de7541924b798c95bb3ac32` |

## Layout

v54's retry bookkeeping moved the linked kernel entry by one page:

- entry VA `0xfffffff007411488` (v53 `0xfffffff007410488`);
- `_start_first_cpu` `0xfffffff0074130ec`;
- `__TEXT_EXEC __text` vmaddr `0xfffffff007248000`, size `0x008b4000`;
- ADT PA `0x82454000`, boot_args PA `0x82458000` (derived from payload header).

The shim consumes the payload header entry/ADT/boot_args values, so the shim
Image/ELF and the shim region inside `shim-boot.img` remain byte-identical to
the v31 reference. Details in `entry-layout-check.txt`.

## Validation

CI `45206251994` GREEN. Patch order `0426 -> 0427 -> 0428 -> 0429 -> 0430 ->
0431` was preflighted with `git apply --check` against the exact v49 CI base and
verified to reproduce the intended v54 source byte-for-byte. Validators PASS:
buildtree, kernel, platform 9/9, packaging, handoff 18/18, and all applicable
focused tests (`test_m30_16k_pages.py` intentionally inapplicable).
`validate-repo.py` reports only its pre-existing patch-number-gap warnings.

## Status / next physical step

Candidate packaged and validated locally. NOT physically tested. Device is in
TWRP; no flash queued. A BOOT-only flash requires explicit user approval.
If approved: flash `shim-boot.img` to BOOT, resume, wait ~180 s, return to TWRP,
pull pstore, and check for numbered early-start markers, retry messages, the
IRT patch marker, `state=3`, and whether the SpringBoardUI assertion appears
before or after the patch. Do not equate a loaded SpringBoard process with
visible UI.

No UI/lock-screen success claimed. BOOT readback skipped; USERDATA/SYSTEM/RECOVERY
untouched.
