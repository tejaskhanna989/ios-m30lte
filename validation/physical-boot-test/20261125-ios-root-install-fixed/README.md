# Fixed USERDATA install (2026-11-25)

Authorized USERDATA-only write of the CI-built corrected rootfs image.

- Source image: `ios-root-20H392.img`, exact size 21474836480 bytes, CI SHA256
  `dea9110cc5cc5d063785682527d9d0c527896a4fb34d2bacc9e9a182c8d601f4`.
- Release: `ios-root-20H392-45651107666`.
- Identity gate PASS immediately before write: SM-M305F / m30lte /
  M305FDDU8CVK1 / known serial / TWRP.
- Write: `cat IMAGE | adb shell dd of=/dev/block/by-name/USERDATA bs=4194304`,
  exit 0, 21474836480 bytes in 891.868 s (~14.9 min), then `adb shell sync`.
- Bounded read-only readback (first 64 MiB): device SHA256
  `50d4dc2cc965369db0eb23df2e969bd7611ea58fa8bc7e3e990b3b92ba3a4fe3`
  equals local source prefix SHA256.
- No /sdcard copy, no BOOT/SYSTEM/RECOVERY write, no Fastboot, no reboot.
- Backup requirement explicitly waived by the user for this write.
