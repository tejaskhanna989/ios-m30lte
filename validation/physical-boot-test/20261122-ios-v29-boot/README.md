# iOS v29 physical boot — class-probe fix fired, crash persists

Device: m30lte, serial 320081735bb166a3, TWRP 3.4.03.0.0-UNOFFICIAL.
Candidate: v29 (`0c494373dc23d735d809c095c3f123c4b0ad905a`), shim-boot.img
SHA256 `8956e1c6c95ea6b7df2933b007041afef0d585e3a3060ecd8756d9ad37a095a4`.
BOOT flashed only via Heimdall (`--no-reboot`); USERDATA/SYSTEM/RECOVERY untouched.
No BOOT readback performed.

## Evidence

| File | SHA256 |
|---|---|
| `raw/pmsg-ramoops-0` | `c0407fcea26f2f29d3536f78dca6eef2954b67cb051ede165d6a59b83892b5f1` |
| `raw/pre-pmsg-ramoops-0` | `edc4bf88ae53bcba231415345c96b80edb1865191865dbe5b0f1eb3cc3058089` (v28 log) |

Decoded: 16372 bytes, 146 XNU records. Same deep userspace sequence as v28.

## Confirmed milestones (physical)

- Deep genuine iOS 20H392 userspace: launchd, dyld cache loader, HFSX root mount,
  full daemon set, `SpringBoard[27]` starts.
- Patch `0425` fired: `[053] M30 XCTEST: retargeted SpringBoardUI class probe (ascii)`.
  The kernel-side fix-up executed on a code-signed page fault after `cs_validate_page()`.

## Result: fix-up insufficient

SpringBoard still aborts with the same assertion:

```
[055] CRASH SpringBoard[27] sig 6 ... slide 0xc500000 mh 0x100788000
[059]/[062]/[126] *** Terminating app due to uncaught exception
  'NSInternalInconsistencyException', reason: 'This process should not be
  linking or loading SpringBoardUI.framework (<rdar://problem/26143166>)'
```

The assertion string is still emitted at `[123]`, confirming the check still fails.

## Root-cause analysis

Re-reading LiveContainer commit `d2a329d` shows the bypass has **two** parts:

1. `_internal_release_type` in `libsystem_darwin.dylib` set to `3`, which makes
   `os_variant_has_internal_content()` return true (replaces the older breakpoint
   hook that forced the function to return true).
2. `objc_allocateClassPair(NSObject.class, "XCTestConfiguration", 0)` +
   `objc_registerClassPair()` — labeled "Bypass iOS 16's +[SpringBoardUI load]
   crash".

Patch `0425` only retargeted **one** occurrence of the class-name string on
**one** page (one-shot flag `m30_xctest_probe_fixed`). The dyld shared cache
contains multiple copies/forms of the string, and the actual probe's call-site
literal may be on a different page that was never patched. Simply changing a
string literal also cannot create the registered Objective-C class that the
runtime lookup expects in all code paths.

## Next step

Extend the fix-up to patch **every** occurrence on **every** code-signed page
(remove one-shot guard, add per-page diagnostics with `vmp_offset`), and evaluate
a complementary `_internal_release_type = 3` fix-up for
`os_variant_has_internal_content()`. No UI/lock-screen success is claimed.
BOOT readback remains skipped; USERDATA/SYSTEM/RECOVERY untouched.
