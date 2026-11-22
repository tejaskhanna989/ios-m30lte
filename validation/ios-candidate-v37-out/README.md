# iOS candidate v37 — retrigger-gated DSC scan

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `cd64662`.
No physical operations for v37 yet.

## What changed from v36

v36 physically showed the deferred worker starting at `load_init_program` on
launchd's Mach-O vnode (`cffaedfe`), long before the SpringBoard XCTEST
retrigger. Patch `0426` now starts the worker only after
`m30_irt_retriggered` is set, includes the vnode path in the wrong-magic
diagnostic, and resets to `NEED_DSC` so a later post-retrigger fault can retry
with the real DSC vnode. The `.symbols` companion fallback from v36 is kept.

All reads remain `UIO_READ`; in-memory page patching happens strictly after
`cs_validate_page()`; no security check is weakened.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `d68f75da2b9d05580b14b6adf01391aacf8e3420e511580a091ee3fa5383ed0e` |
| payload | `2a5472aa81331d49e257a8a9f34b18d8a3ded7393dd2fbc6cbfc45d5617ddd75` |
| shim-boot.img | `45db21b12eb7c8a20ba8ba5bb0ed4b39e7952aa1698e40574ffdab63db5d2505` |

Entry VA `0xfffffff00740e488`. Shim byte-identical to v6/v30-v36.

## Validation

CI `45042963811` GREEN. Buildtree PASS, kernel PASS, platform 9/9, CPU 17/17,
ADT 22/22, packaging PASS, handoff 18/18, all applicable focused tests PASS
(0417 inapplicable by design). Syntax check clean.

## Next physical step

BOOT-only flash, one boot, force back to TWRP quickly (short window to avoid
ring wrap). Expect: retrigger, `diag 0`, `diag 21 worker started`,
`diag 8 header ... map_off=0x200 map_cnt=1 ls_off=0x0`,
`diag 28 opened symbols file ...`, `diag 30`, `diag 13`, `diag 16`,
`M30 IRT: found ...`, then `M30 IRT: patched ...` on the symbol page fault.

No UI success claimed; BOOT readback skipped; USERDATA/SYSTEM/RECOVERY untouched.
