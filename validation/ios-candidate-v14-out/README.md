# iOS candidate v14 — AMFI MAC policy early registration

Isolated candidate. v6–v13, backups, all physical evidence preserved.
No physical operations performed for v14. Work on `main` @ `5a65d72`.

## Exact cause and fix

Physical v13 pstore (`e7811218…452e`) proved patch 0411 worked:
`SWEET AMFI: built-in interface registered (XML entitlements)` appeared, and the
v12 `accelerate_entitlement_queries` NULL deref did not recur. But a new, earlier
panic appeared in `mac_policy_register` (`pc 0xfffffff007a2ac74`,
`far 0xfffffff007204aec` = `_mac_policy_list+0x14`, `esr=0x9600004f` write fault):
`mac_policy_list` is `SECURITY_READ_ONLY_LATE` in `__DATA_CONST`, frozen by
`machine_lockdown()` during `kernel_bootstrap`. Patch 0411 registered the AMFI
MAC policy from the LATER `bsd_init()` (after lockdown), so the write faulted.
Full analysis: `validation/physical-boot-test/20261121-ios-v13-boot/README.md`.

**v14 fix (patch `0412-m30-amfi-policy-early-register.patch`):**
- `bsd_init.c`: revert to SWEET-only (M30LTE no longer registers from late bsd_init).
- `startup.c`: call `sweet_amfi_policy_register()` in `kernel_bootstrap`, alongside
  vnguard, **before** `machine_lockdown()` — where `__DATA_CONST` is still writable.
- SWEET and non-M30LTE behaviour unchanged. Genuine code signing preserved; no
  bypass boot-args. Cmdline unchanged from v13.

Confirmed compiled in v14: early call at `startup.c:731-733` precedes
`machine_lockdown()`; bsd_init guard is SWEET-only; both AMFI reg/policy strings present.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `b350698c16f9c264802643477b5e5d3109330848a31336f64638a63d7daff6e6` |
| payload | `98c2038bd4adc8cc04c003ca7782499f8b545d960c6dc16c252229be964eb9f6` |
| combined.bin | `f7689faf55266ab557f54f0c183b31582b67d6fe4bfc4733caa6f940c598470a` |
| shim-boot.img | `1a2d6f6940dd1501c36406c257b544bfa7340dc38b870da75ac4b0049fdfdfc3` |
| ios-boot.img | `a8b72adc889c7d6c7f64a01c62c6e391834bddc111d3be46d17d64d9db7c018e` |

Cmdline (unchanged):
`debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292 rd=emmcroot0 emmcroot=USERDATA emmcprobe=1 emmcwrite=1`

## Validation (offline)

CI `44934162919` green (iOS target `SDKROOT=iphoneos`, LSE=0). Buildtree PASS,
kernel PASS, platform 9/9, CPU 17/17, ADT 22/22, handoff 18/18, packaging PASS,
GIC 5/6 (documented inapplicable DAIF check). All focused tests PASS, including
`tools/test_m30_amfi_policy_early_register.py` (reproduces the RO-freeze fault and
proves the fix) and `tools/test_m30_builtin_amfi.py`. Shim region byte-identical
to proven v6 (`864370f6…`); `maxmem=292`, iOS 16 target, and the working HFSX/eMMC
path preserved.

## Status / next physical step

Not physically tested. Do not claim launchd/SpringBoard works without device evidence.
Proposed (needs fresh authorization): flash v14 BOOT only, verify BOOT readback against
`1a2d6f6940dd1501c36406c257b544bfa7340dc38b870da75ac4b0049fdfdfc3`, preserve
USERDATA (no rewrite/format), one boot, capture pstore immediately. Expected: AMFI
interface + policy both register without fault, boot proceeds past vfsinit to root
mount / launchd load.
