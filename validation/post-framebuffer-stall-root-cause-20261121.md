# Post-framebuffer stall root cause (2026-11-21, offline, MAIN only)

## Evidence basis

`validation/physical-boot-test/20261121-ios-v8-flash/pmsg-postboot.bin`:
89 records, 0 decode issues; 68 tagged `XNU`. This is the first genuine XNU
log recovered from the device via the repaired 0406 mirror. Last XNU record:

```
[088] XNU: A5XELTE FB: requested 30 Hz, effective 30 Hz, copy timing on
```

No `M30 ROOT:`, no `A5XELTE eMMC:`, no `BSD root:`, no panic text.

## Exact execution path and where it stops

`kernel_bootstrap_thread()` (osfmk/kern/startup.c):

```
PE_init_iokit()             -> [072] iBoot version, [073-074] DT matching
mac_policy_initmach/vnguard -> [075][076]
load_static_trust_cache()   -> [077] trust caches unavailable
OSKextRemoveKextBootstrap() -> [078] keepsyms ...
machine_lockdown()          -> (no log)
kernel_do_post()            -> [079] "No POST boot-arg set."
PE_lockdown_iokit()         -> StartIOKitMatching()
                                config thread -> [080-088] PE/AKS/WDT/SURF/
                                HID/touch/AppleCLCD/30 Hz
vm_set_restrictions()       -> (no log)
kperf_init_early()          -> *** BLOCKS HERE ***
bsd_init()                  -> never reached (no copyright, no bsd_autoconf)
```

## Concrete cause

`osfmk/kperf/kperf.c:83` `kperf_init_early()` calls `ml_wait_max_cpus()`
unconditionally (`#if KPERF`, which is enabled in this config) immediately
before `bsd_init()`. On arm:

```c
unsigned int ml_wait_max_cpus(void) {
    assert(lockdown_done);
    lck_mtx_lock(&max_cpus_lock);
    while (max_cpus_initialized != MAX_CPUS_SET) {
        max_cpus_initialized = MAX_CPUS_WAIT;
        lck_mtx_sleep(&max_cpus_lock, ..., &max_cpus_initialized, THREAD_UNINT);
    }
    ...
}
```

`max_cpus_initialized` is set to `MAX_CPUS_SET` **only** by
`ml_set_max_cpus()`. Its only callers are `IOCPU.cpp:580`,
`AppleARMSMP.cpp:170`, and `SweetCPU.cpp:193`. On this M30LTE build the CPU
driver is `SweetCPU` (config-table `IONameMatch='arm,cortex-a53'`), and its
`startAll()` — which logs `A5XELTE CPU: ...` before calling
`ml_set_max_cpus()` — **never appears in the recovered log**. No SWEET CPU
records appeared in any earlier build either. Thus `max_cpus_initialized`
stays 0 and `ml_wait_max_cpus()` sleeps forever with `THREAD_UNINT`.

The IOKit config thread keeps running independently, which is why the framebuffer
and IOKit registration logs continue to the 30 Hz line while the bootstrap
thread is parked. `machine_info.max_cpus` is already valid: `machine_conf()`
sets it from `ml_get_topology_info()->max_cpu_id + 1` before kernel bootstrap
(`machine_routines.c:486`), and `vm_set_restrictions(machine_info.max_cpus)`
already ran successfully just before `kperf_init_early()`.

**This single wait is the smallest concrete source-level cause** of the stall
before BSD initialization. It is unrelated to the root filesystem: no
`IOFindBSDRoot()` call ever occurred.

## Fix (patch 0408)

`xnu/patches-minimal/0408-m30-ml-wait-max-cpus.patch`: in
`osfmk/arm/machine_routines_common.c`, under
`ARM64_BOARD_CONFIG_M30LTE`, return `machine_info.max_cpus` directly from
`ml_wait_max_cpus()` instead of waiting on a flag that is never set. Non-M30LTE
arm64 keeps the original lock/sleep path. Adds
`<pexpert/arm64/board_config.h>` (already used by `machine_routines_apple.c`).

Verified by `tools/test_ml_wait_fix.py`: M30LTE model returns with
`lock_calls=0 sleep_calls=0`; non-M30LTE still takes the lock/sleep path.

## Not changed

- genuine iOS target, `maxmem=292`, ramoops reservation, proven shim;
- 0406 pmsg mirror, 0407 root markers;
- no root/filesystem changes, no userspace claims.

## Remaining blockers

- After this fix, `bsd_init()` should run; whether `IOFindBSDRoot()` and the
  eMMC path actually work is still unproven and needs an authorized test.
- No genuine iOS root filesystem exists, so mounting/Userspace cannot be claimed.
