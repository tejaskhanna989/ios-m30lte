# Touch message investigation + next blocker analysis (2026-11-20, offline, MAIN only)

## 0. Evidence discipline

- The ONLY preserved screen transcription is from the **v5** boot (`NOTES.md:585-602`).
  It ends at `SWEET FB: AppleCLCD ...` / `A5XELTE FB: requested 30 Hz ... copy timing on`.
  There is **no recorded v6 screen transcription** in the repo.
- The user asserts a touch-related message also appeared in v6. I accept this as a user
  observation but there is no verbatim v6 text on record, so no exact message is claimed
  as observed below. Section 1 identifies what the source can and cannot produce.

## 1. Search result: no Apple-prefixed touch IOLog exists

Exhaustive search of `xnu/patches-minimal/*.patch`, the full CI buildtree
(`milestone_artifacts/ci_44579283250/buildtree/xnu/xnu`), and the linked kernel
(`mach.development.m30lte` strings) found **no** `IOLog("Apple...")` call and
**no** Apple-prefixed touch/log string. Touch-related log strings in the kernel:

| String | Prefix | Source |
|---|---|---|
| `SWEET HID: touch registered` | SWEET HID | `SweetHID.cpp:457` |
| `SWEET HID: touch %d %s at %d,%d%s` | SWEET HID | `SweetHID.cpp` |
| `SWEET HID: buttons registered (test every %u s)` | SWEET HID | `SweetHID.cpp:395` |
| `SWEET FB: AppleCLCD %ux%u ... presented as %ux%u` | SWEET FB (contains "AppleCLCD") | `SweetFramebuffer.cpp:260` |
| `"AAPL,phandle" not a kext` | AAPL (device-tree property, not touch) | IOKit DT matching |

**Conclusion:** the only touch initialization message in the binary is
`SWEET HID: touch registered` (not Apple-prefixed). The only Apple-prefixed line in
this boot region is the framebuffer message `SWEET FB: AppleCLCD ...`. If the user saw
an "Apple ..." line near touch, it is most plausibly `SWEET FB: AppleCLCD ...`
(a display message) or a conflation of it with `SWEET HID: touch registered`.

## 2. Exact driver/service responsible

`SweetHIDTouch` — a **pure-software IOKit HID event service** (subclass of
`IOHIDEventService`) that publishes digitizer events. `SweetHIDTouch::start()` at
`iokit/Kernel/arm/hid/SweetHID.cpp:429-458` allocates a lock, calls
`IOHIDEventService::start()`, sets digitizer properties, calls `registerService()`,
then logs `SWEET HID: touch registered` (line 457).

Matched via `IOResources` with `IOMatchCategory = SweetHIDTouch`
(`iokit/KernelConfigTables.cpp:92-97`). It touches **no hardware**.

Important distinction: the **raw hardware touch driver** `a5xelte_touch_probe()`
(Exynos touch IC) is compiled in but **gated OFF for M30LTE** in `IOKitBSDInit.cpp:776-778`:
```
a5xelte_keys_init();
#if !defined(ARM64_BOARD_CONFIG_M30LTE)
a5xelte_touch_probe();
#endif
```
(The build defines both `ARM64_BOARD_CONFIG_A5XELTE` and `ARM64_BOARD_CONFIG_M30LTE`,
per `makedefs/MakeInc.def:68`.) So any touch message seen is the software
`SweetHIDTouch` service, not a hardware touch probe.

## 3. Initialization sequence (relative order)

- `AppleCLCD::start()` (`SweetFramebuffer.cpp:260-266`) logs
  `SWEET FB: AppleCLCD ...` then `A5XELTE FB: requested 30 Hz ... copy timing on`
  as its **last two statements** before `return true`. `registerService()` already
  happened at line 259.
- `SweetHIDTouch::start()` logs `SWEET HID: touch registered` (SweetHID.cpp:457).
  Both are IOKit services matched **asynchronously** during the IOKit matching phase;
  the config table lists AppleCLCD (index 6) before SweetHIDTouch (index 8), but
  start() order is not strictly guaranteed.
- `IOFindBSDRoot()` (`IOKitBSDInit.cpp:660`) runs later, from
  `bsd_init()` → `bsd_autoconf()` → `IOKitBSDInit()` (publishes "IOBSD") → `setconf()`
  (`bsd_init.c:1139`). Its **first** action is
  `waitForMatchingService(gIOBSD, 30s)` (line 691), then
  `a5xelte_keys_init()` (line 775), then root-device selection (line 786+).

## 4. Does touch init indicate IOKit progressed beyond framebuffer startup?

**Conditionally yes.** IF the `SWEET HID: touch registered` line did appear on v6 after
the framebuffer lines, that proves IOKit asynchronous service matching is actively
running and instantiated/started an additional IOKit driver beyond AppleCLCD. That
would mean the hang is **not** at framebuffer startup. It does NOT by itself prove
IOKit matching completed or that BSD root selection was reached.

Note a confounder: `sweet_fbcon` writes glyphs directly to framebuffer 0xec000000
(the same physical FB AppleCLCD uses). If AppleCLCD reconfigured the display/panel
after registering, later IOLogs may still be generated but no longer be **visible**
on screen. This makes on-screen text an unreliable "last stage" indicator — which is
exactly why the pmsg mirror (patch 0406) is valuable.

## 5. v5 vs v6 paths and next likely blocker

| | v5 (OSX target) | v6 (iOS target) |
|---|---|---|
| Shim / framebuffer | same physically-proven shim region | same |
| Kernel target | OSX | `XNU_TARGET_OS_IOS` (genuine iOS) |
| Last recorded text | AppleCLCD + 30 Hz, then hang | not recorded; user reports a touch line too |
| No-root outcome | recovery boot path (no panic) | **`panic("Failed to mount root device")`** (IOKitBSDInit.cpp ~line 948, `#elif XNU_TARGET_OS_IOS`) |

**Next blocker: BSD root-device selection in `IOFindBSDRoot()`.** Reasons:
- v6 cmdline is `debug=0xc serial=3 cpus=1 keepsyms=1` — **no `rd=`**, no `emmcprobe=1`
  (`validation/ios-candidate-v6-out/manifest.json:54`).
- With no `rd=`, matching defaults to "any `IOMedia` with `Content=Apple_HFS`"
  (IOKitBSDInit.cpp:893-899). The M30 eMMC has Android ext4/f2fs partitions, not HFS,
  so no match → `ROOTDEVICETIMEOUT` → on iOS target, panic "Failed to mount root device".
- The eMMC driver exists but is gated: probe only if `emmcprobe=1`, root only if
  `rd=emmcroot0` (lines 780-792). Neither is set.
- There is **no genuine iOS root filesystem** (IPSW DMGs not unpacked), so even a
  successful root selection cannot mount iOS userspace. This is a later milestone.

## 6. Recommended smallest actionable fix (implemented offline on main)

**Patch `xnu/patches-minimal/0407-m30-root-stage-markers.patch` (implemented):**
Adds 6 M30LTE-guarded `IOLog` progression markers inside `IOFindBSDRoot()` at:
entry, after `waitForMatchingService(IOBSD)`, at the A5XELTE keys/emmc stage,
after `a5xelte_keys_init`, after the emmcprobe stage, and before the wait-for-root loop.
Low-risk (IOLog only, no behavior change), applies cleanly after 0400/0404/0405/0406.

**Plus** patch `0406-m30-console-pmsg-mirror.patch` (already in source; auto-applied by
the CI patch loop) mirrors every IOLog into the ramoops pmsg zone so the full boot text
can be recovered from TWRP after the next boot. Together these give exact hang-stage
evidence instead of relying on the framebuffer-visible text.

**Next physical test (NOT performed; needs fresh authorization):**
1. Rebuild iOS kernel with 0406 + 0407 (CI). 2. Boot once. 3. In recovery, run
`python3 tools/m30_bootlog.py start` to pull/decode pmsg. The `M30 ROOT:` markers will
show precisely how far `IOFindBSDRoot()` got.

**Optional follow-up (needs its own test):** add `rd=emmcroot0 emmcprobe=1` to the
cmdline to exercise the eMMC root path (its own `A5XELTE eMMC:` IOLogs will appear).
This advances root selection but cannot mount iOS without a genuine root FS.

No physical operations were performed. All work on main. No existing evidence modified.
