# iOS v32 physical boot — BOOT only, 2026-11-22

Flashed only `validation/ios-candidate-v32-out/shim-boot.img` to BOOT
(`heimdall flash --BOOT ... --no-reboot`), resumed with
`heimdall print-pit --resume`, booted once, forced back to TWRP, captured
pstore immediately. USERDATA/SYSTEM/RECOVERY untouched. BOOT readback skipped.

- Boot image SHA256: `ba40d65572e87115ba9bd62ef83a5d50c06201e2c393a1a7e7d994b109776068`
- Pre-boot pstore (v31): `e6210f009d706c13c46547593ff7ffcb2abae80520028a362dcbf8911b1c3c0c`
- Fresh pstore: `62ae73ff4ff92e7d6f9d5500c039e5bd4c1f3d2ba758473a643dc2cc26e3d301`
- 16,372 B, 145 records; first record starts mid-message -> ring has wrapped.

Result: deep genuine iOS userspace confirmed (launchd, cache signing, many
daemons), `M30 XCTEST: patched ascii off 0x42a4000+1164 (total 1)` fired, but
`CRASH SpringBoard[27] sig 6` and the SpringBoardUI assertion persist.
Zero `M30 IRT` records in the captured window even though the kernel contains
all 20 `M30 IRT diag` format strings.

Root cause of missing diagnostics: the pmsg ring is only 16 KB and wrapped;
the one-shot IRT diagnostics are emitted at the first code-signed page faults
early in boot and are overwritten before the captured SpringBoard records.
The kernel binary itself is correct (verified disassembly: IRT fix-up and
diagnostics are in `_vm_page_validate_cs_mapped_slow` immediately after
`cs_validate_page()`).

Next: patch 0426 v33 replays the IRT state machine and re-arms one-shot
diagnostics once, when the SpringBoard-related XCTest literal is patched, so
the outcome is captured next to the XCTest line.

No UI/lock-screen success claimed.
