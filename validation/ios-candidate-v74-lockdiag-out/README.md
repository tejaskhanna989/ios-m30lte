# v74 lock-screen diagnostic BOOT candidate (NOT a lock-screen fix)

Source: `main` at `275dcf3d` (implementation `5a16434a` + gate fixes).
XNU CI `45857232644` **GREEN** (19m27s); host CI `45854698703` GREEN.

This candidate changes ONLY the BOOT image. It keeps the v73 userspace untouched
(USERDATA release `ios-root-20H392-45819973935` stays installed). It adds patch
`0455-m30-lockscreen-diag.patch`: a bounded, read-only sampler that routes the
existing SpringBoard/backboardd user backtraces into the durable pmsg sink when
`m30sblockdiag=1` is present. Disabled by default; at most 6 samples (first at
45 s, then every 60 s). No SpringBoard/UIKit, AMFI, code-signing, auth or input
code is changed.

Hashes:
- Kernel: `9cd703f14dea423db64b7c4b9b0746718c36c812dde54be9a7af5678819edfd5`
- Payload: `9f33d9cc16c0896d59ebcee1fa1a104752a003f1aeac33b88cd1af73d8f63676`
- `ios-boot.img`: `1b5143e72e4a502ad05b87f7b96d2ccbc93d187de647d9fb70bb6b2b1ad09f77`
- `shim-boot.img`: `3b67bbfe6c9d90f1e6a830f8149fd51ab449b17663ec516a5e82b57a6b578949`

Cmdline = exact v68 + `m30sblockdiag=1`; NO `m30touch`, `m30touchhid` or
`m30uihb`. Touch is compiled but dormant; no touch claim is made.

Why: v73 proved `lsd` is stable (single spawn, 0 CRASH), but the user confirmed
no native lock screen. The first failing call inside SpringBoard scene creation
remains unobserved. This candidate is the smallest bounded instrumentation that
can capture it before any functional patch is justified.

Physical test (requires separate explicit authorization; NOT performed):
1. Verify exact SM-M305F / m30lte / bootloader M305FDDU8CVK1 / known serial in
   TWRP and Download Mode; verify the original BOOT backup hash `469c12d2…`.
2. BOOT-only flash `ios-boot.img` with `--no-reboot`, then resume.
3. Let it settle ~3 min; pull `/sys/fs/pstore/pmsg-ramoops-0` read-only promptly
   (the 16 KiB ring wraps).
4. Decode: `python3 tools/decode_pmsg.py raw -o decoded.txt` then
   `python3 tools/decode_sweet_sample.py decoded.txt -o backtraces.json`.
5. Symbolicate SpringBoard frames against the genuine dyld shared cache; only
   then consider a functional patch. Do not claim lock-screen or touch success.
