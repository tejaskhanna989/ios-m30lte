# Mach service observation for the lockscreen path — implementation design

Branch: `investigation/native-lockscreen-independent`. Diagnostic-only, gated,
bounded, no Apple binary modification.

## What the kernel can and cannot observe

| Question | Kernel visibility | Method |
|---|---|---|
| Was a named Mach service port registered, by whom, when? | **Yes** | `mach_port_construct()` receives `mach_service_port_info_t` from userspace via `copyin()` before `ipc_service_port_label_alloc()`. The string name and calling process are available here regardless of `CONFIG_SERVICE_PORT_INFO`. |
| Did SpringBoard send to a named service port? | **Yes**, with `CONFIG_SERVICE_PORT_INFO` enabled | `ipc_kmsg.c` extracts `sp_info` from the destination port's service label during `ipc_object_copyin`. Service name, process name, `msgh_id` and timestamp are available. |
| Did SpringBoard call `mach_service_lookup("com.apple.frontboard.systemappservices")`? | **No, not by name** | `service_lookup`/`mach_service_checkin` are not in the open-source XNU tree; the kernel sees only IPC to launchd. The requested name lives in a MIG payload whose format is not defined in this repository. |
| Was a FrontBoard scene created/activated? | **No** | Scene creation is private SpringBoard/FrontBoard userspace. No kernel event identifies it. |
| Did a MIG call succeed or fail semantically? | **Partial** | Kernel return code from `mach_msg` is visible; the MIG `retCode` in the reply body is not decoded. |

Conclusion: kernel instrumentation can **decisively answer service registration
and named-port access**, but **cannot** prove scene creation/activation. Any
claim of kernel visibility into SpringBoard scene internals would be false.

## Observation points implemented

1. `osfmk/ipc/mach_port.c`, inside `mach_port_construct()` immediately after a
   successful `ipc_service_port_label_alloc()`.
   - Emits `M30 SVC REG <ticks> <proc> <service_name>`.
   - Proves: a service port with that name was created by that process at that
     time. For `com.apple.frontboard.systemappservices` this is the kernel-side
     registration/launchd-handoff event.
   - Does not prove: the service was usable by SpringBoard, or that SpringBoard
     looked it up successfully.
2. `osfmk/ipc/ipc_kmsg.c`, inside the existing `CONFIG_SERVICE_PORT_INFO` block
   where `sp_info` is extracted from the destination port.
   - Emits `M30 SVC SEND <ticks> <proc> -> <service_name> id=<msgh_id>`.
   - Proves: a process sent a Mach message to a named service port, with the
     MIG message ID. Repeated `SpringBoard -> com.apple.frontboard.systemappservices`
     demonstrates access to that service.
   - Does not prove: which FrontBoard method was called, or its result.

## Minimal patch design

`xnu/patches-minimal/0456-m30-mach-service-trace.patch`:
- `config/MASTER.arm64.m30lte`: enable Apple's existing
  `config_service_port_info` option (needed only for the send-side name).
- `mach_port.c`: M30LTE-only statics + `PE_parse_boot_argn("m30svctrace", ...)`,
  24-line registration cap, `m30_pmsg_diag_line()` durable sink.
- `ipc_kmsg.c`: same gate, 48-line send cap, same sink.
- No changes to return values, locks, allocation, service semantics, AMFI,
  code signing, framebuffer or HID. Disabled unless `m30svctrace=1`.

## Expected diagnostic output

```
M30 SVC REG 1234567890 launchd com.apple.frontboard.systemappservices
M30 SVC SEND 1234600000 SpringBoard -> com.apple.frontboard.systemappservices id=1234
```

Interpretation:
- REG for frontboard but no SEND from SpringBoard -> service exists, SpringBoard
  never accesses it (Stage 4 blocker).
- SEND present -> service access verified; failure is downstream (Stage 5/6).
- No REG at all -> service never registered in that boot.
- The trace cannot say whether scene creation succeeded.

## CI validation

- `tools/test_m30_mach_service_trace.py`: gate, caps, sink-only, no behaviour
  change, patch applies to the current CI build tree.
- `xnu.yml`: verifies patch 0456 was applied and runs the focused test.
- Kernel build CI: `46054644182` (result recorded in the handoff commit).

## Physical verification (NOT executed)

1. Build a BOOT with this patch, `m30svctrace=1`, v68 cmdline otherwise.
2. Keep USERDATA unchanged. Flash BOOT only (requires separate explicit approval).
3. Observe ≥15 min, record XNU→Apple logo→lockscreen timestamps.
4. Return to TWRP, pull pstore promptly, decode `M30 SVC REG/SEND` lines.
5. Correlate with the observation: REG/SEND presence localises Stage 4; absence
   of a lockscreen with SEND present localises Stage 5/6, which this instrumentation
   cannot further resolve.

## Limitations

- Adds `config_service_port_info` (small kernel memory/struct change).
- Caps are small; a busy boot can fill them before the interesting event.
- `msgh_id` cannot be mapped to FrontBoard methods from this repository.
- No claim of SpringBoard scene visibility is made.
