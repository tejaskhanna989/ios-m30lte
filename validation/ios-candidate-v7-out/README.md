# iOS candidate v7 — console→pmsg mirror + BSD root-stage markers

isolated candidate; v6 and all earlier candidates/physical evidence untouched.

## What changed vs v6

| Item | v6 | v7 |
|---|---|---|
| Kernel target | genuine iOS (`XNU_TARGET_OS_IOS`) | same |
| Kernel SHA256 | `790c841d…d3047` | `23ea642e…98206e` |
| Kernel size | 16,697,344 | 16,713,848 |
| 0406 console→pmsg mirror | absent | **linked** (`_m30_pmsg_base`, `_m30_pmsg_cap`) |
| 0407 `M30 ROOT:` markers | absent | **linked** (6 strings) |
| Payload cmdline | `debug=0xc serial=3 cpus=1 keepsyms=1` | `debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292` |

The shim region (first `0x20000` bytes) is byte-identical to the physically
proven v5/v6 flash image:
`864370f63a4208a41675e739d4bdb295f53ea3aea8ac58ef81b09f875d15211a`.

## Why `maxmem=292` (ramoops reservation)

The ramoops region `0x92400000`/`0x8000` (pmsg zone `0x92404000`/`0x4000`) lies
**inside** the ADT-declared kernel RAM window `[0x80000000, 0xBDA00000)`. Without
a reservation XNU's VM could allocate that page, so the pmsg mirror could both
corrupt kernel data and lose its own records.

`maxmem` is an XNU boot arg parsed in `arm_init.c` (`xmaxmem = maxmem * 1 MiB`),
and `arm_vm_init.c` caps `mem_size` to it before computing
`avail_end = gPhysBase + mem_size`. The shim copies the payload cmdline verbatim
into `boot_args.CommandLine`, so:

```
maxmem = 292 MiB = 0x12400000
avail_end = 0x80000000 + 0x12400000 = 0x92400000
```

XNU's VM page database therefore ends exactly at the ramoops base; physical
pages `[0x92400000, 0x92408000)` can never be allocated by XNU. This is a static,
provable reservation that requires no kernel/ADT/shim changes. (The physmap still
maps that range, but mapping is not allocation.)

## Exact build recipe (reproducible)

```bash
# 1) kernel from green CI run 44686553586 (HEAD 52674ef, xnu_target=iphoneos)
K=milestone_artifacts/ci_44686553586/kernel/mach.development.m30lte   # 23ea642e…

# 2) payload — maxmem=292 reserves the ramoops region
cd validation/ios-candidate-v7-out
python3 mkpayload.py inputs/kernel.development.m30lte inputs/m30lte-corrected.adt \
  payload/xnu-payload.bin --cmdline "debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292"

# 3) boot images
python3 package_boot_images.py --shim-image shim_fixed.Image --shim-elf shim_fixed.elf \
  --payload payload/xnu-payload.bin --kernel inputs/kernel.development.m30lte \
  --adt inputs/m30lte-corrected.adt \
  --expected-kernel-sha256 23ea642eb8224c05ea31b28c5a8a9db7782306fd66762013f8f115c2b798206e \
  --expected-payload-sha256 bfdd0ab500ba9efb36904224f1512baf89e80ddf1823827d494b2b9413fdbe5f \
  --payload-offset 0x20000 --project-root /home/tejas/Projects/m30lte-ios \
  --out-dir . --mkbootimg /usr/bin/mkbootimg
```

## Hashes

| File | SHA256 |
|---|---|
| kernel | `23ea642eb8224c05ea31b28c5a8a9db7782306fd66762013f8f115c2b798206e` |
| payload | `bfdd0ab500ba9efb36904224f1512baf89e80ddf1823827d494b2b9413fdbe5f` |
| combined.bin | `d5d872c08a84807068e03f6f369564dd1c285e745cef193fce6df405161eb904` |
| shim-boot.img | `6e1fcfabc2110ebc4c4d3a3802cf718882a9b343d68bdcacc38c57f0a7f998dd` |
| ios-boot.img | `387f141c1f2b9ed8a87c773ada40c003a559039b33a207c6b31e45d7f1dc21a5` |
| shim Image / ELF | `2d7aea80…` / `a3fd2653…` (identical to v6) |

## Validation results (all offline; no physical operations)

- CI run `44686553586`: **success**, `ios_define_present=True osx_define_present=False target=iphoneos`, LSE instructions = 0.
- `verify_m30_buildtree.py`: **PASS** (all critical patches reverse-apply).
- `verify_m30_kernel.py`: **PASS** (6 checks).
- `verify_platform_match.py`: **9/9 PASS**.
- `verify_cpu_fallback.py`: **17/17 PASS**.
- `verify_adt_restore.py`: **22/22 PASS**.
- `verify_shim_audit.py` (GIC): **5/6 PASS** — the single FAIL is the known inapplicable "entry masks interrupts (DAIFSet #0xf)" check; the proven shim dispatches on `CurrentEL` first (documented in NOTES.md; dedicated verifiers authoritative).
- `verify_handoff_v7.py` (adapted v5 handoff verifier): **18/18 PASS**.
- `validate_boot_images.py` (packaging): **PASS** — combined exact, structural, partition-compatible.
- `validate-repo.py`: tool/shell syntax PASS; its 7 "patch sequence gap" errors are pre-existing and unrelated to v7.
- pmsg format: standalone model of the **exact** 0406 write logic compiled with `-Wall -Wextra -Werror`; decoder round-trip 7/7 records, plus pre-populated-zone boundary test 4/4 records, 0 issues.

## Safety assessment

Static analysis says the mirror is memory-safe **in this candidate**: it writes
only inside the 16 KiB pmsg zone via `ml_io_map`, bounds-checks every record
(`reclen <= 255`, `<= cap`), validates the `DBGC` header before touching it,
never allocates/locks, and the exact Linux `persistent_ram_write` cursor
semantics were verified against the Linux v6.1 source. The ramoops page is
reserved from XNU by `maxmem=292`. Framebuffer console output is untouched —
the mirror is strictly additive in `fbcon_transmit_data`.

**What is still unproven:** XNU→TWRP survival of records written by our code,
and real-hardware behavior of `maxmem` in this boot path. No persistence claim is
made without a physical test. Candidate v7 is ready for a freshly authorized
BOOT-only physical test; stop here otherwise.
