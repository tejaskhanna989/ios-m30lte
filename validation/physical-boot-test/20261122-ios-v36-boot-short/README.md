# iOS v36 physical boot — BOOT only, 2026-11-22

Two boots of `validation/ios-candidate-v36-out/shim-boot.img`
(`2d629c034d114ff88b3dab71d75bea80088fee5868e804c55ef0bffc81c0817f`).
USERDATA/SYSTEM/RECOVERY untouched. BOOT readback skipped.

## Boot 1 (long, 150 s)

Fresh pstore `a8c137098fb4c4e7d2f3899c212c9c7090b2b30f1233184e063517a8ab452525`
(16,372 B, 163 records). The 16 KB ring wrapped completely: the first captured
record starts mid-message at `0x14`, and all early XCTEST/IRT lines are gone.

This boot reached substantially deeper userspace than v35: `backboardd[57]`,
`lsd[94]`, `powerd`, `securityd[111]`, `identityservices[53]`, `mediaserverd`,
`liveactivitiesd`, etc. The SpringBoardUI assertion (`STR ... SpringBoardUI
framework`) is still present, and `lsd`/`backboardd` crash with sig 6 plus a
`securityd` sig 5. No recursive-lock panic.

## Boot 2 (short, ~35 s)

Fresh pstore `97857d5391a3475e873cd10a54acfabb2765d7fe0f74295b06bd0d8daa148346`
(16,372 B, 175 records). Early lines captured:

```
[024] load_init_program: attempting to load /usr/appleinternal/sbin/launchd.development
[025] load_init_program: attempting to load /sbin/launchd
[026] M30 IRT diag 0: enter state=0 vp=0xfffffff818dbbab0 pager=0xfffffff818d5be60 mo=0x14000 kaddr[0:4]=e0010034
[027] M30 IRT diag 21: worker started vp=0xfffffff818dbbab0
[028] M30 IRT diag 4: no dyld magic: cffaedfe
```

Root cause: the worker started at `load_init_program` on launchd's Mach-O
vnode (`cffaedfe` = Mach-O 64-bit LE), long before the SpringBoard XCTEST patch
retrigger. v37 gates worker start on `m30_irt_retriggered`, records the path on
wrong magic, and resets state so a later post-retrigger fault can retry with
the DSC vnode.

No UI/lock-screen success claimed.
