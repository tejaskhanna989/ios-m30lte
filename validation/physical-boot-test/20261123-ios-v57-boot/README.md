# v57 physical boot — Apple logo observed, pstore capture pending

Status: **partial evidence**. The BOOT-only write and resume completed, and the
user observed an **Apple logo** on the device. The device has not yet been
returned to TWRP, so pstore/pmsg has not been pulled or decoded. No final
success claim is made until that log evidence is preserved and analyzed.

## Identity and write gate

Before Download Mode, the device was positively identified in TWRP as:

- model `SM-M305F` (`ro.boot.em.model`)
- device `m30lte` (`ro.product.device`)
- bootloader `M305FDDU8CVK1`
- TWRP `ro.twrp.boot=1`

Samsung Download Mode was then confirmed with `heimdall detect` →
`Device detected` immediately before the write.

Only BOOT was written, using:

```text
heimdall flash --BOOT validation/ios-candidate-v57-out/shim-boot.img --no-reboot
```

`shim-boot.img` SHA256 `0b85cc7666a45c761abf29002f42b5f24b395f9d7386112e5ade8748b2fcca31`
matched the committed v57 candidate. No BOOT readback. USERDATA, SYSTEM and
RECOVERY were not touched. No Fastboot was used.

## Timing

| Event | UTC |
|---|---|
| Identity check start/end | `2026-11-23T18:06:30Z` |
| Download Mode entered / detected | `18:06:42Z` / `18:06:49Z` |
| BOOT upload start / end | `18:06:56Z` / `18:07:01Z` |
| Resume (`heimdall print-pit --resume`) | `18:07:23Z` |
| 180 s observation end | `18:10:38Z` |

The resume used the correct `print-pit --resume` form and reported
`Rebooting device...`.

## Observed result

The user reports:

- console text continued after resume;
- “booting system started” appeared;
- a large amount of text scrolled;
- an **Apple logo** was displayed and remained visible.

This is the first visible iOS UI milestone observed in this bring-up. It is
materially beyond v55, which stopped after `load_init_program` with no further
console output and no Apple logo. It is still being recorded as a user
observation until pstore confirms the internal state.

## Why pstore is still pending

At `18:10:38Z` the device was not back in ADB recovery. Multiple watcher jobs
waited for recovery ADB but it did not reappear; the device remained booted and
was also not in Download Mode. Pulling `/sys/fs/pstore/pmsg-ramoops-0` requires
recovery, so the physical key method used for v54/v55 is needed. A watcher is
armed to capture and hash pstore automatically as soon as recovery ADB returns.

## Raw evidence so far

Hashes are in `raw/SHA256SUMS.partial`. Key files:

| File | SHA256 |
|---|---|
| `raw/boot-image-sha256.txt` | `23c1d36f2ba469402a2d13258f4b6539201436d42e62e15831ca0363543ca463` |
| `raw/heimdall-flash.log` | `4bf2478fcc951372568ebaba583f3bf005df3bedf67a5f85337ccc1d817d2a4c` |
| `raw/heimdall-resume.log` | `976bfbc1f24490c104e56b66df50dea00a09959115d921fb0e38b39e77f07b4a` |
| `raw/observation-full-end.txt` | `a27064651b6496d050c0886a3f468ef537b04c14800f71d0d17388b98fb14418` |

## Next

1. Force the device back to TWRP with the established hardware-key method.
2. Let the armed watcher pull `/sys/fs/pstore/pmsg-ramoops-0` and hash all raw files.
3. Decode with `tools/decode_pmsg.py` and `tools/m30_bootlog.py inspect`.
4. Analyze for `M30 CS diag 5`, `M30 CS diag 0/1/2`, `csblk`/`csfail`/`csvok`
   in the IRT heartbeat, progress past `load_init_program`,
   `Early boot complete`, SpringBoard/UI assertions, and compare with
   v45/v52/v54/v50/v55.
5. Only then record the final physical verdict. No lock-screen claim is made
   from the Apple logo alone.
