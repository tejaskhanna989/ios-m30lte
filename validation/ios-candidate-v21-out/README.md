# iOS candidate v21 — platform-binary marking for launchd boot tasks

Baseline: v18 exclusively. 4K config preserved (no 0417). Work on `main` @ `baa5b33`.
No physical operations performed for v21.

## Exact cause and fix

v20 physical: daemon crash loop fixed (0418), genuine iOS userspace runs real
launchd boot tasks, but launchd panicked:
`boot task is not a platform binary (fsck, /sbin/fsck)` via csops — a userspace
decision, not a kernel signature failure. On Apple hardware all iOS system
binaries are platform binaries via the static trust cache; SWEET has none.

**v21 fix (patch `0419-m30-amfi-platform-binaries.patch`):** `sweet_amfi_vnode_check_signature`
marks every validated signature as CS_PLATFORM_BINARY (not just MNT_ROOTFS ones),
matching genuine iOS trust-cache behavior. Signature/page hashes still fully
verified by the kernel. Adds a diagnostic log for the platform decision.
No bypass boot-args; 4K config, shim, AMFI, HFSX, maxmem=292 preserved.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `90b41e398710e9d8b040c0bc5db828148dbbb6ebc7c2b0decb8820edab940428` |
| payload | `860a17f925516c7b6598733d91714d13150d5437dc6a96de0c7a6f1142b8de98` |
| shim-boot.img | `9db28ba44e213d44541943da520cb3f07decb7ca8b07a9abd6b2595bb9e35d10` |

Cmdline: `debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292 rd=emmcroot0 emmcroot=USERDATA emmcprobe=1 emmcwrite=1`

## Validation (offline)

CI `44989935348` green (iOS target, LSE=0). Buildtree/kernel/platform/CPU/ADT/
handoff/packaging all PASS, GIC 5/6. All focused tests PASS. Shim byte-identical
to proven v6. 4K config confirmed (no 0417).

## Status / next physical step

Not physically tested. Flash v21 BOOT only, one boot, capture pstore immediately.
Expected: launchd boot tasks pass platform check (fsck runs), progress toward
SpringBoard. No success claim until device evidence proves it.
