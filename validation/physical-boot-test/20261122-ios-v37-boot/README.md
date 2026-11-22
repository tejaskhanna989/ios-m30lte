# iOS v37 physical boot — BOOT only, 2026-11-22 — short window

Flashed `validation/ios-candidate-v37-out/shim-boot.img`
(`45db21b12eb7c8a20ba8ba5bb0ed4b39e7952aa1698e40574ffdab63db5d2505`) to BOOT
only, resumed, waited ~30 s, forced back to TWRP. USERDATA/SYSTEM/RECOVERY
untouched. BOOT readback skipped.

Fresh pstore `104b1404a54f9319883dde9d59bc4121f53ea4aec5c4fcbd0827e4043bd0508e`
(16,372 B, 194 records). Ring starts mid-message at `0x20`; log ends at
`lockdownd` — SpringBoard had not loaded yet, so the XCTEST retrigger never
fired and there are no `M30 IRT` / `M30 XCTEST` lines in this capture.

This confirms the fundamental timing problem: the 16 KB ring wraps before the
interesting userspace event. v38 adds a bounded periodic status replay from the
IRT worker thread so the final state is always present in a fresh pstore,
regardless of when the device is forced back.

No UI/lock-screen success claimed.
