# iOS v30 physical boot — all-copy string patch fired, crash persists

Device: m30lte, serial 320081735bb166a3, TWRP 3.4.03.0.0-UNOFFICIAL.
Candidate: v30 (`a02f1978987413f93ff97d124de04bcdbf8d916e`), shim-boot.img
SHA256 `8bcd7d2d8898e0123a42c9f4b1ffff5a1fb04b14e744f72f13f125440d6fff68`.
BOOT flashed only via Heimdall (`--no-reboot`); USERDATA/SYSTEM/RECOVERY untouched.
No BOOT readback performed.

## Evidence

| File | SHA256 |
|---|---|
| `raw/pmsg-ramoops-0` | `e21a9dc50314ac1366a7db81baa904d81d372fc593669ff484323fc758ede4f9` |
| `raw/pre-pmsg-ramoops-0` | `c0407fcea26f2f29d3536f78dca6eef2954b67cb051ede165d6a59b83892b5f1` (v29 log) |

Decoded: 16372 bytes, 150 XNU records.

## Confirmed milestones (physical)

- Deep genuine iOS 20H392 userspace: launchd, dyld cache loader, HFSX root mount,
  full daemon set, `SpringBoard[27]` starts.
- Patch 0425 (v30) fired with diagnostics:
  `[044] M30 XCTEST: patched ascii off 0x42a4000+1164 (total 1)` — exactly ONE
  occurrence exists in the code-signed pages and it was rewritten to `NSObject`.

## Result: string patching alone is insufficient

SpringBoard still aborts with the same assertion:

```
[046] CRASH SpringBoard[27] sig 6 ... slide 0x2d8cc000 mh 0x100f18000
[050]/[076]/[089] *** Terminating app due to uncaught exception
  'NSInternalInconsistencyException', reason: 'This process should not be
  linking or loading SpringBoardUI.framework (<rdar://problem/26143166>)'
```

## Root-cause analysis

LiveContainer commit `d2a329d` bypasses this assertion with TWO steps that both
appear necessary (the check likely requires both conditions):

1. `_internal_release_type = 3` in `libsystem_darwin.dylib` — makes
   `os_variant_has_internal_content()` return true. This was the ORIGINAL hook
   (forced the function to return true), simply reimplemented in the new commit.
2. `objc_allocateClassPair(..., "XCTestConfiguration", ...)` + register — the NEW
   addition in d2a329d, labeled "Bypass iOS 16's +[SpringBoardUI load] crash".

Patch 0425 handles part 2 (string retarget). It fires but the assertion remains,
so part 1 is also required. The dyld shared cache has only one `XCTestConfiguration`
literal (the v30 diagnostic shows `total 1`), confirming the one-shot guard was
not the issue — the second bypass is genuinely needed.

## Next step

Patch `0426` locates `_internal_release_type` through the dyld shared cache
local-symbol table (read-only `vn_rdwr`, in-memory page patch only) and sets it
to 3 strictly after `cs_validate_page()`. No UI/lock-screen success is claimed.
BOOT readback remains skipped; USERDATA/SYSTEM/RECOVERY untouched.
