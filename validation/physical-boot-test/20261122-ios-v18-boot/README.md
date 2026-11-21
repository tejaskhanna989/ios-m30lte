# iOS candidate v18 — physical boot result (2026-11-22)

## Authorization / actions

Standing project authorization. Work on `main` @ `32e4a87`.
Device `m30lte`, `320081735bb166a3`, `M305FDDU8CVK1`, TWRP.
v18 candidate hash verified `8a68ada1373b597c4ae1253e59b1fba9a612609f1c74d27308afc38fb2d8f1eb`.

- Flash v18 `--BOOT --no-reboot` → "BOOT upload successful" (first attempt).
- BOOT readback skipped per standing instruction (not claimed).
- USERDATA / SYSTEM / RECOVERY untouched. One boot. Pstore captured immediately:
  `raw/pmsg-ramoops-0` SHA `2d94c77826a1ed49855b483f6c324ec7f604e23bf03c9d24ff74c170e553f73e`
  (16,372 B, 164 records). Pre-boot baseline preserved.

## Result — deep iOS userspace; 0416 did not stop the daemon crashes

Patch 0416 applied (no AKS/AMFI abort), iOS userspace ran very deep — many
daemons: seserviced, bluetoothd, securityd, mediaserverd, fairplayd.H2, tccd,
backboardd, lsd, identityservices, mDNSResponder, apsd, etc. AKS stand-in calls
and Sandbox messages show real daemon activity. **No kernel panic** — user
returned to TWRP manually (key records 152-163).

But lsd, securityd, backboardd, identityservices, UserEventAgent still crash
(sig 5/6) with `Text page corruption detected`. Analysis: `revalidate_text_page()`
(vm_fault.c:8177) is called AFTER a fatal signal to check text integrity; the
"corruption" message is a symptom printed during crash handling, not the cause.
Patch 0416 (skip 16K-CD page validation, no taint) did not prevent the crashes,
so the root cause is deeper than the taint: the 4K kernel vs 16K-signed dyld
cache / 16K-page iOS rootfs mismatch (shared-region mapping, page hash
granularity). The consistent crash PCs across restarts point to deterministic
dyld-cache mapping issues, not random corruption.

## Next — fundamental page-size fix (patch 0417, planned)

Genuine iOS 16.7.16 for iPhone10,3 (D22) uses 16K pages; the M30 kernel is 4K
because `arm_init.c` selects 4K when memSize <= 1GB (maxmem=292). `PAGE_MAX_SHIFT`
is 14 and the TCR translation granule is compile-time (`__ARM_16K_PG__`), which
SWEET.h defines. Planned patch 0417 defines `__ARM_16K_PG__ 1` for M30LTE so the
kernel uses 16K pages natively — dyld cache 16K CDs validate/mapping natively;
patches 0413/0414/0416 become harmless no-ops. Then physical test v19.

## Honest status

- Genuine iOS userspace runs deep (many daemons) ✓.
- Daemon crash loop remains; not a signature/entitlement bypass.
- No kernel panic; no SpringBoard/UI claim; no full boot success claim.
