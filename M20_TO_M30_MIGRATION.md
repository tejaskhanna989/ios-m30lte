# M20 to M30 XNU Migration Plan

**M20 Donor Commit:** `7eb541d7fdc7ae70c1661a075a39e4b990165101` (branch `m20lte`)  
**M20 Repo:** https://github.com/madesh-ops/ios-m20lte  
**Our Target:** Samsung Galaxy M30 SM-M305F, Exynos 7904 / S5E7904

---

## 1. Verified M20 Achievements (Against Source)

| Milestone | Evidence | Status |
|-----------|----------|--------|
| XNU kernel execution on physical M20 | `M20LTE_PROGRESS.md` + probe photos + pstore logs | ✅ Confirmed |
| MMU + RAM window isolation (0x94000000-0xB4000000) | `shim/m20lte/xnu_boot.c`, boot 1→2 fix | ✅ Working |
| GICv2 + 26 MHz timer + SGI1 cross-CPU | Boot 2 log: "SGI1 OK", "1/1 CPUs initialized" | ✅ Working |
| Framebuffer console (DECON_F trigger) | `shim/m20lte/fbtext.c`, boot 2 photo | ✅ Working |
| eMMC read (GPT probe on SYSTEM p20) | `bsd/dev/a5xelte_emmc.c`, boot 2 | ✅ Working |
| Keys (GPA1 ALIVE 0x11CB0000) | `bsd/dev/a5xelte_keys.c`, boot 3 | ✅ Working |
| iOS root mount + launchd + services | Boot 4 log: 60 services via xpcproxy | ✅ Working |
| Log ring (persistent pstore) | Boot 4: 31KB log, flush #15 | ✅ Working |
| Process sampler (SpringBoard/backboardd) | Boot 6: `sweet_sample.c` on M20 | ✅ Working |
| **Lock screen (iOS 16.7.16)** | **A40 prebuilt kernel only** (2 A73s, 16K pages, 1 GiB) | ⚠️ Not M20-native |

**Critical distinction:** The lock screen was achieved with **tlfares/iOS16-on-A40's prebuilt kernel** (A73s, 16K pages), NOT the M20-native A53 kernel (4K pages). The M20-native kernel reached SpringBoard exec but blocked on logd.

---

## 2. Hardware Comparison: M20 vs M30

| Component | M20 (SM-M205F) | M30 (SM-M305F) | Action |
|-----------|----------------|----------------|--------|
| **SoC** | Exynos 7904 | Exynos 7904 | Same |
| **CPUs** | 6×A53 (0x100-0x103, 0x200-0x201) + 2×A73 (0x0, 0x1) | Same per `/proc/device-tree` | Reuse |
| **Boot MPIDR** | 0x100 (A53) | 0x100 (A53) | Reuse |
| **GIC** | GIC-400 @ 0x12301000/0x12302000 | GICv3 @ 0x12301000/0x12302000* | **ADAPT** |
| **Timer** | 26 MHz, vtimer PPI 11 (INTID 27) | Same | Reuse |
| **RAM** | 3 GB: 0x80000000-0xBD9FFFFF, 0xC0000000-0xFFFFFFFF, 0x880000000-0x8BFFFFFFF | Need live DT | **VERIFY** |
| **XNU RAM Window** | 0x94000000-0xB4000000 (512 MiB, avoids FB) | Must avoid FB @ 0xEC000000 | **ADAPT** |
| **Framebuffer** | 0xEC000000, 1080×2340 ARGB8888, stride 4320, DECON_F 0x14860000 | Same per our `shim/devices/m30lte.c` | Reuse |
| **eMMC** | DesignWare MSHC @ 0x13500000 | Same per our `shim/devices/m30lte.c` | Reuse |
| **PMU** | 0x11C80000 (INFORM2/3, SWRESET) | Need verify | **VERIFY** |
| **Keys** | ALIVE @ 0x11CB0000, GPA1 | Need verify | **VERIFY** |
| **Display Ctrl** | DECON_F 0x14860000, HW_SW_TRIG 0x70=0x1281 | Same | Reuse |
| **Page Size** | 4 KiB (A53 boot) | 4 KiB | Reuse |
| **Kernel Load** | 0x80080000 (S-Boot slot) | Same | Reuse |
| **ADT RAM** | 0xC8000000 512 MiB (boot 1) → 0x94000000 (boot 2+) | Must match XNU window | **ADAPT** |

*Our `shim/devices/m30lte.c` says GICv3 but M20 uses GICv2 (GIC-400). M30 DT may differ.

---

## 3. Reusable M20 Implementation Files

### Kernel Patches (xnu/patches/)
| File | Purpose | M30 Adaptation |
|------|---------|----------------|
| `0400-m20lte-board-target.patch` | **Core M20 support** - adds MACHINE_CONFIG=M20LTE | **HIGH REUSE** - rename to M30LTE, update addresses |
| `0082-a5xelte-4k-entry.patch` | 4K page entry (nos_arm_asm, nos_arm_pmap) | Reuse as-is |
| `0085-a5xelte-board-target.patch` | A5XELTE base config (GICv2, MSHC eMMC, 4K pages) | Reuse as-is |
| `0086-a5xelte-gicv2-platform.patch` | GICv2 platform expert | Reuse as-is |
| `0099-a5xelte-architected-timer.patch` | 26 MHz timer | Reuse as-is |
| `0101-a5xelte-cpu-identity.patch` | CPU MIDR/MPIDR | Reuse as-is |
| `0104-a5xelte-emmc-gpt-probe.patch` | eMMC GPT read | Reuse as-is |
| `0108-a5xelte-userdata-write.patch` | eMMC multiblock writes | Reuse as-is |
| `0401-m20lte-hfs-link-notes.patch` | HFS link repair limit | Reuse as-is |

### Platform Expert (`pexpert/arm64/A5XELTE.h`)
```c
// M20 values - M30 MUST VERIFY/UPDATE:
#define A5XELTE_FB_PA       0xec000000    // Same
#define A5XELTE_FB_WIDTH    1080          // Same
#define A5XELTE_FB_HEIGHT   2340          // Same
#define A5XELTE_FB_STRIDE   4320          // Same
#define A5XELTE_MARKER_PA   0x93fff100    // Log page - ADAPT to M30 window
#define A5XELTE_BOOT_MPIDR  0x100         // Same
#define A5XELTE_EMMC_PA     0x13500000    // Same
#define SWEET_SMP_MAX_CPUS  1             // Start with 1 CPU
```

### Shim (Bootloader)
| File | Purpose | M30 Adaptation |
|------|---------|----------------|
| `shim/m20lte/xnu_boot.c` | XNU loader, 512 MiB window @ 0x94000000 | **ADAPT RAM window** to M30 free region |
| `shim/m20lte/xnu_boot.S` | Assembly entry | Reuse |
| `shim/m20lte/fbtext.c` | Framebuffer console + pstore | Reuse (same FB/DECON) |
| `shim/m20lte/probe.c` | Stage-0 diagnostics | Reuse |
| `shim/m20lte/build.sh` | Build script | Reuse |

### ADT Generator
| File | Purpose | M30 Adaptation |
|------|---------|----------------|
| `tools/mkadt_m20lte.py` | Builds ADT for M20 | **ADAPT** RAM base/size, CPU MPIDRs, reserved regions |

### CI/Build
| File | Purpose | M30 Adaptation |
|------|---------|----------------|
| `.github/workflows/xnu.yml` | Uses `blacktop/darwin-xnu-build` | **HIGH REUSE** - change MACHINE_CONFIG=M30LTE |

---

## 4. Incompatible M20 Assumptions (Must Change for M30)

1. **GIC Version**: M20 uses GICv2 (GIC-400); M30 may be GICv3. `pexpert/arm64/A5XELTE.h` and ADT `gic` node must match.
2. **RAM Window**: M20 uses 0x94000000-0xB4000000. M30 must find a 512 MiB region avoiding FB (0xEC000000) and reserved zones.
3. **Log Page / Marker**: M20 uses 0x93FFF100. Must sit in M30's XNU RAM window.
4. **PMU Recovery**: M20 uses 0x11C80000 INFORM2/3=0x12345674. Verify M30 PMU base.
5. **Keys**: M20 uses ALIVE 0x11CB0000 GPA1. Verify M30 key GPIO.
6. **Upper RAM Bank**: M20 3 GB has 0x880000000-0x8BFFFFFFF. M30 may differ.
7. **ADT dram-base/dram-size**: Must match XNU's actual RAM window.

---

## 5. Required M30-Specific Hardware Changes

| Item | Source of Truth | Action |
|------|-----------------|--------|
| Live DT (`/proc/device-tree`) | ADB on M30 running Android/TWRP | Dump and compare |
| GIC version | `/proc/device-tree/interrupt-controller@*` | Check compatible string |
| RAM banks | `/proc/device-tree/memory@*` | Map all banks |
| Reserved memory | `/proc/device-tree/reserved-memory/*` | Identify free window |
| PMU base | `/proc/device-tree/soc/pmu@*` or Samsung DT | Verify INFORM2/3/SWRESET |
| Key GPIO | `/proc/device-tree/gpio-keys*` or ALIVE node | Find GPAx DAT/CON |
| eMMC DT | `/proc/device-tree/dwmmc* or mmc@*` | Verify base address |
| DECON_F | `/proc/device-tree/display* or decon*` | Verify trigger register |

---

## 6. Build-System Differences & Fixes

| Issue | M20 Solution | M30 Action |
|-------|--------------|------------|
| Sysroot/header conflicts | Uses macOS SDK via `darwin-xnu-build` (not iPhoneOS) | **Use M20's workflow exactly** |
| Config generation | Standard doconf + MASTER.arm64.m20lte | Copy MASTER, update for M30LTE |
| Generated headers | `darwin-xnu-build` handles via xcodebuild | Same |
| Compiler flags | `-mcpu=cortex-a53 -march=armv8-a+crypto` (no LSE) | Same |
| LSE check | CI scans for LSE instructions | Same |

**Our current M30 CI fails because it uses iPhoneOS SDK (`-isysroot .../iPhoneOS.sdk`)** which pulls in SDK headers conflicting with kernel types. M20 uses macOS SDK via blacktop's build script.

---

## 7. Minimal Sequence to Linked M30 XNU Kernel

### Phase 1: Establish M30 Hardware Baseline (Day 1)
```bash
# On M30 in TWRP/Android:
adb pull /proc/device-tree /tmp/m30-dt
# Extract: GIC, RAM, reserved, PMU, keys, eMMC, DECON
```

### Phase 2: Create M30LTE Machine Config (Day 1-2)
1. Copy `xnu/patches/0400-m20lte-board-target.patch` → `0400-m30lte-board-target.patch`
2. Replace `M20LTE` → `M30LTE` throughout
3. Update `pexpert/arm64/A5XELTE.h` with M30 addresses
4. Update `SUPPORTED_ARM64_MACHINE_CONFIGS` in `makedefs/MakeInc.def`
5. Update `MACHINE_FLAGS_ARM64_M30LTE` with M30 RAM window

### Phase 3: Adapt Shim/Loader (Day 2)
1. Copy `shim/m20lte/` → `shim/m30lte/`
2. Update `xnu_boot.c`: RAM_BASE/RAM_END to M30 free window
3. Update `LOG_BASE` and marker PA
4. Verify PMU recovery registers
5. Build: `CROSS=aarch64-linux-gnu- shim/m30lte/build.sh`

### Phase 4: ADT Generator (Day 2)
1. Copy `tools/mkadt_m20lte.py` → `tools/mkadt_m30lte.py`
2. Update DRAM_BASE/DRAM_SIZE to match Phase 3
3. Update CPU MPIDRs if topology differs
4. Update reserved-memory exclusions

### Phase 5: CI Build (Day 3)
1. Copy `.github/workflows/xnu.yml` from M20 repo
2. Set `MACHINE_CONFIG: M30LTE`
3. Push and verify kernel builds on `macos-15-intel`
4. Artifact: `kernel.development.m30lte`

### Phase 6: Boot Test (Day 4+)
1. Pack BOOT: `tools/m20lte-pack-boot.py` adapted for M30
2. Flash to BOOT partition (TWRP)
3. Boot with `cpus=1 emmcprobe=1` cmdline
4. Verify: green entry → blue "MMU on" → framebuffer → eMMC read → root wait

---

## 8. Remaining Physical Boot Requirements

| Requirement | M20 Status | M30 Need |
|-------------|------------|----------|
| RAM window isolation | ✅ Done (0x94000000) | Do Phase 3 |
| GICv2 + timer | ✅ Working | Verify GIC version |
| Framebuffer + DECON | ✅ Working | Same addresses |
| eMMC read | ✅ Working | Same MSHC |
| Keys | ✅ Working | Verify GPIO |
| iOS root mount | ✅ Working (USERDATA) | Same partition |
| Multiblock eMMC write | ✅ Working (0197/0198/0208) | Reuse patches |
| SMP (6×A53 + 2×A73) | ⚠️ cpus=1 only | Start cpus=1 |
| GPU (Mali-G71) | Not ported | Later |
| Touch (HX83112A) | Not ported | M30 may differ |

---

## 9. Fastest Credible Path Summary

**Do NOT continue current M30 CI approach** (iPhoneOS SDK conflicts, broken config generation).

**Instead:**
1. **Adopt M20's entire build system** (`.github/workflows/xnu.yml` + `darwin-xnu-build`)
2. **Create M30LTE machine config** by patching M20's `0400-m20lte-board-target.patch`
3. **Adapt 3 hardware-specific files**: `A5XELTE.h`, `xnu_boot.c`, `mkadt_m30lte.py` with M30 addresses from live DT
4. **Build on macos-15-intel** → get `kernel.development.m30lte` in ~15 min
5. **Test on device** using M20's proven loader + packer

**Estimated time to linked kernel:** 2-3 days (hardware verification + 3 file adaptations + CI build)

**Estimated time to root-device wait:** +1 day (BOOT flash + cmdline tuning)

**Lock screen:** Requires A73 bringup + 16K pages + GPU → separate effort (M20 hasn't achieved this natively)

---

## 10. License & Attribution

M20 code is GPL-2.0 (shim) and MIT/BSD-style (XNU patches). Retain all copyright headers. Our M30 work must preserve M20 attributions in reused files.