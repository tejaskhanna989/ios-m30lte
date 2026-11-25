# v68t BOOT-only flash (2026-11-25)

Authorized BOOT-only Heimdall flash of combined candidate
`validation/ios-candidate-v68t-out/ios-boot.img`.

- Image SHA256 gate PASS: `a5c05b020fa81203ebca3eaecfe2234ab3babaf11d8d857b5739a91b6cbe52e4`.
- Identity gate PASS immediately before write: SM-M305F / m30lte /
  M305FDDU8CVK1 / known serial / TWRP.
- Download Mode detected by Heimdall immediately before write.
- Flash: `heimdall flash --BOOT <image> --no-reboot`, exit 0,
  `BOOT upload successful`.
- No USERDATA/SYSTEM/RECOVERY write, no Fastboot, no original backup overwrite.
- **No reboot and no resume performed** — device left in Download Mode by
  explicit instruction. Physical boot observation is still pending.
