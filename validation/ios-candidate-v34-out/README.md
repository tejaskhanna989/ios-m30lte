# iOS candidate v34 — 4 KB IRT buffers + allocation diagnostics

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `c317e04`.
No physical operations for v34 yet.

## What changed from v33

v33 physical captured the retrigger and `M30 IRT diag 0` with a valid vnode,
then went silent. The only silent exits in the `NEED_DSC` path are the
`Z_NOWAIT` allocations, so patch `0426` now uses a single 4 KB page chunk
instead of 64 KB and emits `M30_IRT_DIAG(19/20)` at both allocation sites.
Read-only file access, post-validation in-memory patching and all security
checks are unchanged.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `8d7896268fc77bb05410940bf297fa362ecafeea227c02e879254786c5c10d4d` |
| payload | `6ec1d9ffc041c4a9a27baeed87d90e16dc29b3048cd79d6b366b1d5fbbd96b65` |
| shim-boot.img | `24486a2652dbc9360da1caa6e747757a44aea111aef936e6b1b710ca88f66cf4` |

Entry VA `0xfffffff00740e488`. Shim byte-identical to v6/v30/v31/v32/v33.

## Validation

CI `45034826739` GREEN (iphoneos, LSE=0). Buildtree PASS, kernel PASS,
platform 9/9, CPU 17/17, ADT 22/22, packaging PASS, handoff 18/18, all
applicable focused tests PASS (0417 inapplicable by design).

## Next physical step

BOOT-only flash, one boot, force back to TWRP, capture pstore. Look for
`M30 IRT diag 19/20`, `diag 3/4/5...`, or `M30 IRT: found/patched`.
No UI success claimed; BOOT readback skipped; USERDATA/SYSTEM/RECOVERY untouched.
