# HFS journal EROFS blocker — exact cause and minimal fix (2026-11-21)

## Evidence (physical, commit b918a6a)

The genuine iOS HFSX image was written to USERDATA and recognized by XNU:
```
A5XELTE eMMC: /dev/emmcroot0 ready, GPT USERDATA read-only
BSD root: emmcroot0, major 1, minor 0
hfs: Initializing the journal (joffset 0xa2000 sz 0x800000)...
jnl: b(1, 0): do_jnl_io: strategy err 0x1e       (0x1e = EROFS)
jnl: b(1, 0): write_journal_header: error writing the journal header!
hfs: late jnl init: failed to open/create the journal (retval 0)
hfs_mounthfsplus: hfs_late_journal_init returned (22)
cannot mount root, errno = 19
```

## Exact source-level root cause

`bsd/dev/a5xelte_emmc.c` (shipped iOS buildtree):
- line 439: `PE_parse_boot_argn("emmcwrite", &enable_write, ...)`
- line 440: `emmc_writable = !strcmp(emmc_partition_name, "USERDATA") && enable_write == 1;`
- line 484 (`emmc_open`): `return ... ((flags & FWRITE) && !emmc_writable ? EROFS : 0);`
- line 507 (`emmc_strategy`): `else if (!(buf_flags(bp) & B_READ) && !emmc_writable) error = EROFS;`
- line 225 (`emmc_write_sector`): `if (!root_write && !log_write) return EROFS;`

The **v11 payload cmdline** is
`debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292 rd=emmcroot0 emmcroot=USERDATA emmcprobe=1`
— it has `emmcroot=USERDATA` but **no `emmcwrite=1`**, so `emmc_writable == false`.
HFS journal init writes the journal header through the block device; that write
hits `emmc_strategy`'s EROFS gate → `strategy err 0x1e` → journal_create fails →
mount fails. This is the exact EROFS cause — not the filesystem format, not GPT.

Layers ruled out:
- eMMC block driver: **this is the cause** (EROFS gate above).
- GPT partition handling: fine — GPT parsed, `/dev/emmcroot0` created, correct LBA window.
- BSD root selection: fine — `BSD root: emmcroot0` printed.
- HFS mount flags: HFSX volume header validated (journal init reached); failure is the
  device write, not a mount-flag rejection.
- `rootrw=1`: consumed ONLY under `ARM64_BOARD_CONFIG_SWEET` in `bsd/vfs/vfs_subr.c`,
  **not** in this M30LTE kernel (string absent). Adding `rootrw=1` would be a no-op
  and does NOT fix journal init. Confirmed by source, not assumed.

## Minimal fix

**Cmdline-only** (no kernel source patch): add `emmcwrite=1` to the payload cmdline.
New cmdline: `debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292 rd=emmcroot0 emmcroot=USERDATA emmcprobe=1 emmcwrite=1`.

Why safe:
- `emmc_writable` is true only when `emmc_partition_name == "USERDATA"` AND `emmcwrite==1`.
  `emmcroot` itself accepts only SYSTEM/USERDATA.
- All writes are bounds-checked to `[emmc_first_lba, emmc_first_lba+emmc_nsectors)`
  (the selected USERDATA GPT partition) in `emmc_write_sector` and `emmc_strategy`.
- Therefore SYSTEM, RECOVERY, BOOT and all other partitions remain unwritable through
  `/dev/emmcroot0`. This is proven by `tools/test_emmc_write_gating.py`.

No kernel source change is required; the `emmcwrite` consumer already exists in v11.
The HFSX image is unchanged (source evidence shows the image is valid — it reached
journal init).

## Tests

`tools/test_emmc_write_gating.py` PASS — asserts:
- emmcwrite consumed, gated on USERDATA;
- only SYSTEM/USERDATA accepted as emmcroot;
- all three EROFS write gates present;
- writes bounds-checked to selected partition;
- rootrw is SWEET-only (no-op on M30);
- v11 cmdline lacks emmcwrite=1; fix adds it.

## Candidate

See `validation/ios-candidate-v12-out/README.md` for the CI-built candidate and hash.

## Proposed physical test procedure (needs fresh authorization)

1. Re-write the same verified HFSX image to USERDATA (it is already there from the
   last test; USERDATA content unverified by full readback — re-write if desired under
   authorization; do NOT claim the old readback was verified).
2. Flash ONLY BOOT with candidate v12 (cmdline includes emmcwrite=1); verify BOOT readback.
3. One boot; capture pstore immediately on recovery return.
4. Expected: journal init succeeds, `hfs: mounted iOSRoot`, `load_init_program /sbin/launchd`.
5. No claim of launchd/SpringBoard until the captured log proves it.
