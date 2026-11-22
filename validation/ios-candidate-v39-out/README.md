# iOS candidate v39 — correct .symbols path

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `f5c993b`.
No physical operations for v39 yet.

## What changed from v38

v38 physically proved the retrigger gate and periodic status replay work, but
`vn_getpath()` reports `plen` including the NUL terminator. Appending
`.symbols` at `path+plen` wrote past the NUL, so `vnode_open()` reopened the
main DSC (same vnode) and the worker failed with `ls_off=0` again.

v39 computes the path length with a manual loop before appending `.symbols`,
and logs `plen`, the real strlen, and both the opened and main vnode pointers.
Everything else (retrigger gate, deferred worker, bounded status replay,
read-only scans, post-`cs_validate_page()` in-memory patch) is unchanged.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `7ca0b8f2e5f3b6abb9ce63ed2e56a7d1f8e02ea81cb31bddcdee569af6295552` |
| payload | `d36326acc4bfab9d179e27d9ea55b5d954122af11ea8b8b2dcce1898a88c720a` |
| shim-boot.img | `85c6125fd81b94da4cfd59b1f6ee44626a2ce970e7e45e6ca061be919423aa47` |

Entry VA `0xfffffff00740e488`. Shim byte-identical to v6/v30-v38.

## Validation

CI `45048935684` GREEN. Buildtree PASS, kernel PASS, platform 9/9, CPU 17/17,
ADT 22/22, packaging PASS, handoff 18/18, all applicable focused tests PASS
(0417 inapplicable by design). Syntax check clean.

## Next physical step

BOOT-only flash, one boot, force back to TWRP at any time; read the latest
`M30 IRT status:`. Expect `diag 31` (plen vs strlen), `diag 28` with a
distinct `.symbols` vnode and path ending `.31.symbols`, `diag 30` with a
non-zero `ls_off`, then symbol name/address diagnostics and
`M30 IRT: found ...`.

No UI success claimed; BOOT readback skipped; USERDATA/SYSTEM/RECOVERY untouched.
