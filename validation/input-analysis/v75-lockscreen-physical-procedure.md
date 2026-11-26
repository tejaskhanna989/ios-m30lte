# v75 native lockscreen candidate — physical test procedure (NOT executed)

## Change under test
v75 adds SpringBoard's native MCM system container to the staged USERDATA:
`com.apple.springboard` / `97F8E922-00A4-48E1-B62F-CC799A4D0795`, with
`Library/Caches` and a matching metadata plist (UUID == directory name). The
UUID is the value recorded on the device where the native lockscreen was
previously observed (`v68-container-metadata-finding.md`). The v73 lsd/MCM
build input is preserved; Melfas touch remains dormant (no `m30touch` args).

## Artifact
CI rootfs run `45868285795`, release `ios-root-20H392-45868285795`
(exact hash/size to be filled from the published manifest after CI succeeds).

## Required preconditions
- Device in TWRP with ADB; exact identity SM-M305F / m30lte /
  bootloader `M305FDDU8CVK1` / known serial; Download Mode gate if flashing BOOT.
- Original BOOT backup `m30-boot-original/boot.img` hash `469c12d2…` intact.
- Use a BOOT without `m30sblockdiag=1` so the 16 KiB pstore ring is not flooded:
  the native candidate `validation/ios-candidate-v68t-native-out/ios-boot.img`
  (`9c022561…`) is recommended. USERDATA v73 remains in place until the
  explicit authorized write of this candidate.

## Procedure (requires separate explicit authorization)
1. Verify the four release part hashes against `parts-sha256.txt`.
2. Stream `cat parts | gunzip | adb shell dd of=/dev/block/by-name/USERDATA bs=4194304`
   (no `/data/local/tmp` staging, no local 20 GiB reassembly); `sync`; bounded
   readback hash check.
3. Reboot only if authorized; let it settle several minutes.
4. Report the VISUAL result: native iOS lockscreen (wallpaper, clock, unlock
   controls) vs Apple logo/console. Process liveness or framebuffer counters
   alone are NOT acceptance evidence.
5. If needed, pull pstore read-only; keep diagnostic output bounded.

## Acceptance
Visible, persistent native iOS lockscreen on the physical M30. Touch is a
separate, unproven feature and must not be inferred from this test.
