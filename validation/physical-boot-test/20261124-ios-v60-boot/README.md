# v60 physical boot, first attempt — healthy UI processes, no lock screen seen

Status: **promising but no lock screen observed**. Pstore was captured about
five minutes after resume, while SpringBoard and backboardd were both alive and
no crashes had occurred. It is likely the boot was stopped too early.

## Identity and write gate

TWRP identity verified before Download Mode: `SM-M305F`, `m30lte`, serial
`320081735bb166a3`, bootloader `M305FDDU8CVK1`, `ro.twrp.boot=1`. Download Mode
confirmed. BOOT-only flash of `shim-boot.img`
`c8db86b4526916da532b410b47f299d71787ad7618caa5c077096390c5b318c8`
completed `06:24:03Z..06:24:08Z`; resume `06:24:18Z`. USERDATA/SYSTEM/RECOVERY
untouched, no Fastboot, no BOOT readback.

## Evidence

| File | SHA256 |
|---|---|
| `raw/pmsg-ramoops-0` (16,372 bytes) | `3299f42228ae42958c6b8946feb217d71acfc8e0139215fd782edff115e2097d` |
| `decoded-pmsg.txt` | `e47bbe7806a94a3d0ebae94dbcfd1ad1d557020b3ea30d5d4e5131bfcd1f00cb` |
| `decode-pmsg-report.json` | `6c314812eedae15ae4251682764c04af9b29d7974251c0859857690441cd846e` |
| `decoded-bootlog.txt` | `bac7e7fa9f78bc8bc3148a130f7682533e4d1ae93da66b59bc23e07a6a432438` |

Decode: 144/143 records (decoder reports 144), `clean=False`, ring wrapped.

## Result

- `SMP SpringBoard[27]` and `SMP backboardd[57]` — both UI processes were
  alive at the 90 s sampler point and had multiple threads.
- **Zero** `CRASH`, zero `NSInternal`, zero `state=4`.
- Only 5 `cs_invalid_page` records, all auxiliary daemons: `ReportCrash`,
  `dmd`, `imagent`, `locationd`, `PowerUIAgent`. None are SpringBoard/backboardd.
- Durable counters: `csblk=7787 csfail=9 csvok=60944 cfa=4 cfi=5 cfp=0`.
  Nine fail-closed readback rejections remain, but none hit UI processes in
  this window.
- No `M30 SLOW` line because the capture happened before the first 10-minute
  slow report.

This is materially better than v58, where SpringBoard pid 739 and six
backboardd pids crash-looped. v60 has no such crash loop in the captured five
minutes.

## Verdict

No lock screen was reported. The boot was forced back to recovery at ~5 min,
which may have been before the lock screen appeared. This attempt is treated as
**inconclusive on the lock-screen objective**, not a failure of the CS fix.

Next: reflash the same validated v60 image with a longer observation window
(~12–15 min) to see whether the lock screen appears and to capture the first
`M30 SLOW` durable report.
