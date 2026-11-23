# iOS candidate v44 — companion-mapping symbol fallback

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `2d39841`.
No physical operations for v44 yet.

## What changed from v43

v43 physically showed that the nlist vmaddr (`0x1e1d3ad84`) lies below the real
base cache mapping (`0x1ecc80000/0x62ac000@0x0`), and the target image address
is even lower. No vmaddr-based real-cache mapping matched, so the in-memory
page could not be patched.

v44 adds a translation fallback:

- `diag 52` prints the `.symbols` companion's own mapping table.
- If no real-cache vmaddr mapping matches, `diag 53` translates the nlist value
  through the companion mapping to a file offset
  (`sym_map_fileoff + (sym_vmaddr - sym_map_addr)`) and targets the base cache
  vnode at that offset.
- System and Cryptex subcache searches now cover `.0`–`.511`.
- Periodic `M30 IRT status:` includes `tries`, `symmap`, and `fb` so the
  decisive values survive the 16 KB pmsg ring wrap.

The companion remains read-only. The only write is to the already-faulted
in-memory page strictly after `cs_validate_page()`, gated on the target cache
vnode. No signature, hash, AMFI, trust-cache, or other security check is
weakened.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `a4b02c4ce766b309d6b734e26c0af7dc35c1997010670c2d7d583315993b0ce4` |
| payload | `594922b14453349296a8c6cfb7426ac2fc2c7861d85b49c0908eb34bb5b66fe1` |
| shim-boot.img | `671e8d81c2cb2517cda696727cb37d54163beb1102221cf03d93ed00c6687dfc` |

The shim Image/ELF hashes remain byte-identical to v6/v30–v43, and the shim
region inside `shim-boot.img` matches the v31 reference byte-for-byte. The
kernel entry moved one page later to `0xfffffff007410488`; the shim consumes
the payload header entry, so the handoff remains 18/18 PASS.

## Validation

CI `45118566540` GREEN. Buildtree PASS, kernel PASS, platform 9/9, CPU 17/17,
ADT 22/22, packaging PASS, handoff 18/18, all applicable focused tests PASS
(`test_m30_16k_pages.py` intentionally inapplicable). Standalone syntax check
clean; patch dry-runs cleanly against pristine and the v43 buildtree.

## Next physical step

BOOT-only flash; capture pstore. Read `diag 52/53` and status `symmap=... fb=...`.
Expect either `M30 IRT: patched ...` or a new precise failure diagnostic. Check
whether SpringBoard proceeds past `+[SpringBoardUI load]`.

No UI success claimed; BOOT readback skipped; USERDATA/SYSTEM/RECOVERY untouched.
