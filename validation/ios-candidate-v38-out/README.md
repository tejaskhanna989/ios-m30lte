# iOS candidate v38 — periodic IRT status replay

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `4bff101`.
No physical operations for v38 yet.

## What changed from v37

v37's short capture window ended before SpringBoard, so the XCTEST retrigger
never fired and no IRT lines were present. The 16 KB pmsg ring wraps before the
interesting userspace event. Patch `0426` now has the deferred worker replay a
compact status line every 2 s for up to 60 s:

`M30 IRT status: state=<n> off=0x<off> err=<e> replay=<i>`

This guarantees the final IRT state is present in any fresh pstore regardless
of when the device is forced back. The retrigger gate, deferred scan, and
`.symbols` fallback from v37 are unchanged. All reads are `UIO_READ`; the
in-memory page patch remains strictly after `cs_validate_page()`; no security
check is weakened.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `868024e7b432c61a6e60f2db36c3650ee80a52ac4bde30513986a43bd2107626` |
| payload | `71a4799757b695d54f651703548959cdd77771e1b569427ea0d830d0b778475e` |
| shim-boot.img | `73378ba9e48dbd58c1ec967a266a74d6ba5016d3b73059f568e3a4b85b98b919` |

Entry VA `0xfffffff00740e488`. Shim byte-identical to v6/v30-v37.

## Validation

CI `45046427792` GREEN. Buildtree PASS, kernel PASS, platform 9/9, CPU 17/17,
ADT 22/22, packaging PASS, handoff 18/18, all applicable focused tests PASS
(0417 inapplicable by design). Syntax check clean.

## Next physical step

BOOT-only flash, one boot, force back to TWRP at any convenient time, capture
pstore. Read the latest `M30 IRT status:` line to learn the final state:
`state=2` means the symbol offset was found but no page was patched yet;
`state=3` means the page was patched; `state=4` means a failure with `err=`.

No UI success claimed; BOOT readback skipped; USERDATA/SYSTEM/RECOVERY untouched.
