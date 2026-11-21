# Canonical v9 recovery pstore capture

This directory is the single canonical home of the v9 "immediate recovery"
pstore capture. It was moved (not copied) from the external directory
`/home/tejas/v9-immediate-pstore/` into the repository; byte-for-byte hashes
were verified before and after the move.

| File | SHA-256 | Size | Notes |
|---|---|---:|---|
| `pmsg-ramoops-0` | `9ed6020f9a52abbf1cc45da9edf9b5022175e7f4fb3a94af1440150a7d08c5ca` | 7633 B | Raw pstore pmsg capture — **unmodified**, preserve as-is |
| `pmsg-decoded.txt` | `74d57b9a6d7b9ffcecfde8f98ce82abdc5531bba7269ee2b3353d0a58e4a8fe2` | 5579 B | Decoded companion (also reproducible with `tools/m30_bootlog.py`) |

Decode check: `python3 tools/m30_bootlog.py inspect --file pmsg-ramoops-0`
→ 93 records, 72 tagged `XNU`, 0 decode issues. The XNU records include
`No POST boot-arg set.`, the BSD copyright banner,
`MAC Framework successfully initialized`, `using 1308 buffer headers …`,
A5XELTE platform-expert registration, AppleKeyStore/IOWatchdog/IOCoreSurfaceRoot,
HID buttons/touch, AppleCLCD and the final 30 Hz framebuffer line. No
`M30 ROOT:` / eMMC / `BSD root:` record is present.

This capture supersedes the delayed `../pmsg-postboot.bin` (3439 B, 1 XNU
record) for determining how far XNU progressed. Analysis:
`validation/bsd-progress-analysis-20261121.md`.

No physical device operations were performed during relocation.
