# iOS candidate v62 — compact UI liveness telemetry

Baseline: v61 (`24ea91af`). v62 source: `b667f247`. MAIN only.

## Why

v61 still showed no lock screen even after 13 minutes. Backboardd was actively
rendering surfaces, but the 16 KB pstore ring wrapped before SpringBoard's
final state could be seen. v62 does not change CS/AMFI/security; it adds a
compact `M30 UI: sb=<pid> bb=<pid> reason=<string>` line every 30 seconds, and
moves full backtraces to every fourth tick (2 minutes) so they stop erasing the
ring. This will tell whether SpringBoard is alive and whether any NS exception
reason was captured, enabling the targeted final fix.

## CI and hashes

CI `45356410574` GREEN for source `b667f247`, `XNU_TARGET=iphoneos`, M30LTE,
DEVELOPMENT; patch `0440-m30-compact-ui-state.patch` applied; LSE count 0.

| File | SHA256 |
|---|---|
| buildtree `bsd/dev/sweet_sample.c` | `c7e92cc467a5c0fe062d8f4cd77dbe99c10a3909a4287dcd78c517963489fcf0` |
| linked kernel | `45aff1b01f85b1dbe5a77903050005333eb858980cd1118465c3f11f02bda13d` |
| payload | `e1c41dd83ee70cafc7af9ab91c8c20ed5320ee54a87392434790870d99d39bd0` |
| `shim-boot.img` (BOOT candidate) | `7798b211ebc9773df3225732e572dc18d091d2805cc1f7be72f967fbdd0913c7` |
| `ios-boot.img` | `9809ba2fa7b001ae100eb6725cd7b2fd2d34f13b931e3e57137d8c03adfd58be` |

Cmdline unchanged from v61: `cpus=6`, `a5fb_noconsole=1`, `a5fb_keep_on=1`.

## Validation

Buildtree PASS, kernel 6 checks PASS, platform 9/9 PASS, packaging PASS, handoff
23/23 PASS, all applicable focused tests PASS. No QEMU claim.

## Physical step

BOOT-only flash after identity/Download Mode gate. Pull pstore whenever
convenient; the compact line repeats every 30 s. No lock-screen claim without a
visible persistent render plus logs.
