# iOS v35 physical boot — BOOT only, 2026-11-22 — deferred scan OK

Flashed only `validation/ios-candidate-v35-out/shim-boot.img` to BOOT, resumed,
booted once, forced back to TWRP, captured pstore immediately.
USERDATA/SYSTEM/RECOVERY untouched. BOOT readback skipped.

- Boot image SHA256: `83c2ca87928ecef5cad9b8a5ba412f2d750c8483d94f2192b5b6b082d6fe3618`
- Fresh pstore: `c38189acd2b8e4718ef4d5ed50ed5e80837f5289f9c5d7ae28126ca4eff9a5a9`
- 16,372 B, 148 records.

Result: the one-shot kernel thread ran with no recursive-lock panic. Captured:

```
[068] M30 IRT: retrigger after XCTEST patch (total 1)
[069] M30 IRT diag 0: enter state=0 vp=0xfffffff67d460670 pager=0xfffffff3ca5ac5c0 mo=0x42a4000 kaddr[0:4]=4c657665
[070] M30 IRT diag 21: worker started vp=0xfffffff67d460670
[071] M30 IRT diag 8: header map_off=0x200 map_cnt=1 ls_off=0x0
[072] M30 IRT diag 24: header has no symbol table
[077] CRASH SpringBoard[27] sig 6 ...
```

The v34 `lock_rw.c:877` panic is gone. The main dyld shared cache header reports
`localSymbolsOffset == 0`, so local symbols are not in the main cache: on this
device they live in the `<cache>.symbols` companion file (the same split-symbol
layout LiveContainer handles). v36 opens that companion file from the deferred
worker, re-reads its DSC header, and continues the symbol scan there.

No UI/lock-screen success claimed.
