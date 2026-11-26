# Sweetsample diagnostic candidate — capture SpringBoard user backtrace

Only change from the proven v68 runtime configuration is one boot arg:
`sweetsample=SpringBoard,backboardd`. `sweetsample=1` would match no process
because `sweet_sample_thread()` parses a comma-separated process-name list.

Kernel: 464b410cf4e6a942a3588d79e06e8a0c3f0e34ef5d211a1ffa2f51f0e2731221
Payload: fbcc2fea3cf725abddf36a0ddef6a76d195c55d8a6ee70e6159ac467bc7896c9
BOOT image: 2dbd2ffaf3112b132278244b5d35dc256320fb0775427f173439ff4fa714b7d2
Structural PASS.

## What the sampler does
From `bsd/dev/sweet_sample.c`:
- `sweet_sample_start()` starts `sweet_sample_thread()`.
- Thread sleeps 30 s, then for i=0..79 (30 s ticks, 40 min):
  prints `M30 UI: sb=<pid> bb=<pid> reason=<reason>` every tick, and when
  i%4==0 prints `SMP --- sample <n>` followed by per-process/thread records via
  `sweet_sample_task()` in `osfmk/kern/exception.c`:
  `SMP <name>[pid] slide ... mh ...` and
  `SMP <name> tN pc 0x... lr 0x... sp 0x... bt 0x... ...` (up to 16 frame-pointer frames).
- First full backtrace at ~30 s, then every ~120 s, up to 20 samples.

## Physical test instructions (NOT performed here)
1. BOOT-only Heimdall flash of this image with `--no-reboot` after exact
   SM-M305F identity and Download Mode gates.
2. Resume manually; let it settle at the Apple logo for at least 2-3 minutes
   so the first `SMP --- sample 0` backtrace is captured.
3. Return to TWRP; read-only pull `/sys/fs/pstore/pmsg-ramoops-0`.
4. Decode:
   `python3 tools/decode_pmsg.py raw/pmsg-ramoops-0 -o decoded-pmsg.txt`
   `python3 tools/decode_sweet_sample.py decoded-pmsg.txt -o backtraces.json`
5. Symbolicate raw frames by subtracting the recorded `slide` and using the
   iOS 16.7.16 SpringBoard binary / dyld shared cache. Do not invent symbols.
