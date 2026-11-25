# v68t persistent Apple logo — read-only root-cause assessment

All data collected read-only from the device in TWRP and from the already
written USERDATA via `tools/hfsplus_ro.py`. No flash, reboot, mount or write.

## Evidence excerpts

pstore (`fa00fa43…`, 174 records, wrapped ring):
- `[043] XNU: M30 UI: sb=27 bb=57 reason=none` — SpringBoard pid 27 and
  backboardd pid 57 were both alive; no termination reason.
- `M30 IRT final: state=2` in early records (002, 003, 005, 018, 019, 028,
  044, 045, 051), then `[058] XNU: M30 IRT: patched _internal_release_type
  off 0xa432d84 (0 -> 3)` and `[089]/[092] M30 IRT: patched (final state=3 …)`.
  The internal-release visibility patch did complete.
- Framebuffer heartbeats progress `sw=0 pr=0 copied=0` -> `sw=3 pr=2
  copied=20217600` (record 136) -> `sw=6 pr=5 copied=50544000 skip=15
  last=1 dirty=0 cl=1` (records 151-173, to v=18600). Presentation was active
  with copied pixels; `cl=1` (client) present.
- `SWEET FB: backboardd sel … -> 0x0` for selectors 74, 12, 79, 6, 27, 17, 84,
  50, 68, 4, 5, 3, 55; `SWEET SURF: backboardd create id 2 1080x2340
  fmt 0x42475241 bpe 4 bpr 4352 planes 0 size 10186752 keys 11 -> 0x0` plus
  selectors 13, 9, 27, 5 and traps 2, 3. backboardd was processing display
  and surface requests without errors.
- 0 `NSException`, 0 `SBERR`/`BBERR` fatal, 0 panic/watchdog.
- 0 `M30 TOUCH`/`Melfas`/probe/heartbeat/packet records survive.
- 72 `SWEET AKS` records (securityd sel 10 -> 0xe00002c7 and similar), but no
  matching crash report.

launchd.log (read-only extract from USERDATA):
- `16:00:14.881 … Successfully spawned SpringBoard[27] because system support`
- `16:00:17.332 (pid/27 [SpringBoard]) created`
- `16:00:27.905 (user/501/com.apple.SpringBoard [27]) job state = running`
- `16:00:17.303 … Successfully spawned backboardd[57] because speculative`
- `16:00:29.016 (user/501/com.apple.backboardd [57]) job state = running`
- No SpringBoard/backboardd exit, crash, or respawn through end of log
  (16:01:15).
- Warnings only: `failed lookup: name = com.apple.oscard … requestor =
  backboardd[57]`, and known-removed commcenter/wifi/baseband services.

mobileactivationd.log:
- `hardware_model: samsung,m30lte`, `product_type: iPhone10,3`,
  `has_baseband: false`, `should_hactivate: true`,
  `dealwith_activation: Activation State: Activated`.

Preferences:
- purplebuddy: `SetupDone=True`, `SetupFinishedAllSteps=True`,
  `SetupVersion=11`, `daemonizeNeedsToRun=False`.
- migration: `LastSystemVersion=20H392`, `SyntheticDidUpgrade=False`.
- springboard: `BKNoWatchdogs=True`,
  `FBLaunchWatchdogExceptions={'com.apple.purplebuddy': 100.0}`,
  `MCForceShowCloudConfigurationUI=False`.

Crash reports: 0 `.ips` files under USERDATA CrashReporter.

## Findings by question

1. SpringBoard: alive (pid 27, job state running), no assertion failure,
   crash, blocked-thread evidence or exit in surviving logs. No positive
   evidence that a lock-screen scene/interface was constructed.
2. Backboardd: alive (pid 57, job state running), processing FB and IOSurface
   selectors successfully, creating a 1080x2340 surface, presenting frames.
   Only non-fatal warning is a failed lookup of `com.apple.oscard`.
3. Launchd: SpringBoard and backboardd started and stayed running. Failed XPC
   lookups are for knowingly removed baseband/wifi/commcenter services, plus
   `com.apple.oscard`; none is proven to gate the lock screen. No service
   restart loop for the UI processes.
4. Display: not a static boot framebuffer. Framebuffer heartbeats show active
   swaps/presents with copied pixels and a client attached (`cl=1`). The
   Apple logo remains the visible content because userspace has not drawn a
   lock-screen scene over it — or SpringBoard is waiting before doing so.
5. Melfas: cmdline has `m30touch=1 m30touchhid=1`; no M30 TOUCH record
   survives. Cannot distinguish "probe never ran" from "early records wrapped
   out of pstore". No evidence the driver affected SpringBoard; no HID client
   records to prove dispatch.
6. Earliest proven stop: after `M30 UI sb=27 bb=57 reason=none`, IRT state=3,
   and backboardd surface creation/presentation; before any lock-screen scene
   construction evidence. No fatal event marks the stop.

## Root-cause assessment

The container-path NSException that killed v71/v72 userspace is gone. The
failure is not a kernel panic, not a framebuffer failure, and not a detected
SpringBoard/backboardd crash. The most probable failure class is a userspace
UI-initialization stall: SpringBoard is alive but has not created/presented a
lock-screen scene; backboardd is presenting whatever layer stack exists. The
specific blocking dependency is **not established** by surviving evidence.
The `SWEET AKS` errors and `com.apple.oscard` lookup failure are the only
positive anomalies, but neither is proven causal.

Confidence: high that the stop is in userspace UI construction after
SpringBoard/backboardd are running; low on the exact cause.

## Smallest proposed source-only fix

No functional source fix is justified by this evidence. The smallest
responsible source-only change is **diagnostic**: add a durable kernel tag
(e.g. `M30 UI: heartbeat sb=<pid> bb=<pid> irt=<state> hidclients=<n>`) emitted
once per second from the existing debug hook, so the next boot can show
whether SpringBoard scene creation or HID client registration is the point of
stall. Do not change AMFI, code signing, SpringBoard binaries, framebuffer,
IRT behavior, or the Melfas driver until that evidence exists.
