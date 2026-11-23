# iOS candidate v50 — XCTEST gate restored, fast path opens it

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `4adddb7e`.

## Why this candidate exists

v49 physically regressed: starting the IRT worker on the first dyld-pager fault
produced `state=4`, `hits=0`, `tries=0`, and no patch marker. The captured
replay still reached `comp=0 ls=0x4000`, showing the worker picked a companion
before the pager had the real DSC, then failed before mapping.

v50 keeps v49's bitmap-fast-path fix-ups but restores the v48-proven timing:

1. The worker again starts only after the XCTest literal is patched:
   `m30_irt_retriggered && !m30_irt_thread_started`.
2. The retrigger reset is factored into `m30_irt_retrigger_after_xctest()` and
   called from **both** validation paths, so an XCTest literal rewritten on the
   bitmap fast path opens the same gate instead of being ignored.
3. Both durable heartbeat forms now carry `xctest=<count>`. This proves in the
   captured pmsg ring whether the class-name fix-up fired, even after wrap.

All file reads remain `UIO_READ`. The only write is in-memory after validation.
No signature, hash, AMFI, trust-cache or page-validation check is weakened.

## CI history

| Run | Result |
|---|---|
| `45162621882` | v49 GREEN; 0426 applied; physically tested and found to regress |
| `45169239555` | v50 GREEN; both `0426` and `0427` applied; buildtree matches intended source; entry VA correct |

## Hashes

| File | SHA256 |
|---|---|
| kernel | `a439f7070b90577e53703a1190ddad06c3b0d40e2b7fce8d6a19acf6e7168a41` |
| payload | `609b10f498b0b501db86ed378f46cc844da27dd26470c9b2e372147965af3b01` |
| shim-boot.img | `859b5d08dab9dd2f7a9aff80eb9c5f2c77ea6677969480f8ece332b7de74b07a` |

Kernel entry remains `0xfffffff007410488`. Shim Image/ELF and the shim region
inside `shim-boot.img` remain byte-identical to the v31 reference.

## Validation

CI `45169239555` GREEN (12m16s). Buildtree PASS, kernel PASS, platform 9/9,
CPU 17/17, ADT 22/22, packaging PASS, handoff 18/18, all applicable focused
tests PASS (`test_m30_16k_pages.py` intentionally inapplicable). Patch order
`0426 -> 0427` preflighted with `git apply --check` and verified to reproduce
the intended `vm_fault.c` byte-for-byte.

## Next physical step

BOOT-only flash; capture pstore. Check the heartbeat for `state=3` and
`xctest=<nonzero>`, look for `M30 XCTEST: patched` / `M30 IRT: retrigger`, and
compare ordering with any SpringBoardUI assertion. Do not equate a loaded
SpringBoard process with a visible UI.

No UI success claimed; BOOT readback skipped; USERDATA/SYSTEM/RECOVERY untouched.
