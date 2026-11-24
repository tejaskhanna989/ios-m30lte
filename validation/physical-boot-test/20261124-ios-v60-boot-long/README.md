# v60 long-run physical boot — UI processes alive, no lock screen; console mute bug found

Status: **no lock screen**, but SpringBoard and backboardd remained alive for
the full 14-minute window with no crashes. The likely reason the lock screen
was not visible is a boot-argument name mismatch: the kernel console was never
muted, so kernel text kept being drawn over the UI.

## Identity and write gate

TWRP identity verified: `SM-M305F`, `m30lte`, serial `320081735bb166a3`,
bootloader `M305FDDU8CVK1`, `ro.twrp.boot=1`. Download Mode confirmed. BOOT-only
flash of the same v60 image
`c8db86b4526916da532b410b47f299d71787ad7618caa5c077096390c5b318c8`
at `06:34:45Z..06:34:50Z`; resume `06:34:59Z`. USERDATA/SYSTEM/RECOVERY
untouched, no Fastboot, no BOOT readback.

The capture watcher was killed by a server restart but rearmed; pstore was
pulled at `06:54Z`, ~19 minutes after resume.

## Evidence

| File | SHA256 |
|---|---|
| `raw/pmsg-ramoops-0` (16,372 bytes) | `1f78fb3f8e5111d5d5676a8a1f3a4ea9c8293dea14cae4490c0465db37af21e4` |
| `decoded-pmsg.txt` | `d7f67f920cc41fb91cf31511a7f52a95e7ada186c206589279085ca10bc426b0` |
| `decode-pmsg-report.json` | `e6a9017cafeb19c69472c03e450bbd884eb679faec8cd2aa2984905728b93c6e` |
| `decoded-bootlog.txt` | `a60460ef671a6ced1843fd4ceaf0b2881d0d4b485af80603abe5981226cd9b35` |

Decode: 122 records, `clean=False`.

## Result

- `SMP SpringBoard[27]` and `SMP backboardd[57]` appear in multiple samples
  across the whole window. Both remain alive; there are **zero** `CRASH` records
  and zero `NSInternal` records. No `state=4`.
- Main threads are repeatedly sampled at the same shared-library PC
  `0x1c587d030` / LR `0x1c588eb18` (unslid ~`0x1c2611030` / `0x1c2622b18`),
  suggesting both are waiting in the same libsystem/IPC path. Not yet
  symbolicated; no dyld cache is available locally.
- 12 `cs_invalid_page` records, all auxiliary daemons (`bluetoothd` x3,
  `fairplayd.H2`, `lsd`, `UserEventAgent`, `ReportCrash`, `healthd`, `geod`,
  `callservicesd`, `fmfd`, `identityservices`). None are SpringBoard/backboardd.
- Counter fragment: `csblk=15551 csfail=15 csvok=105904 cfa=8 ...`. Fail-closed
  rejections remain but did not hit UI processes in the captured window.
- **Root cause of invisible UI found:** the payload cmdline contains
  `sweetfb_noconsole=1`, but M30LTE defines `ARM64_BOARD_CONFIG_A5XELTE`, and
  `SweetFramebuffer.cpp` uses `a5fb_noconsole` under that config. Therefore the
  framebuffer console was never muted. The user saw “a lot of logs” — consistent
  with kernel text still being drawn over the GUI, hiding any lock screen.

## Verdict

No lock screen observed. v60's CS fix is holding: SpringBoard and backboardd
survive without crashes for 19 minutes, which is far beyond v58. The next change
is not a security or code-signing change: repackage the same validated v60
kernel with the correct boot argument `a5fb_noconsole=1` (optionally also
`a5fb_keep_on=1`) so the GUI is actually visible, then retest.
