# v12 launchd code-signing panic — exact cause and minimal fix (2026-11-21)

## Physical evidence (commit `75d9d3b`, pstore `2b243c96…f4b38`)

Genuine iOS 16.7.16 HFSX root mounted, `/sbin/launchd` load attempted, then:
```
panic(cpu 0 caller 0xfffffff007a885ec): Kernel data abort.
  pc 0xfffffff0077d9770  lr 0xfffffff0077d89b0
  esr 0x96000007 (data abort, EL1)  far 0x00000000000001a0
  Panicked task pid 1: init
```

## Phase 1 — Diagnosis (exact, symbolicated against v12 kernel `ab645b13…114426`)

`llvm-addr2line` on the exact v12 kernel:
| Address | Symbol |
|---|---|
| `0xfffffff0077d9770` (pc) | `accelerate_entitlement_queries` |
| `0xfffffff0077d89b0` (lr) | `ubc_cs_blob_add` |
| `0xfffffff007812acc` | `load_code_signature` |
| `0xfffffff007810184` | `parse_machfile` |
| `0xfffffff00780f7f0` | `load_machfile` |
| `0xfffffff007a885ec` | `sleh_synchronous_sp1` (panic wrapper) |

Disassembly of the faulting instruction (`bsd/kern/ubc_subr.c:4295`):
```
fffffff0077d9768: ldr x0, [x0, #0xc8]     ; cs_blob->csb_entitlements
fffffff0077d976c: ldr x8, [x8, #0x958]     ; load global _amfi
fffffff0077d9770: ldr x8, [x8, #0x1a0]     ; _amfi->OSEntitlements.adjustContextWithMonitor  <-- FAULT
fffffff0077d9774: blr x8
```
`x8` (the global `_amfi`) is NULL → `ldr` from `NULL+0x1a0` → `far=0x1a0`, `esr=0x96000007`.
This is the `ret = amfi->OSEntitlements.adjustContextWithMonitor(...)` call in
`accelerate_entitlement_queries()` (source line ~4321), reached from `ubc_cs_blob_add()`
→ `load_code_signature()` → `parse_machfile()` → `load_machfile()` of launchd.

### Why `_amfi` is NULL
`libkern/amfi/amfi.c:amfi_interface_register()` is the only writer of the global;
`if (amfi) panic("already set"); amfi = mfi;`. The only in-tree implementation is
`bsd/kern/sweet_amfi.c`, which calls `amfi_interface_register(&sweet_amfi)` from a
`STARTUP(EARLY_BOOT, ...)` hook — but the entire file is wrapped in
`#if defined(ARM64_BOARD_CONFIG_SWEET)`. The entitlement parser it needs,
`iokit/Kernel/arm/SweetEntitlements.cpp`, is likewise wrapped in `#if defined(SWEET)`.
The policy registration call in `bsd_init.c:700` is also SWEET-only.

M30LTE defines `ARM64_BOARD_CONFIG_A5XELTE` + `ARM64_BOARD_CONFIG_M30LTE`
(`makedefs/MakeInc.def:68`), **not** `ARM64_BOARD_CONFIG_SWEET`/`SWEET`.
Confirmed by absence of the `SWEET AMFI: built-in interface registered` string in the
v12 kernel. So on this genuine iOS-targeted M30LTE kernel **no AMFI interface is ever
registered** — `CODE_SIGNING_MONITOR` is off, so `ubc_cs_blob_add()` takes the
non-monitor branch and dereferences the NULL `amfi`.

### Classification
This is an **M30 platform-initialization gap**, not a malformed launchd signature and
not an XNU 8796/iOS 16 incompatibility: launchd's signature is processed by the
generic code-signing path; the crash is a missing platform AMFI registration that every
Apple iOS board supplies (via the AppleMobileFileIntegrity kext). `root volume is not
authenticated (error 25); continuing unsealed` (`bsd_init.c:954`) is a separate,
non-fatal informational message (sealed-volume auth unavailable on this board) and is
not the cause of this panic.

## Phase 2 — Minimal fix (patch `0411-m30-builtin-amfi.patch`)

Enable the **existing, genuine** built-in AMFI interface for M30LTE by widening three
guards to also match `ARM64_BOARD_CONFIG_M30LTE`:
- `bsd/kern/sweet_amfi.c` — compile the interface + its `STARTUP` registration.
- `iokit/Kernel/arm/SweetEntitlements.cpp` — compile the entitlement parser.
- `bsd/kern/bsd_init.c` — call `sweet_amfi_policy_register()` in BSD init.

Why this preserves real code signing (does not bypass/weak security):
- `sweet_amfi_attach_entitlements()` calls `csblob_get_entitlements()` first, which
  validates the XML entitlements against the code directory's hash; mismatches grant
  none ("entitlements do not match the code directory, granting none"). Signature and
  page-hash validation remain in the kernel.
- Registration goes through the standard `amfi_interface_register()` KPI.
- No `launchd_unsecure_cache=1`, `cs_enforcement_disable=1`, or
  `amfi_get_out_of_my_way=1` — none used, none relied upon.

Non-fixes rejected: adding `rootrw=1` (SWEET-only, no-op — already proven); touching the
HFSX image or eMMC write path (both working); disabling AMFI (forbidden and unnecessary).

## Regression tests

`tools/test_m30_builtin_amfi.py` PASS:
- compiles a faithful C model with the callback pointer at struct offset `0x1a0`:
  `amfi == NULL` → SIGSEGV (reproduces `far=0x1a0` panic); registered interface → success.
- asserts patch 0411 widens all three guards, keeps SWEET first, registers via
  `amfi_interface_register`, validates entitlements against the code directory, and
  contains no bypass boot-args.
- asserts SWEET and non-M30LTE behaviour unchanged.

## Status

Built via GitHub Actions CI as v13 (see `validation/ios-candidate-v13-out/README.md`).
**Not physically tested.** Do not claim launchd is fixed until a fresh physical pstore
proves progression past the failing path.
