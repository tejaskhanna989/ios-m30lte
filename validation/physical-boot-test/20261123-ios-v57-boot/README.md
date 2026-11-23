# v57 physical boot — CS fix validated; Apple logo reached

Status: **physically accepted for the 16K code-signing fix and visible Apple
logo UI milestone**. This is not a lock-screen/home-screen claim. The device
was returned to TWRP, pstore was captured and decoded, and the IRT heartbeat
proves the v57 readback path ran successfully at scale.

## Identity and write gate

Before Download Mode the device was positively identified in TWRP as
`SM-M305F` / `m30lte`, bootloader `M305FDDU8CVK1`, `ro.twrp.boot=1`. Samsung
Download Mode was confirmed with `heimdall detect` → `Device detected`
immediately before the write.

Only BOOT was written:

```text
heimdall flash --BOOT validation/ios-candidate-v57-out/shim-boot.img --no-reboot
```

`shim-boot.img` SHA256
`0b85cc7666a45c761abf29002f42b5f24b395f9d7386112e5ade8748b2fcca31`
matched the committed v57 candidate. USERDATA, SYSTEM and RECOVERY were not
touched. No Fastboot, no BOOT readback.

## Timing

| Event | UTC |
|---|---|
| Identity check | `2026-11-23T18:06:30Z` |
| Download Mode entered / detected | `18:06:42Z` / `18:06:49Z` |
| BOOT upload start / end | `18:06:56Z` / `18:07:01Z` |
| Resume (`heimdall print-pit --resume`) | `18:07:23Z` |
| 180 s observation end | `18:10:38Z` |
| Recovery returned / pstore pulled | later; `raw/recovery-returned.txt` |

## Raw evidence

| File | SHA256 |
|---|---|
| `raw/pmsg-ramoops-0` (16,372 bytes) | `8c17a9ed26c055a5a02cbf1f5643009327aa8876bf8e5c7c3c34ca7b1faee969` |
| `decoded-pmsg.txt` | `c68cf9de63e0ee5a9d873c572ccb4aa7bd4cb86715b10921d149814afc1e7eec` |
| `decode-pmsg-report.json` | `b0a5d8ffb8b0f29bb498d0beadea74b8de1e0c255fe75c6910ebdf4022780339` |
| `decoded-bootlog.txt` | `b6f780dcc4782731e98ea51b5623b1a7b58e576d13cfb571123e7d56831b4ea2` |
| `analysis.txt` | see `raw/SHA256SUMS` |

`tools/decode_pmsg.py` decoded 166 records from all 16,372 bytes but reported
`clean=False` with `bad_magic` issues: the 16 KB ring had wrapped during the
long userspace boot. This is expected and is exactly why the IRT heartbeat
replays the one-shot CS counters. `tools/m30_bootlog.py inspect` produced
`decoded-bootlog.txt`.

## Physical result

User observation during the boot window:

- console text continued after resume;
- “booting system started” appeared;
- an **Apple logo** was displayed and remained visible.

Pstore confirms deep userspace progress and a healthy CS validation path:

```text
M30 IRT: patched (final state=3 ... hb=179 xctest=1 xctchunk=0
          csblk=30025 csfail=12 csvok=192519)
```

That is the final replayed heartbeat in the captured ring. Earlier heartbeats
show the same stable pattern, e.g. `csblk=27905 csfail=12 csvok=178243` through
`csblk=30025 csfail=12 csvok=192519`. Interpretation:

- `csblk=30025` — 30,025 attempted 16K block readbacks;
- `csvok=192519` — 192,519 successful full-block validations;
- `csfail=12` — only 12 fail-closed rejections (allocation/read/pager/busy peer),
  never a false validation;
- IRT `final state=3` — patch succeeded, no terminal `state=4`;
- no `SpringBoard`, `NSInternalInconsistencyException`, or SpringBoard
  `cs_invalid_page` record anywhere in the captured window;
- no `M30 CS diag 0/1/2/3/4/5` records — those are one-shot and were overwritten
  by the ring wrap, but their counters survive in the heartbeat.

The remaining `CODE SIGNING: cs_invalid_page ... (remove VALID)` records (19)
are for auxiliary daemons such as `fairplayd.H2`, `xpcproxy`, `bluetoothd`,
`searchpartyd`, `fmfd`, `networkserviceproxy`, `webbookmarksd` and
`usermanagerd`, **not** SpringBoard. There are also 8 `CRASH` records for
`coreduetd` and `fmfd`. These are residual userspace issues and do not block
the Apple logo / UI milestone.

## Comparison

| Candidate | Result |
|---|---|
| v45 | `SpringBoard` `cs_invalid_page` with status `0x22000000` after `Early boot complete` |
| v52 | SpringBoardUI assertion before IRT patch marker |
| v54 | IRT `state=3`, no CS counters, no visible UI |
| v55 | No IRT/CS telemetry; stopped after `load_init_program`; no UI |
| v57 | IRT `state=3`, `csblk=30025 csfail=12 csvok=192519`; deep userspace; **Apple logo visible** |

## Verdict

The v57 busy-page-safe 16K readback fixes the v55 early hang and the CS_VALID
loss that previously blocked SpringBoard UI. The visible Apple logo is the
first verified visible iOS UI milestone on the M30. The fix fails closed on
allocation failure, short reads, busy peer pages and pager changes; all
signature/hash/AMFI/trust-cache/page-validation checks remain enabled.

Not claimed: lock screen, home screen, fully usable iOS, or absence of all
daemon crashes. Residual daemon crashes and auxiliary `cs_invalid_page` records
remain for later investigation. USERDATA/SYSTEM/RECOVERY untouched.
