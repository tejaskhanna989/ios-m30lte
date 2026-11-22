# iOS candidate v33 — replay IRT diagnostics after XCTEST patch

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `32f3936`.
No physical operations for v33 yet.

## What changed from v32

v32 BOOT-only physical proved the pmsg ring is full/wrapped (record 0 begins
mid-message) and all one-shot `M30 IRT` diagnostics were emitted too early to
survive in the 16 KB capture. Disassembly of the v32 kernel confirmed the fix-up
is compiled and called immediately after `cs_validate_page()` in
`_vm_page_validate_cs_mapped_slow`.

Patch `0426` now replays the IRT state machine exactly once when the
SpringBoard-related XCTest literal is patched (`m30_xctest_patch_count != 0`):
it resets `m30_irt_state`, `m30_irt_file_offset`, `m30_irt_last_err` and
`m30_irt_diag_seen`, prints `M30 IRT: retrigger after XCTEST patch`, then reruns
the DSC symbol scan on subsequent SpringBoard code-page faults. Diagnostics
therefore land next to the XCTest record inside the captured log window.

All file access remains read-only (`UIO_READ`); the in-memory page is patched
strictly after `cs_validate_page()`. No signature, hash, AMFI, trust-cache or
other security check is skipped or weakened.

## Hashes

| File | SHA256 |
|---|---|
| kernel (`mach.development.m30lte`) | `1fd31bc33cc8d5277ed1a95d5c408d2f2755230ac9ec0607cf3d3e2bf1754f20` |
| payload | `1c97fcf2b4628ea6201e4717a457350c1f55c3628d80bc8fb27b48d74647d268` |
| shim-boot.img | `d4f817b5df758b40225b14b497493f8d610bdad8d084f6055ca2515426efab6c` |

Entry VA `0xfffffff00740e488`. Shim region byte-identical to v6/v30/v31/v32.

Cmdline: `debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292 rd=emmcroot0 emmcroot=USERDATA emmcprobe=1 emmcwrite=1`

## Validation (offline)

CI `45031964267` GREEN (iphoneos target, patch `0426` retrigger applied, LSE=0).
- Buildtree verifier: PASS. Kernel verifier: PASS.
- Platform match: 9/9 PASS. CPU fallback: 17/17 PASS. ADT restore: 22/22 PASS.
- Packaging validator: PASS. Handoff structural check: 18/18 PASS.
- Focused tests: all applicable tests PASS, including
  `test_m30_internal_release_type.py` with v32 physical evidence and the
  retrigger model. `test_m30_16k_pages.py` is inapplicable (0417 removed).

## Status / next physical step

Not physically tested. Flash `shim-boot.img` to BOOT only, boot once, force back
to TWRP, capture and decode pstore. Expected near the XCTest record:
`M30 IRT: retrigger after XCTEST patch`, followed by `M30 IRT diag 0: enter ...`
and either a specific failure or `M30 IRT: found ...` / `M30 IRT: patched ...`.

No UI/lock-screen success claimed until physical evidence confirms it. BOOT
readback remains skipped; USERDATA/SYSTEM/RECOVERY untouched.
