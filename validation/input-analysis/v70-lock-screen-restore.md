# v70 — restore v68 lock screen after v69 input-diagnostic run (facts only)

## Final v69 `SBERR` record

Source: `validation/physical-boot-test/20261125-ios-v69-boot/decoded-pmsg.txt`
and `raw/pmsg-ramoops-0`.

The final three records are:

- `XNU: SBERR libc++abi: `
- `XNU: SBERR terminating due to uncaught exception of type NSException`
- `XNU: SBERR `

No exception name beyond the C++ type `NSException`, no reason string, no
crashing thread, and no backtrace survived in the 16 KiB ramoops ring. A
targeted read-only check found no SpringBoard crash report under the mounted
TWRP data log paths. The immediate cause that can be stated is **SpringBoard
terminated on an uncaught `NSException`**; its reason is unobserved. Do not
invent a reason or a selector-79 meaning.

For comparison, the accepted v68 capture also contains three `SBERR` records,
but they are benign Objective-C duplicate-class warnings from
`MobileStoreDemoKit`, not a fatal termination. The fatal `NSException` record
is unique to the v69 run.

## Relevant v68 -> v69 delta

Only three kernel patches were added after v68:

- `0446-m30-framebuffer-status-quiet.patch`: caps the periodic
  `M30 FB: v=` pstore heartbeat to the first eight records. It changes only a
  logging condition; framebuffer counters, staging, presentation, notify
  handshake and selector behavior are unchanged.
- `0447-m30-key-input-diag.patch`: adds bounded pstore records around the
  existing M30 key GPIO polling and `sweet_hid_key()` call.
- `0448-m30-hid-event-diag.patch`: adds bounded pstore records in
  `sweet_hid_key()` dispatch and in `IOHIDEventServiceUserClient::open()` /
  `enqueueEvent()`, the path backboardd uses.

No v69 patch added a functional touch producer or changed code signing, AMFI,
trust cache or entitlement checks. The GPIO -> HID path was already present in
v68; v69 only proved it at runtime (66 GPIO transitions, 67 HID dispatches,
`1 clients`).

The smallest behavioral difference that could plausibly interact with
SpringBoard is `0448`, because it is the only new code on the HID consumer path
used by backboardd. `0447` is on the producer side. Neither can be proven from
the surviving pstore to be the cause of the `NSException`; the exception reason
was lost.

## v70 targeted correction

Keep `0446` (it preserves early ABI evidence and does not change display
behavior). Revert `0447` and `0448` exactly with two new patches:

- `0449-m30-revert-key-input-diag.patch`
- `0450-m30-revert-hid-event-diag.patch`

Both are pure removals of the v69 diagnostic code; they add no lines other than
diff headers. Functional GPIO polling, `sweet_hid_key()`, HID event
construction, entitlement check and queue enqueue are restored byte-for-byte
to their v68 source state. No selector response is synthesized.

Effective v70 source hashes after applying `0441` through `0450`:

- `iokit/Kernel/arm/SweetFramebuffer.cpp`
  `d3199f92c608b8c7d874d83087c0a8409b6488a3acc93d40599deb0bc32e3c8f` (v69,
  heartbeat cap retained)
- `bsd/dev/a5xelte_keys.c`
  `d53238ba0ca163a36ef17d1847d56f442bca3964001e0b998aa50d073a6f12db` (v68)
- `iokit/Kernel/arm/hid/SweetHID.cpp`
  `d30c9adf85a89b5c94151e57bad24007655d1a9beb06742fc3d821a0f89805f3` (v68)
- `iokit/Kernel/arm/hid/IOHIDEventServiceUserClient.cpp`
  `0e8df68c047322c220cdbd1b4c9db194c5dc1fb80117bfc8c726e9fab967637e` (v68)
- `pexpert/arm/pe_serial.c` and `bsd/kern/sys_generic.c` unchanged from v68.

No touchscreen work is included. Touch remains unsupported.
