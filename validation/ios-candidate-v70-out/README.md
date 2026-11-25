# iOS-M30LTE v70 candidate — restore v68 lock screen (MAIN only)

Source: `528bb2760e040f1e23ae4f94ae8f870775188797` (`v70: revert v69 input diagnostics to restore v68 lock screen`).
CI: `45592281185`, `M30LTE XNU Kernel Build`, GREEN, head
`528bb2760e040f1e23ae4f94ae8f870775188797`, `2026-11-25T10:09:40Z..10:25:21Z`
(`15:39:40..15:55:21 IST`), macOS 15 Intel / Xcode 16 / iphoneos / DEVELOPMENT
/ M30LTE / `DXB_SHA=663906528d1cd5ea8fde7de6f16de73db9511549`.

## Correction

The final v69 pstore record proved only SpringBoard termination on an uncaught
`NSException`; no reason, thread or backtrace survived. v68's `SBERR` records
were benign duplicate-class warnings. The smallest relevant v69 delta was the
new input diagnostics: `0447` on the GPIO/key producer and `0448` on the HID
consumer used by backboardd. `0446` only caps framebuffer heartbeat logging.

v70 keeps `0446` and adds pure-revert patches `0449` and `0450`, restoring
`bsd/dev/a5xelte_keys.c`, `SweetHID.cpp` and
`IOHIDEventServiceUserClient.cpp` byte-for-byte to v68. Functional GPIO-to-HID
behavior remains unchanged from v68 and is still runtime-proven by the v69
capture (66 GPIO transitions, 67 HID dispatches, `1 clients`). No selector 79
response, compatibility bypass, security change or touch work is included.

## Candidate hashes

- Kernel: `1537f9add321d2fada363788d7c9532660c6c29df476e7cb7fd785f17d2e2e28`
- Payload: `61f21979227c09c01dd6e2a57e8ef7fdaf1bca9f330d77cd59bf271aa9c56d7b`
- `shim-boot.img`: `4a3ae86cd7cba0692322d06aa7204aba36d21809567ed42b48e4208a288493cf`
- `ios-boot.img`: `51eef66440cc4abb0fe99db6a28628e440ee2406813929e587f3b5d5fce4a6e9`

Payload cmdline: `debug=0xc serial=3 cpus=6 keepsyms=1 maxmem=292 rd=emmcroot0 emmcroot=USERDATA emmcprobe=1 emmcwrite=1 a5fb_noconsole=1 a5fb_keep_on=1`.
This preserves `serial=3`, muted framebuffer console, persistent display-on
behavior and all v68 security/validation settings.

## Validation review

- CI patch-chain gate PASS for `0441` through `0450` with exact effective source
  hashes; exact kernel-binary gate PASS with kernel SHA256 above.
- Boot-image structural validation PASS; `verify_handoff_v70.py` 29/29 PASS.
- `tools/verify_m30_kernel.py` 6/6 PASS; `tools/verify_m30_buildtree.py` 4/4
  critical provenance PASS; `tools/verify_platform_match.py` 9/9 PASS.
- Focused tests: 26 PASS / 1 known unrelated FAIL
  (`tools/test_m30_16k_pages.py` still expects absent
  `0417-m30-16k-pages.patch`).
- Kernel contains v68 GPIO/HID producer strings and M30 framebuffer tags. The
  bounded v69 `M30 KEY:` / `M30 HID:` tags are absent, as intended. No Melfas
  touch-driver strings are present.

## Physical status

Not flashed yet. Any BOOT-only physical test must still pass a fresh exact
SM-M305F identity gate and Heimdall Download Mode detection immediately before
the write, then use `--no-reboot` with no USERDATA/SYSTEM/RECOVERY write.
Acceptance requires a visually observed persistent lock screen, no fatal
SpringBoard exception, and retained GPIO-to-HID evidence. Touch remains
unsupported and must not be claimed.
