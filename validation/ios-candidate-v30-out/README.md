# iOS candidate v30 — all-copy SpringBoardUI class-probe fix-up

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `d80d556`.
No physical operations for v30 yet.

## What changed from v29

v29 physical proved the one-shot fix-up fired on the first page containing the
`XCTestConfiguration` literal (timing suggests `logd`), but SpringBoard still
aborted in `+[SpringBoardUI load]`. The dyld shared cache has multiple copies of
the literal on different pages; SpringBoard's copy was never patched.

Patch `0425` is regenerated to:
- Remove the one-shot guard — patch every code-signed page as it faults in.
- Patch **every** occurrence within a page (ASCII C-string and UTF-16 NSString
  forms), not just the first.
- Log each patch with object offset + running total for physical diagnostics.

It still runs **strictly after** `cs_validate_page()` and does not skip, disable
or weaken any signature, hash, AMFI, trust-cache or security check.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `818b741d27a8c39b8c202b4bfc9c2c7135a58b7c9e3288bf49a66f7cdb5e30b5` |
| payload | `dab66b30c039cf41140fad70441d90acf928f101118c1360b019c29cba26518f` |
| shim-boot.img | `8bcd7d2d8898e0123a42c9f4b1ffff5a1fb04b14e744f72f13f125440d6fff68` |

Cmdline: `debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292 rd=emmcroot0 emmcroot=USERDATA emmcprobe=1 emmcwrite=1`

## Validation (offline)

CI `45017347740` green: iOS target confirmed, LSE=0, regenerated 0425 applied
(no one-shot guard in code). Buildtree/kernel/platform 9/9/CPU 17/17/ADT 22/22/
packaging PASS; handoff 18/18; GIC 5/6 (known inapplicable DAIF check); all 11
focused tests PASS including the updated `test_m30_xctest_class_probe`. Shim
region byte-identical to v6.

## Status / next physical step

Not physically tested. Flash v30 BOOT only, one boot, capture pstore immediately.
Expected: multiple `M30 XCTEST: patched ascii/utf16 off 0x...` records and,
if the check is a presence probe, SpringBoard proceeding past `+load`. If the
assertion persists, next step is a `_internal_release_type = 3` fix-up (the
other half of LiveContainer's bypass). No UI/lock-screen success claimed until
physical evidence confirms it. BOOT readback remains skipped; USERDATA/SYSTEM/
RECOVERY untouched.
