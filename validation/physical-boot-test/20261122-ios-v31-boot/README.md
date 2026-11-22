# iOS v31 physical boot — IRT fix-up emitted no diagnostics, crash persists

Device: m30lte, serial 320081735bb166a3, TWRP 3.4.03.0.0-UNOFFICIAL.
Candidate: v31 (`ffc2ccb`), shim-boot.img
SHA256 `b9a6ecf59322c5ae1c21d7026f92982af6bf5183635ce6a3be06ead736400b17`.
BOOT flashed only via Heimdall (`--no-reboot`, "BOOT upload successful");
USERDATA/SYSTEM/RECOVERY untouched. One boot. No BOOT readback performed.

## Evidence

| File | SHA256 |
|---|---|
| `raw/pmsg-ramoops-0` | `e6210f009d706c13c46547593ff7ffcb2abae80520028a362dcbf8911b1c3c0c` |
| `raw/pre-pmsg-ramoops-0` | `e21a9dc50314ac1366a7db81baa904d81d372fc593669ff484323fc758ede4f9` (v30 log) |

Decoded: 16372 bytes, 143 XNU records.

Actions: `adb reboot download`; `heimdall detect` OK; `heimdall flash --BOOT
validation/ios-candidate-v31-out/shim-boot.img --no-reboot` (exit 0);
`heimdall print-pit --resume` (read-only PIT, ends session with reboot into
flashed BOOT). Phone booted into iOS and disconnected from USB; user forced it
back to TWRP with hardware keys, pstore captured immediately.

## Confirmed milestones (physical)

- Deep genuine iOS 20H392 userspace again: launchd boot tasks, dyld cache
  loader, HFSX root mount, full daemon set, `SpringBoard[27]` starts.
- Patch 0425 fired as in v30:
  `[046] M30 XCTEST: patched ascii off 0x42a4000+1164 (total 1)`.

## Result: patch 0426 was completely silent

- `strings` on the linked kernel confirms both `M30 IRT: found ...` and
  `M30 IRT: patched ...` format strings are compiled in.
- The pstore contains **zero** `M30 IRT` records — neither success nor any
  failure diagnostic (v31 had no failure diagnostics; every failure path
  silently set `M30_IRT_STATE_FAILED`).
- SpringBoard still aborts with the same assertion:
  `[049] CRASH SpringBoard[27] sig 6 ...`
  `[053] STR *** Terminating app ... 'NSInternalInconsistencyException',
  reason: 'This process should not be linking or loading SpringBoardUI.framework
  (<rdar://problem/26143166>)'`

## Root cause (offline analysis, not device proof)

The dyld shared cache is mapped through the **dyld pager** (`dyld_pager_ops`),
not the vnode pager. `vm_page_validate_cs_mapped_slow()` obtains its vnode via
`vnode_pager_lookup_vnode(pager)`, which returns `NULL` for non-vnode pagers.
Patch 0426's `vp == NULL` guard therefore returned on every cs page fault,
including the DSC page where 0425 fired — explaining the complete silence.

## Next step

v32 patch 0426: recover the DSC file vnode through the generic
`memory_object_backing_object()` callback (dyld pager -> backing VM object ->
vnode pager -> vnode) and add one-shot diagnostics at every failure point
(header magic, `vn_rdwr` error, string-pool/nlist/mapping lookups). Rebuild in
CI, revalidate, package, BOOT-only flash, one boot, capture pstore.

No UI/lock-screen success claimed. BOOT readback remains skipped;
USERDATA/SYSTEM/RECOVERY untouched.
