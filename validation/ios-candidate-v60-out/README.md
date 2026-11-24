# iOS candidate v60 — v59 CS fix with durable result reporting

Baseline: v59 (`5e9a8169`). v60 source: `f561e630`. MAIN only.

## Why

v59 changed the CS readback so busy/cleaning peer pages are overlaid from real
physical bytes instead of rejecting the whole 16K block. Its physical test was
inconclusive because pstore was pulled ~4 hours after boot and the 16 KB ring
contained only auxiliary-daemon noise.

v60 keeps that fix and adds durable telemetry so the result is visible in any
later recovery pull:

- `M30 SLOW:` line every 10 minutes with IRT state, `csblk/csfail/csvok` and
  `cfa/cfi/cfp` fail-reason counters. At ~6 records/hour this stays near the
  pmsg ring tail.
- The first UI NS-exception reason from the heap scanner is saved and replayed
  as `reason=...` in that slow line.

No signature/hash/AMFI/trust-cache/page-validation change. No 0417, no OSX
target, no branch/settings change.

## CI and hashes

CI `45334020730` GREEN for source `f561e630`, `XNU_TARGET=iphoneos`, M30LTE,
DEVELOPMENT. Log applied 0435-0439; iOS target passed; LSE count 0.

| File | SHA256 |
|---|---|
| buildtree `osfmk/vm/vm_fault.c` | `cb010af81d89fa10ddf9d7aa03579225bd2860fb001de309c815ecfaf650551d` |
| buildtree `osfmk/kern/exception.c` | `335dba8e00448a9e4e06480cc3b4dfb4a5f4521c1b0cbb1610dffbd89f87668b` |
| linked kernel | `a24d220685d42b51a1ac8f74c9256480fd81fe1103195fc99c2da1f4b79c7637` |
| payload | `3fd1b3d5486285b35eb3bce1cd29d42bae832c690aac4a067729ff15a2c04cdf` |
| `shim-boot.img` (BOOT candidate) | `c8db86b4526916da532b410b47f299d71787ad7618caa5c077096390c5b318c8` |
| `ios-boot.img` | `e72af1646e57c80c11afbfe2184b13215c2447a9d67d16ec5b5277be39345945` |

Cmdline, ADT, shim and layout unchanged from v59.

## Validation

Buildtree PASS, kernel 6 checks PASS, platform 9/9 PASS, packaging PASS, handoff
22/22 PASS, all applicable focused tests PASS. No QEMU claim.

## Physical step

BOOT-only Heimdall flash after identity/Download Mode gate. Recovery timing is
no longer critical because of the slow durable report, but capture pstore as
soon as convenient. Accept only a visible, persistent lock screen on the M30
with supporting logs; Apple logo, IRT state, or a short-lived process is not
enough.
