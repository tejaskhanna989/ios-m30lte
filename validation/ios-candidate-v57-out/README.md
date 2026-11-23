# iOS candidate v57 — busy-page-safe 16K code-signing readback

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @
`60379849`. v55 source was `28a8a1ee`; v56 source `989eb983` was stopped before
any flash; v57 source is `60379849`.

## Why this candidate exists

v55 physically stalled immediately after `load_init_program`: the pstore decode
was complete and un-wrapped (154/154 records) and contained no IRT heartbeat,
no CS telemetry, no `Early boot complete` and no SpringBoard records. The
first code-signing validation of a 16K-hashed page was the last observable step.

Two lock-safety defects were identified in v55:

1. `kalloc_data(CS_16K_BLOCK_SIZE, Z_WAITOK)` ran while the VM object lock was
   still held. v56 (`0433`) changed this to `Z_NOWAIT` with fail-closed handling
   and a `object->pager == pager` recheck.
2. More importantly, the full 16K `vn_rdwr()` still included the busy faulting
   page. Even with `IO_NOCACHE`, `cluster_read()` creates a UPL;
   `vm_object_upl_request()` sleeps on `vmp_busy`/`vmp_cleaning`. The thread
   waiting on the UPL owns the busy page, so v56 would self-deadlock. Its CI
   run `45229034214` was cancelled and **v56 was never flashed**.

v57 (`0434`) fixes the second defect: it never includes the busy faulting page
(or any other busy/cleaning page) in vnode I/O. Only absent 4K slots are read,
one page at a time with the object lock dropped. The faulting page is hashed
from `kaddr`; other resident pages are hashed from their real physical bytes.
Pager identity and object life are rechecked after every lock drop/reacquire,
and `M30_CS_DIAG(5)` records the start of each read before I/O. Allocation
failure, short/failed reads, busy peer pages and pager changes all fail closed.
No signature, hash, AMFI, trust-cache or page-validation check is weakened.

The v54 retryable IRT scan, v45 Cryptex-first lookup, v18 baseline and 4K
config are preserved. No 0417, no OSX target, no branch or GitHub settings
changes, no disk write introduced.

## CI history

| Run | Result |
|---|---|
| `45206251994` | v54 GREEN; 0426–0431 applied |
| `45219943492` | v55 GREEN; 0432 applied; physically rejected |
| `45229034214` | v56 CANCELLED before completion; never flashed |
| `45230106038` | v57 GREEN; 0432 + 0433 + 0434 applied |

CI `45230106038` was GREEN for source `60379849`, built with
`XNU_TARGET=iphoneos`, `M30LTE`, `DEVELOPMENT`. The CI log explicitly applied
`0434-m30-cs-16k-no-busy-upl.patch`; `ios_define_present=True`,
`osx_define_present=False`, and the Cortex-A53 LSE scan reported 0.

## Hashes

| File | SHA256 |
|---|---|
| buildtree `osfmk/vm/vm_fault.c` | `a10ab98b0506e521090402674b5ce533f1edb6e901350b39ce8c36e42365aa77` |
| linked kernel | `3d3c58d6834a2af83d1480f6a74c6cc7047bdbee334f99eb6d3994b83844d827` |
| M30LTXNU payload | `ea47b84a1f0d353e5d3cfcdf8d992f42164c8269bd053bf0212eed00a024990d` |
| `combined.bin` | `25819d7cc0aa6639c037fe625c71f26290948a072b949100e6c9a842512f4f6e` |
| `shim-boot.img` (BOOT-flash candidate) | `0b85cc7666a45c761abf29002f42b5f24b395f9d7386112e5ade8748b2fcca31` |
| `ios-boot.img` (alternate cmdline) | `a803796692f0560f5532dd723c7e94e5903da62c7f93e6207918f493ee1d6595` |
| `shim_fixed.Image` | `2d7aea8036feac3b8b2dd64e08e788ae3e660300f00d9ce53686be423e1ce2ff` |
| `shim_fixed.elf` | `a3fd265382b2229e6b785a882d599e3f597ddc9a77874fe3a00f20bd422c51ea` |
| `m30lte-corrected.adt` | `2dc36c056e62a563bc5b2262c296d8731e1d8ad9e804d388054c156cec7bd577` |

## Layout

The v57 CS changes did not move the kernel entry relative to v55:

- LC_UNIXTHREAD PC / entry VA `0xfffffff007411488`;
- `_start_first_cpu` `0xfffffff0074130ec`;
- `__TEXT_EXEC __text` vmaddr `0xfffffff007248000`, size `0x008b4000`;
- kernel end `0xfffffff008454000`;
- ADT PA `0x82454000`, boot_args PA `0x82458000`;
- payload size 16,179,264 bytes (unchanged from v55).

The shim consumes entry/ADT/boot_args from the payload header, so the shim
Image/ELF remain byte-identical to v55/v54/v53/v31. Details in
`entry-layout-check.txt`.

## Validation

- `verify_m30_buildtree.py`: PASS, all critical patches reverse-apply.
- `verify_m30_kernel.py`: PASS (6 checks).
- `verify_platform_match.py`: 9/9 PASS.
- `validate_boot_images.py`: PASS.
- `verify_handoff_v57.py`: 20/20 PASS.
- Focused tests: all applicable PASS, including `test_m30_cs_16k_no_busy_upl.py`
  and `test_m30_cs_16k_nowait.py`. `test_m30_16k_pages.py` remains intentionally
  inapplicable without 0417. `validate-repo.py` reports only the pre-existing
  patch-number-gap warnings.
- CI Cortex-A53 compatibility check: PASS (0 ARMv8.1 LSE instructions).

No QEMU result is claimed as evidence: the generic `virt` board lacks the M30
GICv2/timer/board handoff and cannot validate this fix. Physical pstore is the
authoritative test.

## Status / physical step

Candidate packaged and fully validated offline. The existing authorization
permits autonomous physical testing of validated candidates, but identity and
Download Mode confirmation still apply immediately before the write. Positive
device identity must be confirmed in TWRP before entering Download Mode.

Only `shim-boot.img` may be flashed to BOOT with Heimdall. Never USERDATA,
SYSTEM, or RECOVERY; never Fastboot. After the BOOT-only write, resume, wait
~180 s, return to recovery, pull pstore/pmsg promptly, decode it, compare with
v45/v52/v54/v50/v55, and preserve the raw evidence. The decisive markers are
`M30 CS diag 5` before I/O, `csblk`/`csfail`/`csvok` in the IRT heartbeat,
progress past `load_init_program`, `Early boot complete`, and any later
SpringBoard/UI evidence. A merely loaded SpringBoard process is not visible UI.
No UI/lock-screen success is claimed from packaging or from a BOOT upload.
