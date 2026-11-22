# iOS candidate v35 — deferred DSC symbol scan

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `309d7d5`.
No physical operations for v35 yet.

## What changed from v34

v34 physically panicked before userspace: inline `vn_rdwr()` in the page-fault
path recursed on the held `vm_object` lock. Patch `0426` now runs the
read-only DSC symbol scan on a one-shot deferred kernel thread
(`kernel_thread_start_priority`, with `vnode_ref`/`vnode_rele`). The fault
path only recovers the vnode and patches an already-faulted in-memory page once
the symbol file offset is known. No signature/hash/AMFI/trust-cache check is
skipped or weakened; the file on disk is never written.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `5c7b0938cb660889576034f7829ae9a26ee7a8b131e638191bd6b9ce9f9cb5e5` |
| payload | `7d17f990b96c5dffba3d7421b91a9f2072892c421920927d648f9eae5e9be32e` |
| shim-boot.img | `83c2ca87928ecef5cad9b8a5ba412f2d750c8483d94f2192b5b6b082d6fe3618` |

Entry VA `0xfffffff00740e488`. Shim byte-identical to v6/v30-v34.

## Validation

CI `45037476029` GREEN (iphoneos, LSE=0). Buildtree PASS, kernel PASS,
platform 9/9, CPU 17/17, ADT 22/22, packaging PASS, handoff 18/18, all
applicable focused tests PASS (0417 inapplicable by design). Standalone C
syntax check of the new fix-up block is clean.

## Next physical step

BOOT-only flash, one boot, force back to TWRP, capture pstore. Expected:
`M30 IRT: retrigger`, `diag 0`, `diag 21 worker started`, then `diag 3/4/...`
or `M30 IRT: found ...` / `M30 IRT: patched ...`, with no recursive-lock panic.

No UI success claimed; BOOT readback skipped; USERDATA/SYSTEM/RECOVERY untouched.
