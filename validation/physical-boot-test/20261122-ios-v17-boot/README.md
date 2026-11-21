# iOS candidate v17 — physical boot result (2026-11-22)

## Authorization / actions

Standing project authorization. Work on `main` @ `29f17ab`.
Device `m30lte`, `320081735bb166a3`, `M305FDDU8CVK1`, TWRP.
v17 candidate hash verified `4f14d23c81279d47c86889f6efbe9c7cfa241b68affe11fdb86f114f0e5b30b0`.

- Flash v17 `--BOOT --no-reboot` → "BOOT upload successful" (first attempt).
- BOOT readback skipped per standing instruction (not claimed).
- USERDATA / SYSTEM / RECOVERY untouched. One boot. Pstore captured immediately:
  `raw/pmsg-ramoops-0` SHA `2fabc50d0469ffd27a664b4e2ca79cef8fcf974c6169538ad4608e13aacb55eb`
  (16,372 B, 155 records). Pre-boot baseline preserved.

## Result — AMFI IOService fix VERIFIED; deep iOS userspace; new lsd crash loop

Patch 0415 worked: NO "Unable to find AMFI" abort. `launchd_cache_loader`
found the service and boot proceeded into deep iOS userspace — many real daemons
ran: lsd, xpcproxy, identityservices, fairplayd.H2, mediaremoted, aggregated,
OTACrashCopier, contextstored. **No kernel panic in this log** — the user
returned to TWRP manually (key-press records 151-154); no launchd_cache_loader
or initproc panic. This is further than v16.

### New blocker — lsd killed by "Text page corruption"
```
Text page corruption detected for pid N
Process[N] crashed: lsd. Too many corpses being created.
CRASH lsd[N] sig 6 code 0x0 ... (repeated for pids 179-200)
```
Symbolicated source: `vm_fault.c:8313` returns KERN_FAILURE when
`page->vmp_cs_tainted != VMP_CS_ALL_FALSE` (`vm_fault.c:8246`) — the VM treats a
tainted TEXT page as corruption and kills the process.

Root cause: patch 0414 (v16) marked dyld-cache pages TAINTED because a 4K chunk
cannot match a 16K CD hash. That was fine while `cs_invalid_page` only removed
CS_VALID, but once the boot advanced far enough for `lsd` to execute dyld-cache
text pages, the VM's text-corruption guard started killing it in a loop.

### Fix (patch `0416-m30-skip-16k-cs-page-validate.patch`)
For `csb_hash_pageshift > PAGE_SHIFT`, `continue` (skip that blob) instead of
round-and-taint: the page stays UNVALIDATED (not tainted), so no text-corruption
kill; `cs_invalid_page` applies the process CS_VALID policy as it did in v16.
No false validation, no entitlement/signature bypass; genuine misalignment
(shift <= PAGE_SHIFT) still panics. Regression test
`tools/test_m30_skip_16k_cs_page.py` PASS.

## Honest status

- AMFI IOService fix verified; iOS userspace runs deep (many daemons) ✓.
- Blocker is a code-signing taint/kill loop, not a signature-validation bypass.
- No kernel panic; user returned to recovery; no full SpringBoard/UI claim.
- Next: CI build v18 with 0416, then physical test.
