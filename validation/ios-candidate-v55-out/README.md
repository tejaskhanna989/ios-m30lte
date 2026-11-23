# iOS candidate v55 — full 16K code-signing block readback on first fault

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `28a8a1ee`
(patch source commit `28a8a1ee`; v54 source remained `25b905f8`).

## Why this candidate exists

v45 pstore contains the decisive line:

```text
CODE SIGNING: cs_invalid_page(0x1d5839000): p=26[SpringBoard] final status 0x22000000, allowing (remove VALID) page
```

`0x22000000` clears `CS_VALID`. willowios showed the exact downstream chain:
losing that flag drops the `com.apple.springboard-ui.client` entitlement and
triggers the `+[SpringBoardUI load]` `NSInternalInconsistencyException` seen in
v52 before the IRT patch marker. v30 proved that rewriting the literal string
alone does not remove the assertion.

In the v54 buildtree, `vm_page_validate_cs_mapped_slow()` only assembles a full
16K validation block when all four resident 4K pages are already present. The
first fault of a 16K-hashed page has one resident page, so the code validates
only one page, leaves `validated == 0`, and `vm_fault_cs_check_violation()`
calls `cs_invalid_page()`.

v55 fixes the cause rather than the symptom. When the full block is not
resident, it reads the exact 16K bytes from the code-signed vnode with
`vn_rdwr(UIO_READ, ..., IO_NOCACHE, ...)`, temporarily dropping the VM object
lock as the existing kernel comment permits. After re-locking and re-looking-up
the pages, it overlays the bytes actually mapped from the resident pages (the
faulting page from `kaddr`) before calling `cs_validate_page()` over the full
16K block. Tampered resident bytes therefore fail closed. Short/failed reads,
a terminating object, or a changed pager also fail closed. No disk write is
introduced.

All signature, hash, AMFI, trust-cache and page-validation checks remain
enabled. The v54 bounded-retry IRT scan, v45 Cryptex-first lookup, v18 baseline
and 4K config are preserved. No OSX target, no 0417, no branch or GitHub
settings changes.

## CI history

| Run | Result |
|---|---|
| `45179499798` | v52 GREEN; IRT restored, assertion still early |
| `45185667251` | v53 GREEN; physically rejected (`state=4`, no patch) |
| `45206251994` | v54 GREEN; 0426 + 0427 + 0428 + 0429 + 0430 + 0431 applied |
| `45219943492` | v55 GREEN; 0426 + 0427 + 0428 + 0429 + 0430 + 0431 + 0432 applied |

CI `45219943492` was GREEN for source `28a8a1ee`, built with
`XNU_TARGET=iphoneos`, `M30LTE`, `DEVELOPMENT`. The CI log explicitly shows
`Applying patch: .../0432-m30-cs-16k-block-readback.patch`. The buildtree
`osfmk/vm/vm_fault.c` matches the locally reproduced v55 source byte-for-byte.

## Hashes

| File | SHA256 |
|---|---|
| buildtree `osfmk/vm/vm_fault.c` | `ab3cf37eac16a1dbf91472335153ce6b92ef8daa3e5565103b8a92b75afe62dd` |
| linked kernel | `16fbec8acd87de5c34bc3487097dcea24e3fcd608a270de6f7de955eca0112cb` |
| M30LTXNU payload | `0718b348b3ffa691ac89bb502ae81b02af61ff0ef5e886ee4749023fe47fd343` |
| `shim-boot.img` (BOOT-flash candidate) | `e58de8b007ad1d9149d5161fb3ba2b7aef698c7177130257a8463e230ca0550b` |
| `ios-boot.img` (alternate cmdline) | `17328c3f3e76340ea1060d53bc94c206288a832bbcb0895865c1d019004efccc` |

## Layout

The 0432 bookkeeping did not move the kernel entry relative to v54:

- LC_UNIXTHREAD PC / entry VA `0xfffffff007411488`;
- `_start_first_cpu` `0xfffffff0074130ec`;
- `__TEXT_EXEC __text` vmaddr `0xfffffff007248000`, size `0x008b4000`;
- kernel end `0xfffffff008454000`;
- ADT PA `0x82454000`, boot_args PA `0x82458000`;
- payload size 16,179,264 bytes (v54 16,178,944).

The shim consumes entry/ADT/boot_args from the payload header, so the shim
Image/ELF remain byte-identical to v54/v53/v31. Details in
`entry-layout-check.txt`.

## Validation

- `verify_m30_kernel.py`: PASS (6 checks).
- `verify_m30_buildtree.py`: PASS, all patches reverse-apply.
- `verify_platform_match.py`: 9/9 PASS.
- `validate_boot_images.py`: PASS.
- `verify_handoff_v55.py`: 20/20 PASS.
- Focused tests: all applicable PASS (`test_m30_16k_pages.py` intentionally
  inapplicable without 0417). `validate-repo.py` reports only its pre-existing
  patch-number-gap warnings.
- CI Cortex-A53 compatibility check: PASS (no ARMv8.1 LSE atomics).

A generic QEMU smoke run was retained only as a non-authoritative trace. The
generic `virt` board lacks the M30 GICv2/timer/board handoff and defaults to
cortex-a76; its undefined-instruction loop and blank framebuffer are not used
as evidence for or against the candidate. See `qemu/qemu-trace-summary.txt`.

## Status / physical step

Candidate packaged and fully validated offline. New explicit authorization
permits autonomous physical testing of v55 and later validated candidates;
the identity gate still applies. The M30 was positively identified in TWRP as
SM-M305F / `m30lte`, bootloader `M305FDDU8CVK1`, serial `320081735bb166a3`,
`ro.twrp.boot=1` before any write. Download Mode must be confirmed immediately
before the flash.

Only `shim-boot.img` may be flashed to BOOT with Heimdall. Never USERDATA,
SYSTEM, or RECOVERY; never Fastboot. After the BOOT-only write, resume, wait
~180 s, return to recovery, pull pstore/pmsg, decode it, compare with
v45/v52/v54/v50, and preserve the raw evidence. A loaded SpringBoard process
is not visible UI. No UI/lock-screen success is claimed.
