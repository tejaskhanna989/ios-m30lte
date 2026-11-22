# iOS v33 physical boot — BOOT only, 2026-11-22

Flashed only `validation/ios-candidate-v33-out/shim-boot.img` to BOOT
(`heimdall flash --BOOT ... --no-reboot`), resumed with
`heimdall print-pit --resume`, booted once, forced back to TWRP, captured
pstore immediately. USERDATA/SYSTEM/RECOVERY untouched. BOOT readback skipped.

- Boot image SHA256: `d4f817b5df758b40225b14b497493f8d610bdad8d084f6055ca2515426efab6c`
- Pre-boot pstore (v32): `62ae73ff4ff92e7d6f9d5500c039e5bd4c1f3d2ba758473a643dc2cc26e3d301`
- Fresh pstore: `1291fb1a55f205c5bb2f5ccdaf35c5041ccc7a30a52487c680d5ec10747df51a`
- 16,372 B, 142 records.

Result: the retrigger worked. Captured records:

```
[061] M30 XCTEST: patched ascii off 0x42a4000+1164 (total 1)
[062] M30 IRT: retrigger after XCTEST patch (total 1)
[063] M30 IRT diag 0: enter state=0 vp=0xfffffff80d0fd780 pager=0xfffffff80cdcbe60 mo=0x42a4000 kaddr[0:4]=4c657665
[066] CRASH SpringBoard[26] sig 6 ...
[070] *** Terminating app ... SpringBoardUI.framework ...
```

This disproves the earlier dyld-pager-vnode theory: a valid vnode is available.
No further IRT diagnostic appeared. The only silent exits after `diag 0` are
the `Z_NOWAIT` buffer allocations, so v34 shrinks the chunk from 64 KB to one
4 KB page and adds diagnostics at both allocation sites.

No UI/lock-screen success claimed.
