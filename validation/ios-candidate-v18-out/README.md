# iOS candidate v18 — skip 16K-CD page validation (avoid tainted-text kill)

Isolated candidate. v6–v17, backups, all physical evidence preserved.
No physical operations performed for v18. Work on `main` @ `bf79da7`.

## Exact cause and fix

Physical v17 (`2fabc50d…aacb55eb`): patch 0415 worked — no AMFI abort, deep iOS
userspace ran (lsd, xpcproxy, fairplayd, identityservices...). New blocker:
`lsd` killed repeatedly by `Text page corruption detected` (sig 6). Patch 0414
marked dyld-cache pages TAINTED (4K chunk can't match a 16K hash); `vm_fault.c:8246`
treats a tainted TEXT page as corruption and kills the process.

**v18 fix (patch `0416-m30-skip-16k-cs-page-validate.patch`):** for
`csb_hash_pageshift > PAGE_SHIFT`, `continue` (skip that blob) instead of
round-and-taint — the page stays UNVALIDATED (not tainted), so no text-corruption
kill; `cs_invalid_page` applies the normal CS_VALID policy as in v16. No false
validation, no entitlement/signature bypass; genuine misalignment still panics.
Cmdline and all prior fixes unchanged.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `9a823cc066c56b846bf895de406a5579fb16d58ec0ec7f9ec1a19cd73ce2fd01` |
| payload | `97fbd00d1012cc72710ed8e999b45de62af635aa5db39a7daeafb77976097bce` |
| combined.bin | `77add949e93c1265fc9551d5a5b70be06407b048a30fcc06cfbf54eb318abc7f` |
| shim-boot.img | `8a68ada1373b597c4ae1253e59b1fba9a612609f1c74d27308afc38fb2d8f1eb` |
| ios-boot.img | `6eb4a193a58caf15d42c8c744fa629e53e6e69b4857ea3b09d7aa9b6178e2337` |

Cmdline: `debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292 rd=emmcroot0 emmcroot=USERDATA emmcprobe=1 emmcwrite=1`

## Validation (offline)

CI `44946634655` green (iOS target confirmed, LSE=0). Buildtree PASS, kernel
PASS, platform 9/9, CPU 17/17, ADT 22/22, handoff 18/18, packaging PASS, GIC
5/6 (inapplicable). All focused tests PASS including
`test_m30_skip_16k_cs_page.py` (reproduces the taint/kill and proves the fix).
Shim byte-identical to proven v6; `maxmem=292`, iOS 16 target preserved.

## Status / next physical step

Not physically tested. Proposed: flash v18 BOOT only, preserve USERDATA/SYSTEM/
RECOVERY, one boot, capture pstore immediately. Expected: no lsd crash loop, iOS
userspace continues further (SpringBoard may start). No full SpringBoard/UI
claim until device evidence proves it.
