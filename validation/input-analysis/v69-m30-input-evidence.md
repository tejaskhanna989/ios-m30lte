# v69 M30 input hardware evidence (facts only)

This document records evidence already present in the repository. It does not
propose a driver or register map. No hardware address in this file was guessed.

## Touchscreen controller

- **Controller:** Melfas **MSS100**, bound by `melfas,mms_ts` / `mms_ts`.
- **I²C address:** `0x48`.
- **I²C controller:** Exynos `s3c-i2c` MMIO `0x13870000`, Linux `i2c-10`.
- **IRQ:** GPA0-0, Linux GPIO `6`, IRQ `243`.
- **I²C GPIOs:** SDA GPP4-0 / GPIO `91`; SCL GPP4-1 / GPIO `92`.
- **Supply:** fixed regulator `tsp_ldo_en`, 3.3 V, active-high GPIO GPG2-1,
  boot-on.
- **Firmware names:** `tsp_melfas/mss100_m30.fw` and
  `tsp_melfas/mss100_m30_old.fw`.
- **Runtime Android evidence:** probe starts, parses the DT, registers
  `sec_touchscreen`/`sec_touchproximity`, and reports
  `MELFAS MSS100 Touchscreen is initialized successfully`.
  IRQ thread `irq/243-mms_ts` emits contact press/release reports.

Sources:
- `m30-boot-original/boot.img` embedded stock DTB, node
  `/i2c@13870000/mms_ts@48` and `/tsp-ldo-en`.
- `validation/physical-boot-test/20261121-ios-v12-boot/dmesg-postboot.txt`
  lines 426, 985, 991, 992, 1022.
- `validation/physical-boot-test/20261121-ios-v12-boot/last_kmsg-postboot.txt`
  lines 12324, 12327, 12337, 12341.
- Stock kernel strings in the same `boot.img`: `melfas,mms_ts`, `mms_probe`,
  `mms_interrupt`, `MELFAS %s Touchscreen is initialized successfully`,
  `MSS100`, `melfas_mss100`.

### Claims that are not hardware evidence for M30

- `README.md` Goodix GT9896 narrative and
  `bsd/dev/sweet_touch.c` are a Xiaomi SWEET experiment; `GT9896` is absent
  from the stock M30 boot image.
- ZT7538 / HX83112A / `sec_ts` references belong to other board experiments
  and are explicitly excluded for M30 in the certified build tree.
- The iOS-side ADT has no touch, I²C, Melfas, Goodix, ZT7538 or HX83112A
  properties.

## Physical buttons

- Verified M30 board constants in the certified build tree:
  - ALIVE MMIO `0x11cb0000`
  - GPA1 CON/DAT/PUD offsets `0x60/0x64/0x68`
  - power pin `7`, volume-up pin `5`, volume-down pin `6`
- Consumer: `bsd/dev/a5xelte_keys.c`. It maps ALIVE read-only, polls GPA1DAT
  every 10 ms with 3-sample debounce, and calls `sweet_hid_key(key, down)` on
  transitions.
- HID side: `iokit/Kernel/arm/hid/SweetHID.cpp` provides software key/touch
  entry points; it does not touch hardware itself.

## State of v68

- The linked v68 kernel contains `SweetHIDTouch`/`SweetHIDKey` software HID
  symbols but no Melfas/MSS100/`mms_ts` strings or active hardware touch
  driver.
- `a5xelte_touch.c` and its `IOKitBSDInit.cpp` call site are excluded for
  M30LTE, and that exclusion is a certified buildtree invariant.
- Therefore no touch-controller probe, chip-ID read, IRQ registration or
  contact event path currently exists in the iOS kernel.
- Button GPIO mapping and polling code do exist; whether sampled transitions
  reach IOHID/SpringBoard must be determined from bounded diagnostics.

## Unknowns

- No XNU-side I²C controller driver evidence has been identified yet.
- No evidence yet that GPIO IRQ 243 is routed to XNU; current button code polls
  GPIO rather than using interrupts.
- No preserved Melfas register map or chip-ID register value. Any register-level
  driver must be derived from credible source, not invented.
- No proof yet that `sweet_hid_key()`/`sweet_hid_touch()` events reach IOHID and
  SpringBoard in this build.

## XNU input plumbing already present in v68 (facts)

Derived from the certified v68 tree (`/tmp/opencode/v68-buildtree/unpacked/xnu`)
and the linked kernel
`validation/ios-candidate-v68-out/inputs/kernel.development.m30lte`.

- The M30 build defines both `ARM64_BOARD_CONFIG_A5XELTE` and
  `ARM64_BOARD_CONFIG_M30LTE`, but not `ARM64_BOARD_CONFIG_SWEET`
  (`build/xnu.obj/DEVELOPMENT_ARM64_M30LTE/.CFLAGS:1`). The SWEET keys/touch
  sources are therefore compiled out despite their `.o` file list entries.
- `iokit/bsddev/IOKitBSDInit.cpp:786-790` calls `a5xelte_keys_init()`
  unconditionally under A5XELTE, and calls `a5xelte_touch_probe()` only when
  M30LTE is **not** defined.
- `bsd/dev/a5xelte_keys.c:112-131` defaults `a5keys` to enabled, maps ALIVE
  read-only, and starts the polling thread. The linked kernel contains
  `_a5xelte_keys_init` at `0xfffffff0074747b0`, `_a5_keys_thread` at
  `0xfffffff0074748a0`, and calls to `_sweet_hid_key` for all three M30 key
  bits.
- `iokit/KernelConfigTables.cpp:93-102` registers `SweetHIDButtons` and
  `SweetHIDTouch` personalities. `iokit/Kernel/arm/hid/SweetHID.cpp:381-397`
  and `:428-459` register the services; `:399-410` constructs keyboard events,
  `:461-549` constructs digitizer events, and `:551-571` exposes the C entry
  points.
- `iokit/Kernel/arm/hid/IOHIDEventServiceUserClient.cpp:41` requires
  `com.apple.hid.system.user-access-service`; `:227-256` checks the
  entitlement, `:261-333` creates the shared queue, `:365-388` opens the
  service, and `:604-641` enqueues events. The extracted backboardd binary
  contains the matching entitlement string.
- This is a custom IOHID user-client path; there is no `IOHIDSystem`,
  `IOHIDDevice` or `AppleHID*` service in the linked kernel. The intended
  consumer is backboardd, with SpringBoard/UIKit above it.
- There is no active producer calling `sweet_hid_touch()` in the M30 source.
  The touch HID service exists, but no hardware touch driver feeds it.

## v69 diagnostic plan (logging only)

- Patch 0446 caps the framebuffer status heartbeat to the first eight
  records (ticks 600..4800). v68 emitted 138 records / 15,164 bytes, 92.6% of
  the ramoops data ring, which is why early `M30 FB: ABI sel=` records were
  lost.
- Patch 0447 emits at most one M30 key init/failure line per outcome and the
  first four transitions per key, preserving the existing polling and
  `sweet_hid_key()` call.
- Patch 0448 emits bounded HID service registration, producer dispatch, user
  client open and successful enqueue records. This distinguishes "GPIO sampled
  a transition" from "HID event was constructed and queued to a consumer".
- No touch-controller driver is added in this candidate: there is still no
  evidence-backed XNU register map or chip-ID procedure. The touch and button
  paths remain separate.
