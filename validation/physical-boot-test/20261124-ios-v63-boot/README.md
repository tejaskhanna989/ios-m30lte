# v63 physical boot test — REJECTED (blank screen)

MAIN only. Candidate: `validation/ios-candidate-v63-out/` (commit `41834be6`).
The only change from v62 was removal of `serial=3` from the payload cmdline.

## Identity and flash gate

- Identity verified in TWRP at `13:22:59Z..13:22:59Z`: `SM-M305F`, `m30lte`,
  serial `320081735bb166a3`, bootloader `M305FDDU8CVK1`, `ro.twrp.boot=1`.
- Download Mode detected `13:23:05Z`.
- BOOT-only flash `13:23:16Z..13:23:21Z` with Heimdall `--no-reboot`.
  Image SHA256
  `37c6c85af81e45c4ae687f8d36b8eada82cb2f3f3b843595c7502e1559654c13`.
- No USERDATA / SYSTEM / RECOVERY write; no Fastboot.

## Visual result

User-confirmed at `13:25:10Z`: **blank screen**, no Apple logo, no console text,
no lock screen. v63 is definitively rejected for the lock-screen objective.

## Pstore evidence

Pulled read-only from TWRP at `13:26Z` after the user reconnected the device
(identity re-verified: same serial/model/bootloader, `ro.twrp.boot=1`).

- Raw `pmsg-ramoops-0`: 3550 bytes, SHA256
  `6dfe5fadc1a10fcdfd87618c8d27f1be11a32ef4757b036e982491d8fbb63765`.
- Decode: 45 records, `clean=True`.
- Record tags: 40 `adbd`, 4 `ArmToArm64Assembler`, 1 `cutils-trace`.
  **Zero `XNU:` records** — the iOS kernel wrote no pstore log lines at all.

For comparison, v62's pstore (also pulled from TWRP) was 16372 bytes, 158
records, 157 of them `XNU:` (SpringBoard/backboardd/IRT/CS telemetry) and no
Android records. SHA256
`2bc2179e27603d997ebe97851b7e0dd7eccdb878c56b8838f211d763004a85e7`.

## Conclusion and correction

The v63 hypothesis (symbolicated `fprintf_stderr`/`write(2)` stall caused by the
serial console) is **not supported**. Removing `serial=3` did not produce a
visible GUI; it removed the console and all log capture.

The source explains why: the console→pmsg mirror in patch
`xnu/patches-minimal/0406-m30-console-pmsg-mirror.patch` is hooked only in
`fbcon_transmit_data()` in `pexpert/arm/pe_serial.c`, and `serial=3` is what
keeps console output enabled on this board (`arm_init.c` clears
`disableConsoleOutput` in the serial branch). Without it there is no console
transmit path, hence no framebuffer text and no `XNU:` pmsg records. The exact
board-specific initial value of `disableConsoleOutput` is inferred from this
behaviour, not read directly.

## Device restoration

After evidence capture, the device was re-identified in TWRP and the known-good
v62 BOOT image was restored (`13:33:23Z..13:33:28Z`, SHA256
`7798b211ebc9773df3225732e572dc18d091d2805cc1f7be72f967fbdd0913c7`). The
device left Download Mode by `13:34:51Z`. No other partition was written.

## Next

Restore `serial=3` (v62 baseline) and diagnose what SpringBoard is writing to
stderr before making another change. Do not disable the console again.
