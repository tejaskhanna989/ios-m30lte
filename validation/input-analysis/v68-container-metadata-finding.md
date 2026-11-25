# v68 userspace container-resolution finding (read-only evidence)

## Evidence
Read-only HFS+ inspection of USERDATA (`/dev/block/mmcblk0p28`) via
`tools/hfsplus_ro.py` over `adb shell dd if=…` (no mount, no write):

- 595 `.com.apple.mobile_container_manager.metadata.plist` files exist under
  `/private/var/containers` and `/private/var/mobile/Containers`.
- **0 of 595** `MCMMetadataUUID` values match any directory name in the
  catalog. All UUIDs are stale relative to the container directory names.
- `com.apple.backboardd` system-container metadata sits in directory
  `6532C5C7-7AF8-4D04-94D3-6E13239457D2` (which has `Library/Caches`), but
  declares `MCMMetadataUUID = 7993DF92-69FB-42C8-963A-B1E3B7AAF64F`.
  No directory with that UUID exists anywhere in USERDATA.
- `com.apple.springboard` metadata similarly declares UUID
  `97F8E922-00A4-48E1-B62F-CC799A4D0795`, which also has no directory.
- `/private/var/containers/Temp` is absent (root-tweak script expected it);
  this is secondary and not directly in the backboardd backtrace.

## Correlation
Crash reports recovered from the same filesystem show backboardd dying in:

```
__exceptionPreprocess -> objc_exception_throw -> _NS_os_log_callback ->
+[NSURL(NSURL) fileURLWithPath:] ->
-[BSSystemContainerForCurrentProcessPathProvider libraryPath] ->
-[BSSystemContainerForCurrentProcessPathProvider cachesPath]
```

BaseBoard resolves container paths from the metadata UUID; a UUID with no
matching directory yields a nil path, which Foundation rejects. The same
pattern explains simultaneous `lsd` (`userContainerURL`), `assistantd`
(CloudKit container) and `installcoordinationd` failures. XNU, framebuffer,
AMFI, IRT, SweetHID and SweetSurface are not implicated.

## Origin in source
`tools/m30lte-root-tweaks.py` creates the container directories
(`containers()`) but never reconciles `MCMMetadataUUID` with the directory
names copied from the donor iOS root. This is the smallest justified place
for a fix; it runs on a host-staged rootfs image, never on the device.

## Minimal fix candidate
Add `fix_container_metadata(root)` to `m30lte-root-tweaks.py`: for every MCM
metadata plist, set `MCMMetadataUUID` to the basename of its containing
directory, preserving all other keys and file ownership/mode. Add a read-only
verifier `tools/verify_ios_container_metadata.py` and 4 focused tests.

No device partition, BOOT image, XNU source, framebuffer or security setting
is changed by this fix. A new rootfs image must be staged, verified and
approved separately before any physical write.
