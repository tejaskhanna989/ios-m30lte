# iOS candidate v31 — `_internal_release_type = 3` fix-up

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `e0682cf`.
No physical operations for v31 yet.

## What changed from v30

v30 physical proved the all-copy `XCTestConfiguration` string fix-up fired
(`total 1`, exactly one literal in the shared cache) but SpringBoard still
aborted in `+[SpringBoardUI load]`. LiveContainer commit `d2a329d` applies two
changes that appear to be ANDed:

1. `_internal_release_type = 3` in `libsystem_darwin.dylib`, making
   `os_variant_has_internal_content()` return true;
2. registration of an `XCTestConfiguration` Objective-C class.

Patch `0425` handles part 2. New patch `0426` handles part 1 by locating the
`_internal_release_type` global via the dyld shared cache local-symbol table
and setting the **already-faulted in-memory page** to 3. The file on disk is
opened read-only and is never written. The fix-up runs strictly **after**
`cs_validate_page()`; no signature, hash, AMFI, trust-cache or other security
check is skipped or weakened.

Compile note: `vm_fault.c` cannot include `<sys/vnode.h>` in this build (it
resolves to the non-self-contained exported public header). Patch 0426 includes
`<sys/uio.h>` + `<sys/kauth.h>` and declares `vn_rdwr()` locally instead.

## Hashes

| File | SHA256 |
|---|---|
| kernel (`mach.development.m30lte`) | `d4676b0703b274b3f31fdbe93833a4e3be9954e13cb9ee50a56004d7fe169569` |
| payload | `8e0451fdb46330a0952c2e4857d74cff02b4dee46ab869554d651c56568c6516` |
| shim-boot.img | `b9a6ecf59322c5ae1c21d7026f92982af6bf5183635ce6a3be06ead736400b17` |
| ios-boot.img | `b2dea98cd728ea81ac2b36efcafb8503c8e0146b390b65b77bef1aa99d539d53` |

Kernel size 16,788,896 bytes; payload size 16,161,120 bytes.
Entry VA `0xfffffff00740e488`. Shim region byte-identical to v6/v30.

Cmdline: `debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292 rd=emmcroot0 emmcroot=USERDATA emmcprobe=1 emmcwrite=1`

## Validation (offline)

CI `45022958043` GREEN (iphoneos target, patch `0426` applied, LSE=0).
- Buildtree verifier: PASS (critical patches reverse-apply cleanly).
- Kernel verifier: PASS (all 6 board-critical binary checks).
- Platform match: 9/9 PASS. CPU fallback: 17/17 PASS. ADT restore: 22/22 PASS.
- Packaging validator: PASS. Handoff structural check: 18/18 PASS.
- Focused tests: all applicable tests PASS, including
  `test_m30_internal_release_type.py` and `test_m30_xctest_class_probe.py`.
  `test_m30_16k_pages.py` is inapplicable because patch 0417 was removed.

## Status / next physical step

Not physically tested. Flash `shim-boot.img` to BOOT only, boot once, capture
and decode pstore immediately. Expected diagnostics:
`M30 IRT: found _internal_release_type ...` followed by
`M30 IRT: patched _internal_release_type ...`. If neither appears and the
SpringBoardUI assertion persists, the next step is to add one-shot failure
diagnostics to patch 0426 (e.g. `localSymbolsOffset == 0` or symbol not found)
and iterate. No UI/lock-screen success claimed until physical evidence confirms
it. BOOT readback remains skipped; USERDATA/SYSTEM/RECOVERY untouched.
