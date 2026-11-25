# v68t XNU boot-path verification (evidence-based, read-only)

This documents which boot stages are *proven* by evidence and which are not.
The Apple logo alone is not treated as proof of any stage.

## Proven stages and evidence

| Stage | Evidence | Confidence |
|---|---|---|
| Samsung/Exynos 7904 handoff -> XNU entry | v68 accepted physical lock-screen boot plus v68t handoff verifier 30/30 (shim entry `0x80080000`, ADT PA `0x82454000`, boot-args PA `0x82458000`); same shim/ADT bytes in v68t candidate | High (structural + prior physical) |
| Kernel entry / early print | pstore `M30 IRT` and `M30 FB` tags are emitted by XNU after entry | High |
| CPU / interrupt init | CI `verify_m30_kernel.py` 6/6: M30 framebuffer base, relocated markers, eMMC/ALIVE constants, GICv2 MMIO init/EOI, virtual-timer ownership; no LSE CI gate PASS | High (static/linked) |
| Memory / platform init | CI handoff 30/30, platform verifier 9/9 (`samsung,m30lte`, `m30lte,display`, `arm,cortex-a53`), ADT DRAM base/size checks | High (static/linked) |
| Device-tree/platform matching | linked kernel `SweetPlatformExpert` name match `samsung,m30lte`; AppleCLCD `m30lte,display` | High (static) |
| IOKit startup | pstore `M30 IRT: patched (final state=3 …)`, `SWEET FB`, `SWEET SURF`, `M30 UI: sb=27 bb=57 reason=none` | High |
| Root filesystem mount | `launchd.log` read from USERDATA records SpringBoard/backboardd spawned and running; v68 fail-closed root-mount panic string absent from pstore | High (indirect but strong) |
| launchd handoff | launchd.log `16:00:14.881 Successfully spawned SpringBoard[27]`, `16:00:17.303 Successfully spawned backboardd[57]`, both `job state = running` | High |

## Stages NOT proven by current evidence
- Exact runtime register-level GICv2/timer initialization sequence (only linked-binary verification).
- Any SpringBoard lock-screen scene construction or presentation.
- Melfas I2C probe / IRQ line / contact delivery (no surviving `M30 TOUCH` record).

## Earliest missing transition
The last proven stage is: SpringBoard and backboardd running, IRT state 3,
backboardd creating a 1080x2340 surface and presenting frames. The earliest
missing transition is **SpringBoard lock-screen scene construction/presentation**.
Its dependencies that are already satisfied: activation `Activated`, SetupDone
true, migration synthetic, IRT state 3, display surface created. No further
dependency can be confirmed from surviving logs; adding invasive instrumentation
is not justified.

## Diagnostic-only next step
Patch `0453` adds a boot-arg-gated (`m30uihb=1`) 1 Hz heartbeat reporting
SpringBoard/backboardd PIDs, last crash reason, and IRT state. HID client count,
scene construction, and surface identity remain `unknown` because no safe
existing API exposes them in v68. No SpringBoard/framework patch is added.
