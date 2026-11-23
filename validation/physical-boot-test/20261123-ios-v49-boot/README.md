# v49 physical boot — IRT worker regressed (early start)

Device: Samsung Galaxy M30 SM-M305F (`m30lte`), serial `320081735bb166a3`,
TWRP recovery. Package: `validation/ios-candidate-v49-out/shim-boot.img`
SHA256 `81b4626da7c3fbc787ef824e8c7d73470e04f5fea5ee60a4ed3d605c9e812c79`.

BOOT-only flash succeeded. No BOOT readback. USERDATA, SYSTEM, and RECOVERY
were not rewritten. The device was returned to TWRP and pstore was pulled.

## Raw evidence

- `raw/pre-pmsg-ramoops-0`: pstore before v49, SHA256
  `ea99ef076996bd636f19516f7a34d815119bbcfd913d3a952e1badffd6679b03`.
- `raw/pmsg-ramoops-0`: v49 pstore, 16,372 B, SHA256
  `fd517375e9dbab5561cb9511808a33b96f6b35b3d32eaf79a348fc28a0370e0e`.
- `decoded-bootlog.txt`: decoded with `tools/m30_bootlog.py inspect`
  (80 records, 1 gap issue).

## Result

The v49 change that starts the IRT worker on the **first dyld-pager fault**
regressed the state machine. The durable status line shows failure before any
symbol work was possible:

```text
M30 IRT status: state=4 off=0x0 err=0 replay=9 comp=-1 ls=0x0 sym=0x0 img=0x0 hits=0 tries=0 sc=0 si=-1 fo=0 vh=0 oh=0 pr=0 mo=0x0 symmap=0x0/0x0@0x0 fb=0x0 basecnt=0 base0=0x0/0x0@0x0
```

There is no `M30 IRT: patched` marker, no `M30 XCTEST: patched` marker, and no
`M30 IRT: retrigger` line. `tries=0`, `hits=0`, `fo=0`, `vh=0`, `oh=0`, and
`err=0` mean the worker never reached the DSC mapping step and recorded no
read error. However the second replay line already shows `comp=0 ls=0x4000`,
so the worker did reach the companion `.symbols` file and read a plausible
local-symbol offset before failing. That is consistent with the v48 note that,
before the XCTEST retrigger, the pager hands the fault path launchd/dyld Mach-O
vnodes rather than the real DSC: the early worker picks the wrong companion /
symbol source and dies before any subcache mapping (`sc=0 si=-1`).

The worker's own 30 x 2 s status replay then consumed the 16 KB pmsg ring, so
the original one-shot diagnostic was wrapped out of the captured window. v50
adds `xctest=<count>` to the durable heartbeat so this evidence survives wrap.

## Interpretation

- Starting the scan earlier is **not** safe in this boot chain. v48's XCTEST
  retrigger gate waited until the allocator and pager were ready; that timing
  must be restored.
- The bitmap-fast-path fix-up change itself is not disproven by this boot: no
  SpringBoardUI assertion appears in the captured window (the capture covered
  only early userspace: `lockdownd`, `nfcd`, `remoted`, `driverkitd`, `timed`,
  `backboardd`), and the status flood may have wrapped any XCTEST markers.
- No `Early boot complete` and no UI/lock-screen evidence. No UI success is
  claimed.

Next correction (v50): restore the `m30_irt_retriggered` worker gate, retain
the bitmap-fast-path fix-ups, shorten the status replay so diagnostics survive,
and inspect the next boot with a full boot window.
