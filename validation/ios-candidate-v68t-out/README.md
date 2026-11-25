# Combined candidate v68t — corrected iOS rootfs + v68 XNU + Melfas touch

Source: `main` head `b7cd214f` (commit that added patch `0451`). CI kernel run
`45663503730` **GREEN**; rootfs CI run `45651107666` **GREEN**.

## Components
- USERDATA (already written to device under explicit approval):
  release `ios-root-20H392-45651107666`, image
  `ios-root-20H392.img`, size 21474836480 bytes, SHA256
  `dea9110cc5cc5d063785682527d9d0c527896a4fb34d2bacc9e9a182c8d601f4`.
  CI verified all 595 container metadata UUIDs match directory names and
  `Library/Caches` paths exist. Device write exit 0; first 64 MiB readback hash
  matched the source exactly.
- BOOT (NOT yet flashed): v68-based XNU plus `0451-m30-melfas-touch.patch`.
  Kernel SHA256 `5e898ee0ec7bffee85c5b49cfcda82ff5d0624762233b438a778f26861f83758`.
  Boot image SHA256 `a5c05b020fa81203ebca3eaecfe2234ab3babaf11d8d857b5739a91b6cbe52e4`.
  Payload SHA256 `45aae173f85a19b965a00826af03a3176ce2fd525944137115879c74c10718e9`.

## Cmdline
Exact v68 cmdline plus `m30touch=1 m30touchhid=1`; all serial/console/display
and security settings unchanged.

## Driver scope
M30LTE-only, opt-in, bounded I2C reads, MIP 4.0 status/packet parsing, format-8
12-byte decoder, 0..4095 -> 1080x1920 scaling, multi-finger press/move/release,
contact timeout releases, GPA0-0 IRQ-line sampling (diagnostic, not an XNU IRQ
handler), durable heartbeat. All `sweet_hid_touch()` calls gated by
`m30touchhid=1`. No controller config/firmware/NVM writes.

## Review
Boot structural PASS; handoff 30/30; kernel verifier 6/6; platform 9/9;
buildtree 5/5 critical provenance including 0451. Focused tests 32 PASS /
1 known unrelated 0417 FAIL. No v69-v72 patches (0446-0450, 0452) present.

## Physical status
USERDATA corrected image is installed. BOOT must still be flashed with this
candidate's `ios-boot.img` before touch can be tested. No flash/reboot was
performed for this candidate. Touch support is NOT claimed until physical
contact logs and a touch action above IOHID are observed.
