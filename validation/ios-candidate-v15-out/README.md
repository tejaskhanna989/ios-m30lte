# iOS candidate v15 — accept 16K code directories for dyld shared cache

Isolated candidate. v6–v14, backups, all physical evidence preserved.
No physical operations performed for v15. Work on `main` @ `1874208`.

## Exact cause and fix

Physical v14 (`0c19b79f…865f5e`) proved patch 0412 worked: both AMFI registrations
succeeded, root mounted, and launchd Mach-O loaded, code-signing validated, and
**EXECUTED** (`hello from launchd.1`). New blocker: the genuine iOS dyld shared
cache code directory uses 16K pages (`pageSize=14`), but this 4K kernel's
`cs_validate_codedirectory()` (`bsd/kern/ubc_subr.c:374`) only accepted 12 and
`PAGE_SHIFT`(12) → EBADEXEC(85) → `libSystem.B.dylib` not loaded → initproc failed.

**v15 fix (patch `0413-m30-accept-16k-code-directory.patch`):** add
`PAGE_SHIFT_16K (14)` to the accepted code-directory page shifts. This preserves
full validation: `cs_blob_init_validated()` uses `csb_hash_pageshift = cd->pageSize`
and `hash_pagemask = (1U<<cd->pageSize)-1`, so all page hashes are validated at the
CD's native 16K granularity; structural CD validation unchanged; no `pmap_cs` on
this config; no bypass args. Cmdline unchanged from v14.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `96608a3b4e543fbfc18500e8c5befd2567e2f5354cc919e4a61ea295ff061fce` |
| payload | `145c59120d74b4708aa50bc172d10c80f885a6abebc5fbf42c593de0db1ff8fb` |
| combined.bin | `a53bee1683439edee4e1bbbf75a8ea07e3dda768f3d4e58a2119193c8324c8ee` |
| shim-boot.img | `408e2177fcfd8af9a02537547ec860d617d930773a2c9d0ee11dab186d6db1ab` |
| ios-boot.img | `e0dd41fc63922c200062731f3ad631d797b15089bd009c603867931834846b84` |

Cmdline: `debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292 rd=emmcroot0 emmcroot=USERDATA emmcprobe=1 emmcwrite=1`

## Validation (offline)

CI `44938520752` green (iOS target confirmed, LSE=0). Binary shows new
`cmp #0xe` (16K) check. Buildtree PASS, kernel PASS, platform 9/9, CPU 17/17,
ADT 22/22, handoff 18/18, packaging PASS, GIC 5/6 (inapplicable DAIF). All
focused tests PASS including `test_m30_16k_codedirectory.py` (reproduces the 85
failure and proves the fix without weakening validation). Shim byte-identical
to proven v6; `maxmem=292`, iOS 16 target preserved.

## Status / next physical step

Not physically tested. Proposed: flash v15 BOOT only, preserve USERDATA/SYSTEM/
RECOVERY, one boot, capture pstore immediately. Expected: dyld shared cache
code signature validates, `libSystem.B.dylib` loads, launchd proceeds past
`hello from launchd.1` into ignition stages. No launchd/SpringBoard success
claim until device evidence proves it.
