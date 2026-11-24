# iOS candidate v59 — busy-peer CS overlay

Baseline: v58 (`df43336a`). v59 source: `dccbc33b`. MAIN only.

## Why

v58 physically proved SpringBoard launches (pid 739) but aborts with an NS
exception, and backboardd crash-loops at the same PC `0x1cd897198`. It also
showed CS_VALID still being stripped from `backboardd` and a later
`SpringBoard` pid via `cs_invalid_page` (`0x22000000`). In v57/v58 the 16K
readback rejected a whole block when a non-faulting peer page was busy or
cleaning, so that page fell back to a single 4K validation and lost CS_VALID.

v59 keeps the full 16K hash and resident-byte overlay but copies busy/cleaning
peer pages through `phystokv()` instead of rejecting them. Only absent slots go
to the vnode/UPL, so the busy faulting page is still excluded and is hashed from
`kaddr`. A torn or tampered page can only fail the full hash. Per-reason
counters `cfa`/`cfi`/`cfp` (allocation, I/O, pager) are replayed in the IRT
heartbeat. No security check is weakened.

## CI and hashes

CI `45295419663` GREEN for source `dccbc33b`, `XNU_TARGET=iphoneos`, M30LTE,
DEVELOPMENT; log applied `0436-m30-cs-busy-peer-overlay.patch`; LSE count 0.

| File | SHA256 |
|---|---|
| buildtree `osfmk/vm/vm_fault.c` | `98196f90fef3f7cc382678dbee83799b8bfd7893ac008ca0cefd0e8e262bf65d` |
| linked kernel | `82d1e1443a2260535195a12c12714ac2b2248355ca60af30bfce05f94f6c2448` |
| payload | `6c4c3ddf1aafd4991b23a2839bdc4499dbc0a7622d6be83b0cdd1014a69a128b` |
| `shim-boot.img` (BOOT candidate) | `9890079d8d801aef5639d79a0eba5e8cb468c4ab735dec17eb2a1092eda1b421` |
| `ios-boot.img` | `a420db7a9d33fb297aee32c91c2d70231b25b96adfd99594349795eddb373606` |

Cmdline, ADT, shim and layout are unchanged from v58: `cpus=6`,
`sweetfb_noconsole=1`, entry `0xfffffff007411488`, payload 16,179,264 bytes.

## Validation

Buildtree PASS, kernel 6 checks PASS, platform 9/9 PASS, packaging PASS, handoff
22/22 PASS, all applicable focused tests PASS. No QEMU claim.

## Physical step

BOOT-only Heimdall flash after identity/Download Mode gate. **Force recovery at
~3 minutes after boot** to capture early pstore — v58 lost the exact NS
exception reason to ring wrap. Accept only a visible, persistent lock screen
with supporting logs; Apple logo or IRT state alone is not enough.
