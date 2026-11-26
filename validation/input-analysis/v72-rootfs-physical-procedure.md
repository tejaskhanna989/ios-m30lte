# Corrected rootfs — physical test procedure (NOT executed)

Artifact: released by CI run `45804599066` as `ios-root-20H392-<run id>`
(new tag; the previous release `ios-root-20H392-44905109656` is preserved).

## Safety boundary
No device operation has been performed for this artifact. A physical rootfs
test requires separate explicit authorization. USERDATA is protected.

## Backup requirement
There is currently **no preserved USERDATA image backup**. Before any rootfs
write, with the device in TWRP:
1. `adb shell blockdev --getsize64 /dev/block/by-name/USERDATA` (expect
   `57038340096`).
2. Stream a read-only copy to host storage (do not write to the device):
   `adb exec-out 'dd if=/dev/block/by-name/USERDATA bs=4194304 2>/dev/null' > userdata-backup.img`
3. Verify size and SHA-256; record both. Keep this file untouched.
4. Verify the original BOOT backup `m30-boot-original/boot.img` SHA-256 is
   `469c12d2d304ff4b2f07ea89ff1bc329a77f8f73037420aa260c9e68db441e78`.

## Restore path if the test is rejected
Only after explicit authorization, from TWRP:
`cat userdata-backup.img | adb shell dd of=/dev/block/by-name/USERDATA bs=4194304`
then `adb shell sync`. Verify restored size/hash before booting. BOOT can be
restored independently from `m30-boot-original/boot.img` only if explicitly
authorized.

## Test sequence (after authorization)
1. Verify exact SM-M305F / m30lte / M305FDDU8CVK1 / known serial identity and
   TWRP state.
2. Verify the new rootfs image SHA-256 and size against the CI manifest.
3. Stream the image directly to `/dev/block/by-name/USERDATA` with `dd bs=4M`
   (no `/sdcard` staging, no Fastboot).
4. `adb shell sync`; verify a bounded readback hash.
5. Reboot only if explicitly authorized; observe whether the native lock
   screen appears (not merely process liveness).
6. If rejected, return to TWRP and restore from `userdata-backup.img` as above.

## Expected verification signals
- Lock screen visible and persistent (primary success condition).
- No `CRASH lsd` records in pstore; no `NSException`/`BBERR` fatal record.
- MCM UUID directories present; `lsd` stays running.
- Touch is a separate task; no touch claim from this test.

## Update: CI evidence changes the premise (2026-11-26)

CI diagnostics from run `45809286569` show the built image contains only empty
container skeleton dirs; `find` over `$MNT/private/var` returned **zero**
`.com.apple.mobile_container_manager.metadata.plist` files. The 595 plists
recorded in `v68-container-metadata-finding.md` were read from device USERDATA
**before** the 2026-11-25 USERDATA write (finding commit `bd9dada6` 21:24 IST,
install commit `b7cd214f` 22:49 IST). They are not part of the IPSW-derived
OS volume.

Consequently:
- `fix_container_metadata()` and `ensure_metadata_uuid_dirs()` are **no-ops**
  on the CI-built rootfs; this image does not carry the lsd UUID fix.
- Writing this image to USERDATA does not by itself deliver the fix. It also
  removes the existing container metadata; iOS repopulates containers at boot.
- The earlier claim of "595 UUIDs verified in CI" is unsupported and should
  not be relied upon.

Do not flash this artifact expecting the lsd fix. Either (a) supply the real
device metadata plists as an explicitly approved, out-of-git build input so
the staging tool has something to reconcile, or (b) apply the reconciliation
directly on the device under separate explicit authorization with a verified
read-only backup first. Both are blocked until the user authorizes them.

## v73 update — artifact now carries an explicit, limited reconciliation

A new CI candidate (`45819973935`, workflow input `require_mcm_input=true`)
consumes the device-derived build input described in
`v73-mcm-build-input.md`. Unlike the v72 artifacts, its image contains the
five allow-listed metadata plists and UUID-named directories for the
LaunchServices chain plus backboardd. It still does NOT contain the other
~590 containers from the original USERDATA.

Limitations that remain:
- No physical boot has been performed; `lsd` stability is unverified.
- No USERDATA backup exists; one is mandatory before any authorized write.
- Writing any rootfs image to USERDATA removes the existing container metadata;
  iOS repopulates containers at boot. The five reconciled records are the only
  ones this build controls.
- Lock-screen and touch claims remain separate and unproven.

Do not flash until the user explicitly authorizes a physical test and a
read-only USERDATA backup has been verified.
