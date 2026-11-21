# iOS candidate v13 — physical boot result (2026-11-21)

## Authorization / actions

Standing authorization for all project operations. Work on `main` @ `566ee98`.
Device confirmed: `m30lte`, `320081735bb166a3`, `M305FDDU8CVK1`, TWRP `3.4.03.0.0-UNOFFICIAL`.

- Candidate hash verified `a9412d63cb01cc817379eef3e39000536a7cde41b96f842204ec8d0b017d4462`.
- `heimdall flash --BOOT ... --no-reboot` → "BOOT upload successful" after two transient
  protocol errors (`Failed to send file part size packet` / `Protocol initialisation
  failed`) resolved by a USB re-enumeration. See `heimdall-flash.log` (full attempt log).
- **BOOT readback skipped per user decision** ("skip readback ... i have did the boot").
  Do not claim BOOT readback was verified.
- USERDATA / SYSTEM / RECOVERY untouched (no rewrite/format/repartition). One boot only.
- Pstore captured immediately on recovery return: `raw/pmsg-ramoops-0`, SHA
  `e78112183279b6dd1584cb10f50f48b01e026ceeac8797c1a44ec3b6345d452e` (13,800 B).
  Pre-boot baseline `raw/pre-pmsg-ramoops-0` (v12 log) preserved.

## Result — AMFI fix verified, NEW earlier panic

The v13 AMFI interface fix **worked**:
```
[070] SWEET AMFI: built-in interface registered (XML entitlements)
[071] calling mpo_policy_init for vnguard
[072] Security policy loaded: Guarded vnode policy (vnguard)
[073] SWEET: trust caches unavailable (Image4/AMFI not installed)
```
`_amfi` is non-NULL and the built-in interface registered. The original v12
`accelerate_entitlement_queries` NULL deref did **not** recur — but boot now panics
**earlier**, before BSD autoconf / root mount / launchd:
```
[083] M30 BSD: vfsinit returned
[084] panic(cpu 0 caller 0xfffffff007a88c8c): Unexpected fault in kernel static region
       at pc 0xfffffff007a2ac74, lr 0xfffffff007a2a908
       esr 0x9600004f (write permission fault), far 0xfffffff007204aec
```
Symbolicated against v13 kernel `f7e0c4c8…fb2586`:
- `pc 0xfffffff007a2ac74` = `mac_policy_register` (`str w9,[x10,#0xaec]`)
- `lr 0xfffffff007707688` = `sweet_amfi_policy_register`
- `0xfffffff0076f7340` = `bsd_init`, `0xfffffff007a5f94c` = `kernel_bootstrap_thread`

`far 0xfffffff007204aec` = `_mac_policy_list+0x14` (`_mac_policy_list` @ 0xfffffff007204ad8).

### Exact cause
`security/mac_base.c:254` declares `SECURITY_READ_ONLY_LATE(mac_policy_list_t)
mac_policy_list;` → symbol is in `__DATA_CONST,__const`. `machine_lockdown()`
(`startup.c:760`) makes that region read-only during `kernel_bootstrap`. Patch 0411
called `sweet_amfi_policy_register()` from **bsd_init()**, which runs from
`kernel_bootstrap_thread` *after* lockdown — so `mac_policy_register()`'s write to
`mac_policy_list.numloaded` faults. Vnguard registers correctly at `startup.c:722`
inside `kernel_bootstrap`, **before** `machine_lockdown()`.

### Fix (patch `0412-m30-amfi-policy-early-register.patch`)
- `bsd_init.c`: revert to SWEET-only (M30LTE no longer registers from late bsd_init).
- `startup.c`: call `sweet_amfi_policy_register()` in `kernel_bootstrap`, alongside
  vnguard, before `machine_lockdown()`. SWEET behaviour unchanged.
- Regression test `tools/test_m30_amfi_policy_early_register.py` PASS: models
  mac_policy_list going RO at lockdown; late registration → SIGSEGV (reproduces v13
  panic), early registration → success.

## Honest status

- Built-in AMFI interface registration VERIFIED on device (record 070).
- Original v12 NULL-deref in `accelerate_entitlement_queries` did NOT recur.
- **New blocker**: `mac_policy_register` write to frozen `mac_policy_list` from late
  bsd_init. Boot does not reach root mount / launchd yet. No launchd/SpringBoard claim.
- BOOT readback not verified (skipped per user). Do not claim it.
- Next: CI build v14 with patch 0412 (in progress), then propose a fresh physical test.
