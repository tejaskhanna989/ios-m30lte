# M30LTE Boot Console → pmsg Log Tool

## What it does

Mirrors XNU's framebuffer console into the ramoops pmsg RAM zone so boot text
survives a reboot and can be recovered from TWRP/PBRP **without framebuffer
capture hardware, serial cable, or ADB during boot**.

## Components

1. **Kernel patch** `xnu/patches-minimal/0406-m30-console-pmsg-mirror.patch`
   - Hooks `fbcon_transmit_data()` in `pexpert/arm/pe_serial.c` (M30LTE only)
   - Accumulates a line (max 230 chars), emits a framed pmsg record on newline
   - Maps pmsg zone `0x92404000` with `ml_io_map()`, validates `sig=0x43474244`
   - Writes Linux `persistent_ram_buffer` header (sig/start/size) + Android pmsg
     record framing; no allocation, no locks, bounds-checked, wrap-safe
   - If the header signature doesn't match, it writes nothing (safe on unknown layouts)

2. **Host tool** `tools/m30_bootlog.py`
   - `start` — pull `/sys/fs/pstore/pmsg-ramoops-0` from connected recovery device,
     decode, append to timestamped `bootlog-<UTC>.jsonl`; keeps raw `<ts>.bin`
   - `inspect` — show records from a raw pmsg file or latest capture
   - `export` — merge all JSONL logs into a text/JSON file
   - `selftest` — synthetic round-trip + defensive decode validation (offline)

## Hardware / software requirements

- Samsung Galaxy M30 SM-M305F in TWRP/PBRP recovery with ADB root after the boot
- ramoops enabled with pmsg zone at `0x92404000` size `0x4000` (verified live on this device:
  `mem_address=0x92400000`, `mem_size=0x8000`, `record_size=0x4000`, `pmsg_size=0x4000`)
- Kernel built with patch 0406 (currently NOT in main's build — needs enabling)

## Storage usage

- pmsg zone is 16 KiB (fixed); newest data wraps oldest
- Each capture: raw ~0–16 KiB + JSONL log (~200 B/record)
- Logs append to `validation/bootlog/`

## Limitations / honesty

- Only captures text sent through the framebuffer console hook **after** the console
  is registered (fbcon_probe). Earliest shim-stage markers before that are not captured.
- Recovery overwrites/erases pmsg records on some firmwares; XNU→recovery survival of
  records written by our code is **UNPROVEN** — needs one physical test to confirm.
- The region `0x92404000` is inside the RAM window XNU manages; if XNU reuses that
  page, records may be lost. Mitigated by signature check, not eliminated.
- Does not capture graphics/panic colors — only text. For visual evidence, a camera
  capture remains necessary; this tool complements it.
- No physical device operations were performed while building/validating this tool.

## Commands

```bash
# offline validation
python3 tools/m30_bootlog.py selftest

# after a boot, with device in recovery and ADB connected:
python3 tools/m30_bootlog.py start
python3 tools/m30_bootlog.py inspect
python3 tools/m30_bootlog.py export --format text -o /tmp/m30-boot.txt
```
