# iOS candidate v15 — physical boot result (2026-11-22)

## Authorization / actions

Standing project authorization. Work on `main` @ `984cf70`.
Device confirmed `m30lte`, `320081735bb166a3`, `M305FDDU8CVK1`, TWRP.
v15 candidate hash verified `408e2177fcfd8af9a02537547ec860d617d930773a2c9d0ee11dab186d6db1ab`.

- Flash v15 `--BOOT --no-reboot` → "BOOT upload successful" (first attempt).
- BOOT readback skipped per user standing instruction (not claimed).
- USERDATA / SYSTEM / RECOVERY untouched. One boot. Pstore captured immediately:
  `raw/pmsg-ramoops-0` SHA `91ed6b9df587f84fd7e0e4454c0ed78aed093499df38be1696d7a3a6417c281e`
  (16,372 B, 213 records). Pre-boot baseline preserved.

## Result — 16K CD fix VERIFIED; further progress; new alignment panic

Patch 0413 worked: the "disallowing unsupported code signature page shift: 14"
and `EBADEXEC(85)` errors are GONE. The dyld shared cache code signature validated,
`libSystem.B.dylib` loaded (no "Library not loaded" message), and launchd advanced:
```
[095] hfs: mounted iOSRoot on device b(1, 0)
[099] load_init_program: attempting to load /sbin/launchd
[135] hello: commence primary ignition
[136] hello: hello from launchd.1
[137] preboot: mounting preboot
```
`ignite() returned 25` (preboot not found) is the same non-fatal condition as v14.

### New blocker — 16K CD page-offset alignment assertion
```
[146] CODE SIGNING: cs_invalid_page(0x100838000): p=1[launchd] final status 0x22000000, allowing (remove VALID) page
[147] panic: offset not aligned to cshash boundary @ubc_subr.c:5739
```
Symbolicated: `cs_validate_hash.cold.6` ← `cs_validate_hash` ← `cs_validate_page`
← `vm_page_validate_cs_mapped_slow` ← `vm_fault_enter` (pid 1 launchd).

**Exact cause:** `cs_validate_hash()` (ubc_subr.c:5739) asserts
`offset & ((1U<<csb_hash_pageshift)-1) == 0`. With the now-accepted 16K CD
(`csb_hash_pageshift=14`) on this 4K kernel (`PAGE_SHIFT=12`), the fault offset
(4K-aligned) is not 16K-aligned → panic. The dyld-cache page was already being
tolerated (`allowing (remove VALID) page`) — no CS_HARD/CS_KILL on launchd.

### Fix (patch `0414-m30-align-16k-cs-page-offset.patch`)
When `csb_hash_pageshift > PAGE_SHIFT`, round the offset down to the CD hash
boundary (correct first-level hash index) and bound the actual-hash computation
to the single mapped 4K VM page (no 16K overread). A 4K chunk cannot match a 16K
hash, so the page is conservatively marked TAINTED, never falsely validated;
existing `cs_invalid_page` policy still decides. Genuine misalignment (shift ≤
PAGE_SHIFT) still panics — no validation disabled. Regression test
`tools/test_m30_16k_cs_offset.py` PASS.

## Honest status

- 16K CD fix verified; dyld cache + libSystem load; launchd runs deeper.
- New blocker is per-page hash offset alignment, not signature validation bypass.
- No launchd success / SpringBoard claim (panic during dyld-cache page fault).
- Next: CI build v16 with 0414, then physical test.
