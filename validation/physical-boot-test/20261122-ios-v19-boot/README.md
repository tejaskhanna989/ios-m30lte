# iOS candidate v19 — physical boot result (16K pages, FAILED, reverted)

## Authorization / actions

Standing project authorization. Work on `main` @ `d927709`.
Device `m30lte`, `320081735bb166a3`, `M305FDDU8CVK1`, TWRP.
v19 candidate hash verified `55f66a95648c2dbd23e81d9e7226ee06f3058f4d724f8d92957d49087097a57f`.

- Flash v19 `--BOOT --no-reboot` → "BOOT upload successful" (first attempt).
- BOOT readback skipped per standing instruction (not claimed).
- USERDATA / SYSTEM / RECOVERY untouched. One boot.
- Pstore captured: `raw/pmsg-ramoops-0` SHA
  `33aa0dc311cf180020e5580a2903198991b11323846608dc9b6edeb921c7ed3f` (1,384 B).

## Result — FAILED: 16K kernel does not boot on M30 hardware

Only 1,384 bytes of pstore, **zero XNU records** (adbd + assembler scanlines only).
User reported the phone stops at the shim's "XNU Entry" text / green box. The
16K-page kernel produces no kernel log at all — the `__ARM_16K_PG__` change breaks
early boot on this Exynos 7904 / Cortex-A53 board (likely the shim/kernel handoff
or TCR configuration does not work with a 16K translation granule here).

This was the explicitly flagged risk in the v19 README. The change has been
REVERTED: `xnu/patches-minimal/0417-m30-16k-pages.patch` removed and the
`verify_m30_buildtree.py` critical-patch list restored. v18 (4K pages, deep iOS
userspace) remains the best candidate. All earlier candidates and evidence intact.

## Where things stand

- Confirmed on device across v12-v18: AMFI interface + policy registration fixed,
  dyld cache 16K code directory accepted, AMFI IOService present, genuine iOS
  16.7.16 userspace boots deep (launchd + many daemons, `OS version: 20H392`).
- Remaining blocker: daemon crash loop (lsd, securityd, backboardd,
  identityservices; sig 5/6) tied to the 4K-kernel vs 16K-signed dyld cache
  mismatch. Patch 0416 (skip 16K page validation) did not stop it; forcing 16K
  pages (0417) regressed and was reverted.
- Proper fix would need mapping a full 16K block for page-hash validation
  (vm_paging_map_object maps only one page) or equivalent deeper VM work — a
  substantially larger change than the focused patches so far.
- No SpringBoard/UI boot claim. No kernel panic in v16-v18 logs (user returned
  to recovery manually).
