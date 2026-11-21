# iOS candidate v14 — physical boot result (2026-11-22)

## Authorization / actions

Standing project authorization. Work on `main` @ `f8dc49c`.
Device confirmed: `m30lte`, `320081735bb166a3`, `M305FDDU8CVK1`, TWRP `3.4.03.0.0-UNOFFICIAL`.
v14 candidate hash verified `1a2d6f6940dd1501c36406c257b544bfa7340dc38b870da75ac4b0049fdfdfc3`.

- Flash v14 `--BOOT --no-reboot` → "BOOT upload successful" (first attempt).
- **BOOT readback skipped per user decision** ("skip readback from now on"). Not claimed verified.
- USERDATA / SYSTEM / RECOVERY untouched. One boot. User reported phone ran and returned to TWRP.
- Pstore captured immediately: `raw/pmsg-ramoops-0`, SHA
  `0c19b79fe1aa3dead5edb785e04248ef8f630880d76bb77378c9240467865f5e` (16,372 B, 208 records).
  Pre-boot baseline `raw/pre-pmsg-ramoops-0` (v13 log) preserved.

## Result — registration-order fix VERIFIED; launchd RAN; new dyld cache blocker

Patch 0412 fully verified on device — both AMFI registrations succeeded:
```
[026] SWEET AMFI: built-in interface registered (XML entitlements)
[029] calling mpo_policy_init for SWEET AMFI
[030] Security policy loaded: SWEET built-in Mobile File Integrity (SWEET AMFI)
[031] SWEET AMFI: platform binary policy registered (0)
[032] calling mpo_policy_init for Sandbox
[034] SWEET Sandbox: permissive policy registered (0)
```
No v13 `mac_policy_register` static-region fault. Boot progressed far past it:
`vfsinit` → `bsd_autoconf` → `IOFindBSDRoot` → eMMC USERDATA writable →
`hfs: mounted iOSRoot` → `load_init_program /sbin/launchd`.

**launchd successfully Mach-O-loaded, code-signing validated, and EXECUTED** — the
v12 `accelerate_entitlement_queries` NULL deref is gone. launchd reached:
```
[085] load_init_program: attempting to load /sbin/launchd
[089] Darwin Ignition Sequence Version 1.0.0
[123]        hello: hello from launchd.1
[124]      preboot: mounting preboot
```

### New blocker — dyld shared cache 16K code directory rejected
```
[125] failed to lookup preboot: 25
[128] ignition boot failed: 25
[133] disallowing unsupported code signature page shift: 14
[134] unable to create a validated cs_blob object: 85   (EBADEXEC)
[135] dyld cache '(null)' not loaded: code signature registration for shared cache failed
[136] Library not loaded: /usr/lib/libSystem.B.dylib
[143] panic: initproc failed to start -- ... Library not loaded: /usr/lib/libSystem.B.dylib
```
Panic in `proc_prepareexit` → `exit_with_reason` → `postsig_locked` → `bsd_ast`
(launchd pid 1 exited because libSystem could not load from the dyld cache).

**Exact cause:** this M30 kernel is 4K (`PAGE_SHIFT=12`). `cs_validate_codedirectory()`
(`bsd/kern/ubc_subr.c:374`) only accepts `PAGE_SHIFT_4K (12)` or `PAGE_SHIFT (12)`,
rejecting the genuine iOS dyld shared cache code directory's 16K page size (14).
Confirmed in binary: `cmp w8,#0xc` then compare with runtime `PAGE_SHIFT`.
`failed to lookup preboot: 25` is a separate known non-fatal preboot absence.

### Fix (patch `0413-m30-accept-16k-code-directory.patch`)
Add `PAGE_SHIFT_16K (14)` to the accepted code-directory page shifts. This does
NOT weaken verification: `cs_blob_init_validated()` sets `csb_hash_pageshift =
cd->pageSize` and `hash_pagemask = (1U<<cd->pageSize)-1`, so all page hashes are
still validated at the CD's native 16K granularity; full structural CD validation
is unchanged; no `pmap_cs` hardware enforcement on this config; no bypass args.
Regression test `tools/test_m30_16k_codedirectory.py` PASS.

## Honest status

- AMFI registration-order fix VERIFIED. launchd Mach-O loads and EXECUTES ✓.
- Blocker is now dyld shared cache 16K code-sign page size, not AMFI.
- No launchd success / SpringBoard claim (initproc failed to start).
- Next: CI build v15 with patch 0413, then propose physical test.
