# iOS candidate v61 — correct console-mute boot argument

Baseline: v60 (`8254c7ee`). v61 reuses the CI-green v60 kernel/source; only the
payload cmdline changes. MAIN only.

## Why

v60's long physical run proved the CS fix is holding: SpringBoard pid 27 and
backboardd pid 57 stayed alive for ~19 minutes with zero crashes and no UI
`cs_invalid_page`. But no lock screen was visible. The user saw many console
logs.

Root cause found: `M30LTE` defines `ARM64_BOARD_CONFIG_A5XELTE`, and
`iokit/Kernel/arm/SweetFramebuffer.cpp` reads **`a5fb_noconsole`** under that
guard. v60's cmdline contained `sweetfb_noconsole=1`, so the framebuffer console
was never muted and kept drawing over the GUI. v61 uses the correct
`a5fb_noconsole=1` and also adds `a5fb_keep_on=1` so the panel is not blanked.

No kernel, code-signing, AMFI, trust-cache or page-validation change. No new CI
build is required because the kernel is byte-identical to v60's CI-green kernel
(run `45334020730`, source `f561e630`).

## Hashes

| File | SHA256 |
|---|---|
| linked kernel (same as v60) | `a24d220685d42b51a1ac8f74c9256480fd81fe1103195fc99c2da1f4b79c7637` |
| payload | `06a492b5b6a8d747956f8c7f5cb870d79c736813c588af14cbc79377e95cbf4e` |
| `shim-boot.img` (BOOT candidate) | `0a224fdb7c6a3e284d565a26e70c46094ef901b0b3c9c2b62e97affba4b421d1` |
| `ios-boot.img` | `015afe8809d737f64d21cdbc10faaf5ced7c7d06f64c47700a2fe8a77e330273` |
| `combined.bin` | `1076734b93afbbf24c6439bc5e5dc37a140fff353f717541e9949ac1d4e1552f` |

Cmdline: `debug=0xc serial=3 cpus=6 keepsyms=1 maxmem=292 rd=emmcroot0
emmcroot=USERDATA emmcprobe=1 emmcwrite=1 a5fb_noconsole=1 a5fb_keep_on=1`.

## Validation

- Reused v60 CI GREEN result and buildtree validators (kernel unchanged).
- `validate_boot_images.py`: PASS.
- `verify_handoff_v61.py`: 23/23 PASS (includes both corrected boot args).
- All applicable focused tests PASS from v60; no security change.

## Physical step

BOOT-only flash after identity/Download Mode gate. Watch for the lock screen;
with the console muted it should be visible if the GUI is rendering. Pull pstore
when convenient. Accept only a visible, persistent lock screen plus logs — not
a boot animation, not IRT counters, and not a short-lived process.
