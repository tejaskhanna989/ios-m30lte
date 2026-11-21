# iOS candidate v13 — built-in AMFI fix for v12 launchd code-signing panic

Isolated candidate. v6–v12, backups, all physical evidence preserved.
No physical operations performed for v13. Work on `main` @ `9d68948`.

## Exact cause and fix

Physical v12 pstore (`2b243c96…f4b38`, commit `75d9d3b`) showed the genuine iOS HFSX
root mounted and `/sbin/launchd` load attempted, then a data abort in
`accelerate_entitlement_queries` (`pc 0xfffffff0077d9770`, `far=0x1a0`,
`esr=0x96000007`) reached via `ubc_cs_blob_add` → `load_code_signature` →
`load_machfile`. Disassembly: `ldr x8,[x8,#0x1a0]` with the global `_amfi == NULL`
— the `amfi->OSEntitlements.adjustContextWithMonitor()` call.

The only in-tree AMFI interface (`bsd/kern/sweet_amfi.c`) was compiled SWEET-only,
so the genuine iOS-targeted M30LTE kernel registered **no** AMFI interface at all.
Full analysis: `validation/launchd-codesign-panic-v12-analysis.md`.

**v13 fix (patch `0411-m30-builtin-amfi.patch`):** widen three guards to also match
`ARM64_BOARD_CONFIG_M30LTE` — `sweet_amfi.c` (interface + STARTUP registration),
`iokit/Kernel/arm/SweetEntitlements.cpp` (parser), `bsd/kern/bsd_init.c` (policy
registration). This registers the existing **genuine** built-in AMFI: entitlements
are validated against the code directory via `csblob_get_entitlements()`; signature
and page-hash checks remain in the kernel. No `launchd_unsecure_cache`,
`cs_enforcement_disable` or `amfi_get_out_of_my_way`. Cmdline unchanged from v12.

Confirmed compiled in: `SWEET AMFI: built-in interface registered (XML entitlements)`
string, `sweet_amfi_register` STARTUP entry, `_sweet_amfi` interface, and `_amfi`
global are present in the v13 kernel (all absent in v12).

## Hashes

| File | SHA256 |
|---|---|
| kernel | `f7e0c4c82aa51a059850ab0581d6c7c11c4fb641c35be0b379e8d4a597fb2586` |
| payload | `43d9862a41aad61a604f7b5e16e245aea9996e0a879041d099e42a8f7e2852ab` |
| combined.bin | `3e4e5f17eac1d27e64167f1ccd71a8d501bca6ca91d82d96f29c2640c0f18e54` |
| shim-boot.img | `a9412d63cb01cc817379eef3e39000536a7cde41b96f842204ec8d0b017d4462` |
| ios-boot.img | `bc6d3cf69724d10e94b78c7d0666b63ec308ca0ad8d1a4ae40f3081b9e310e3d` |

Cmdline (unchanged from v12):
`debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292 rd=emmcroot0 emmcroot=USERDATA emmcprobe=1 emmcwrite=1`

## Validation (offline)

CI `44931911670` green (iOS target confirmed `SDKROOT=iphoneos, XNU_TARGET_OS_IOS`,
LSE=0). Kernel `f7e0c4c8…fb2586`. Buildtree PASS, kernel PASS, platform 9/9,
CPU 17/17, ADT 22/22, handoff 18/18, packaging PASS, GIC 5/6 (documented
inapplicable DAIF check). All focused tests PASS, including new
`tools/test_m30_builtin_amfi.py` (reproduces the NULL deref at +0x1a0 and verifies
registration/validation; SWEET and non-M30 configs unchanged). Shim region
byte-identical to proven v6 (`864370f6…`); `maxmem=292`, iOS 16 target, and the
working HFSX/eMMC write path preserved.

Note: ADT PA / boot_args PA in the handoff verifier shifted from 0x82444000 /
0x82448000 to 0x82448000 / 0x8244c000 (both +0x4000) because the kernel's linked
segment grew with the AMFI code. Both remain in RAM, aligned, and non-overlapping;
the verifier's stale expected constants were updated accordingly.

## Status / next physical step

Not physically tested. Do not claim launchd is fixed until a fresh physical pstore
proves progression past the failing path. Proposed (needs fresh authorization):
flash v13 BOOT only, verify BOOT readback against
`a9412d63cb01cc817379eef3e39000536a7cde41b96f842204ec8d0b017d4462`, preserve
USERDATA (no rewrite/format), one physical boot, capture pstore immediately on
recovery return. Expected: `SWEET AMFI: built-in interface registered` in log,
then launchd Mach-O load proceeds past `accelerate_entitlement_queries`.
