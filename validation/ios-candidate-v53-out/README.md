# iOS candidate v53 — early DSC-header IRT gate

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `ffcb6466`.

## Why this candidate exists

v52 restored the IRT patch but the SpringBoardUI assertion still appeared before
the patch. The remaining timing problem is the gate itself: the IRT worker is
started by the SpringBoard XCTest literal page fault, which happens inside
SpringBoard after the probe has already run.

v49 proved that starting the worker on the first arbitrary fault fails
(`state=4`) because the pager initially hands over launchd/dyld Mach-O vnodes,
not the dyld shared cache.

v53 changes the gate to a positive DSC identification:

- Start the read-only IRT worker on the first validated page that is genuinely
  a dyld shared-cache header: `mo_offset == 0` and `dyld_v` at `kaddr[0:6]`.
  This occurs when dyld maps the cache, before SpringBoard starts.
- Keep the v50 XCTest retrigger only as a fallback. If the early scan has
  already started, the later XCTest patch records `m30_irt_retriggered` but
  does not reset `m30_irt_state` or restart the worker.
- Keep v52's range-limited chunk rewrite, with no chunk-path retrigger.

All file reads remain `UIO_READ`. The in-memory uint32 write is strictly after
code-signing validation. No signature, hash, AMFI, trust-cache, page-validation
or other security check is weakened. No disk write is introduced.

## CI history

| Run | Result |
|---|---|
| `45169239555` | v50 GREEN; physically tested (`state=3`, full heartbeat) |
| `45173700250` | v51 GREEN; physically rejected (`state=2`) |
| `45179499798` | v52 GREEN; IRT restored, assertion still early |
| `45185667251` | v53 GREEN; 0426 + 0427 + 0428 + 0429 + 0430 applied |

CI `45185667251` completed in 18m51s for source commit `ffcb6466`. The buildtree
`osfmk/vm/vm_fault.c` matches `/tmp/m30_v53/modified.c` byte-for-byte.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `de84396fb0268ac2129737af5ad37bfe2b8fba52da7bb9e93f840d6534f9dcf4` |
| payload | `3522a4447de58d8b23a11c06486d4452286247e54f93835e2e41a10f55c7bbba` |
| shim-boot.img | `7cf35ab74045307f69f752eb6f6c1cfc638c402116a91f3e30f3ec5c1046df00` |
| ios-boot.img | `94f04c6c654108b9272300dec631f8d60a835dfde86c8574cdc9a4a32ae3aafe` |

## Layout

v53 has the same linked layout as v52:

- entry VA `0xfffffff007410488`;
- `_start_first_cpu` `0xfffffff0074120ec`;
- `__TEXT_EXEC __text` vmaddr `0xfffffff007248000`, size `0x008ae9d8`;
- ADT PA `0x82450000`, boot_args PA `0x82454000`.

`shim/loader.c` derives ADT and boot_args from the payload header. The shim
Image/ELF and the shim region inside `shim-boot.img` remain byte-identical to
the v31 reference.

## Validation

CI `45185667251` GREEN. Patch order `0426 -> 0427 -> 0428 -> 0429 -> 0430` was
preflighted with `git apply --check` against the exact v49 CI base and verified
to reproduce the intended v53 source byte-for-byte. Validators all PASS:
buildtree PASS, kernel PASS, platform 9/9, CPU 17/17, ADT 22/22, packaging PASS,
handoff 18/18, and all applicable focused tests (`test_m30_16k_pages.py`
intentionally inapplicable).

## Next physical step

BOOT-only flash, resume, one ~180 s boot window, return to TWRP, pull pstore.
Check for `M30 IRT: early scan started on DSC header`, the IRT patch marker,
`state=3`, and whether the SpringBoardUI assertion now appears after or absent
before the patch. Do not equate a loaded SpringBoard process with visible UI.

No UI success claimed. BOOT readback skipped; USERDATA/SYSTEM/RECOVERY untouched.
