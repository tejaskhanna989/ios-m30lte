# iOS candidate v16 — align 16K code-directory page hashes on 4K kernel

Isolated candidate. v6–v15, backups, all physical evidence preserved.
No physical operations performed for v16. Work on `main` @ `0b0e538`.

## Exact cause and fix

Physical v15 (`91ed6b9d…7c281e`): patch 0413 worked — dyld cache 16K code
directory accepted, libSystem loaded, launchd ran to `hello from launchd.1`.
New blocker: `cs_validate_hash()` (ubc_subr.c:5739) asserted the fault offset be
16K-aligned (`csb_hash_pageshift=14`), but this 4K kernel (`PAGE_SHIFT=12`)
faults in 4K-aligned pages → `offset not aligned to cshash boundary` panic.
The dyld-cache page was already tolerated (`allowing (remove VALID) page`).

**v16 fix (patch `0414-m30-align-16k-cs-page-offset.patch`):** for
`csb_hash_pageshift > PAGE_SHIFT`, round the offset down to the CD hash boundary
(correct first-level hash index) and bound the actual-hash computation to the
single mapped 4K VM page (no 16K overread). A 4K chunk cannot match a 16K hash,
so the page is conservatively marked TAINTED, never falsely validated; existing
`cs_invalid_page` policy still decides. Genuine misalignment (shift ≤ PAGE_SHIFT)
still panics — no validation disabled; no bypass args. Cmdline unchanged.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `2ecc0290728b7675e97492f03b2309748a30e2ea320d8829ecdc5bd3910c3dd6` |
| payload | `9ed56d066c4c9d2bb42c2eec84e5d65ff58f41fc525a51b54da8619d5e02f521` |
| combined.bin | `c79e143becd8bf1027f12c69e195d062f359753d5fd8f54d25ec1750930227cd` |
| shim-boot.img | `131459fa51afa5ef5e368a50121e4f1bab6e9887d9656ceb07778026bc8ef3d3` |
| ios-boot.img | `61c1dad8c7428c6eed7aa336556832b44fd3087ae995be4d4b42372a61c6da4d` |

Cmdline: `debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292 rd=emmcroot0 emmcroot=USERDATA emmcprobe=1 emmcwrite=1`

## Validation (offline)

CI `44941797998` green (iOS target confirmed, LSE=0). Buildtree PASS, kernel
PASS, platform 9/9, CPU 17/17, ADT 22/22, handoff 18/18, packaging PASS, GIC
5/6 (inapplicable DAIF). All focused tests PASS including
`test_m30_16k_cs_offset.py` (reproduces the panic and proves the fix while
keeping genuine-misalignment validation). Shim byte-identical to proven v6;
`maxmem=292`, iOS 16 target preserved.

## Status / next physical step

Not physically tested. Proposed: flash v16 BOOT only, preserve USERDATA/SYSTEM/
RECOVERY, one boot, capture pstore immediately. Expected: no alignment panic,
launchd proceeds past the dyld-cache page faults into further ignition stages.
No launchd/SpringBoard success claim until device evidence proves it.
