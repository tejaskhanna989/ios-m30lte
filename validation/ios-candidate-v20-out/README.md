# iOS candidate v20 — full 16K code-directory block validation on 4K kernel

Baseline: v18 exclusively. Isolated candidate. v6–v19, backups, physical evidence preserved.
No physical operations performed for v20. Work on `main` @ `a6910c2`.

## Exact cause and fix

v18 baseline: 4K kernel, genuine iOS 20H392 userspace boots deep but lsd/securityd/
backboardd/identityservices crash in a loop. A 16K code directory cannot be verified
from a single 4K mapping; patch 0416 left dyld-cache pages unvalidated, so processes
lost CS_VALID and died.

**v20 fix (patch `0418-m30-validate-16k-cs-block.patch`):**
- VM layer (`vm_fault.c`): gather the entire 16K block from the object's four
  resident 4K pages via the permanent 1-to-1 physical mapping (object lock held,
  non-blocking `kalloc Z_NOWAIT`, guarded paging_offset/alignment). If any page
  is absent or allocation fails, fall back to the single mapped page.
- BSD (`ubc_subr.c`): `cs_validate_page`/`cs_validate_hash` take an explicit
  `data_size`; a 16K CD is validated by hashing the FULL 16K block against the
  code directory hash at `offset >> 14`. Hash size is bounded by `data_size`
  (no overread); loop/page-boundary/4-bit-mask logic corrected for 16K.
- **Fail secure**: without a full block, no validation and no taint -- never
  marks unverified executable pages valid. Genuine misalignment still panics.
- No security weakened: full cryptographic verification of the genuine signature.
  Cmdline, 4K config, shim, AMFI, HFSX root, maxmem=292 all preserved.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `afcaea9a301450d0df7e62a469817ac0e19ee91f4fe9b8747f9afcf8ed84c971` |
| payload | `4578a2d070a0017ae70cbfe1a5d78d956a28a023bfa664611a9822affd2c094c` |
| combined.bin | `015c379b5bb4e63e796c5f2672c04c84fef67665a5741cf327379631bd84ed56` |
| shim-boot.img | `3fdd4246d78d830ebdd9147cf7f8b01538e60f2e8ee5703275d661fe4e363e78` |
| ios-boot.img | `5fa972701c33c9a3662fb1acdd9d43c67cc8f9de5c2d3aa619988c66b0951fff` |

Cmdline: `debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292 rd=emmcroot0 emmcroot=USERDATA emmcprobe=1 emmcwrite=1`

## Validation (offline)

CI `44953949472` green (iOS target confirmed, LSE=0). Buildtree PASS, kernel
PASS, platform 9/9, CPU 17/17, ADT 22/22, handoff 18/18, packaging PASS, GIC
5/6 (inapplicable). All focused tests PASS including `test_m30_validate_16k_cs_block.py`
(valid/invalid/partial/4K/boundaries/alignment/no-overread). Shim byte-identical
to proven v6. 4K config confirmed: no `__ARM_16K_PG__`, no patch 0417.

## Status / next physical step

Not physically tested. Proposed: flash v20 BOOT only, preserve USERDATA/SYSTEM/
RECOVERY, one boot, capture pstore immediately. Expected: dyld-cache pages fully
validated, processes keep CS_VALID, no daemon crash loop, progress toward
SpringBoard. No success claim until device evidence proves it.
