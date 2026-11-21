# iOS candidate v12 — HFS journal EROFS fix (emmcwrite=1)

Isolated candidate. v6–v11, backups, all physical evidence preserved.
No physical operations performed for v12.

## Exact cause and fix

Physical evidence (commit b918a6a): the genuine HFSX image was recognized
(`hfs: Initializing the journal ...`) but journal header writes failed with
`do_jnl_io: strategy err 0x1e` (EROFS). Root cause: `bsd/dev/a5xelte_emmc.c`
returns EROFS for writes when `emmc_writable == false`, and that flag requires
both `emmcroot=USERDATA` **and** `emmcwrite=1`. v11's cmdline had the former
but not the latter. Full analysis: `validation/hfs-journal-eroos-fix-20261121.md`.

**v12 fix: cmdline-only — add `emmcwrite=1`.** No kernel source change, no HFSX
image change. `rootrw=1` was investigated and rejected: it is compiled only
under `ARM64_BOARD_CONFIG_SWEET`, absent from this M30LTE kernel (a no-op).

Cmdline: `debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292 rd=emmcroot0 emmcroot=USERDATA emmcprobe=1 emmcwrite=1`

Safety: `emmc_writable` is true only for partition USERDATA with emmcwrite=1;
writes are bounds-checked to `[emmc_first_lba, +emmc_nsectors)` of the selected
GPT partition. SYSTEM/RECOVERY/BOOT remain protected — proven by
`tools/test_emmc_write_gating.py`.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `ab645b13f8dc16a21fa9fbb7507e39fadd5faa01832998c1ea1a56aad7114426` |
| payload | `40a253b7ae9e1c1badc849508884bdce17f12db00c4c59decb074e614db6b1dd` |
| combined.bin | `666c9a0205a666aa5f3f67b6d706588c12954c01cf5512530ba2ac828dbed4e3` |
| shim-boot.img | `fccd2422d16ba9adc3d0d3bd8474f6d4e488f81086df35abdfeb7be7a8d1dd41` |
| ios-boot.img | `f2f537789f9d3a1e571eebb02be6079f905c2dacd9aff19630af9a1118e2931a` |

## Validation (offline)

CI `44927412685` green (iOS target confirmed, LSE=0). Buildtree PASS, kernel
PASS, platform 9/9, CPU 17/17, ADT 22/22, handoff 18/18, packaging PASS,
GIC 5/6 (documented inapplicable DAIF check). All focused tests PASS including
`test_emmc_write_gating.py` (non-M30LTE configs unaffected). Shim region
byte-identical to proven v6; `maxmem=292` and iOS 16 target preserved.

## Status / next physical step

Not physically tested. Needs fresh authorization: re-verify/re-write USERDATA if
desired, flash BOOT only with v12, verify BOOT readback, one boot, capture pstore
immediately. Expected: journal init succeeds, `hfs: mounted iOSRoot`,
`load_init_program ... /sbin/launchd`. No launchd/SpringBoard claim until proven.
