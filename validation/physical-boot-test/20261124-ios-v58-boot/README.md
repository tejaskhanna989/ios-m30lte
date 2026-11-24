# v58 physical boot — SpringBoard launched, then crashed; no lock screen

Status: **v58 did not reach a lock screen.** It produced the first direct
physical evidence that SpringBoard actually starts on this boot chain, but it
then aborts and backboardd enter-crashes. The candidate is rejected as a
lock-screen candidate; its evidence is preserved for the next fix.

## Identity and write gate

Identity was verified in TWRP immediately before Download Mode:

- `ro.boot.em.model=SM-M305F`
- `ro.product.device=m30lte`
- serial `320081735bb166a3`
- bootloader `M305FDDU8CVK1`
- `ro.twrp.boot=1`

Heimdall then confirmed Samsung Download Mode. Only BOOT was written:

```text
heimdall flash --BOOT validation/ios-candidate-v58-out/shim-boot.img --no-reboot
```

Image hash `2ef2e3a09cb501fb4b4ed4dd8e888441fe7d5895f29fb6b73397be1d982f783d`
matched the committed candidate. USERDATA, SYSTEM and RECOVERY were untouched;
no Fastboot; no BOOT readback.

## Timing

| Event | UTC |
|---|---|
| Identity verified | `2026-11-23T19:36Z` |
| Download Mode detected | `19:37:29Z` |
| BOOT upload start / end | `19:37:32Z` / `19:37:37Z` |
| Resume attempt (device already auto-booted) | `19:37:46Z` |
| Observation watcher timed out | `~19:58Z` |
| Device returned to TWRP / pstore pulled | `~20:02Z` |

The resume command failed with `Failed to send file part size packet!` because
the device had already left Download Mode, so the flash auto-booted. The boot
was observed by the user as XNU console text; no framebuffer photo was taken.

## Raw evidence

| File | SHA256 |
|---|---|
| `raw/pmsg-ramoops-0` (16,372 bytes) | `7d16f9fd557ae757c2713b03b26bd319cc1a7b5396db9a97c546ab3007ee07d2` |
| `decoded-pmsg.txt` | `04601e72eb6880019ccb5287d0077e96e8f6f7d060923c4a1087095d4bb4cde0` |
| `decode-pmsg-report.json` | `4579a10a9d12204b175a3424765d0417b5a44d6bdb2fd83940e079610d359872` |
| `decoded-bootlog.txt` | `eb406c94fa4ff6e4a66ba5c6443ba779e88fa110f8233cac9de2bd7fdc8a5a46` |

`decode_pmsg.py` decoded 153/153 records over all bytes with `clean=False`:
the ring had wrapped again by the time it was pulled ~25 minutes after resume.
The reduced heartbeat did free the ring for later userspace events, but the
early sampler/IRT records were overwritten.

## Result

The decisive new evidence:

```text
CRASH SpringBoard[739] sig 6 code 0x0 sub 0x0
CRASH SpringBoard pc 0x1cd897198
CRASH SpringBoard reason ns 2 code 0x6: (none)

CODE SIGNING: cs_invalid_page(...): p=752[backboardd] final status 0x22000000, allowing (remove VALID) page
CODE SIGNING: cs_invalid_page(...): p=758[backboardd] ...
CODE SIGNING: cs_invalid_page(...): p=783[SpringBoard] ...
```

- SpringBoard **did launch** (pid 739) — the first direct proof on this chain.
- It then aborted with SIGABRT / uncaught NS exception (`sig 6`, `reason ns 2
  code 0x6`). The assertion text is not in the captured window.
- `backboardd` crash-looped through pids 746, 752, 758, 763, 770, 777. Its
  crash PC `0x1cd897198` is identical to SpringBoard's, so both die in the
  same shared-library abort path.
- There are 36 `cs_invalid_page` records; six are for `backboardd` and one for
  a later `SpringBoard` pid 783, all `0x22000000` (CS_VALID removed).
- `M30 XCTEST: patched ascii ... (total 113)` appears, so the XCTest class-name
  fix-up fired, but that did not prevent the abort.
- No `SMP SpringBoard`/`SMP backboardd` sampler records survived the ring wrap;
  no `M30 IRT`/`csblk` heartbeat survived either. Their absence is not evidence
  they did not run.
- No `NSInternalInconsistencyException` text survived, so the exact NS reason
  is unproven. No lock screen was observed.

## Verdict and next step

v58 is physically rejected for the lock-screen objective. It advanced the
diagnosis substantially: the blocker is no longer “does SpringBoard launch?” —
it launches, then SpringBoard and backboardd abort in a common path, with
continued CS_VALID stripping for both.

The next candidate must:
1. eliminate the remaining fail-closed CS readback rejections that still strip
   CS_VALID from SpringBoard/backboardd (busy peer pages currently cause a
   full-block rejection), and
2. preserve durable per-reason CS failure counters and an early crash-reason
   marker so the next capture can identify the exact NS exception without
   depending on the wrapped 16 KB ring.

No security check may be weakened; the full 16K hash and resident-byte overlay
must remain.
