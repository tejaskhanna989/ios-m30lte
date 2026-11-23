# v55 physical boot — early regression: no IRT heartbeat, no launchd progress

Device: Samsung Galaxy M30 SM-M305F (`m30lte`), serial `320081735bb166a3`,
TWRP `3.4.03.0.0`, bootloader `M305FDDU8CVK1`, `ro.twrp.boot=1`. Identity was
positively re-confirmed in TWRP immediately before Download Mode, and Heimdall
confirmed Samsung Download Mode immediately before the write.

Package: `validation/ios-candidate-v55-out/shim-boot.img` SHA256
`e58de8b007ad1d9149d5161fb3ba2b7aef698c7177130257a8463e230ca0550b`, matching
the committed candidate. Only BOOT was written with
`heimdall flash --BOOT ... --no-reboot`; USERDATA, SYSTEM and RECOVERY were not
touched. No Fastboot and no BOOT readback.

## Timing

| Event | UTC |
|---|---|
| BOOT upload start | `2026-11-23T17:17:38Z` |
| BOOT upload end | `2026-11-23T17:17:43Z` |
| Resume attempt / boot window start | `2026-11-23T17:17:53Z` |
| Full 180 s observation end | `2026-11-23T17:21:00Z` |
| Recovery ADB available / pstore pull | after `17:21Z` |

The first resume command used the invalid standalone form `heimdall --resume`,
so it printed usage and wrote nothing. A corrected `heimdall print-pit --resume`
then reported that the device had already left Download Mode: the flash had
booted automatically. The 180 s window was timed from the first resume attempt.
The device later reappeared in TWRP ADB and pstore was pulled immediately.

## Raw evidence

| File | SHA256 |
|---|---|
| `raw/pmsg-ramoops-0` (12,402 bytes) | `a0897bebe812f89006b0dfaba4c4484d0bdb96c3f9a0ef720ec5c193323fdbef` |
| `decoded-pmsg.txt` | `4a34cba38106ad0260a09bef7c48ac90a724a906fbe28667ccbd1e4f494a82d8` |
| `decode-pmsg-report.json` | `581633edf507e13ae59174cd042596e3e52aecfded55f949ff605222cdc4627d` |
| `decoded-bootlog.txt` | `0245d9bd34c4a81d59fe40b6f8fd10cfec49a79e1c96a2bd3710c19a0d4dc7e2` |

`tools/decode_pmsg.py` decoded **154/154 records, 12,402/12,402 bytes consumed,
clean=true, zero issues**. Unlike v54 (16,372 bytes, 87 records, 4 wrap/gap
issues, stream starting mid-message), this is a complete, un-wrapped early-boot
capture. It starts with recovery `adbd` records before XNU and then follows XNU
from kernel startup through root mount and `load_init_program`.

## Result

The boot reached:

```text
M30 ROOT: IOFindBSDRoot entered
SWEET FB: AppleCLCD 1080x2340 ...
M30 ROOT: waitForMatchingService(IOBSD) returned service
M30 ROOT: A5XELTE keys/emmc stage ... done
/dev/emmcroot0 ready, GPT USERDATA writable
BSD root: emmcroot0, major 1, minor 0
hfs: mounted iOSRoot on device b(1, 0)
load_init_program: attempting to load /usr/appleinternal/sbin/launchd.development
load_init_program: attempting to load /sbin/launchd
```

After that, the only XNU records are `SWEET HID` / key-down-up events from the
hardware keys used to force the device back to recovery. There are **no**
records containing:

- `M30 IRT` (neither `patched` nor `final` nor diagnostic markers);
- `csblk`, `csfail`, `csvok`, or `M30 CS diag`;
- `CODE SIGNING` or `cs_invalid_page`;
- `SpringBoard`, `NSInternalInconsistencyException`, or `CRASH`;
- `Early boot complete`.

A case-insensitive combined grep for all of those terms returned **0 matches**.

## Comparison with baselines

- v45: reached `Early boot complete` and showed many `cs_invalid_page` records,
  including record `[177]` for `SpringBoard` with final status `0x22000000`.
- v52: SpringBoardUI assertion appeared before the IRT patch marker; IRT still
  reached durable `state=3`.
- v54: durable IRT `state=3` heartbeat replayed across the wrapped ring; 75
  full status lines, no terminal `state=4`.
- v55: no IRT heartbeat at all, and no launchd progress after
  `load_init_program`. This is an **early regression**, not a CS fix.

The clean capture is decisive for the negative result: the absence of IRT and
CS counters is not explained by ring wrap. v55 did not reach the stage where
the v54/v52 baselines produced their durable markers.

## Likely cause and next candidate

The v55 patch allocates its 16K readback buffer with
`kalloc_data(CS_16K_BLOCK_SIZE, Z_WAITOK)` at `vm_fault.c:8981` **while the VM
object lock is still held**. `Z_WAITOK` may sleep; the surrounding v54 code
deliberately used `Z_NOWAIT` with the comment “non-blocking: do not sleep while
holding the object lock”. A sleeping allocation under the object lock is a
credible cause of the first-fault hang before launchd starts.

This is a code-supported hypothesis, not yet proven by a panic. The next
candidate (v56) will change that allocation to `Z_NOWAIT`, fail closed if
allocation fails, and verify the pager is unchanged after dropping/reacquiring
the object lock. No validation, signature, hash, AMFI, trust-cache or page
validation check is to be weakened.

## Status

v55 is physically rejected. No UI/lock-screen milestone is claimed. BOOT-only
flash succeeded; the kernel did not reach a usable userspace milestone.
USERDATA/SYSTEM/RECOVERY untouched. Next step is build/test v56, not another
v55 flash.
