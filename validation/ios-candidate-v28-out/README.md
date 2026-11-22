# iOS candidate v28 — clean production candidate (diagnostics removed)

Baseline: v18 exclusively. 4K config preserved (no 0417). Work on `main` @ `e66cd8e`.
No physical operations for v28 yet.

## What changed from proven v27

v27 physical proved the full functional fix chain works: full-page hash validation
preserves `CS_VALID`, process `CS_SIGNED`/platform reporting works, the daemon
crash loop is gone, and genuine iOS userspace starts SpringBoard. The only
difference in v28 is **removal of the diagnostic printfs** that flooded the 16KB
pstore ring buffer (0420/0421/0423 deleted; the 0419 platform diagnostic printf
removed; 0424 regenerated to apply after the removals). Functional behavior is
identical to v27; only log noise is removed so the next pstore captures the full
boot sequence instead of wrapping.

## Functional fix chain (unchanged from v27)

- `0418` — full 16K code-directory block validation (4 resident 4K pages,
  full 16K SHA-256, fail-secure if unavailable).
- `0419` — mark every validated signature as platform binary (trust-cache stand-in),
  keeping signature/page hashes fully verified.
- `0422` — loader gathers full 16K hash block from vnode when CD page shift > 4K.
- `0424` — loader validates the full 4096-byte page (`MIN(PAGE_SIZE, alloc_size)`)
  so the genuine CD hash matches; `CS_VALID` stays set, process `CS_SIGNED` and
  platform reporting propagate correctly.
- 4K XNU config, shim, handoff, HFSX root mount, AMFI, maxmem=292 all preserved.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `07e043eb2b4e4d516b27ddeb00c2d1918f20d7376dbfed209ccd1520e5c2819f` |
| payload | `9a83a3ec64e9839a863a6f7676cff467eac77722e75b5c013d5b8f3f0cb2439e` |
| shim-boot.img | `03fa2d70cdb5b169ce9d124199645594c96640f87ec3b6d1c0eb792d581434a6` |

Cmdline: `debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292 rd=emmcroot0 emmcroot=USERDATA emmcprobe=1 emmcwrite=1`

## Validation (offline)

CI `45008761962` green: iOS target confirmed, LSE=0. No 04xx patch skipped.
Diagnostics absent from kernel (pre-existing policy string only).
Buildtree/kernel/platform 9/9/CPU 17/17/ADT 22/22/handoff 18/18/packaging PASS;
GIC 5/6 (known inapplicable DAIF check); all 10 focused tests PASS.
Shim region byte-identical to proven v6. 4K config confirmed.

## Status / next physical step

Not physically tested. Flash v28 BOOT only, one boot, capture pstore immediately.
Expected: same deep boot as v27 without diagnostic wrap — visible root mount,
launchd/dyld, platform binaries, SpringBoard start. No success claim beyond
existing v27 evidence until v28 device evidence is captured.
