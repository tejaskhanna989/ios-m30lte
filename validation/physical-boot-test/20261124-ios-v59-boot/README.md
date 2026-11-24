# v59 physical boot — late capture, inconclusive

Status: **inconclusive**. No lock screen was reported, but the only pstore
capture happened roughly four hours after boot, so the 16 KB ring was again
overwritten. This run neither confirms nor refutes the busy-peer CS fix.

## Identity and write gate

Verified in TWRP before Download Mode: `SM-M305F`, `m30lte`, serial
`320081735bb166a3`, bootloader `M305FDDU8CVK1`, `ro.twrp.boot=1`. Download Mode
confirmed with `heimdall detect`.

BOOT-only flash of `shim-boot.img` SHA256
`9890079d8d801aef5639d79a0eba5e8cb468c4ab735dec17eb2a1092eda1b421`
completed `00:34:44Z..00:34:49Z`. USERDATA/SYSTEM/RECOVERY untouched, no
Fastboot, no BOOT readback. Resume succeeded at `00:34:59Z`.

## Capture problem

The requested 3-minute early recovery capture was missed. The device did not
return to recovery and later had to be reconnected; pstore was finally pulled
at `04:50Z`, about four hours after resume. The ring contains only late daemon
noise.

## Evidence

| File | SHA256 |
|---|---|
| `raw/pmsg-ramoops-0` (16,372 bytes) | `8f2e5b306d07863000c29e5e43c8b3f54307ce991a4cb1c020e343a805a2d32d` |
| `decoded-pmsg.txt` | `8b7d62c4c44f8ebd1304f16255d68bfd39208a837fd6d8ebcff25ffa97513bd5` |
| `decode-pmsg-report.json` | `35cbcf58012e618c30638610b3ae12653d68810421b2ad4a9cddb16eb745f8f5` |
| `decoded-bootlog.txt` | `6091a3ad5509a4faca882e0af845f50285acc949fd05633678d2510055b1f226` |

`decode_pmsg.py` decoded 139/139 records over all bytes with `clean=False`.

Surviving markers:

- 50 `cs_invalid_page` records: `fairplayd.H2` (27), `bluetoothd` (17),
  `xpcproxy` (5), `fseventsd` (1). This is continued CS_VALID stripping in
  auxiliary daemons.
- **Zero** occurrences of `SpringBoard`, `backboardd`, `M30 IRT`, `csblk=`,
  `cfa=`, `cfi=`, `cfp=`, `SMP `, `CRASH`, `NSInternal`, `state=4`, or
  `Early boot complete` in the captured window.
- Those absences are explained by ring wrap and are **not** evidence that the
  processes or counters were absent during boot.

## Verdict

No lock screen observed. v59 cannot be scored from this capture: the early
window that would show the NS exception reason and the new fail-reason counters
was lost. The candidate is neither accepted nor rejected on CS grounds.

Next step must remove the dependence on perfect user timing: keep a very slow
(≈10 min interval) durable IRT/CS report in the pmsg ring and a replay of the
last SpringBoard/backboardd crash reason, so any later recovery pull contains
the decisive state. No security weakening.
