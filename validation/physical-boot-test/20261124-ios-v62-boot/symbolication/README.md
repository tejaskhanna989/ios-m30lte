# v62 SpringBoard stuck-PC symbolication

All extraction was read-only on the physical M30 in TWRP. Identity was verified
before reads: `SM-M305F`, `m30lte`, serial `320081735bb166a3`, bootloader
`M305FDDU8CVK1`, `ro.twrp.boot=1`. No USERDATA write was performed.

## Source

The genuine iOS 16.7.16 (20H392) dyld symbols file was resolved through the
HFSX catalog with `tools/m30_hfsx_read.py`:

- catalog path: `/private/preboot/Cryptexes/OS/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.symbols`
- catalog entry: old-style `hlnk`/`hfs+` stub, `linkRef=664485424`
- resolved hardlink target: `iNode664485424`, fileID `318463`, under the
  file-hardlink private directory (parent id 18)
- real data fork: one extent, `(2905235, 144556)` blocks; logical size
  `592101376` bytes
- dyld header: `dyld_v1   arm64`, `mapping_off=0x200`, `mapping_count=1`,
  `local_symbols_off=0x4000`, `nlist_count=8705811`, `nlist_off=0xa980`,
  `str_off=0x84e1ab0`, `str_size=451573533`, `entries_count=2710`

`springboard-pc-lr.json` SHA256:
`ae2b78d59e9280ca840dbb166daf72d37b7b09eed1a602703802a335df8611a5`.

## Sampled state

From `../decoded-pmsg.txt`:

- SpringBoard pid 27, shared-region slide `0x3f420000`, mach header
  `0x100008000`
- main thread PC `0x201a31030` -> unslid `0x1c2611030`
- main thread LR `0x201a42b18` -> unslid `0x1c2622b18`
- repeated in v60 long run and v62 after ~20 min; no SpringBoard crash

## Nearest local symbols

Nearest preceding symbols from the genuine dyld local-symbol table:

| Unslid address | Nearest symbol | Offset |
|---|---|---|
| `0x1c2611030` | `___commpage_gettimeofday_internal` (`0x1c2610ce0`) | `+0x350` |
| `0x1c26114f0` | `_mach_msg_destroy_port` (`0x1c261136c`) | `+0x184` |
| `0x1c2611524` | `_mach_msg_destroy_port` (`0x1c261136c`) | `+0x1b8` |
| `0x1c2622b18` | `_do_compat` (`0x1c262298c`) / `fprintf_stderr` (`0x1c2622830`) | `+0x18c` / `+0x2e8` |

The main thread is repeatedly in the libsystem stderr/log write path
(`fprintf_stderr` -> `write(2, ...)`) with a timestamp helper in PC, not in a
UIKit lock-screen method. Backtrace frames `0x201a42db8` and `0x201a31524`
also unslide into libsystem; deeper frames are in IKit/UI framework code.

## Interpretation and next targeted fix

The payload cmdline still has `serial=3` (`SERIALMODE_OUTPUT|SERIALMODE_INPUT`).
In XNU `osfmk/arm/arm_init.c`, that flag switches the console to serial with
`serial_console_enabled=true`. `fprintf_stderr` writes fd 2 and can block in
that path when nothing drains the serial console. This matches the symbolicated
stuck PC/LR and the user's observation that logs appeared before the Apple-logo
stall.

Targeted v63 change: keep the CI-green v62 kernel and all security state
unchanged, but remove only `serial=3` from the payload cmdline. Kernel pstore
logging remains active through `a5xelte_log_append()` in `_cnputs()`,
independent of serial output. Accept only a persistent visible lock screen plus
logs; process liveness, IRT state, framebuffer activity and Apple logo are not
success.
