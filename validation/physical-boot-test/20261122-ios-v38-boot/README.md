# iOS v38 physical boot — BOOT only, 2026-11-22 — status replay works

Flashed `validation/ios-candidate-v38-out/shim-boot.img`
(`73378ba9e48dbd58c1ec967a266a74d6ba5016d3b73059f568e3a4b85b98b919`) to BOOT
only, resumed, booted once, forced back to TWRP. USERDATA/SYSTEM/RECOVERY
untouched. BOOT readback skipped.

Fresh pstore `cb467b90af306023c6821670d7bac759a63a33a262b2ec5bdca53201d2543d2d`
(16,372 B, 152 records).

Success: the periodic status replay survived the ring wrap. Records 63-151
contain `M30 IRT status: state=4 off=0x0 err=0 replay=0..15`.

Critical evidence (records 35-42):

```
[035] M30 XCTEST: patched ascii off 0x42a4000+1164 (total 1)
[036] M30 IRT: retrigger after XCTEST patch (total 1)
[037] M30 IRT diag 0: enter state=0 vp=0xfffffff2670ee230 ... mo=0x42a4000 kaddr=4c657665
[038] M30 IRT diag 21: worker started vp=0xfffffff2670ee230
[039] M30 IRT diag 8: header map_off=0x200 map_cnt=1 ls_off=0x0
[040] M30 IRT diag 28: opened symbols file /System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.31 vp=0xfffffff2670ee230
[041] M30 IRT diag 30: symbols map_off=0x200 map_cnt=1 ls_off=0x0
[042] M30 IRT diag 24: header has no symbol table
[045] CRASH SpringBoard[27] sig 6
```

The retrigger gate worked — the worker started on the real DSC vnode. But
`vn_getpath()` reports `plen` including the terminating NUL, so our `.symbols`
suffix was written *after* the NUL: the printed path has no `.symbols`, and the
opened vnode (`0xfffffff2670ee230`) is identical to the main DSC vnode. We
re-parsed the main cache and failed again with `ls_off=0`.

v39 computes the string length manually before appending `.symbols`, and logs
both `plen` and the opened/main vnode pointers for confirmation.

No UI/lock-screen success claimed.
