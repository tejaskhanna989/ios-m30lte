# How the trace obtains the textual service name — source-level proof

Source examined: CI build tree `v74-ci-buildtree/extracted/xnu` (the same tree
the kernel patch is generated against). All line references are from that tree.

## 1. Registration point: `osfmk/ipc/mach_port.c`, `mach_port_construct()`

Exact path from userspace string to kernel struct:

```
osfmk/ipc/mach_port.c:2546   struct mach_service_port_info sp_info = {};
osfmk/ipc/mach_port.c:2562   service_port_info = CAST_USER_ADDR_T(options->service_port_info64);  // or 32-bit
osfmk/ipc/mach_port.c:2630   if (copyin(service_port_info, (void *)&sp_info, sizeof(sp_info))) return KERN_MEMORY_ERROR;
osfmk/ipc/mach_port.c:2633   sp_name_length = strnlen(sp_info.mspi_string_name, MACH_SERVICE_PORT_INFO_STRING_NAME_MAX_BUF_LEN);
osfmk/ipc/mach_port.c:2643   kr = ipc_service_port_label_alloc(&sp_info, &port_splabel);
```

The struct definition is in `osfmk/mach/port.h:407-417`:

```
#define MACH_SERVICE_PORT_INFO_STRING_NAME_MAX_BUF_LEN 255
typedef struct mach_service_port_info {
    char mspi_string_name[MACH_SERVICE_PORT_INFO_STRING_NAME_MAX_BUF_LEN];
    uint8_t mspi_domain_type;
} mach_service_port_info_data_t;
```

So the textual name is **copied verbatim from the caller's userspace buffer** into
a kernel stack struct. The kernel does not look it up in a plist or derive it;
it is the string the caller supplies when registering the port.

There is exactly one caller of `ipc_service_port_label_alloc` in the tree:
`mach_port.c:2643`. Service-port labels are created at this single choke point.

The port is then marked as a service port and the label attached:

```
osfmk/ipc/mach_port.c:2673   port->ip_service_port = (bool)(options->flags & MPO_SERVICE_PORT);
osfmk/ipc/mach_port.c:2674   port->ip_splabel = port_splabel;
```

Restriction note: `mach_port.c:2602-2621` enforces "only launchd may add service
port labels" **only in non-DEVELOPMENT/non-DEBUG kernels**. Our CI builds use
`KERNEL_CONFIG=DEVELOPMENT`, so the restriction is not enforced. Therefore the
trace must record the **calling process**, which it does; provenance is
established from the record, not assumed from the flag.

**What `M30 SVC REG <ticks> <proc> <name>` proves:** process `<proc>` constructed
a Mach port and declared it, via the kernel's service-port API, with the
textual name `<name>` at that time. For `launchd`, this is the kernel-side
creation of the named service port. It does **not** prove that launchd
subsequently advertised the name in its bootstrap directory, nor that any
client looked it up.

## 2. Send point: `osfmk/ipc/ipc_kmsg.c`, `ipc_object_copyin()`

The name on the send side comes from the **destination port's label**, not from
a second copyin:

```
osfmk/ipc/ipc_kmsg.c:4145   mach_service_port_info_t sp_info = NULL;
osfmk/ipc/ipc_kmsg.c:4146   struct mach_service_port_info sp_info_filled = {};
osfmk/ipc/ipc_kmsg.c:4147   if (ip_active(dport) && dport->ip_service_port && dport->ip_splabel) {
osfmk/ipc/ipc_kmsg.c:4148       ipc_service_port_label_get_info((ipc_service_port_label_t)dport->ip_splabel, &sp_info_filled);
osfmk/ipc/ipc_kmsg.c:4149       sp_info = &sp_info_filled;
osfmk/ipc/ipc_kmsg.c:4150   }
```

The label's stored name is written in `osfmk/ipc/ipc_service_port.c:102-108`:

```
#if CONFIG_SERVICE_PORT_INFO
    size_t sp_string_name_len = strlen(sp_info->mspi_string_name);
    sp_label->ispl_service_name = kalloc_data(sp_string_name_len + 1, Z_WAITOK);
    strlcpy(sp_label->ispl_service_name, sp_info->mspi_string_name, sp_string_name_len + 1);
#endif
```

and read back in `ipc_service_port.c:302-310`:

```
#if CONFIG_SERVICE_PORT_INFO
void ipc_service_port_label_get_info(ipc_service_port_label_t port_splabel, mach_service_port_info_t info) {
    info->mspi_domain_type = (uint8_t)port_splabel->ispl_domain;
    size_t sp_string_name_len = strlen(port_splabel->ispl_service_name);
    strlcpy(info->mspi_string_name, port_splabel->ispl_service_name, sp_string_name_len + 1);
}
#endif
```

`CONFIG_SERVICE_PORT_INFO` is **not enabled** in the current M30 config
(`config/MASTER.arm64.m30lte` has no enabling line; the generic MASTER only lists
it in a commented template at line 768). Patch 0456 enables it so the name is
stored and readable. Without that config change the send-side name would be
unavailable — this is a real dependency, not an assumption.

**What `M30 SVC SEND <ticks> <proc> -> <name> id=<msgh_id>` proves:** process
`<proc>` sent a Mach message to a port whose kernel service label carries the
textual name `<name>`. The name's provenance is the `REG` record that created
that label; the two records must be correlated by name and process (typically
`launchd` for REG, `SpringBoard` for SEND). It does **not** prove that the
message was a `mach_service_lookup`, nor which FrontBoard method was invoked:
`msgh_id` has no mapping to FrontBoard methods in this repository.

## 3. Revised claim boundaries

- Kernel **can** identify the textual name at both points, from the caller's
  `copyin` and from the stored label respectively.
- Kernel **cannot** independently verify that a name corresponds to a genuine
  launchd bootstrap entry in DEVELOPMENT builds; it relies on the recorded
  calling process. The trace is therefore self-qualifying: REG records show who
  created each name.
- Kernel **cannot** observe `mach_service_lookup("…")` by name, scene creation,
  scene activation, or MIG-level success/failure. No change to the patch can
  make those observable with the available XNU source.
- The diagnostic answers: "was the named port created, by whom, and did
  SpringBoard send to it?" It does not answer "was a lockscreen scene created?"
