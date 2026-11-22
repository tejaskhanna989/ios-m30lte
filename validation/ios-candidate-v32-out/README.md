# iOS candidate v32 — dyld-pager vnode recovery + IRT diagnostics

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `d12154f`.
No physical operations for v32 yet.

## What changed from v31

v31 physical proved patch 0426 was completely silent: zero `M30 IRT` records in
the pstore even though both format strings are linked into the kernel. The dyld
shared cache is mapped through `dyld_pager_ops`, not `vnode_pager_ops`, so
`vnode_pager_lookup_vnode(pager)` returns `NULL` and 0426's `vp == NULL` guard
returned on every code-signed page fault.

Patch 0426 now:
- recovers the DSC file vnode via the generic
  `memory_object_backing_object(pager, mo_offset, &backing, &boff)` callback,
  then `vnode_pager_lookup_vnode(backing->pager)`;
- accepts the pager as an argument to the fix-up;
- emits 21 one-shot `M30 IRT diag N:` messages covering entry, vnode recovery,
  header magic, every `vn_rdwr` error, local-symbol info, string pool, nlist,
  mapping table, success and patch.

All file access remains read-only (`UIO_READ`); the in-memory page is patched
strictly after `cs_validate_page()`. No signature, hash, AMFI, trust-cache or
other security check is skipped or weakened.

## Hashes

| File | SHA256 |
|---|---|
| kernel (`mach.development.m30lte`) | `391cb37910791bd0067db7b6fbcfd89d1b3a5611fa8e6b58340fd7ebfda0c26f` |
| payload | `369304987fa922bd049ac259a141073a34dc967255931158e12e4465cb14042c` |
| shim-boot.img | `ba40d65572e87115ba9bd62ef83a5d50c06201e2c393a1a7e7d994b109776068` |
| ios-boot.img | `3c79ab9cf998e5d39fdbb92c6077de73e4696c62c792357b1c20fa678dc55910` |

Entry VA `0xfffffff00740e488`. Shim region byte-identical to v6/v30/v31.

Cmdline: `debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292 rd=emmcroot0 emmcroot=USERDATA emmcprobe=1 emmcwrite=1`

## Validation (offline)

CI `45027980928` GREEN (iphoneos target, patch `0426` applied, LSE=0).
- Buildtree verifier: PASS (all critical patches reverse-apply cleanly).
- Kernel verifier: PASS (all 6 board-critical binary checks).
- Platform match: 9/9 PASS. CPU fallback: 17/17 PASS. ADT restore: 22/22 PASS.
- Packaging validator: PASS. Handoff structural check: 18/18 PASS.
- Focused tests: all applicable tests PASS, including
  `test_m30_internal_release_type.py` (v31 pstore evidence + compiled model of
  dyld-pager vnode recovery). `test_m30_16k_pages.py` is inapplicable because
  patch 0417 was removed by design.

## Status / next physical step

Not physically tested. Flash `shim-boot.img` to BOOT only, boot once, capture
and decode pstore immediately. Expected new diagnostics:
`M30 IRT diag 0: enter ...`, `M30 IRT diag 1: backing=... -> vnode=...`, then
either `M30 IRT diag 3/4/...` (specific failure) or
`M30 IRT: found ... / patched ...`.

No UI/lock-screen success claimed until physical evidence confirms it. BOOT
readback remains skipped; USERDATA/SYSTEM/RECOVERY untouched.
