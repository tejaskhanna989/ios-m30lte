# iOS candidate v29 — SpringBoardUI class-probe fix-up

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `99b1261`.
No physical operations for v29 yet.

## What changed from v28

v28 physical proved the platform/CDS fixes work and isolated the remaining
blocker: `SpringBoard[26]` aborts in `+[SpringBoardUI load]` with
`NSInternalInconsistencyException: This process should not be linking or loading
SpringBoardUI.framework (<rdar://problem/26143166>)`. LiveContainer works around
the identical iOS 16 assertion by registering an `XCTestConfiguration`
Objective-C class before the probe runs.

Patch `0425` satisfies the same class-presence probe from the kernel: on the
page fault that makes the probe string accessible, it retargets the
`XCTestConfiguration` C-string/UTF-16 literal in the dyld shared cache page to
an always-present class name (`NSObject`). It runs **strictly after**
`cs_validate_page()` and does not skip, disable or weaken any signature, hash,
AMFI, trust-cache or security check. All v28 functional fixes are unchanged.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `384b760347bf9f24c7e9954b9c6bd21bf14f783783c017d674bb9eb53e4be287` |
| payload | `1139031c88ffe55cfc188b12745a43efdc6e33ac549406a5a01e4d81c5eec1f9` |
| shim-boot.img | `8956e1c6c95ea6b7df2933b007041afef0d585e3a3060ecd8756d9ad37a095a4` |

Cmdline: `debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292 rd=emmcroot0 emmcroot=USERDATA emmcprobe=1 emmcwrite=1`

## Validation (offline)

CI `45014061864` green: iOS target confirmed, LSE=0, patch 0425 applied (not
skipped). Buildtree/kernel/platform 9/9/CPU 17/17/ADT 22/22/handoff 18/18/
packaging PASS; GIC 5/6 (known inapplicable DAIF check); all 11 focused tests
PASS, including `test_m30_xctest_class_probe`. Shim region byte-identical to v6.

## Status / next physical step

Not physically tested. Flash v29 BOOT only, one boot, capture pstore immediately.
Expected: same deep boot as v28, with SpringBoard proceeding past `+load` if the
class-probe retarget works. No UI/lock-screen success is claimed until physical
evidence confirms it. BOOT readback remains skipped; USERDATA/SYSTEM/RECOVERY
untouched.
