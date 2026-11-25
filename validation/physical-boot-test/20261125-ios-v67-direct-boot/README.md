# v67 direct reboot — read-only pstore capture (2026-11-25, IST)

## Device identity gate (before read)

`adb devices` reported serial `320081735bb166a3`; `getprop` returned:

- `ro.boot.em.model=SM-M305F`
- `ro.product.device=m30lte`
- `ro.boot.serialno` / `ro.serialno=320081735bb166a3`
- `ro.bootloader=M305FDDU8CVK1`
- `ro.twrp.boot=1`

Identity PASS. The device was already in TWRP; no flash or write was
performed. Serial-bearing values are redacted from repository files.

## Capture

Read-only pull with `adb exec-out dd if=/sys/fs/pstore/pmsg-ramoops-0`.

- Raw: `raw/pmsg-ramoops-0`
- Size: 16,464 bytes
- SHA-256: `04ab4e093b19184c5ad67f212c47c46dce06063067c9b4480dbd09d3a0ae9028`
- Decoded: `decoded-pmsg.txt`
- Decoded SHA-256: `7d5dac276670018c4f05d32947342391ff40ac9da45d26912e8e0877dbe8bf09`
- Decoder: `tools/decode_pmsg.py`

## Result

The capture contains 186 valid `XNU:` records and ends during launchd early
boot tasks (`restore-datapartition`). It contains no `M30 FB:` selector,
staged/present/wait/done, or `M30 UI:` records and no IRT patch-hit status.

This is **not** a reproduction of the earlier v67 capture
(`validation/physical-boot-test/20261125-ios-v67-boot/`), which had 171
records including framebuffer telemetry and the selector call shapes. It is
therefore recorded as a separate early-boot artifact and is **not** used as
evidence that the direct reboot reached SpringBoard/backboardd.

The user's observation for the direct reboot remains **Apple logo only**, so
that run is REJECTED for the lock-screen objective. No rollback was performed
and the v67 BOOT image remains installed.
