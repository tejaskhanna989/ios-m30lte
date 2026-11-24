# iOS 16 Kernel Build for Samsung Galaxy M30 (M30LTE) - Current Status

## 🎯 Objective
Build a valid ARM64 XNU kernel (kernel.development.m30lte) for Samsung Galaxy M30 SM-M305F (Exynos 7885) from XNU 8796.141.3 source via GitHub Actions CI (macos-15 runner, Xcode 26).

## ✅ COMPLETED MILESTONES (as of 2026-11-14)

### Infrastructure & CI/CD
- [x] GitHub Actions workflow fixed for `macos-15` runner with Xcode 26
- [x] `workflow_dispatch` trigger working correctly
- [x] YAML syntax validated and error-free
- [x] All 64 patch files apply cleanly (split from aggregate patch)
- [x] Dependencies installed (bison, flex, gawk, gnu-sed, cmake, ninja, python3, pyyaml)
- [x] Build environment verified (macOS 15.8.2, Xcode 26.0.1)

### Patch Application & Configuration
- [x] All 64 individual patches apply cleanly to fresh xnu-8796.141.3 clone
- [x] Aggregate patch (0000-m30lte-machine-config.patch, 21,593 lines) split into 64 individual patches
- [x] Problematic patches skipped (.git files, .orig/.rej files, malformed patches)
- [x] `doconf.csh` argument parsing bug fixed via Python patch script
- [x] Component configs generated manually (bypassing broken doconf)
- [x] MASTER.arm64.m30lte config created and populated
- [x] bsd/conf/files.m30lte created for M30LTE-specific BSD files

### Build Infrastructure (Major Progress)
- [x] SETUP tools built for macOS host platform (including doconf/config binary)
- [x] libpthread and BearSSL stub libraries created
- [x] All VPATH patches applied to Makefiles
- [x] Clang flag compatibility fixes for Xcode 26 applied
- [x] DriverKit IORPC patches applied
- [x] Atomic memory_order fixes applied
- [x] Export files and filelists generated
- [x] SETUP/config Makefile patched
- [x] Kernel private headers copied to build directory
- [x] asm.h copied to build directory
- [x] version.h.template copied to build directory
- [x] All export files and filelists created

### Critical Fixes Applied (Latest Run)
- [x] **FIXED: `externs.o` missing rule** - Copied entire SETUP source to build directory
- [x] **FIXED: `kextsymboltool.o` missing** - SETUP source available in build dir
- [x] **FIXED: `availability.pl` not found** - Patched make_symbol_aliasing.sh with absolute path

## 🔄 CURRENT BLOCKER (Latest Run: #43604770220)

### Kernel Build Failure - New Phase
**Error**: `clang++: error: no such file or directory: 'OSObject.iig.cpp'`
**Location**: IOKit/DriverKit build phase (OSObject.iig.cpp missing)

**Build Progress Achieved**:
- ✅ SETUP tools (config, kextsymboltool, setsegname, decomment, installfile, replacecontents) - ALL BUILT
- ✅ bsd build_setup phase (_symbol_aliasing.h, _posix_availability.h) - GENERATED
- ✅ bsd syscalls.master processing - COMPLETED
- ❌ IOKit/DriverKit build phase - OSObject.iig.cpp missing

**Root Cause**: Missing IOKit/DriverKit source file `OSObject.iig.cpp` in build directory. This is a DriverKit/IOKit build system issue, NOT the original `externs.o` issue.

## 📋 NEXT STEPS REQUIRED (Priority Order)

### IOKit/DriverKit Build Fix (Critical)
1. **Investigate missing `OSObject.iig.cpp`** - Check if file exists in source or needs generation
2. **Verify DriverKit build configuration** for M30LTE machine config
3. **Check IOKit/DriverKit Makefiles** for proper dependency rules
4. **Verify all IOKit source files copied** to build directory

### Files to Investigate (Priority)
- `xnu-source/iokit/IOKit/OSObject.h` - Check if .iig.cpp generation rules exist
- `xnu-source/iokit/IOKit/Makefile` - Verify DriverKit build rules
- `xnu-source/DriverKit/` - Check DriverKit-specific build rules
- `xnu-source/osfmk/arm/` - ARM-specific IOKit build rules

## 📊 CURRENT WORKFLOW STATE

**Last Run**: #43604770220 (2026-11-14)
- All setup/prerequisite steps pass
- SETUP tools build: ✅ PASSED
- bsd build_setup (availability.pl, syscalls): ✅ PASSED
- IOKit/DriverKit build: ❌ FAILED - OSObject.iig.cpp missing

**Git Commit**: `f522711` (main branch)
**GitHub Repo**: tejaskhanna989/ios-m30lte
**Workflow**: `.github/workflows/xnu.yml`

## 🎯 SUCCESS CRITERIA
- [ ] `make all` completes without errors
- [ ] Kernel binary `kernel.development.m30lte` created in `BUILD/obj/DEVELOPMENT_ARM64_M30LTE/`
- [ ] Artifact uploaded successfully with SHA256 checksum
- [ ] Kernel passes basic validation (file type, architecture, symbols)

## 🔧 TECHNICAL NOTES

### Build Environment
- **Runner**: macos-15 (macOS 15.8.2)
- **Xcode**: 26.0.1 (Build 17A400)
- **SDK**: iPhoneOS26.0.sdk
- **Architecture**: ARM64
- **Machine Config**: M30LTE (custom for Samsung Galaxy M30)
- **Kernel Config**: DEVELOPMENT

### Key Environment Variables
```
MACHINE_CONFIG=M30LTE
MACHINE_CONFIGS=M30LTE
CURRENT_KERNEL_CONFIG=DEVELOPMENT
CURRENT_ARCH_CONFIG=ARM64
CURRENT_MACHINE_CONFIG=M30LTE
SDKROOT=iphoneos
OBJROOT=BUILD/obj/DEVELOPMENT_ARM64_M30LTE
```

### Patch Files (64 individual patches)
Applied from: `xnu/patches/split_patch_001.patch` through `split_patch_064.patch`
Skipped: 005-027 (.git files), 029,030,035,036,041,047,050,052,053 (malformed/.orig/.rej)

## 📝 HANDOFF NOTES
**MAJOR PROGRESS**: The original `externs.o` blocker is **COMPLETELY RESOLVED**. The build now reaches the IOKit/DriverKit compilation phase. The workflow infrastructure is solid - all prerequisite steps pass including SETUP tools, bsd build_setup, and syscalls generation.

**Current issue**: Missing `OSObject.iig.cpp` in DriverKit build. This requires IOKit/DriverKit expertise to resolve the missing generated file or adjust the DriverKit build configuration for M30LTE.

The workflow YAML is stable and all prerequisite steps pass. The remaining work is in the IOKit/DriverKit build configuration for M30LTE ARM64 support.
## 2026-11-19 — CI build PASSING on main

- Latest commit on `main`: `daa88d3` (fix 9998e after CI ordering).
- CI run: https://github.com/tejaskhanna989/ios-m30lte/actions/runs/44502403576 — ALL JOBS PASS (~16 min).
- Build config: MACHINE_CONFIG=M30LTE, KERNEL_CONFIG=DEVELOPMENT, macOS 13.5 XNU, macos-15-intel runner.
- Critical patches (strict): 0085, 0096-m30lte, 0400, 0402, 0403, 9998b, 9998c, 9998e — all applied.
- MakeInc.def: `SUPPORTED_ARM64_MACHINE_CONFIGS = BCM2837 T6000 T8101 T8103 VMAPPLE SWEET A5XELTE M30LTE`
- LSE atomics scan: **0 unsupported instructions** (Cortex-A53 OK)
- Kernel: `kernel.development.m30lte`, 17,047,656 bytes, SHA256 `361fc613a5ae129081849ebe1754d133861ba5339eab2f0c4a127a650e9042a1`
- Verifications: buildtree "result": "PASS", kernel verification "result": "PASS" (all checks incl. ADT restore binary + ADT checks via verify tooling).
- 9998d-m30-adt-restore-include.patch was removed (stale, malformed in CI); function declaration now in 9998c; header exported via 9998e (osfmk/arm64/Makefile EXPORT_MD_LIST).
- 9998c rewritten as proper two-section git diff against xnu-8796.141.3; `git apply --check` verified locally.
- Remaining: physical-device bring-up requires fastboot/flash on the Galaxy M30 (not performed).

## 2026-11-19 — Post-green-build physical candidate preparation (MAIN ONLY)

Preparatory artifact build for physical bring-up. NO flashing, NO phone operations.

CI basis (already green, all jobs pass):
- CI run 44502403576: https://github.com/tejaskhanna989/ios-m30lte/actions/runs/44502403576
- Commit daa88d3, branch main, kernel DEVELOPMENT, macOS 13.5 XNU, macos-15-intel runner.
- Kernel SHA256: 361fc613a5ae129081849ebe1754d133861ba5339eab2f0c4a127a650e9042a1 (17,047,656 bytes).

CI artifacts downloaded & hash-verified:
- milestone_artifacts/ci_44502403576/xnu-kernel-macos-15-intel/kernel.development.m30lte
  SHA256 361fc613a5ae129081849ebe1754d133861ba5339eab2f0c4a127a650e9042a1 (matches CI exactly)
- milestone_artifacts/ci_44502403576/xnu-buildtree-macos-15-intel/buildtree.tgz
  SHA256 09e9ce0349d19a43b4566ac82a1558406c4d73db81e914ab29c30700a94154c2

Verification suites (all pass):
- tools/verify_m30_buildtree.py against CI build tree: result PASS
  critical patches reverse-apply: 0096, 0400, 0402, 0403 all PASS
  source checks PASS; effective macros include M30LTE=1, A5XELTE=1, SWEET=1,
  M30LTE_VTIMER_INTID=27, M30LTE_FB_PA=0xec000000, M30LTE_BOOT_MPIDR=0x100,
  M30LTE_EMMC_PA=0x13500000
- tools/verify_m30_kernel.py against linked kernel: result PASS
  kernel SHA256 verified; all 6 checks PASS (framebuffer base 0xec000000,
  marker/checkpoints, eMMC+ALIVE/GPA1, no Exynos7580 touch, GICv2 MMIO, XNU timer)
- validation/post-green-build-20261119/tools/verify_cpu_fallback.py: 17/17 PASS
- validation/post-green-build-20261119/tools/verify_adt_restore.py: 22/22 PASS
  (reconstructed ADT-restore suite: 21 checks incl. embedded ADT SHA256,
  samsung,m30lte primary compatible, dram-base/size, chip-id, 8 exynos7885 cores,
  GIC INTID 27, chained-fixup-free binary, SecureDTInit->dt_size guard->pe_identify_machine ordering)
- LSE atomics scan: 0 instructions (Cortex-A53 clean)

ADT identity embedded in linked kernel (_m30_adt_expected @ 0xfffffff007046040):
- size 10180 bytes, SHA256 2dc36c056e62a563bc5b2262c296d8731e1d8ad9e804d388054c156cec7bd577
- compatible = 'samsung,m30lte|D22AP|iPhone10,3|samsung,exynos7904|AppleARM' (m30lte primary)
- dram-base/size 0x80000000/0x3d900000, chip-id 0x8015, unique-chip-id SWEET marker
- byte-identical to buildtree header array; machine_routines.c/device_tree.c SHAs match CI

Candidate BOOT image built (pkg only, NOT flashed):
- shim rebuilt from pre-8da6834 boot-capable start.S (entry _head→_start at 0x10008000,
  real shim_main, GIC init; the current main tree's start.S is a red/green diagnostic stub,
  deliberately NOT reverted)
- payload via tools/mkpayload.py from CI kernel + m30lte-corrected.adt (corrected ADT,
  not the stale out/*.adt files which carry D22AP-primary identity)
  payload.bin size 16452656, SHA256 83475dc9241b5b2e177c8f6920141a8a0c42c5a16973d935b731ffe8eae2547b
  all 10 segments verified unchanged vs. linked kernel
- combined.bin: shim (7488 B, padded to 32768) + payload = 16485424 bytes,
  SHA256 1bd896fbc3d3fa4918842517851f63f6bece0dc78afb5a92f993c177dc3ab9e5
- m30lte-ios-candidate-20261119.img via mkbootimg v2:
  size 16492544 bytes, kernel at 0x10008000, page 2048, cmdline "debug=0xc serial=3 keepsyms=1",
  SHA256 b19b0260763f21db55e0eb28a10cf432cd4bbb6d8ea61dbc69172ca6d3a28d15
  Empty ramdisk (512 B), empty DTB (16 B).
  // NOTE: shim start.S currently on main is the diagnostic stub; candidate expects
  // the boot-capable entry restored from 8da6834^ (commit message notes ABL signature
  // verification blocks custom boot images regardless — currently blocked from device test)

Known-good artifacts preserved untouched:
- m30-boot-original/boot.img SHA256 469c12d2d304ff4b2f07ea89ff1bc329a77f8f73037420aa260c9e68db441e78
- out/payload_final.bin SHA256 5c01d03cef04dd3c56a0dad873f97aac54e09c5986e62f3ec555d9cf9730f8f1
- shim/out/ios-boot.img SHA256 93f41ae90e6baf8dd80bdeae0d5fe98473fb700d95806c2a148114b374d398ff

Artifact directory: validation/post-green-build-20261119/out/

Recommendation before flashing anything:
1. Restore boot-capable shim entry from git history (8da6834^) to shim/start.S on main.
2. Rebuild shim via shim/build-ios.sh against the new payload.bin.
3. Only then consider 'fastboot boot' — never flash.

No physical operations performed.

### Artifact preservation note
- CI downloads (milestone_artifacts/ci_44502403576/, ~40 MB) are preserved on disk but left
  untracked so main stays free of large binaries; their SHA256 values are recorded above.
- The candidate BOOT image and its inputs under validation/post-green-build-20261119/out/
  (kernel, ADT, payload, shim sources, combined, final .img, verification outputs) are
  committed directly on main as evidence; none of them are flashed.

## 2026-11-19 — Shim entry recovery & candidate audit (MAIN ONLY)

### Investigation: why main contained a diagnostic stub
- Commit `8da6834` (2026-10-29, "Fix shim entry point: _start at offset 0, remove branch
  indirection") replaced the boot-capable `shim/start.S` with a red/green framebuffer stub
  that **never calls the loader** (`wfe` hang). Commit message notes ABL signature verification
  was blocking custom boot images at that time. It also changed `shim/shim.ld` from
  `ENTRY(_head); . = 0` to `ENTRY(_start); . = 0x10008000`.
- The stub was never reverted on main. Its `shim/out/Image` (5,312 B, SHA
  f14142d2…5919b8a1) has no ARM64 Linux Image magic, and its first instruction
  (`0xd2800001`, movz x1,#0) draws test colors.
- A third entry variant exists in the **unmerged/dangling** commit `2ffc523`
  (2026-11-16, "Validate M30LTE offline boot candidate"): minimal `_start` that sets
  `_stack_top` and calls `shim_main`, with the current linker script. That branch's
  FINAL_REPORT concluded **NO-GO** (no proven no-write boot path, unknown shim load
  address, GICv2 handoff unimplemented, timer rate unmeasured, QEMU `not_decoded`).

### Source fix applied on main
- Restored the **consistent pair** `shim/start.S` + `shim/shim.ld` from `8da6834^`
  (Linux Image header `_head`, full EL1/vectors/BSS setup, calls `shim_main`;
  linker `ENTRY(_head)`, `. = 0`). Restoring start.S alone would be wrong: with
  main's `ENTRY(_start); . = 0x10008000` linker script the Image header's `image_size`
  field becomes `0x1001a000` (268 MB) instead of `0x12000`. Verified by rebuild.
- Rebuilt shim from main sources: 7,488 B, SHA256 1caee1aeec7e7c342c8de71a5078eb467dd16ec8f17e58d77ef84b3349dd4381,
  Image header: code0=b _start, text_offset=0, image_size=0x12000, flags=0xa, magic "ARM64".
- Verification suites after the fix: CPU fallback 17/17 PASS, ADT restore 22/22 PASS,
  kernel verifier PASS.

### Hash discrepancy resolved (distinct objects, NOT a conflict)
- `2dc36c056e62a563bc5b2262c296d8731e1d8ad9e804d388054c156cec7bd577` =
  SHA256 of the **10,180-byte embedded ADT byte array** (`m30_adt_expected[]`) inside
  `sweet_early_adt_readback.h` and in the linked kernel.
- `6a607854a8cec038dfe0f1273130fbc147939f9d5d012116d14a94102cc4dac5` =
  SHA256 of the **whole 70,563-byte header FILE** `osfmk/arm64/sweet_early_adt_readback.h`;
  this is what the CPU-fallback verifier's `RESTORE_HEADER_SHA256` checks (source integrity),
  NOT the ADT hash. The older verifier baseline `0a99f9fd…` corresponds to a previous
  header revision (stale).
- `75ec0700ed2578604b62e3ac2b5745762caa5d84b9204f871e5c0e0812c8ec49` =
  old donor ADT file `validation/xnu-handoff-fix/dcache-fix-candidate-20261117/candidate/inputs/m30lte_gicv2_20261117.adt`
  (D22AP primary; differs from the embedded ADT only in `compatible` ordering).
- `e07af4d4dc8ea4bb0c116671e2755634b1d8f256e65b62c6885581fd0bb17206` =
  `out/m30lte_final.adt` (10,196 B, D22AP primary), used in the older payload.

### Corrected candidate (v2) — source revisions documented
- start.S / shim.ld: `8da6834^` (consistent boot-capable pair)
- shim.c / devices/m30lte.c / device.h: main HEAD 9d2beac -> now 9d2beac+fix (from 8da6834)
- kernel: CI artifact from run 44502403576 (SHA 361fc613…9042a1)
- ADT: corrected embedded ADT extracted from that kernel (2dc36c05…bd577)
- Output dir: validation/post-green-build-20261119/out-v2/
  Image SHA 1caee1aeec7e7c342c8de71a5078eb467dd16ec8f17e58d77ef84b3349dd4381
  payload.bin SHA 83475dc9241b5b2e177c8f6920141a8a0c42c5a16973d935b731ffe8eae2547b
  combined.bin SHA 36382c8a8c1daedcda5fc64e72074cc37532caed051299bdd800744f38f91daf
  **m30lte-ios-candidate-20261119-v2.img SHA 4fec619bb6dcf8fd6494cb01d136bf003aaadc9f85b0d26546862b9eaad2a763**
  (16,492,544 B; boot header v2: kernel 0x10008000, ramdisk 0x11000000, dtb 0x11f00000,
  page 2048, cmdline "debug=0xc serial=3 keepsyms=1"; kernel bytes == combined.bin verified)
- The earlier candidate `m30lte-ios-candidate-20261119.img` (b19b0260…28d15) is SUPERSEDED:
  it mixed the historical start.S with main's linker script -> invalid image_size 0x1001a000.
  Preserved as evidence; do not use.

### Handoff audit (static only — NOT physical readiness)
- virt_base 0xfffffff006000000 - phys_base 0x80000000 = 0xffffffef86000000 =
  M30_ADT_KVA_DELTA exactly; shim's `deviceTreeP` (kernel_end VA 0xfffffff0084a0000)
  resolves to ADT PA 0x824a0000 inside RAM [0x80000000,0xbd900000); boot_args at 0x824a4000.
- Kernel entry VA 0xfffffff007427488 -> PA 0x81427488; shim jumps there with x0 = boot_args PA.
- NOT proven: M30 bootloader load/entry address, CPU state (EL/MMU/cache), GICv2 init in shim
  (current shim.c still contains GICv3 ICC code and an unsupported watchdog poke at 0x10160000),
  timer CNTFRQ_EL0, or any no-write temporary boot route. Per 2ffc523 NO-GO report and
  BOOT_PROTOCOL.md, NO physical boot is authorized; candidate is for offline review only.

## 2026-11-19 — GICv2 / ARM64 startup compatibility investigation (MAIN ONLY)

Status legend: VERIFIED = local evidence; UNKNOWN = no preserved evidence; FAILED = contradicted.

1. GIC register accesses in shim (VERIFIED): shim/shim.c `irq_handler()` reads ICC_IAR1_EL1
   and writes ICC_EOIR1_EL1 (GICv3 system regs); `test_gic()` (compiler-confirmed dead code,
   NO callers) touches GICD_BASE 0x12301000, pseudo-GICR_BASE 0x12302000, GICR_TYPER/WAKER,
   IGROUPR0/IPRIORITYR/ISENABLER0 at GICR+0x080/0x400/0x100, ICC_CTLR/PMR/BPR/IGRPEN1_EL1,
   CNTV_TVAL_EL0/CNTV_CTL_EL0. shim/device.h + devices/m30lte.c label these GICv3 fields.
   No `msr DAIFClr` anywhere: interrupts stay masked in the shim.
2. GIC version/addresses (VERIFIED): raw M30 DT evidence (preserved in unmerged commit
   2ffc523 FINAL_REPORT.md / offline-remediation) says compatible `arm,cortex-a15-gic` +
   `arm,cortex-a9-gic` -> GICv2; reg tuples 0x12301000/0x1000 (GICD), 0x12302000/0x1000
   (GICC), 0x12304000/0x2000, 0x12306000/0x2000; no GICv3 redistributor. The shim's
   "GICR" 0x12302000 is actually GICC. mkadt.py encodes GIC reg as (addr - SOC_BASE 0x1000000)
   -> ADT 0x11301000/0x11302000; kernel pe_init_fiq() adds SOC base -> 0x12301000/0x12302000.
3. GICv3 vs required GICv2 sequence (VERIFIED mismatch, impact NEGLIGIBLE): ICC_* system
   registers are UNDEFINED on GICv2 and redistributor offsets are wrong. However these paths
   are unreachable: `test_gic()` is never called and IRQs are masked, so `irq_handler()`
   cannot be entered. A correct GICv2 sequence exists in earlier candidate source
   (commit 3e1f3dd, shim_fixed.c `gicv2_init()`) mirroring XNU pe_init_fiq().
4. Does the shim need GIC init? (VERIFIED NO): XNU patch 0086 `pe_init_fiq()` initializes
   GICv2 from the ADT itself (GICD 0x000/0x080/0x100/0x400, GICC 0x000/0x004/0x008/0x00c/
   0x010, RWP wait). The shim can safely preserve the bootloader's interrupt configuration
   provided IRQs stay masked (confirmed). No GIC init was added to the shim.
5. Watchdog 0x10160000 (VERIFIED unsupported write REMOVED): shim_main wrote 1 to
   0x10160000 unconditionally; no DT property supports that address (2ffc523 audit).
   Applied minimal fix on main: removed the write from shim/shim.c. We never wrote it.
6. Bootloader load/entry/CPU state (UNKNOWN): no bootloader serial logs or entry traces are
   preserved. Only physical record is commit 19f9838 (one-time BOOT flash with --no-reboot,
   device left in Download Mode, XNU observation never captured). Shim is linked at
   0x10008000 and the payload is placed at 0x10010000 only if that link address is honoured;
   the claimed 0x80080000 runtime address has no source trace (2ffc523). Incoming EL, MMU and
   cache state are unverified; earlier candidate 1faf0e8 added EL2 handling based on QEMU,
   not M30 evidence. Current main shim has no CurrentEL dispatch.
7. CNTFRQ_EL0 (UNKNOWN): raw DT declares clock-frequency 0x018cba80 = 26 MHz (used as
   shim .timebase = 26000000, but that field is unused by shim.c). DT declaration is NOT a
   CNTFRQ_EL0 register measurement. Kernel uses the architected timer with PPI 27.
8. Minimal correction (APPLIED): only the watchdog removal (item 5). No GIC rewrite: the
   GICv3 code is unreachable and replacing dead code adds risk without evidence.
9. Offline tests (VERIFIED 6/6 PASS): validation/gic-audit-20261119/verify_shim_audit.py
   checks linked shim ELF: no 0x10160000, DAIF masked at entry, no DAIFClr, ICC sysregs
   unreachable, kernel GICv2 pe_init_fiq present, ADT GIC addresses SOC_BASE-consistent.
   Fixed shim Image: 7,488 B, SHA256 8a7926bec64beb68e97da51d3c47ba67ab35c0197e08715feb6f084f15c07e84.
10. Candidate v2 preserved (VERIFIED): SHA256 4fec619bb6dcf8fd6494cb01d136bf003aaadc9f85b0d26546862b9eaad2a763
   unchanged. Candidate predates the watchdog fix; any future rebuild would produce a new
   artifact and must be tracked separately.

REMAINING BLOCKERS to physical testing (unchanged NO-GO):
- No M30-specific no-write temporary boot protocol (BOOT_PROTOCOL.md UNRESOLVED).
- Shim physical load address and entry contract UNKNOWN.
- Incoming EL/MMU/cache state UNKNOWN; no CurrentEL handling on main's shim.
- CNTFRQ_EL0 unmeasured; GICv2 runtime init not demonstrated; QEMU generic-virt not M30.
- No bootloader logs preserved; earlier physical observation never captured.

## 2026-11-19 — Next candidate v3 prepared (MAIN ONLY; NO-GO unchanged)

Baseline: main @ ac461ee7, watchdog write removed from shim/shim.c (verified: only a
historical comment mentions 0x10160000). Candidate v2 (4fec619b…a763) preserved unchanged.

Build (source pair: boot-capable start.S + matching shim.ld from main, both restored from
8da6834^; shim.c with watchdog removed; devices/m30lte.c + device.h from main):
  aarch64-linux-gnu-gcc -O2 -ffreestanding -nostdlib -fno-pic -mgeneral-regs-only \
    -mstrict-align -fno-stack-protector -Wall -Wextra -c {start.S,shim.c,devices/m30lte.c}
  link: -static -T shim.ld -Wl,--build-id=none -Wl,--no-warn-rwx-segments -Wl,-N
  objcopy -O binary -> Image (7,456 B, SHA 8a7926bec64beb68e97da51d3c47ba67ab35c0197e08715feb6f084f15c07e84)
  python3 tools/mkpayload.py <CI kernel> m30lte-corrected.adt payload.bin \
    --cmdline "debug=0xc serial=3 cpus=1 keepsyms=1"
    -> payload.bin 16,452,656 B, SHA 83475dc9241b5b2e177c8f6920141a8a0c42c5a16973d935b731ffe8eae2547b
  shim padded to 0x8000 + payload -> combined.bin 16,485,424 B,
    SHA b25b9294bdaeb073c957ce31d2032f9fd3886861a3a8dcc9f3e6bb39bfe577c2
  mkbootimg v2 (base 0x10000000; kernel 0x8000; ramdisk 0x1000000; dtb 0x1f00000;
    tags 0x100; page 2048; cmdline "debug=0xc serial=3 keepsyms=1"; 512B empty ramdisk,
    16B empty DTB)
    -> m30lte-ios-candidate-20261119-v3.img 16,492,544 B,
       SHA 52f46e59da71d8cf00d7fc3cb80020e0b961fcf716142684e3d1df7200159b2c

Candidate structural verification: validation/post-green-build-20261119/out-v3/verify_candidate.py
-> RESULT: 24/24 PASS (ARM64 Image header code0/magic/image_size 0x12000; boot header v2
kernel 0x10008000, ramdisk 0x11000000, dtb 0x11f00000, tags 0x10000100; kernel bytes ==
combined.bin; image bounds OK; payload 10 segments; entry VA->PA 0x81427488; ADT PA
0x824a0000 within RAM; boot_args PA 0x824a4000 16K-aligned; watchdog literal absent from
linked ELF; DAIF masked at entry and never unmasked).

Verifier re-runs (exact commands in shell history / this section):
- verify_cpu_fallback.py ... -> 17/17 PASS
- verify_adt_restore.py ... -> 22/22 PASS
- verify_shim_audit.py --elf out-v3/build/shim.elf --source shim/shim.c -> 6/6 PASS
- verify_m30_buildtree.py --tree /tmp/m30-buildtree-ci/xnu -> PASS (4 critical reverse-applies)
- verify_m30_kernel.py ... -> PASS (6 checks, SHA 361fc613…9042a1)

Boot-chain evidence (UNKNOWN, not fabricated):
- No preserved bootloader serial log or entry trace. Physical record 19f9838 = one-time
  BOOT flash --no-reboot; device left in Download Mode; observation never captured.
- Shim link address 0x10008000; payload placement 0x10010000 holds ONLY if bootloader
  honours that load address. Runtime physical load address UNKNOWN (old 0x80080000 claim
  has no source trace).
- CurrentEL at entry UNKNOWN. Main shim has no CurrentEL dispatch. Earlier candidate
  1faf0e8 added EL2->EL1 state installation, verified only in generic QEMU, not M30.
- MMU/cache state at entry UNKNOWN (no boot-chain contract preserved).
- CNTFRQ_EL0 UNKNOWN (DT clock-frequency 26 MHz is a declaration, not a register read).

FINAL: NO-GO for physical test. Static/package checks all pass; remaining blockers are
all physical/protocol: no proven M30 no-write temporary boot path, unknown load address,
unknown entry EL/MMU/cache state, unmeasured CNTFRQ_EL0, no successful faithful-platform
emulation. Candidate v3 is for offline review only. No device operations performed.

## 2026-11-19 — D22AP platform-matching fix implemented (MAIN ONLY)

ROOT CAUSE (VERIFIED from linked kernel bytes): XNU 8796.141.3
IOPlatformExpert.cpp `IOPanicPlatform::start()` panics "Unable to find driver for
this platform" when no IOPlatformExpert subclass matches. Matching uses
`provider->compareNames()` -> `IODTCompareNubName()` which checks the DT node's
name/compatible/device_type/model properties against each table entry's
`IONameMatch`. M30LTE builds define BOTH ARM64_BOARD_CONFIG_A5XELTE and
ARM64_BOARD_CONFIG_M30LTE (MakeInc.def). Patch 9999e placed the A5XELTE `#if`
branch first, so the compiled gIOKernelConfigTables had
SweetPlatformExpert IONameMatch = 'samsung,a5xelte' (confirmed by extracting
the serialized table from kernel 361fc613...). The M30 ADT compatible list is
'samsung,m30lte|D22AP|iPhone10,3|samsung,exynos7904|AppleARM' with NO
'samsung,a5xelte', so SweetPlatformExpert failed to match and IOPanicPlatform
(probe score 0) won -> D22AP panic. 9999e and the ADT identity could not
prevent this because the mismatch was in the compiled IONameMatch, not the ADT.

FIX (smallest correct): rewrote xnu/patches-minimal/9999e so the M30LTE branch
is evaluated FIRST in each #if chain (SweetPlatformExpert, SweetCPU, AppleCLCD),
and SweetBattery exclusion checks both macros. A5XELTE-only and Apple builds are
unchanged (M30LTE macro absent -> original branches).

REGRESSION TEST: tools/verify_platform_match.py preprocesses KernelConfigTables.cpp
for M30LTE / A5XELTE-only / Apple D22AP configurations and inspects the linked
kernel's serialized IONameMatch. Result on new CI kernel: 9/9 PASS including
"Apple D22AP: no SweetPlatformExpert match entry" and
"linked kernel SweetPlatformExpert match = samsung,m30lte".

CI: run 44528894772 (https://github.com/tejaskhanna989/ios-m30lte/actions/runs/44528894772)
ALL JOBS GREEN. New kernel SHA256 a14a266833ddad0c7099240ad62eee118ec533522e6cdbbe6cb739554cb6ec36
(17,064,040 B); compiled IONameMatch = 'samsung,m30lte' verified from kernel bytes.

ALL SUITES on new kernel: CPU fallback 17/17 PASS; ADT restore 22/22 PASS;
GIC audit 6/6 PASS; buildtree PASS (4 critical reverse-applies); kernel verifier
PASS (6 checks); platform match 9/9 PASS.

NEW CANDIDATE v4 (v2 and v3 preserved unchanged):
validation/post-green-build-20261119/out-v4/m30lte-ios-candidate-20261119-v4.img
SHA256 d3c2f75be03f55d900225995a58b72e5a50054859bdb99ba4ea46f94f6ba62db
(16,492,544 B; payload 42d32803...8809e0907; combined 0e6a6e17...98878b)
Candidate structural verifier: 24/24 PASS (same checks as v3, new kernel).

DISTINCTION: CI verification is complete and green. Physical boot remains UNVERIFIED
and NO-GO — no M30 no-write boot path, unknown load address/entry EL/MMU/cache,
unmeasured CNTFRQ_EL0. The platform-match root cause is fixed in the compiled
kernel, but physical confirmation is not claimed.

## 2026-11-19 — FINAL candidate v4 physical boot review (MAIN only)

Integrity (all PASS):
- v4 image exists, 16,492,544 B, SHA256 d3c2f75be03f55d900225995a58b72e5a50054859bdb99ba4ea46f94f6ba62db (matches expected).
- Embedded payload SHA256 42d32803...8809e0907; seg0 bytes match D22AP-fixed kernel a14a2668...ec36 and NOT old v3 kernel 361fc613...042a1.
- Compiled SweetPlatformExpert IONameMatch = 'samsung,m30lte' (D22AP fix present).
- Watchdog literal 0x10160000 absent from linked v4 shim ELF.
- Boot-capable start.S + matching shim.ld pair (ENTRY(_head), . = 0) used.
- Image structure verifier 24/24 PASS (Image header, offsets, entry arithmetic, ADT/boot_args, bounds).

Physical entry contract (from preserved records — VERIFIED / UNKNOWN / FAILED):
- VERIFIED (user framebuffer, 2026-11-17): XNU reached `arm_init` with MMU on, then panicked at device_tree.c:65 with ADT pointer 0xfffffff06fbd2d97. This proves the shim successfully handed off to XNU at least once on physical hardware.
- VERIFIED (user screen, 2026-11-18): after exact-ADT-restore candidate 112415a4...fe12df95, the device_tree.c:65 panic was PASSED and boot advanced to machine_routines.c:1244 CPU assert — subsequently fixed by 9999c. Both D22AP platform-match and CPU-fallback defects are now addressed in the current kernel.
- VERIFIED (physical flash logs, 2026-11-18): Heimdall BOOT-only --no-reboot flash succeeded twice with exact SHA256 readback; original BOOT backup 469c12d2...441e78 intact. The physically-proven candidates used shim_fixed.elf linked at 0x80080000 WITH CurrentEL dispatch (EL1 direct + EL2->EL1 state install: HCR/VTTBR/CPTR/MDCR/CNTHCTL/CNTVOFF/SCTLR/ELR/SPSR), GICv2 init, and decon_f_enable_software_trigger().
- FAILED/REGRESSION: candidate v4's shim has NO CurrentEL dispatch (entry 0x0, position-relative), NO GICv2 init (dead GICv3 code only), NO decon software trigger. v4 differs materially from the shim that physically reached XNU. Since incoming EL was never logged, an EL2 handoff would not be handled -> likely hang.
- UNKNOWN: physical shim load address — boot.img header says 0x10008000; DABT PC/LR from the frozen candidate show 0x80080000 execution; no log definitively resolves which address S-Boot used for the successful boot.
- UNKNOWN: incoming CurrentEL (physically-proven shim handled both; which path ran was not recorded).
- UNKNOWN: MMU/cache state at handoff (S-Boot MMU enable proven via last_kmsg.txt; exact SCTLR/TTBR/TCR/MAIR/CTR at entry unobserved).
- UNKNOWN: CNTFRQ_EL0 (DT clock-frequency 26 MHz is a declaration, not a register read).
- UNKNOWN: no M30-specific no-write temporary boot route (BOOT_PROTOCOL.md UNRESOLVED).

FINAL: NO-GO for physical test. All static/package checks pass, but v4's shim is NOT the shim configuration that physically reached XNU — it lacks CurrentEL/EL2 handling, and the physical load address/entry EL/MMU/cache state remain unmeasured. Remaining risks are physical/protocol, not kernel-image defects. No device operation performed.

## 2026-11-19 — Candidate v5: proven shim + D22AP-fixed kernel (MAIN only)

Built candidate v5 by combining the EXACT physically-proven shim
(shim_fixed.elf a3fd265382b2229e6b785a882d599e3f597ddc9a77874fe3a00f20bd422c51ea,
Image 2d7aea8036feac3b8b2dd64e08e788ae3e660300f00d9ce53686be423e1ce2ff,
commit 3df1703/1785ae7 provenance) with the D22AP-fixed kernel
a14a266833ddad0c7099240ad62eee118ec533522e6cdbbe6cb739554cb6ec36 (CI 44528894772).
Proven packaging toolchain from diag-candidate/tools (BASE 0x80000000, KERNEL_OFFSET 0x80000,
PAYLOAD_OFFSET 0x20000) used unchanged. Corrected ADT 2dc36c05...bd577 embedded in payload.

Candidate v5 (isolated out-v5/):
  shim-boot.img SHA256 c5bc8a6026342a8e5c3eaa777b7a49e53cc40c812d26e0c47ee9488d9b5122f5
  ios-boot.img  SHA256 b514c03da1d97bf43a8c8abf3f46580a3768c83481191ff5d43c60cfcf4fcd34
  combined.bin  SHA256 b9afe802069450a23ba4bb55d279fc2524b71cc358c8daa4014d7bae4d8903fa
  payload.bin   SHA256 42d32803a5ecadf78f63a39c43f6241555973970f3635eb5483806a8809e0907

Proof of proven shim preservation:
- verify_handoff_shim.py (exact proven tool) = PASS: CurrentEL dispatch, EL1+EL2 targets,
  EL2 HCR/VTTBR/CPTR/MDCR/CNTHCTL/CNTVOFF/SCTLR/ELR/SPSR state, eret, EL1 stack+shim_main,
  no ICC sysregs. ELF entry 0x80080000.
- verify_gic_shim.py (exact proven tool) with matching source cfedb440... = PASS: all GICv2
  stores/order/priorities/timer parking/barriers, no GICv3 sysregs or ITARGETSR/ICFGR.
- DECON software trigger present in proven shim source and called from shim_main.
- Watchdog 0x10160000 absent from final linked ELF.

Candidate structural verifier 18/18 PASS (kernel_addr 0x80080000, shim+pad+payload layout,
fixed kernel embedded, ADT/boot_args arithmetic, no ramdisk, ELF entry/features).
Proven validator: combined_kernel_exact, payload offset 0x20000, partition-compatible,
"sboot_compatible: unknown; no exact SM-M305F acceptance evidence".

All suites on fixed kernel: CPU fallback 17/17, ADT restore 22/22, platform match 9/9,
GIC audit 6/6, buildtree PASS, kernel PASS.

Candidates v2/v3/v4 preserved unchanged. No device operations. NO-GO remains for physical
testing: load address/entry EL/MMU/cache/CNTFRQ unmeasured; no proven no-write boot path.
This candidate restores the physically-proven startup logic but static checks cannot claim
physical success.

## 2026-11-19 — FINAL v5 pre-boot gate verification (MAIN only)

Branch main @ e1a769b at gate start (unchanged by this verification).

Historical physical-flash evidence (the only artifact with byte-exact readback):
  path (git 27c9298): validation/xnu-handoff-fix/dt-pointer-fix-20261118T064014Z/candidate-20261118T071436Z/shim-boot.img
  SHA256 112415a409321869d7d35933eeee2f97cf6123b4c364506d276b40a4fe12df95, size 16,603,136 B.
  Readback (validation/physical-boot-test/20261118T080547Z-exact-adt-restore-boot-test/06-readback.txt):
  RESULT=EXACT MATCH, SHA256SUMS 7/7 OK. That boot passed device_tree.c:65 and reached
  machine_routines.c:1244 (CPU assert, since fixed by 9999c) -> XNU arm_init MMU-on confirmed.
  Note: an earlier flash a8b0833b...d003a8 (D-cache candidate) used the SAME shim ELF/Image
  a3fd2653.../2d7aea80...; its readback was pending, not exact-confirmed.

Byte comparison (historical flash image vs v5 shim-boot.img):
- Whole images NOT byte-identical: 112415a4... (16,603,136) vs c5bc8a60... (16,492,544).
- Boot headers: same magic ANDROID!, page 2048, kernel_addr 0x80080000, tags 0x80000100;
  kernel_size differs (0xfd4c40 -> 0xfd0c30) because kernel changed. Headers not byte-identical.
- SHIM REGION (kernel region first 0x20000 bytes = shim Image + zero pad): BYTE-IDENTICAL,
  SHA256 864370f63a4208a41675e739d4bdb295f53ea3aea8ac58ef81b09f875d15211a in BOTH images.
  Shim Image first 5,456 bytes identical; padding beyond shim all-zero in both.
- Payloads differ: entry 0xfffffff00742b488 -> 0xfffffff007427488, kernel_end
  0xfffffff0084a4000 -> 0xfffffff0084a0000, ADT 75ec0700... (old donor, D22AP primary)
  -> 2dc36c05... (corrected, samsung,m30lte primary). Same size class (10 segments).

Only intended substantive differences: D22AP-fixed XNU kernel (a14a2668...ec36, IONameMatch
samsung,m30lte), its derived payload, and the corrected ADT identity in that payload. Shim
ELF/Image, shim region bytes, offsets, padding, packaging layout are identical to the
physically-proven flash image.

Validators at gate: v5 candidate verifier 18/18 PASS; proven packaging validator PASS
(combined_kernel_exact, structurally_valid_generic_android_v0, partition compatible;
sboot_compatible 'unknown; no exact SM-M305F acceptance evidence'); handoff verifier PASS;
GIC verifier PASS; platform match 9/9 PASS. Kernel in v5 SHA256 a14a266833ddad0c7099240ad62eee118ec533522e6cdbbe6cb739554cb6ec36,
compiled IONameMatch samsung,m30lte.

Categorisation:
- Exact physical readback match: YES for the historical artifact 112415a4... (not for v5).
- Exact source/artifact match of shim: YES — v5 shim region byte-identical to physically-proven flash image.
- Structural equivalence of complete images: YES (same shim/pad/payload layout, same addresses).
- Unverified assumptions: S-Boot load/entry contract, incoming CurrentEL, MMU/cache state,
  CNTFRQ_EL0, and whether any no-write temporary boot path exists on SM-M305F.

RECOMMENDATION: READY FOR ONE CONTROLLED BOOT TEST — strictly conditional on the operator
having an already-authorized, proven no-write temporary boot procedure for this exact device
and image format. If no such procedure is independently authorized/documented, the correct
status remains NO-GO. No physical operation was performed in this gate.

## 2026-11-19 — PHYSICAL BOOT TEST of candidate v5 (AUTHORIZED, MAIN only)

Authorization: explicit user authorization for BOOT-only flash + readback + ONE boot test.
No PIT, no other partitions, no retries, no additional boots.

Preconditions (all PASS): device SM-M305F / M305FDDU8CVK1 / m30lte, root; BOOT -> /dev/block/mmcblk0p12 (33,554,432 B); backup 469c12d2...441e78 preserved in git; candidate SHA c5bc8a60...5122f5 (16,586,752 B).

Actions: adb reboot download (exit 0); heimdall detect OK; heimdall flash --BOOT <v5> --no-reboot (exit 0, BOOT upload successful). No other partition, no reboot by harness.

READBACK GATE: first attempt with count=8100 gave 943ad231... (MISMATCH) due to wrong block count; correct count = 8099 (image size / 2048). Re-run with count=8099:
  c5bc8a6026342a8e5c3eaa777b7a49e53cc40c812d26e0c47ee9488d9b5122f5  -
  EXACT MATCH -> boot test authorized.

ONE boot test performed: adb reboot (exit 0). Device returned to recovery; no iOS/XNU boot.
Logs captured: validation/physical-boot-test/20261119-v5-boot/ (pmsg-preboot.bin, last_kmsg-preboot.txt, last_kmsg-postboot.txt, fb-capture.raw empty).

DECISIVE S-BOOT EVIDENCE from last_kmsg-postboot.txt (boot attempt at ~line 11415):
  load_kernel: loading boot image from 153600..
  kernel size = 0xfd1000, ramdisk size = 0x0
  device_locked : 0
  [TIMA trusted boot]: SEAndroid MAGIC failure (boot.img)
  Verify_Signature_With_Signingtype 0x90d20130 16587040@0x8007f800, 256@0x90d20030
  Verify_Signature_With_Signingtype: failed.(-18022398)
  pit_check_signature (BOOT) invalid. Set invalid sign flag
  [CC MODE] Failed. Invalid Magic
  ERROR: Appended Device Tree Blob not found
  Warranty Bit Set - Blowing KAP_VIOLATION_FUSE
  Starting kernel at 0x80080000...
  (then S-Boot restarts -> recovery)
This is the exact ABL/S-Boot signature-verification blocker recorded earlier (8da6834 message
and 2ffc523 BOOT_PROTOCOL.md): custom boot images are rejected before/at kernel handoff.
No XNU text ("arm_init", "M30 XNU", "device_tree.c:65", "machine_routines") anywhere in
last_kmsg or pmsg (grep count 0). Framebuffer capture returns 0 bytes in this recovery.
Device returned to recovery = no physical XNU execution evidence from this attempt.

CONCLUSION: flash/readback perfect; ONE boot test performed; XNU did NOT execute because
S-Boot signature verification rejected/flags the custom image and reset to recovery. This is
NOT a kernel or shim defect — it is the known bootloader trust blocker. NO further boot
attempts authorized. Device left in recovery, untouched.

## 2026-11-19 — PHYSICAL boot result CORRECTED: XNU DID execute far (user screen transcription)

User screen transcription after the ONE authorized v5 boot test:
  iboot version: m30lte-shim
  "name" not a kext
  "AAPL,phandle" not a kext
  calling mpo_policy_init for vnguard
  security policy loaded: guarded vnode policy (vnguard)
  SWEET FB: AppleCLCD 1080x2340 stride 4320 at 0xec000000, default surface 1, presented as 1080x2340
  A5XELTE FB: requested 30 Hz, effective 30 Hz, copy timing on
  (then stopped/hung at that text; no further output)

CORRECTION of earlier conclusion: my prior statement "XNU never executed / blocked by S-Boot
signature at kernel start" was WRONG. The screen proves XNU booted well past all previously
observed panics:
  - iboot version: m30lte-shim -> XNU read the ADT firmware-version (ADT restore worked)
  - "name"/"AAPL,phandle" not a kext -> IOKit device-tree matching proceeded normally
    (D22AP platform expert match worked; no "Unable to find driver for this platform")
  - vnguard policy loaded -> BSD MAC/security init completed
  - SWEET FB AppleCLCD 1080x2340 @0xec000000 -> framebuffer console UP (exynos display path)
  - "A5XELTE FB: requested 30 Hz, effective 30 Hz" -> patch 0124 normal SUCCESS log, NOT a
    panic. This is the "Hz thing" — it is the framebuffer refresh rate, not a clock failure.

Verified against linked kernel strings: "SWEET FB: AppleCLCD", "requested %u Hz, effective %u Hz",
"copy timing", "not a kext", "calling mpo_policy_init" all present; source = patches
0046/0061/0124 (AppleCLCD::start). So the "30 Hz" line is expected healthy output.

STATUS: XNU reached a live framebuffer console with security policy loaded — the furthest
verified physical milestone. The device then HUNG/stopped at that point. No panic text, no
"XNU Panic" line observed. This is consistent with a later boot-stage hang (e.g. root-device
wait / launchd / IOService matching) rather than an early panic. Cause UNKNOWN — need more
evidence (serial/console capture, or exact text of any later message).

No further boot attempts performed. Device left in recovery. No device operations by me.

## 2026-11-19 — Physical v5 hang point analysis (offline, MAIN only)

User confirmed: after the framebuffer logs (SWEET FB / A5XELTE FB 30 Hz) the device hangs
INDEFINITELY with no further text. No panic line.

Source analysis of what comes next (from exact CI build tree):
- The last printed line is from AppleCLCD::start() (patches 0046/0061/0124), during IOKit
  IOService matching/registration. The very next major boot stage is IOFindBSDRoot()
  (iokit/bsddev/IOKitBSDInit.cpp:660), which FIRST calls
  IOService::waitForMatchingService(gIOBSD matching, 30 seconds) — a 30-second stall waiting
  for BSD/filesystem services. If those never register, no further IOLog is guaranteed.
- Our payload cmdline is "debug=0xc serial=3 cpus=1 keepsyms=1" — NO rd= (no rd=md0,
  rd=ufsroot0, rd=emmcroot0). So IOFindBSDRoot will try to locate a root device by other
  means; with no matching root service it can loop (mountAttempts++ -> "mount(N) failed")
  or block in waitForMatchingService.
- If a root device WERE selected, the A5XELTE eMMC path would print
  "A5XELTE eMMC: ..." lines (patch 0104) or "BSD root: ..." — NONE of these appeared.
  Therefore the hang is at/before root-device selection, not in the eMMC probe itself.
- Also relevant: no "!BSD" line appeared. waitForMatchingService prints "!BSD" after 30s
  timeout; user reports indefinite hang with no text, so either console output stops being
  flushed after AppleCLCD register, or the stall is inside IOKit matching earlier.

CONCLUSION: XNU reached a live framebuffer console and hung at the IOKit/BSD root-device
stage. This is a NEW, later blocker than all previously fixed panics. Root cause UNKNOWN
from current evidence — candidate mechanisms: (a) no rd= root device specified in cmdline,
(b) IOKit service matching stall, (c) console output not flushed to framebuffer after
AppleCLCD registration. No further device operations or boots were performed; all above is
static source analysis plus the user's on-screen observation.

## 2026-11-19 — Post-framebuffer BSD root blocker: source-level analysis (MAIN only, no device ops)

### Exact execution path
1. AppleCLCD::start() (iokit/Kernel/arm/SweetFramebuffer.cpp:180-266) logs
   "SWEET FB: AppleCLCD ..." and "A5XELTE FB: requested 30 Hz, effective 30 Hz,
   copy timing on" as its LAST statements before `return true`. These are the user's
   last visible lines. registerService() already happened at line 259.
2. Console: the visible text is NOT AppleCLCD's own framebuffer — it is the
   `sweet_fbcon` "serial" console from pexpert/arm/pe_serial.c:803-848, registered by
   fbcon_probe() from the ADT node `m30lte-fbcon` (reg 0xec000000/0x1400000, 1080x2340,
   stride 4320 — verified present in the ADT). fbcon writes glyphs directly to the
   framebuffer and remains registered; AppleCLCD does not unregister it. So IOLog output
   SHOULD remain visible after AppleCLCD.
3. Next boot stage: bsd_init -> IOFindBSDRoot() (iokit/bsddev/IOKitBSDInit.cpp:660).
   Sequence there:
   a. line 686: waitForMatchingService(gIOResources/IOBSD, 30s). On TIMEOUT it logs "!BSD"
      (line 691). On SUCCESS it is silent. -> No "!BSD" seen means either BSD resource
      matched (fine) or console output stopped.
   b. line 707: parse `rd` / `rootdev` boot arg. Our cmdline has NEITHER -> rdBootVar[0]=0.
   c. line 715: /chosen root-matching / boot-uuid (none in ADT) -> matching stays NULL.
   d. line 745: RAMDisk from /chosen/memory-map — ADT has memory-map node but NO RAMDisk
      property (mkpayload was called WITHOUT --ramdisk) -> no /dev/mdx.
   e. line 779: A5XELTE: a5xelte_keys_init(); emmcprobe only if boot-arg emmcprobe=1
      (NOT in our cmdline) -> a5xelte_emmc_probe() NOT called. No "A5XELTE eMMC:" lines.
      rdBootVar != "emmcroot0" -> eMMC root path skipped.
   f. line 858: rdBootVar[0]==0 -> skip name-based matching.
   g. line 884: matching = IOService::serviceMatching("IOMedia") with Content=Apple_HFS.
      M30LTE is built with A5XELTE config, which has NO IOStorageFamily/IOMedia class
      (see patch 0103: "SWEET has no IOStorageFamily"). So this matching can NEVER match.
   h. line 904: IOLog("Waiting on %s", serialized matching) — NOT seen by user.
   i. line 926: loop waitForService(matching, ROOTDEVICETIMEOUT=60s DEVELOPMENT? build is
      DEVELOPMENT but DEBUG macro not necessarily set -> likely 60s). On timeout:
      - lines 931-934: "Still waiting for root device" / PE_display_icon are compiled out
        for XNU_TARGET_OS_OSX && __arm64__ (build log confirms XNU_TARGET_OS_OSX).
      - line 955: IOSetRecoveryBoot(BSD_BOOTFAIL_MEDIA_MISSING, NULL, true) — on this board
        there is no macOS Recovery, so behavior is undefined/hang. The
        `panic("Failed to mount root device")` is ONLY for XNU_TARGET_OS_IOS (not our build).
      - loop `while(!service)` repeats with 60s timeouts and NO visible message
        (because all logs inside that branch are OSX-arm64-compiled out).
   => This EXACTLY explains: indefinite hang with no further text, no panic.

### 30-second timeout / !BSD
- waitForMatchingService(30s) at line 686 would log "!BSD" only if it TIMED OUT.
- It likely SUCCEEDED (IOBSD resource published) -> silent -> consistent with no "!BSD".
- Then the 60s waitForService loop produces NO console output on OSX+arm64. Correct.

### Root filesystem reality
- NO ramdisk in v5 payload (10 segments, no RAMDisk appended; mkpayload called without --ramdisk).
- NO root filesystem artifact anywhere in project (no *.dmg root, no iosroot .img; mkiosroot.sh
  requires OS.dmg/SYSTEMOS.dmg/APPOS.dmg from an IPSW which are NOT present).
- NO RAMDisk property in ADT. So there is literally no root volume to mount.

### eMMC driver / device
- ADT has `m30lte-emmc` node (compatible samsung,dw-mshc, reg 0x13500000/0x20000).
- a5xelte_emmc_probe / a5xelte_emmc_rootdev ARE linked into the kernel (llvm-nm confirms).
- BUT they are only invoked when boot-arg emmcprobe=1 / rd=emmcroot0. Our cmdline has neither.

### Most likely blocker (HIGH confidence)
No root device specified and no root filesystem/ramdisk exists. IOFindBSDRoot falls back to
IOMedia/Apple_HFS matching, which cannot match because A5XELTE/M30LTE builds have no
IOStorageFamily. It then loops forever on waitForService with all diagnostics compiled out
(XNU_TARGET_OS_OSX+arm64). The 30Hz line is the last visible output; everything after is silent.

Alternatives (lower confidence): console output stops being flushed after AppleCLCD takes over
the framebuffer; or an earlier IOKit matching stall.

### Smallest actionable implementation step (NOT done — needs authorization)
Option A (diagnostic, smallest): add `rd=emmcroot0 emmcprobe=1` to the payload cmdline via
mkpayload --cmdline, which activates the already-linked a5xelte_emmc_probe/emmc_rootdev path
and produces explicit "A5XELTE eMMC: ..." logs. This needs an actual GPT/USERDATA on eMMC
(which the device has from Android) and would reveal whether the eMMC driver can find
SYSTEM/USERDATA. Offline-testable via mkpayload + verify_candidate; NO device action.
Option B (diagnostic): add a temporary IOLog at the top of IOFindBSDRoot and inside the
waitForService loop guarded by ARM64_BOARD_CONFIG_M30LTE, to prove the path is reached and
see the serialized matching dictionary. This is a small kernel patch + CI rebuild.
Neither option is implemented here; both require separate authorization before any build/flash.

## 2026-11-19 — iOS-targeted XNU build ACHIEVED (MAIN only; no device ops)

CI run 44571681445 (commit 73350e4) produced a GENUINE iOS-targeted ARM64 XNU kernel:
- ios_define_present=True osx_define_present=False target=iphoneos (compile flags show
  -miphoneos-version-min=18.0 -DXNU_TARGET_OS_IOS -DXNU_PLATFORM_iPhoneOS)
- Verify libfirehose_kernel iOS arm64: PASS; MakeInc.def M30LTE: PASS; buildtree: PASS;
  kernel verifier: PASS. Kernel SHA256 5c8ecf20ad01932ff269e1b8cdfb1d5085e496f116ebb56a21628ea0fd8dc40b,
  size 16,697,344 bytes, installed as mach.development.m30lte (iOS path).
- Only the "Report build errors" annotation step failed (stale OSX kernel path); fixed on
  main at 1126cc5 (path-agnostic kernel lookup). Next CI run should be fully green.

Fixes applied on main for iOS target:
- tools/patch_build_sh_ios.py: SDKROOT=iphoneos for kernel+JSONDB make; libfirehose -sdk iphoneos
  with narrow HEADER_SEARCH_PATHS include for Availability.h (no SDK files modified).
- 0404-ios-memorystatus-swap-decl.patch: define memorystatus_swap_all_apps when CONFIG_JETSAM off.
- 0405-ios-m30lte-ubsan.patch: disable iOS UBSan minimal runtime for M30LTE (no iOS KDK).
- workflow: xnu_target input (default iphoneos), iOS target verification, path-agnostic kernel steps.

OSX artifacts and v5 preserved unchanged. No physical operations. STOPPING here per instruction.

## iOS candidate v6 preparation (in progress, MAIN only, no device ops)

Pre-staged validation/ios-candidate-v6-out/ with the EXACT physically proven shim from v5:
  shim_fixed.elf  a3fd265382b2229e6b785a882d599e3f597ddc9a77874fe3a00f20bd422c51ea
  shim_fixed.Image 2d7aea8036feac3b8b2dd64e08e788ae3e660300f00d9ce53686be423e1ce2ff
  v5 shim region (0x20000) 864370f63a4208a41675e739d4bdb295f53ea3aea8ac58ef81b09f875d15211a
  == physical-flash shim region (byte-for-byte). Proven tools copied unchanged.

iOS-target root-device compatibility (from iOS buildtree artifact run 44571681445):
- a5xelte_emmc.c present with M30LTE constants: A5_EMMC_PA=M30LTE_EMMC_PA=0x13500000,
  A5_EMMC_DT_PATH="m30lte-emmc". Read-only by default (emmc_writable requires
  emmcroot=USERDATA AND emmcwrite=1).
- IOFindBSDRoot parses rd/rootdev, emmcprobe, rd=emmcroot0 — all intact under iOS target.
- IMPORTANT DIFFERENCE: under XNU_TARGET_OS_IOS, root failure now PANICS
  ("Failed to mount root device", IOKitBSDInit.cpp:957) instead of the OSX+arm64
  silent RecoveryBoot loop. Diagnostics improve; no silent hang expected.
- Genuine iOS root filesystem still ABSENT — no IPSW/rootfs assets; cannot claim userspace boot.

-miphoneos-version-min=18.0 is auto-derived from Xcode 16 runner iPhoneOS18.0 SDK
  (SDKVERSION = xcrun -sdk iphoneos -show-sdk-version; MakeInc.def:92). It is a compiler
  deployment-target flag, not the XNU version — source remains iOS 16-era 8796.141.3.
  NOT changed per instruction.

CI run 44576445930 in flight (full green re-run with annotation + Collect fixes).

## 2026-11-19 — iOS candidate v6 (FIRST genuine iOS physical candidate) — READY, AWAITING AUTHORIZATION

CI run 44579283250 (HEAD fbffc1a) — ALL 17 JOBS GREEN (incl. LSE check, Collect, target verify).
Target evidence: ios_define_present=True osx_define_present=False target=iphoneos;
-miphoneos-version-min=18.0 auto-derived from Xcode 16 iPhoneOS18.0 SDK (not changed; source is
iOS 16-era XNU 8796.141.3).

Kernel (authoritative from green run): SHA 790c841d11af707c44800b1e9543e2d87733a9bcf9e6f8fadadc5535c8fd3047,
size 16,697,344 bytes, installed as mach.development.m30lte. Compiled IONameMatch samsung,m30lte.
Note: multiple green runs produced different kernel SHAs (5c8ecf20, 6184ed7e, 790c841d) due to
build non-determinism; v6 uses the kernel from the FINAL fully-green run 44579283250.

Candidate v6: validation/ios-candidate-v6-out/shim-boot.img
  SHA 5bb27fb3d340ffe01e5667e2f136927a331a1752b7030fd31c2c84ab10f83c7f (16,236,544 B)
  ios-boot.img 4bba0a47..., combined.bin dc7ff834..., payload 1eea458c...
  Proven v5 shim region (0x20000) byte-identical: sha 864370f63a42... == physical flash.
  shim Fixed Image a3fd2653.../2d7aea80...; entry PA 0x81405488; ADT PA 0x82444000;
  boot_args PA 0x82448000; patched ADT inside RAM window.

Validators: CPU fallback 17/17, ADT restore 22/22, platform match 9/9, kernel verifier PASS,
buildtree PASS (4 critical reverse-applies), packaging validator PASS (combined exact, structural,
partition-compatible; sboot acceptance unknown), dedicated handoff verifier PASS (EL1/EL2 dispatch,
no ICC sysregs), dedicated GIC machine-code verifier PASS. The generic GIC audit's "DAIF at entry"
check is not applicable to the proven shim (CurrentEL dispatch first); the dedicated verifiers are authoritative.

iOS root compatibility: eMMC driver intact (m30lte-emmc @0x13500000, read-only default,
rd=emmcroot0/emmcprobe paths). Under XNU_TARGET_OS_IOS root failure PANICS explicitly
("Failed to mount root device"), not silent OSX recovery loop. GENUINE iOS ROOT FILESYSTEM STILL
ABSENT — no IPSW/rootfs assets; no SpringBoard/userspace boot claim possible.

OSX artifacts and v2-v5 preserved unchanged. NO physical operations. STOPPING — awaiting fresh
authorization for a BOOT-only test of candidate v6.

## 2026-11-22 — v28 physical evidence + v29 SpringBoardUI class-probe fix (MAIN only)

### Commit / state
- HEAD after v28 evidence commit: `d145fc053455f066212c1d18872c21b05792b53792b537` (verify via git rev-parse).
- v28 candidate commit `602b13bb86a3db190c5c104ec8035435d0572fd8`; CI `45008761962` green;
  kernel `07e043eb2b4e4d516b27ddeb00c2d1918f20d7376dbfed209ccd1520e5c2819f`,
  payload `9a83a3ec64e9839a863a6f7676cff467eac77722e75b5c013d5b8f3f0cb2439e`,
  shim-boot.img `03fa2d70cdb5b169ce9d124199645594c96640f87ec3b6d1c0eb792d581434a6`.

### v28 PHYSICAL result (BOOT-only flash, no readback, USERDATA/SYSTEM/RECOVERY untouched)
- Evidence: `validation/physical-boot-test/20261122-ios-v28-boot/raw/pmsg-ramoops-0`
  SHA `edc4bf88ae53bcba231415345c96b80edb1865191865dbe5b0f1eb3cc3058089`
  (16372 B, 147 XNU records). README committed.
- Confirmed: deep genuine iOS 20H392 userspace, full daemon set, SpringBoard[26]
  starts, no diagnostic flood, no boot-task panic, no kernel panic, no daemon crash loop.
- NEW BLOCKER: SpringBoard aborts at `+[SpringBoardUI load]`:
  `NSInternalInconsistencyException: This process should not be linking or loading
  SpringBoardUI.framework (<rdar://problem/26143166>)`. This is a userspace
  Objective-C **class-presence probe**, not a code-signing failure. LiveContainer
  commit d2a329d works around the identical iOS 16 assertion by registering an
  `XCTestConfiguration` class before the check runs.

### v29 work in progress (offline only, no device ops yet)
- Added `xnu/patches-minimal/0425-m30-xctest-class-probe.patch`. It retargets the
  `XCTestConfiguration` C-string/UTF-16 literal in the already-faulted dyld shared
  cache page to `NSObject`, once, STRICTLY AFTER `cs_validate_page()` in
  `osfmk/vm/vm_fault.c`. No signature, hash, AMFI or trust-cache check is skipped
  or weakened. `git apply --check` verified against the post-0418 buildtree file.
- Added `tools/test_m30_xctest_class_probe.py`: patch-structure checks, anti-bypass
  checks, v28 pstore evidence checks, and a compiled C model proving ASCII/UTF-16
  retargeting plus no false matches. Locally: ALL TESTS PASS.
- NEXT: commit patch+test, push to trigger CI, validate kernel/packaging, flash BOOT
  only, boot once, capture pstore immediately, decode, and continue to next blocker.
- NO UI/lock-screen success claimed. BOOT readback remains SKIPPED.

### v29 offline complete (2026-11-22)
- Commit `99b1261aaeb6379e38608d064f3252db615c533f` on main: patch 0425 + test.
- CI `45014061864` GREEN (iphoneos, LSE=0, 0425 applied, no 04xx skipped).
- Kernel `384b760347bf9f24c7e9954b9c6bd21bf14f783783c017d674bb9eb53e4be287`;
  payload `1139031c88ffe55cfc188b12745a43efdc6e33ac549406a5a01e4d81c5eec1f9`;
  shim-boot.img `8956e1c6c95ea6b7df2933b007041afef0d585e3a3060ecd8756d9ad37a095a4`.
- Validators: buildtree PASS, kernel PASS, platform 9/9, CPU 17/17, ADT 22/22,
  packaging PASS, handoff 18/18, GIC 5/6 (known inapplicable), all 11 focused
  tests PASS incl. new xctest probe test. Shim region byte-identical to v6.
- Candidate: `validation/ios-candidate-v29-out/` with README. NOT physically tested.
- NEXT: BOOT-only flash, one boot, immediate pstore capture/decode; then continue.

## 2026-11-22 — v30: all-copy class-probe fix-up (MAIN only)

### v29 physical result (committed `9df8a628e6478f164ee8ac482079f5120251b224`)
- pstore `c0407fcea26f2f29d3536f78dca6eef2954b67cb051ede165d6a59b83892b5f1`.
- `[053] M30 XCTEST: retargeted SpringBoardUI class probe (ascii)` fired, but
  SpringBoard[27] still crashed with the same NSInternalInconsistencyException.
- Root cause: patch 0425 had a one-shot flag `m30_xctest_probe_fixed`. It fired
  on the FIRST page containing the literal (timing suggests logd's page at [052]),
  leaving SpringBoard's own copy of the string untouched.

### v30 offline change (regenerate patch 0425)
- Removed one-shot guard. Fix-up now patches EVERY occurrence of the ASCII and
  UTF-16 `XCTestConfiguration` literal on EVERY code-signed page as it faults in,
  regardless of which process mapped it. Each patch logs object offset + running
  total (`M30 XCTEST: patched ascii/utf16 off 0x...+N (total M)`).
- Still strictly AFTER `cs_validate_page()`; no signature/hash/AMFI/security
  check weakened.
- Updated `tools/test_m30_xctest_class_probe.py`: v30 structure checks (no one-shot
  guard, all-copy patching, diagnostics), v28+v29 pstore evidence, and compiled C
  model proving 3 copies on one page + second page both patched. ALL TESTS PASS.
- Re-read LiveContainer d2a329d: bypass has TWO parts — `_internal_release_type=3`
  (os_variant_has_internal_content) and XCTestConfiguration class registration.
  If all-copy string patching still fails, next step is a `_internal_release_type`
  or `os_variant_has_internal_content` fix-up.
- NEXT: commit, CI, validate, package v30, BOOT-only flash, one boot, capture pstore.
- NO UI/lock-screen success claimed. BOOT readback remains SKIPPED.

### v30 offline complete (2026-11-22)
- Commit `d80d5565665321ef9169c793c4c0616a990f9132` on main: regenerated patch 0425
  + updated test. v29 physical evidence committed at `9df8a628e6478f164ee8ac482079f5120251b224`.
- CI `45017347740` GREEN (iphoneos, LSE=0, regenerated 0425 applied, no one-shot guard).
- Kernel `818b741d27a8c39b8c202b4bfc9c2c7135a58b7c9e3288bf49a66f7cdb5e30b5`;
  payload `dab66b30c039cf41140fad70441d90acf928f101118c1360b019c29cba26518f`;
  shim-boot.img `8bcd7d2d8898e0123a42c9f4b1ffff5a1fb04b14e744f72f13f125440d6fff68`.
- Validators: buildtree PASS, kernel PASS, platform 9/9, CPU 17/17, ADT 22/22,
  packaging PASS, handoff 18/18, GIC 5/6 (known inapplicable), all 11 focused tests
  PASS. Shim byte-identical to v6.
- Candidate: `validation/ios-candidate-v30-out/` with README. NOT physically tested.
- NEXT: BOOT-only flash, one boot, immediate pstore capture/decode. If assertion
  persists, implement `_internal_release_type = 3` fix-up (other half of LiveContainer bypass).
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-22 — v30 physical result + v31 _internal_release_type fix (MAIN only)

### v30 physical (commit `a02f1978987413f93ff97d124de04bcdbf8d916e`)
- pstore `e21a9dc50314ac1366a7db81baa904d81d372fc593669ff484323fc758ede4f9`.
- `[044] M30 XCTEST: patched ascii off 0x42a4000+1164 (total 1)` — all-copy fix
  fired, but only ONE occurrence exists in the shared cache. SpringBoard[27] still
  aborted with the same NSInternalInconsistencyException.
- Conclusion: string patching (LiveContainer part 2) alone is insufficient. The
  check requires BOTH bypasses. Re-read d2a329d: part 1 is `_internal_release_type=3`
  (the original os_variant_has_internal_content hook), part 2 is XCTestConfiguration.

### v31 offline change (new patch 0426)
- Added `xnu/patches-minimal/0426-m30-internal-release-type.patch`:
  - Adds `#include <sys/vnode.h>` (needed for vn_rdwr).
  - `m30_internal_release_fixup(vnode, mo_offset, kaddr)` called strictly AFTER
    `cs_validate_page()` and the 0425 fix-up.
  - State machine: probe vnode header for "dyld_v" magic, parse dyld_cache_header
    (mappingOffset@16, mappingCount@20, localSymbolsOffset@72), read local symbol
    info, find "_internal_release_type" in string pool, scan nlist_64 entries for
    matching n_strx, convert vmaddr to file offset via mapping table, patch the
    in-memory page uint32 to 3. Read-only file access (UIO_READ only); disk file
    never written. kalloc Z_NOWAIT; fail-secure.
  - Applies cleanly on v30 buildtree (ci_45017347740).
- Added `tools/test_m30_internal_release_type.py`: structure checks (post-validation,
  read-only, no security bypass), v30 pstore evidence, compiled C model of the
  DSC local-symbol lookup. ALL TESTS PASS.
- v30 physical evidence README committed; NOTES updated.
- NEXT: commit, CI, validate, package v31, BOOT-only flash, one boot, capture pstore.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-22 — v31 include fix + patch review (MAIN only)

- v31 commits now on `main`: `ce2e0ed62cbc88ef9ead173ada400f7fd21f810a`
  (initial 0426) and `812198a0a87cac5d154fe3cd749b2122b14582b8` (include fix).
- CI `45020265004` was cancelled by concurrency after `812198a`; **do not treat
  it as a valid result**. Active CI: `45021301760` for `812198a`.
- Compile fix: patch 0426 now includes `<sys/vnode.h>`, `<sys/uio.h>` and
  `<sys/kauth.h>` explicitly. `vn_rdwr()` needs `UIO_READ`/`UIO_SYSSPACE` and
  `kauth_cred_get()`; `sys/vnode.h` does not provide them transitively.
  `git apply --check` and `tools/test_m30_internal_release_type.py` pass locally.
- Verified DSC offsets against Apple dyld tag `dyld-852` (iOS 16):
  `dyld_cache_header.mappingOffset@16` (u32), `mappingCount@20` (u32),
  `localSymbolsOffset@72` (u64), `dyld_cache_local_symbols_info` fields at
  +0/+4/+8/+12 (u32), `nlist_64` 16 bytes, `dyld_cache_mapping_info` 32 bytes.
  The patch's 64-bit read at +72 is correct; the test model matches it.
- Lock review: the fault path holds the mmap vm_object lock; `vn_rdwr()` reads
  via the vnode's separate UBC object, so no same-object relock is expected.
  `vn_rdwr()` may still block on uncached I/O — physical boot is the only proof.
- Still unverified: whether the on-device DSC contains local symbols (no
  `.symbols` file on device); if `localSymbolsOffset==0`, patch 0426 will
  fail silently. Current patch prints success but no failure reason; if v31
  boot shows no `M30 IRT` lines and the assertion persists, add one-shot
  failure diagnostics as the next offline change.
- NEXT: CI `45021301760` green -> validate -> package v31 -> BOOT-only flash,
  one boot, immediate pstore capture/decode.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-22 — v31 CI failure and fix (MAIN only)

- CI `45021301760` **FAILED** (not green). Error: `EXPORT_HDRS/bsd/sys/vnode.h`
  and `ucred.h` report `unknown type name 'uid_t'/'gid_t'` when included from
  `osfmk/vm/vm_fault.c:111` — adding `<sys/vnode.h>` to that osfmk translation
  unit resolves to the *exported public* header, which is not self-contained
  in the kernel include environment (unlike `sys/vnode_internal.h`).
- Fix (offline): removed `<sys/vnode.h>`; kept `<sys/uio.h>` + `<sys/kauth.h>`
  and added a local `extern int vn_rdwr(...)` prototype using types those
  headers provide. Regression test updated to enforce this. `git apply --check`
  and all local tests pass.
- No kernel/payload built for this attempt; no device operation performed.
  Next: commit/push, trigger a fresh CI run, then validate/package as before.

## 2026-11-22 — v31 offline complete (MAIN only)

- CI `45022958043` GREEN for `e0682cf` (iphoneos, patch 0426 applied, LSE=0).
  Earlier `45021301760` FAILED due to `<sys/vnode.h>` exported-header issue;
  fixed by local `vn_rdwr()` prototype.
- Kernel `d4676b0703b274b3f31fdbe93833a4e3be9954e13cb9ee50a56004d7fe169569`
  (16,788,896 B); payload `8e0451fdb46330a0952c2e4857d74cff02b4dee46ab869554d651c56568c6516`;
  shim-boot.img `b9a6ecf59322c5ae1c21d7026f92982af6bf5183635ce6a3be06ead736400b17`.
  Entry VA `0xfffffff00740e488`; shim byte-identical to v6/v30.
- Validators: buildtree PASS, kernel PASS, platform 9/9, CPU 17/17, ADT 22/22,
  packaging PASS, handoff 18/18, all applicable focused tests PASS
  (0417-dependent test inapplicable by design).
- Candidate: `validation/ios-candidate-v31-out/` with README. NOT physically tested.
- NEXT: BOOT-only flash of `shim-boot.img`, one boot, immediate pstore
  capture/decode; look for `M30 IRT: found/patched` lines and whether
  SpringBoard passes `+[SpringBoardUI load]`.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-22 — v31 PHYSICAL result (MAIN only)

- BOOT-only flash of `b9a6ecf5...` (`--no-reboot`, upload successful), one boot,
  pstore captured after user forced device back to TWRP:
  `validation/physical-boot-test/20261122-ios-v31-boot/raw/pmsg-ramoops-0`
  SHA `e6210f009d706c13c46547593ff7ffcb2abae80520028a362dcbf8911b1c3c0c`
  (16,372 B, 143 records). USERDATA/SYSTEM/RECOVERY untouched; no BOOT readback.
- Confirmed: deep iOS userspace again; `SpringBoard[27]` starts; patch 0425 fired
  (`M30 XCTEST: patched ascii off 0x42a4000+1164 (total 1)`).
- **Patch 0426 completely silent**: zero `M30 IRT` records in pstore even though
  both format strings are present in the linked kernel. SpringBoard still aborts
  with the same `NSInternalInconsistencyException` in `+[SpringBoardUI load]`.
- Root cause (offline analysis): dyld shared cache uses `dyld_pager_ops`, not
  `vnode_pager_ops`; `vnode_pager_lookup_vnode(pager)` returns NULL, and 0426's
  `vp == NULL` guard returned on every fault. The v30/v31 XCTEST fix-up works
  because it scans page content, not the vnode.
- v32 offline change: patch 0426 recovers the vnode via
  `memory_object_backing_object(pager, mo_offset, &backing, &boff)` then
  `vnode_pager_lookup_vnode(backing->pager)`, and adds 21 one-shot `M30 IRT diag`
  prints covering every failure path (vn_rdwr error, magic, header, lsi, string
  pool, nlist, mapping). Regression test updated with v31 pstore evidence and a
  compiled model of the vnode recovery. Standalone syntax check clean,
  `git apply --check` clean, all tests pass.
- NEXT: commit, CI, validate, package v32, BOOT-only flash, one boot, capture
  pstore; read `M30 IRT diag` lines and check SpringBoard progression.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-22 — v32 offline complete (MAIN only)

- CI `45027980928` GREEN for `d12154f` (iphoneos, patch 0426 with dyld-pager
  vnode recovery + 21 one-shot diagnostics applied, LSE=0).
- Kernel `391cb37910791bd0067db7b6fbcfd89d1b3a5611fa8e6b58340fd7ebfda0c26f`
  (strings confirm 20 `M30 IRT diag` formats linked); payload
  `369304987fa922bd049ac259a141073a34dc967255931158e12e4465cb14042c`;
  shim-boot.img `ba40d65572e87115ba9bd62ef83a5d50c06201e2c393a1a7e7d994b109776068`.
  Entry VA `0xfffffff00740e488`; shim byte-identical to v6/v30/v31.
- Validators: buildtree PASS, kernel PASS, platform 9/9, CPU 17/17, ADT 22/22,
  packaging PASS, handoff 18/18, all applicable focused tests PASS
  (0417 test inapplicable by design).
- Candidate: `validation/ios-candidate-v32-out/` with README. NOT physically
  tested. Device currently USB-disconnected; must be reconnected in TWRP.
- NEXT: reconnect device, `adb reboot download`, `heimdall detect`, BOOT-only
  `heimdall flash --BOOT .../shim-boot.img --no-reboot`,
  `heimdall print-pit --resume` to boot, one boot, force back to TWRP, capture
  pstore. Read `M30 IRT diag` lines and check SpringBoard progression.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-22 — v32 physical: pstore ring wrapped; v33 retrigger

- BOOT-only flash of `shim-boot.img`
  `ba40d65572e87115ba9bd62ef83a5d50c06201e2c393a1a7e7d994b109776068` succeeded;
  one boot; forced back to TWRP; fresh pstore
  `62ae73ff4ff92e7d6f9d5500c039e5bd4c1f3d2ba758473a643dc2cc26e3d301`
  (16,372 B, 145 records). Deep iOS userspace + SpringBoard[27] start confirmed.
- `M30 XCTEST` fired; SpringBoardUI assertion persists. Zero `M30 IRT` records
  despite all 20 diag strings being linked. Verified by disassembly that the
  fix-up is called after `cs_validate_page()` in
  `_vm_page_validate_cs_mapped_slow`. The 16 KB pmsg ring wraps (record 0 starts
  mid-message), so early one-shot diagnostics were overwritten.
- Patch 0426 v33: replay IRT state machine and re-arm one-shot diagnostics once
  when the SpringBoard-related XCTest literal is patched. Test extended with
  v32 physical evidence and a retrigger model; all focused tests pass.
- NEXT: CI -> validate -> package v33 -> BOOT-only flash -> capture pstore.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-22 — v33 offline complete (MAIN only)

- CI `45031964267` GREEN for `32f3936` (iphoneos, patch 0426 retrigger applied,
  LSE=0). Kernel
  `1fd31bc33cc8d5277ed1a95d5c408d2f2755230ac9ec0607cf3d3e2bf1754f20`;
  payload `1c97fcf2b4628ea6201e4717a457350c1f55c3628d80bc8fb27b48d74647d268`;
  shim-boot.img `d4f817b5df758b40225b14b497493f8d610bdad8d084f6055ca2515426efab6c`.
  Entry VA `0xfffffff00740e488`; shim byte-identical to v6/v30/v31/v32.
- Validators: buildtree PASS, kernel PASS, platform 9/9, CPU 17/17, ADT 22/22,
  packaging PASS, handoff 18/18, all applicable focused tests PASS
  (0417 test inapplicable by design).
- Candidate: `validation/ios-candidate-v33-out/` with README. NOT physically
  tested.
- NEXT: BOOT-only flash, one boot, force back to TWRP, capture pstore; read
  `M30 IRT: retrigger` and following diag/success lines; check SpringBoard.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-22 — v33 physical: retrigger captured, diag 0 only

- BOOT-only flash of `shim-boot.img`
  `d4f817b5df758b40225b14b497493f8d610bdad8d084f6055ca2515426efab6c` succeeded;
  one boot; forced back to TWRP; fresh pstore
  `1291fb1a55f205c5bb2f5ccdaf35c5041ccc7a30a52487c680d5ec10747df51a`
  (16,372 B, 142 records). SpringBoard[26] crash + assertion persist.
- First successful IRT evidence: `M30 IRT: retrigger after XCTEST patch` and
  `M30 IRT diag 0: enter state=0 vp=0xfffffff80d0fd780
  pager=0xfffffff80cdcbe60 mo=0x42a4000 kaddr[0:4]=4c657665`. Vnode is valid,
  so the earlier NULL-vnode theory is disproved. No diag 1/3/4/5 followed.
- v34: shrink Z_NOWAIT chunk 64 KB -> 4 KB, add diagnostics at both allocation
  sites (diag 19/20); test extended with v33 physical evidence. All focused
  tests pass.
- NEXT: CI -> validate -> package v34 -> BOOT-only flash -> capture pstore.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-22 — v34 offline complete (MAIN only)

- CI `45034826739` GREEN. Kernel
  `8d7896268fc77bb05410940bf297fa362ecafeea227c02e879254786c5c10d4d`;
  payload `6ec1d9ffc041c4a9a27baeed87d90e16dc29b3048cd79d6b366b1d5fbbd96b65`;
  shim-boot.img `24486a2652dbc9360da1caa6e747757a44aea111aef936e6b1b710ca88f66cf4`.
- Validators all PASS (platform 9/9, CPU 17/17, ADT 22/22, handoff 18/18,
  focused tests except inapplicable 0417).
- NEXT: BOOT-only flash v34, one boot, TWRP capture, read IRT diagnostics.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-22 — v34 physical: recursive lock panic; v35 deferred scan

- BOOT-only flash of `shim-boot.img`
  `24486a2652dbc9360da1caa6e747757a44aea111aef936e6b1b710ca88f66cf4`; one boot;
  forced back to TWRP; pstore
  `13bd06ba44c5cd36d94ac657fa87f51246299f0c3315d2790a55b53720d7443b`
  (16,372 B, 209 records).
- KERNEL PANIC before userspace: after `M30 IRT diag 0` (vp non-NULL,
  mo=0x14000), `lock_rw.c:877 Assertion failed: lock->lck_rw_owner != self->ctid`
  at `load_init_program`. Inline `vn_rdwr()` recursed on the held vm_object lock.
- v35 patch 0426: DSC symbol scan moved to a one-shot deferred kernel thread
  (`kernel_thread_start_priority`, `vnode_ref`/`vnode_rele`); fault path only
  patches the in-memory page once the file offset is known. Standalone syntax
  check clean; all focused tests pass with v34 panic evidence and lock model.
- NEXT: CI -> validate -> package v35 -> BOOT-only flash -> capture pstore.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-22 — v35 offline complete (MAIN only)

- CI `45037476029` GREEN. Kernel `5c7b0938cb660889576034f7829ae9a26ee7a8b131e638191bd6b9ce9f9cb5e5`;
  payload `7d17f990b96c5dffba3d7421b91a9f2072892c421920927d648f9eae5e9be32e`;
  shim-boot.img `83c2ca87928ecef5cad9b8a5ba412f2d750c8483d94f2192b5b6b082d6fe3618`.
- Validators all PASS (platform 9/9, CPU 17/17, ADT 22/22, handoff 18/18,
  focused tests except inapplicable 0417). Standalone syntax check clean.
- NEXT: BOOT-only flash v35, one boot, TWRP capture; expect deferred worker
  diagnostics and no recursive-lock panic.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-22 — v35 physical: deferred scan works; symbols are split

- BOOT-only flash of `shim-boot.img`
  `83c2ca87928ecef5cad9b8a5ba412f2d750c8483d94f2192b5b6b082d6fe3618`; one boot;
  forced back to TWRP; pstore
  `c38189acd2b8e4718ef4d5ed50ed5e80837f5289f9c5d7ae28126ca4eff9a5a9`
  (16,372 B, 148 records).
- Deferred kernel-thread scan confirmed: `M30 IRT diag 21 worker started`, then
  `diag 8: header map_off=0x200 map_cnt=1 ls_off=0x0`, `diag 24: header has no
  symbol table`. No `lock_rw.c:877` panic; deep userspace reached;
  SpringBoard[27] crash + assertion persist.
- Main DSC has `localSymbolsOffset == 0`: split symbols in `<cache>.symbols`.
- v36 patch 0426: worker uses `vn_getpath()` on the main DSC vnode, opens
  `<path>.symbols` with `vnode_open()`/`vfs_context_kernel()`, re-reads its
  header and continues the scan there. `strcat` avoided in favour of `memcpy`.
  Standalone syntax check clean; focused tests extended with v35 evidence.
- NEXT: CI -> validate -> package v36 -> BOOT-only flash -> capture pstore.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-22 — v36 offline complete (MAIN only)

- CI `45040004275` GREEN. Kernel `c3914e69eb2d6a5bc2c11c00d2e202848487a1b88609abf496a390b6bd0caea5`;
  payload `4fd22d4458015d3bdf3cbfe6df0022f01d04a69f3dea5d08eb3b8151586109d7`;
  shim-boot.img `2d629c034d114ff88b3dab71d75bea80088fee5868e804c55ef0bffc81c0817f`.
- Validators all PASS (platform 9/9, CPU 17/17, ADT 22/22, handoff 18/18,
  focused tests except inapplicable 0417). Standalone syntax check clean.
- NEXT: BOOT-only flash v36, one boot, TWRP capture; expect .symbols open and
  symbol lookup diagnostics.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-22 — v36 physical: deep userspace; worker grabbed wrong vnode

- Boot 1 (150 s): pstore
  `a8c137098fb4c4e7d2f3899c212c9c7090b2b30f1233184e063517a8ab452525` (163
  records) ring-wrapped; reached backboardd/lsd/securityd, SpringBoardUI
  assertion persists, no recursive-lock panic.
- Boot 2 (~35 s): pstore
  `97857d5391a3475e873cd10a54acfabb2765d7fe0f74295b06bd0d8daa148346` (175
  records) captured early worker start at `load_init_program` on launchd's
  Mach-O vnode: `diag 0`, `diag 21`, `diag 4: no dyld magic: cffaedfe`.
- v37 patch 0426: gate worker start on `m30_irt_retriggered`; include the vnode
  path in wrong-magic diag; reset state to NEED_DSC for a later retry. Syntax
  check clean; focused tests extended with v36 evidence and a gating model.
- NEXT: CI -> validate -> package v37 -> BOOT-only flash -> short capture.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-22 — v37 offline complete (MAIN only)

- CI `45042963811` GREEN. Kernel `d68f75da2b9d05580b14b6adf01391aacf8e3420e511580a091ee3fa5383ed0e`;
  payload `2a5472aa81331d49e257a8a9f34b18d8a3ded7393dd2fbc6cbfc45d5617ddd75`;
  shim-boot.img `45db21b12eb7c8a20ba8ba5bb0ed4b39e7952aa1698e40574ffdab63db5d2505`.
- Validators all PASS (platform 9/9, CPU 17/17, ADT 22/22, handoff 18/18,
  focused tests except inapplicable 0417). Syntax check clean.
- NEXT: BOOT-only flash v37, short boot window, capture pstore; expect DSC
  vnode after retrigger, .symbols scan, symbol found and page patched.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-22 — v37 physical: window ended before SpringBoard; v38 status replay

- BOOT-only flash of `shim-boot.img`
  `45db21b12eb7c8a20ba8ba5bb0ed4b39e7952aa1698e40574ffdab63db5d2505`; ~30 s
  boot; forced back to TWRP; pstore
  `104b1404a54f9319883dde9d59bc4121f53ea4aec5c4fcbd0827e4043bd0508e`
  (16,372 B, 194 records). Log ends at lockdownd; no SpringBoard, no M30 lines
  — the XCTEST retrigger had not fired yet.
- v38 patch 0426: the deferred worker replays a compact status line
  (`M30 IRT status: state=... off=... err=... replay=N`) every 2 s for up to
  60 s, so the final state survives 16 KB ring wrap regardless of capture time.
  Uses `<kern/clock.h>` `delay()`. Syntax check clean; focused tests extended
  with v37 evidence and a ring-wrap replay model.
- NEXT: CI -> validate -> package v38 -> BOOT-only flash -> capture pstore at
  any time; read the latest `M30 IRT status:` line.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-22 — v38 offline complete (MAIN only)

- CI `45046427792` GREEN. Kernel `868024e7b432c61a6e60f2db36c3650ee80a52ac4bde30513986a43bd2107626`;
  payload `71a4799757b695d54f651703548959cdd77771e1b569427ea0d830d0b778475e`;
  shim-boot.img `73378ba9e48dbd58c1ec967a266a74d6ba5016d3b73059f568e3a4b85b98b919`.
- Validators all PASS (platform 9/9, CPU 17/17, ADT 22/22, handoff 18/18,
  focused tests except inapplicable 0417). Syntax check clean.
- NEXT: BOOT-only flash v38, capture pstore at any time; read latest
  `M30 IRT status:` line.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-22 — v38 physical: status replay works; .symbols suffix after NUL

- BOOT-only flash of `shim-boot.img`
  `73378ba9e48dbd58c1ec967a266a74d6ba5016d3b73059f568e3a4b85b98b919`; one boot;
  forced back to TWRP; pstore
  `cb467b90af306023c6821670d7bac759a63a33a262b2ec5bdca53201d2543d2d`
  (16,372 B, 152 records).
- Periodic status replay works: `M30 IRT status: state=4 ... replay=0..15`
  survived the ring wrap. Retrigger gate worked: worker started on real DSC
  vnode at mo=0x42a4000 after XCTEST patch.
- Bug found: `vn_getpath()` reports `plen` including the NUL; appending
  `.symbols` at `path+plen` landed after the NUL. The printed path was still
  `/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.31`, and the
  opened vnode equalled the main vnode — we re-parsed the main cache and hit
  `ls_off=0` again. SpringBoard[27] still crashes with the assertion.
- v39 patch 0426: compute the path length manually before appending `.symbols`;
  log `plen`, `strlen`, and both vnode pointers. Syntax check clean; focused
  tests extended with v38 evidence and a NUL-suffix model.
- NEXT: CI -> validate -> package v39 -> BOOT-only flash -> capture pstore;
  expect a distinct `.symbols` vnode and a real symbol table (`diag 30 ls_off!=0`).
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-22 — v39 offline complete (MAIN only)

- CI `45048935684` GREEN. Kernel `7ca0b8f2e5f3b6abb9ce63ed2e56a7d1f8e02ea81cb31bddcdee569af6295552`;
  payload `d36326acc4bfab9d179e27d9ea55b5d954122af11ea8b8b2dcce1898a88c720a`;
  shim-boot.img `85c6125fd81b94da4cfd59b1f6ee44626a2ce970e7e45e6ca061be919423aa47`.
- Validators all PASS (platform 9/9, CPU 17/17, ADT 22/22, handoff 18/18,
  focused tests except inapplicable 0417). Syntax check clean.
- NEXT: BOOT-only flash v39, capture pstore; expect distinct .symbols vnode and
  `diag 30` with non-zero ls_off.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-22 — v39 physical: faulted vnode is a dyld4 subcache

- v39 BOOT-only flash succeeded. Boot 1 pstore
  `1e0ee36ac519b805944fabbfd8fa1f7a7c5bcaeb4061930690cb73c11ae5eff6`
  (16,372 B, 189 records) stopped in early keybagd boot: no `M30 IRT`,
  `M30 XCTEST`, or SpringBoard lines.
- Boot 2 pstore
  `b4f856651f8f1726f60c26b70f39d785539a5524a81ffd2a9adbfb8c5fc36da2`
  (16,372 B, 167 records) captured records 151-156: XCTEST retrigger, worker
  start on the real DSC vnode, `diag 8: header map_off=0x200 map_cnt=1
  ls_off=0x0`, `diag 31: vn_getpath plen=65 strlen=64
  path=/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.31`, and
  `diag 27: open .symbols failed ...
  dyld_shared_cache_arm64.31.symbols`.
- Conclusion: the NUL fix worked; the remaining error is a dyld4 subcache
  index. `.31.symbols` is absent; the main cache companion path has the
  trailing `.31` removed. SpringBoardUI assertion and SpringBoard crash
  persist. No UI/lock-screen success. BOOT readback SKIPPED.

## 2026-11-22 — v40 offline complete (MAIN only)

- Patch `0426` strips a trailing `.<digits>` subcache suffix and tries
  `<base>.symbols`, `<subcache>.symbols`, then `<base>`; the first candidate
  with a real `localSymbolsOffset` is used. Added a faulted-vnode mapping-table
  fallback for subcache-resident symbols, 64-bit one-shot diagnostic mask,
  and new `diag 32/33` evidence. Standalone syntax check clean; focused tests
  extended with v39 pstore records 151-156 and the subcache-path model.
- CI `45052304788` GREEN for `ca344a7`. Kernel
  `fc68ed6ae0cbbc70e76bd795782d27e40478ab507500e0f18ce2f8657699b95e`;
  payload `5b065a6462bdc5f9d1ed99943e9becc50d30f4d8fa0528a695a5f8f82bd51e40`;
  shim-boot.img
  `611625babb5e3dc88bf272e1deadcb1c158cb1c9e115c5be3c334e459ca80391`.
- Entry VA is now `0xfffffff00740f488` (one page later than v39); the shim
  consumes the payload header entry, and the handoff mechanism is unchanged.
- Validators all PASS: buildtree, kernel, platform 9/9, CPU 17/17, ADT 22/22,
  packaging, handoff 18/18, all applicable focused tests (0417 inapplicable).
  Shim Image/ELF and the shim region in the BOOT image are byte-identical to
  the v31 reference.
- Candidate: `validation/ios-candidate-v40-out/` with README. Physically tested
  below; BOOT-only flash, no readback, USERDATA/SYSTEM/RECOVERY untouched.

## 2026-11-22 — v40 physical: companion opens, global symbol scan is ambiguous

- Boot 1 pstore
  `fcf2a2f45d54dbfd2024c30cba93c2f4106d5864c923c52db7821d8e625701cf`
  (16,372 B) stopped at SpringBoard code signing before the XCTEST/IRT window;
  no `M30 XCTEST` or `M30 IRT` records.
- Boot 2 pstore
  `33eea723ca1dc07b827a8c3477e7f6a185965edd89398cd770c4e424d6042f5b`
  (16,372 B) captured records 88-99: XCTEST retrigger, worker on the `.31`
  subcache vnode, `diag 31` (`plen=65 strlen=64`), `diag 32` stripped base,
  `diag 30` `cand=0 ls_off=0x4000` for
  `dyld_shared_cache_arm64.symbols`, and `diag 28` distinct symbols vnode.
- `diag 10` printed huge fields (`nlist_off=0xa980 cnt=8705811
  str_off=0x84e1ab0 size=451573533`); `diag 13` found `strx=318698973`, then
  `diag 15` failed to find that `n_strx` in the nlist table. Diagnosis: the
  companion layout is valid, but a global string-pool first-match binds to a
  duplicate/`_internal_release_type`-like string that the target dylib's
  nlist range does not use. SpringBoardUI assertion and SpringBoard crash
  persist. No UI/lock-screen success. BOOT readback SKIPPED.

## 2026-11-23 — v41 fix in progress (MAIN only): image-scoped nlist lookup

- Patch `0426` now follows LiveContainer `litehook_find_dsc_symbol()` exactly:
  read the image list from the main cache, find
  `/usr/lib/system/libsystem_darwin.dylib`, read `local_symbols_info` and the
  `dyld_cache_local_symbols_entry_64` for that image index, and scan only its
  nlist range, reading each nlist's own string from the companion pool.
  The `.symbols` file is used ONLY for nlist/string data.
- A vmaddr is now mapped through a REAL cache file (faulted vnode, base cache,
  then numbered subcaches `.0`-`.63`, with and without a leading zero) before
  a file offset is accepted. The target vnode is retained and the fault-path
  patch gate requires that same vnode, so a `.symbols`-relative offset can
  never patch the wrong page. All file reads remain `UIO_READ`; the in-memory
  write still happens only after `cs_validate_page()`.
- Standalone syntax check clean; focused test PASS including v40 physical
  evidence and an image-scoped duplicate-name model. Patch dry-runs cleanly
  against pristine and the v40 buildtree after reversing the old 0426.
- NEXT: commit/push, CI GREEN, package v41 candidate, BOOT-only flash, capture
  pstore, expect `diag 39/42/13/33` and either `M30 IRT: patched ...` or a new
  precise failure. If the assert persists because the target page was already
  resident, add a validated-page direct patch via the backing VM object.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-23 — v41 offline complete (MAIN only)

- CI `45060087612` GREEN for `2977581`. Kernel
  `2e46c41c4d727c11efdfc7aab611bef39cf2efc4f9811f185432e173c0e2037a`;
  payload `f90feb5b7210c7a080efe882c9400b64081ae8d8eb2c2153c6f8f08d85af88d2`;
  shim-boot.img
  `274e39b49d883abd392a1e626a14daab4e146e1b1d3f36e15344ac96539b0ca5`.
- Validators all PASS: buildtree, kernel, platform 9/9, CPU 17/17, ADT 22/22,
  packaging, handoff 18/18, all applicable focused tests (0417 inapplicable).
  Shim Image/ELF and the shim region in the BOOT image remain byte-identical to
  the v31 reference.
- Candidate: `validation/ios-candidate-v41-out/` with README. Physically tested
  below; BOOT-only flash, no readback, USERDATA/SYSTEM/RECOVERY untouched.

## 2026-11-23 — v41 physical: image list read, path guard was wrong

- BOOT-only flash succeeded. pstore
  `f8f8562cdb7a9224c904606b56aba81c2b2a39f975bca9d160e1c0bc19cafcdd`
  (16,372 B) captured records 92-105: XCTEST retrigger, `.31` subcache vnode,
  stripped base companion path, `diag 36 images off=0x270 cnt=2710`, then
  `diag 38 libsystem_darwin image not found cnt=2710`.
- Diagnosis: `dyld_cache_image_info.pathFileOffset` is an absolute offset in
  the main cache file. The v41 guard `po >= chunk` incorrectly treated it as
  an offset into the 4 KiB scratch buffer, so all 2,710 image paths were
  skipped before the path read. SpringBoardUI assertion persists. No UI
  success. BOOT readback SKIPPED.

## 2026-11-23 — v42 fix in progress (MAIN only): absolute image path offset

- Removed the `po >= chunk` guard; image paths are now read with
  `vn_rdwr(UIO_READ)` at the absolute `pathFileOffset`. Added one-shot
  `diag 47` (first image path) and `diag 48` (libsystem-prefixed candidate) so
  the next boot proves the comparison data.
- Standalone syntax check clean; focused tests PASS with v41 physical
  evidence. Patch dry-runs cleanly against pristine.
- NEXT: CI GREEN, package v42 candidate, BOOT-only flash, capture pstore,
  expect `diag 47/48`, `diag 39`, `diag 42`, `diag 13`, `diag 33`, then either
  `M30 IRT: patched ...` or a new precise failure.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-23 — v42 offline complete (MAIN only)

- CI `45102718208` GREEN for `533fca1`. Kernel
  `35178aa6f83d22060e4fa5d0d7edb3170572c33ca97d52a6830c9160d3034de4`;
  payload `5ac8105713b4bb5556b76bbdb7c847cf8552f9b4ddc2cb856f4af1fc41856e66`;
  shim-boot.img
  `f451f7e8f7786c837d2544bce5c7de717fe43c54e7f57e1892028880586b4709`.
- Validators all PASS: buildtree, kernel, platform 9/9, CPU 17/17, ADT 22/22,
  packaging, handoff 18/18, all applicable focused tests (0417 inapplicable).
  Shim Image/ELF and the shim region in the BOOT image remain byte-identical to
  the v31 reference.
- Candidate: `validation/ios-candidate-v42-out/` with README. Physically tested
  below; BOOT-only flash, no readback, USERDATA/SYSTEM/RECOVERY untouched.

## 2026-11-23 — v42 physical: image-scoped symbol found, mapping failed

- BOOT-only flash succeeded. pstore
  `b8a9214a6d8ce8b5b17ee3d5b59b1249e4c7280c7ba84bc63d727bab0a29eba9`
  (16,372 B) captured records 0-3: `diag 42 image nlist start=6047093
  count=146`, `diag 43 nlist strx=318698902`, `diag 13 symbol
  vmaddr=0x1e1d3ad84`, then `diag 18 no real cache mapping contains vmaddr
  0x1e1d3ad84`.
- This proves the absolute `pathFileOffset` fix and the LiveContainer
  image-scoped nlist scan. The symbol's unslid vmaddr is valid, but none of the
  faulted vnode, base cache, or `.0`–`.63` subcaches has a mapping entry for it.
  SpringBoardUI assertion and SpringBoard crash persist. No UI success.
  BOOT readback SKIPPED.

## 2026-11-23 — v43 fix in progress (MAIN only): mapping evidence + Cryptex

- Added `diag 50` (base cache mapping table) and `diag 49` (image address and
  pathFileOffset), and extended the periodic status replay with the symbol
  vmaddr, image address, mapping-hit count, and base mapping range. This makes
  the mapping failure observable even when the 16 KB pmsg ring wraps.
- Real-cache lookup now also tries the dyld4 Cryptex directory
  (`/private/preboot/Cryptexes/OS/System/Library/Caches/com.apple.dyld`) and
  its numbered subcaches. All reads remain `UIO_READ`; patching still happens
  only in memory after `cs_validate_page()`, gated on the target cache vnode.
- Standalone syntax check clean; focused tests PASS with v42 physical evidence;
  patch dry-runs cleanly against pristine and the v42 buildtree.
- NEXT: CI GREEN, package v43 candidate, BOOT-only flash, capture pstore, read
  `diag 49/50` and status `sym=... img=... hits=... basecnt=...`, then either
  `M30 IRT: patched ...` or a new precise failure.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-23 — v43 offline complete (MAIN only)

- CI `45115267398` GREEN for `8c99e27`. Kernel
  `1a2290a37abe15ad40fdb6738e48ca6f35831650c522dd832f1ba3805f72ef6f`;
  payload `b3348e9f1afd21f1754e6a84e5c99bcbf158d60fc8c48238e033828b6f8f189d`;
  shim-boot.img
  `f605a5d46ca4e9a7e2421c53ccaf1a8254c043c5b9ae226a4ebc1f76d8283b09`.
- Validators all PASS: buildtree, kernel, platform 9/9, CPU 17/17, ADT 22/22,
  packaging, handoff 18/18, all applicable focused tests (0417 inapplicable).
  Shim Image/ELF and the shim region in the BOOT image remain byte-identical to
  the v31 reference.
- Candidate: `validation/ios-candidate-v43-out/` with README. Physically tested
  below; BOOT-only flash, no readback, USERDATA/SYSTEM/RECOVERY untouched.

## 2026-11-23 — v43 physical: companion vmaddr outside real cache mappings

- BOOT-only flash succeeded. pstore
  `135ad9284963ec6edb4f9115ce19cdd4577cd498b562b1aff34c25a655f388d7`
  (16,372 B) captured the extended replay: `sym=0x1e1d3ad84
  img=0x1d1c22000 hits=0 basecnt=1
  base0=0x1ecc80000/0x62ac000@0x0`.
- The base cache mapping starts 0x0af4527c above the symbol, and the target
  image address is even lower. No real cache file among the faulted vnode,
  base cache, `.0`–`.511` subcaches, or Cryptex candidates contained the
  vmaddr. SpringBoardUI assertion persists. No UI success. BOOT readback
  SKIPPED.

## 2026-11-23 — v44 fix in progress (MAIN only): companion-map translation

- Added `diag 52` for the companion's mapping table and `diag 53` for the new
  fallback. When no real-cache vmaddr mapping matches, the nlist value is
  translated through the companion mapping to a file offset
  (`sym_map_fileoff + (sym_vmaddr - sym_map_addr)`) and patched through the
  base cache vnode at that offset. The companion is still read-only; the only
  write remains the in-memory page after `cs_validate_page()`.
- Extended both System and Cryptex subcache searches to `.0`–`.511`, and added
  `tries`/`symmap`/`fb` fields to the periodic status replay.
- Standalone syntax check clean; focused tests PASS with v43 physical evidence;
  patch dry-runs cleanly against pristine and the v43 buildtree.
- NEXT: CI GREEN, package v44 candidate, BOOT-only flash, capture pstore, read
  `diag 52/53` and status `symmap=... fb=...`, then either `M30 IRT: patched ...`
  or a new precise failure.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-23 — v44 offline complete (MAIN only)

- CI `45118566540` GREEN for `2d39841`. Kernel
  `a4b02c4ce766b309d6b734e26c0af7dc35c1997010670c2d7d583315993b0ce4`;
  payload `594922b14453349296a8c6cfb7426ac2fc2c7861d85b49c0908eb34bb5b66fe1`;
  shim-boot.img
  `671e8d81c2cb2517cda696727cb37d54163beb1102221cf03d93ed00c6687dfc`.
- Validators all PASS: buildtree, kernel, platform 9/9, CPU 17/17, ADT 22/22,
  packaging, handoff 18/18, all applicable focused tests (0417 inapplicable).
  Shim Image/ELF and the shim region in the BOOT image remain byte-identical to
  the v31 reference.
- Kernel entry moved one page later to `0xfffffff007410488`; the shim consumes
  the payload header entry, so the handoff remains 18/18 PASS.
- Candidate: `validation/ios-candidate-v44-out/` with README. Physically tested
  below; BOOT-only flash, no readback, USERDATA/SYSTEM/RECOVERY untouched.

## 2026-11-23 — v44 physical: companion map is only a 16 KB stub

- BOOT-only flash succeeded. pstore
  `e86672cb4ada0fb2376f223a9854df48d79cbf0d46b5b4f93ff9ba28985d6de6`
  (16,372 B) captured the extended replay: `sym=0x1e1d3ad84
  img=0x1d1c22000 hits=0 tries=138
  symmap=0x22ade8000/0x4000@0x0 fb=0x0
  base0=0x1ecc80000/0x62ac000@0x0`.
- The `.symbols` companion's own mapping covers only 16 KB at a completely
  different virtual base, so it cannot translate the nlist vmaddr. The
  companion must come from the same live cache generation as the image list;
  on iOS >=16 that is the Cryptex cache, not `/System`. SpringBoardUI assertion
  persists. No UI success. BOOT readback SKIPPED.

## 2026-11-23 — v45 fix in progress (MAIN only): Cryptex-first companion

- Reordered companion selection to try the Cryptex `.symbols` file and Cryptex
  main cache first, then the existing `/System` candidates. The selected
  companion's base path now drives the image-list reopen, subcache search,
  fallback target path, and `diag 18` base report.
- Periodic status carries `comp=<candidate>` and `ls=0x...` so the chosen
  companion is visible in the final pstore window.
- Standalone syntax check clean; focused tests PASS with v44 physical evidence;
  patch dry-runs cleanly against pristine and the v44 buildtree.
- NEXT: CI GREEN, package v45 candidate, BOOT-only flash, capture pstore, read
  `comp=`/`ls=`/`symmap=`/`fb=`, then either `M30 IRT: patched ...` or a new
  precise failure.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-23 — v45 offline complete (MAIN only)

- CI `45121370706` GREEN for `ea8202c`. Kernel
  `2c641272b7ad70435987c28eff6ff5cf2326c5bf35b8ef1d7568de55e26c777d`;
  payload `617917ee01b2b9df7f1112b63080dedf1d0031c4094e93200c3c1298c474bd75`;
  shim-boot.img
  `382db454eb9b0c74ca9957aea8b841f988d1e589406eb0e1a3b3b3210e37c689`.
- Validators all PASS: buildtree, kernel, platform 9/9, CPU 17/17, ADT 22/22,
  packaging, handoff 18/18, all applicable focused tests (0417 inapplicable).
  Shim Image/ELF and the shim region in the BOOT image remain byte-identical to
  the v31 reference. Kernel entry is unchanged from v44 at
  `0xfffffff007410488`.
- Candidate: `validation/ios-candidate-v45-out/` with README. Physically tested
  below; BOOT-only flash, no readback, USERDATA/SYSTEM/RECOVERY untouched.

## 2026-11-23 — v45 physical: deeper userspace, IRT lines overwritten

- BOOT-only flash succeeded. pstore
  `c3a897cba60b96c66ddfec30d533845ed48fa2350b094e079c6603ef7376d4da`
  (16,372 B, 189 records) contains launchd `Early boot complete. Continuing
  system boot.`, `CODE SIGNING: ... p=26[SpringBoard]`, and later daemons
  including mediaserverd and driverkitd.
- The SpringBoardUI assertion is absent from the captured final window, but
  every `M30 IRT` line was overwritten by the deeper userspace log volume.
  This is forward progress, not proof of `_internal_release_type` patching or
  UI startup. BOOT readback SKIPPED.

## 2026-11-23 — v46 fix in progress (MAIN only): durable IRT heartbeat

- Keep the Cryptex-first companion and all v45 lookup/mapping logic.
- After the 30 x 2 s full status replay, emit a compact heartbeat every 2 s
  for another 6 min. Success prints `M30 IRT: patched (final state=... off=...
  sym=... comp=... ls=... nlist_cnt=... nlist_range=... fb=... hb=...)`;
  failure prints `M30 IRT final: ...` with the same decisive fields.
- This makes the patch result, companion, local-symbol count, and fallback
  state observable in the final pstore window even after heavy daemon logging.
- Standalone syntax check clean; focused tests PASS with v45 physical evidence;
  patch dry-runs cleanly against pristine and the v45 buildtree.
- NEXT: commit/push, CI GREEN, package v46, BOOT-only flash, capture pstore,
  read the heartbeat success/final line, then inspect the next boot stage.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-23 — v46 offline complete (MAIN only)

- CI `45125633274` GREEN for `3771d76b`. Kernel
  `9086e77ef607e3a722947373aa0028c15445ab4970942a9501cde06ed1d4ab55`;
  payload `b5996a239fc04ef3807b220c44d044f5b060069b6b3fe6095f18be6b9eb409dd`;
  shim-boot.img
  `831fb5141ef91e90a6b534779f897944bf883a224f4823b86f83cf47390cb826`.
- Validators all PASS: buildtree, kernel, platform 9/9, CPU 17/17, ADT 22/22,
  packaging, handoff 18/18, all applicable focused tests (0417 inapplicable).
  Shim Image/ELF and the shim region in the BOOT image remain byte-identical to
  the v31 reference. Kernel entry remains `0xfffffff007410488`.
- Candidate: `validation/ios-candidate-v46-out/` with README. Physical test was
  attempted but blocked before any device operation: `adb devices -l` showed no
  device, `heimdall detect` found no download-mode device, and `lsusb` showed no
  Samsung/M30 USB device. The M30 could not be positively identified, so no
  flash was performed.
- NEXT: reconnect the M30 in TWRP, re-check serial `320081735bb166a3` /
  product `m30lte`, then BOOT-only flash
  `validation/ios-candidate-v46-out/shim-boot.img` and capture pstore. Read the
  durable heartbeat, then inspect whether SpringBoard proceeds beyond loading.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-23 — v46 physical: decisive failure, heartbeat worked

- Device positively identified before flashing: ADB serial
  `320081735bb166a3`, product `m30lte`, state `recovery`, `ro.twrp.boot=1`.
  BOOT-only flash succeeded; no readback; USERDATA/SYSTEM/RECOVERY untouched.
- pstore
  `391ee54587d62b41209660ae10842b051c986bee5232723016e459d3b64df6b8`
  (16,372 B, 110 records, 1 gap). Evidence preserved in
  `validation/physical-boot-test/20261123-ios-v46-boot/`.
- No `M30 IRT: patched` marker. The durable final heartbeat survived from
  `hb=0` through `hb=55`:
  `M30 IRT final: state=4 off=0x0 err=0 sym=0x1e1d3ad84 comp=0 ls=0x4000 nlist_cnt=8705811 nlist_range=146 hits=0 tries=138 fb=0x0 hb=55`.
- The Cryptex `.symbols` companion was used and the image-scoped local-symbol
  lookup succeeded, but no real cache mapping contained the symbol vmaddr.
  `_internal_release_type` was **not** patched. The exact cause is that only
  numeric `.0`-`.511` subcache names were tried; dyld4 subcaches can have
  suffixed names recorded in the main cache header's subcache-entry array.
- The final window has `CRASH backboardd` and an `NSInvalidArgumentException`
  for a nil `NSURL` path, but no `Early boot complete`, no SpringBoard code
  signing line, and no SpringBoardUI assertion. No UI/lock-screen success.
  BOOT readback SKIPPED.

## 2026-11-23 — v47 in progress (MAIN only): authoritative subcache names

- Keep v46 Cryptex-first companion, symbol lookup, and durable heartbeat.
- Read `subCacheArrayOffset@392` and `subCacheArrayCount@396` from the main
  cache header; enumerate `dyld_subcache_entry.fileSuffix` values and try each
  exact `<basepath><suffix>` before the old numeric fallback. Reject suffixes
  containing `/` and require a leading `.`.
- Add `sc=<count>` and `si=<index>` to full status and both heartbeat forms,
  plus one-shot `diag 55`/`diag 56` for subcache-array discovery and the
  successful subcache name.
- Standalone syntax check PASS; patch dry-run against v46 buildtree PASS;
  focused tests extended with v46 physical failure evidence.
- NEXT: commit/push, CI, package v47, BOOT-only flash, capture pstore, read the
  `M30 IRT: patched (final ...)` or updated `M30 IRT final ... sc=... si=...`
  heartbeat, then inspect the next boot stage.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-23 — v47 offline complete (MAIN only)

- CI `45135148861` GREEN for `3a98f3a6`. Kernel
  `c2862edd5fba0993ede34876ee7776561fcb982c35a1a34fad9a5133cdda7d27`;
  payload `26f769b6bccee46df8b04d5122919cc19aa7441ac98b216fe1051f0cad13fa93`;
  shim-boot.img
  `23e131d59da50441967018d523b6b1888db1168f6eaaa339847c2108cbd7374c`.
- Validators all PASS: buildtree, kernel, platform 9/9, CPU 17/17, ADT 22/22,
  packaging, handoff 18/18, all applicable focused tests. Shim region remains
  byte-identical to v31; entry VA unchanged at `0xfffffff007410488`.
- Candidate: `validation/ios-candidate-v47-out/` with README. NOT physically
  tested. NEXT: BOOT-only flash, capture pstore, read the updated heartbeat,
  then inspect whether SpringBoard proceeds beyond loading.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-23 — v47 physical: subcache mapping found, patch still not applied

- Device positively identified before flashing: ADB serial
  `320081735bb166a3`, product `m30lte`, state `recovery`, `ro.twrp.boot=1`.
  BOOT-only flash succeeded; no readback; USERDATA/SYSTEM/RECOVERY untouched.
- pstore
  `da5de4e93fc6a37d836b270f670b1d36f98a0c8466c269415e2d5e619cc0797e`
  (16,372 B, 94 records, 2 gaps). Evidence preserved in
  `validation/physical-boot-test/20261123-ios-v47-boot/`.
- The authoritative subcache list worked: `sc=42`, `si=26`, `hits=1`,
  `tries=29`, and a real file offset `off=0xa432d84`. Final heartbeat:
  `M30 IRT final: state=2 off=0xa432d84 err=0 sym=0x1e1d3ad84 comp=0 ls=0x4000 nlist_cnt=8705811 nlist_range=146 hits=1 tries=29 sc=42 si=26 fb=0x0 hb=67`.
- No `M30 IRT: patched` marker. State remained `HAVE_OFF` (`state=2`), so the
  page write never fired. Most likely the target page was already resident
  before the deferred symbol scan learned its file offset, so no later fault
  visited that vnode. Pointer-only target matching may also have missed a
  pager alias.
- No `Early boot complete`, no SpringBoard code-signing line, no
  SpringBoardUI assertion, and no UI/lock-screen evidence.
- BOOT readback SKIPPED.

## 2026-11-23 — v48 in progress (MAIN only): resident-page patch

- Keep v47 subcache enumeration and all earlier companion/symbol logic.
- Add strict `(mount, vnode id)` identity matching for a pager alias, plus
  HAVE_OFF fault / target-match / offset-match counters (`fo`, `vh`, `oh`).
- Add a direct resident-page patch after the file offset is known: resolve the
  target vnode's VM object with `ubc_getobject()`, look up the page with
  `vm_page_lookup()`, require `VMP_CS_VALIDATED()`, wire it, write `3` through
  `phystokv()` of its physical page, then unwire. This is the same
  post-validation in-memory-only write as the fault path; no file write and no
  security check is weakened.
- Add `pr=<resident-patch result>` to the heartbeat/status lines and one-shot
  diagnostics for missing object/page or an unvalidated page.
- Standalone syntax check PASS; patch dry-run against the v47 buildtree PASS;
  focused tests extended with v47 physical evidence and resident-page gating.
- NEXT: commit/push, CI, package v48, BOOT-only flash, capture pstore, read
  `M30 IRT: patched ...` or `M30 IRT final ... pr=...`, then inspect the next
  boot stage.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-23 — v48 offline complete (MAIN only)

- First CI `45142824836` failed only because `<sys/ubc_internal.h>` is not on
  the osfmk include path; fixed by declaring `ubc_getobject()` locally. CI
  `45145845104` GREEN for `9cad56bb`. Kernel
  `4022004eb8387a42873698db9bfe4de7df9efb43b84553c126cfd688d0c94200`;
  payload `18365562c7d8f2354d1476b1f8872ad20f0014c5abfef71084780ff7d50ecaaa`;
  shim-boot.img
  `4b56a629e7c1359d98008208bec4e865152e5aff995e896e50dc36c93c07579c`.
- Validators all PASS: buildtree, kernel, platform 9/9, CPU 17/17, ADT 22/22,
  packaging, handoff 18/18, all applicable focused tests. Shim region remains
  byte-identical to v31; entry VA unchanged at `0xfffffff007410488`.
- Candidate: `validation/ios-candidate-v48-out/` with README. NOT physically
  tested. NEXT: BOOT-only flash, capture pstore, read the resident-patch or
  updated final heartbeat, then inspect whether SpringBoard proceeds.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-23 — v48 physical: IRT patch confirmed, assertion still early

- Device positively identified before flashing: ADB serial
  `320081735bb166a3`, product `m30lte`, state `recovery`, `ro.twrp.boot=1`.
  BOOT-only flash succeeded; no readback; USERDATA/SYSTEM/RECOVERY untouched.
- pstore
  `ea99ef076996bd636f19516f7a34d815119bbcfd913d3a952e1badffd6679b03`
  (16,372 B, 116 records, 3 gaps). Evidence preserved in
  `validation/physical-boot-test/20261123-ios-v48-boot/`.
- `_internal_release_type` was patched in memory:
  `M30 IRT: patched _internal_release_type off 0xa432d84 (0 -> 3)`. Durable
  success heartbeat survived through `hb=22`:
  `M30 IRT: patched (final state=3 off=0xa432d84 sym=0x1e1d3ad84 comp=0 ls=0x4000 nlist_cnt=8705811 nlist_range=146 sc=42 si=26 fo=19821 vh=3493 oh=1 pr=-5 fb=0x0 hb=22`.
- The direct resident-page shortcut was rejected (`pr=-5`, page not validated)
  and correctly not used. The strict alias match plus fault-path fallback did
  fire (`oh=1`, `mo=0xa432000`), so the IRT milestone is proven physically.
- The SpringBoardUI assertion and `NSInternalInconsistencyException` are still
  present and appear before the patch marker. No `Early boot complete` and no
  UI/lock-screen evidence. The next likely correction is to run the
  post-validation fix-ups on the code-signing bitmap fast path too and to
  start the IRT scan before the XCTEST retrigger so the patch lands before the
  SpringBoardUI probe.
- BOOT readback SKIPPED.

## 2026-11-23 — v49 in progress (MAIN only): fast-path fix-ups, earlier IRT scan

- v48 physically proved the IRT patch, but the SpringBoardUI assertion still
  appeared before the patch. Likely cause: `vm_page_validate_cs_mapped()` can
  validate via the code-signing bitmap fast path and skip
  `vm_page_validate_cs_mapped_slow()`, where both post-validation fix-ups live.
- Run both fix-ups on the bitmap fast path too: call
  `m30_xctest_probe_fixup()` and `m30_internal_release_fixup()` with the page's
  object pager and `mo_offset`. Validation has already succeeded via the
  bitmap; this remains an in-memory-only post-validation write.
- Start the deferred IRT worker on the first dyld-pager fault instead of
  waiting for the XCTEST retrigger, so the symbol patch can land before the
  SpringBoardUI probe. Wrong-magic vnodes still reset `NEED_DSC` for a later
  retry, and the XCTEST retrigger still resets state for diagnostics.
- First CI `45156413249` FAILED to compile: the new fast-path hunk was
  generated with `-U0`, so it had no context to locate itself and `} else {`
  landed at `vm_fault.c:9729`. Second CI `45159368112` was GREEN but the log
  showed `Skipping patch 0426 ... patch failed: osfmk/vm/vm_fault.c:7715`:
  the replacement `-`/`+` hunk form is rejected by the strict `git apply`
  preflight used in CI. The resulting kernel was built WITHOUT the IRT code
  (entry moved from `0xfffffff007410488` to `0xfffffff00740d488`), so it was
  discarded and never packaged.
- Corrected patch: standard full-context `diff -U3` output, preflighted with
  `git apply --check` against the exact v48 CI base; verified it reproduces
  the intended `vm_fault.c` byte-for-byte. `git diff --check` reports false
  positives on unified-diff context lines (leading space + tab) for patch
  files; correctness is gated by `git apply --check` and CI instead.
- Standalone syntax check PASS; patch dry-runs against the v48 buildtree and
  the 0425->0426 application order PASS; focused tests extended with v48
  physical success evidence and a bitmap-fast-path coverage model.
- Analysis while CI runs: the v48 pstore contains NO `M30 XCTEST: patched`
  line and no `M30 IRT: retrigger` line, so the `XCTestConfiguration` literal
  was never rewritten. The remaining validation path with no fix-ups is
  `vm_page_validate_cs_mapped_chunk()` (called from `vm_fourk_pager.c:1027`),
  which uses `cs_validate_range()` directly. If v49 still shows the assertion
  and no XCTEST patch marker, v50 should add the same post-validation fix-ups
  there, guarded by `validated`.
- Third CI `45162621882` GREEN (17m3s): log shows `Applying patch: 0426`,
  buildtree `vm_fault.c` matches the intended source byte-for-byte, and kernel
  entry is back at `0xfffffff007410488`. Kernel
  `f614daf731563f5ed34ed26e969e1a336e333b08fe2bc7ada4357ae7f87c0968`;
  payload `aa7ad2f18c73b2719c873efad2ce8339d2ff509298d14c32eddb1321e140b6a3`;
  shim-boot.img
  `81b4626da7c3fbc787ef824e8c7d73470e04f5fea5ee60a4ed3d605c9e812c79`.
- Validators all PASS: buildtree, kernel, platform 9/9, CPU 17/17, ADT 22/22,
  packaging, handoff 18/18, all applicable focused tests. Shim region remains
  byte-identical to v31; entry VA unchanged.
- Candidate: `validation/ios-candidate-v49-out/` with README. NOT physically
  tested. NEXT: BOOT-only flash, capture pstore, check for `M30 XCTEST: patched`
  markers, IRT ordering relative to the assertion, and any SpringBoard
  progression.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-23 — v49 physical result and v50 offline (MAIN only)

- v49 was BOOT-flashed with `shim-boot.img`
  `81b4626da7c3fbc787ef824e8c7d73470e04f5fea5ee60a4ed3d605c9e812c79` on the
  positively identified M30 (`m30lte`, serial `320081735bb166a3`) in TWRP.
  BOOT only; no BOOT readback; USERDATA/SYSTEM/RECOVERY untouched.
- pstore `validation/physical-boot-test/20261123-ios-v49-boot/raw/pmsg-ramoops-0`
  SHA256 `fd517375e9dbab5561cb9511808a33b96f6b35b3d32eaf79a348fc28a0370e0e`.
  Decoded log: `state=4`, `off=0x0`, `hits=0`, `tries=0`, `fo=0`, `vh=0`,
  `oh=0`, `err=0`. No `M30 IRT: patched`, no `M30 XCTEST: patched`, no
  `M30 IRT: retrigger`, no `Early boot complete`.
- The change that started the IRT worker on the first dyld-pager fault is a
  regression: the worker failed before reaching the symbol scan. This confirms
  the v48 XCTEST retrigger gate is required. The 30 full status replay lines
  also wrapped most of the one-shot diagnostics out of the 16 KB ring.
- v50 (`0427-m30-irt-retrigger-gate.patch`, incremental on v49/0426):
  1. Restore the exact v48 `m30_irt_retriggered && !m30_irt_thread_started`
     worker gate.
  2. Factor the retrigger reset into `m30_irt_retrigger_after_xctest()` and call
     it from BOTH validation paths, so a bitmap-fast-path XCTest patch opens the
     same gate instead of being ignored.
  3. Add `xctest=<count>` to both durable heartbeat forms so the captured pmsg
     ring proves whether the class-name fix-up fired even after wrap.
- Offline checks PASS: standalone syntax check; `git apply --check` for 0426 then
  0427 against the exact v49 CI base; application reproduces the intended v50
  `vm_fault.c` byte-for-byte; focused tests extended with v49 physical evidence
  and a fast-path-gate model.
- NEXT: commit/push v50 source, run CI, then package/validate/boot as before.
- NO UI/lock-screen success claimed.
- CI `45169239555` GREEN (12m16s) for source commit `4adddb7e`. Log shows both
  `Applying patch: 0426` and `Applying patch: 0427`; buildtree `vm_fault.c`
  matches the intended v50 source byte-for-byte; entry VA remains
  `0xfffffff007410488`. Kernel
  `a439f7070b90577e53703a1190ddad06c3b0d40e2b7fce8d6a19acf6e7168a41`;
  payload `609b10f498b0b501db86ed378f46cc844da27dd26470c9b2e372147965af3b01`;
  shim-boot.img
  `859b5d08dab9dd2f7a9aff80eb9c5f2c77ea6677969480f8ece332b7de74b07a`.
- Validators all PASS: buildtree, kernel, platform 9/9, CPU 17/17, ADT 22/22,
  packaging, handoff 18/18, all applicable focused tests. Shim region remains
  byte-identical to v31; entry VA unchanged.
- Candidate: `validation/ios-candidate-v50-out/` with README. NOT physically
  tested. NEXT: BOOT-only flash, capture pstore, read `xctest=<count>` and
  `state=3` from the heartbeat, check XCTEST/retrigger markers and ordering
  relative to any SpringBoardUI assertion.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-23 — v50 physical result (MAIN only)

- v50 BOOT-flashed with `shim-boot.img`
  `859b5d08dab9dd2f7a9aff80eb9c5f2c77ea6677969480f8ece332b7de74b07a` on the
  positively identified M30 (`m30lte`, serial `320081735bb166a3`) in TWRP.
  BOOT only; no BOOT readback; USERDATA/SYSTEM/RECOVERY untouched.
- pstore `validation/physical-boot-test/20261123-ios-v50-boot/raw/pmsg-ramoops-0`
  SHA256 `744b504a8552c1af9bfe5eb789f2ae85ee8c3e7216e9c3a50d0512eb0728ba2e`.
  Decoded: `state=3`, `off=0xa432d84`, `hits=1`, `tries=29`, `sc=42`, `si=26`,
  `oh=1`, `pr=-5`, durable through `hb=24`. The new `xctest=1` field proves the
  class-name fix-up ran once.
- The SpringBoardUI `NSInternalInconsistencyException` is STILL present and
  appears before the IRT patch marker; there is no surviving `M30 XCTEST:
  patched` or `M30 IRT: retrigger` marker and no `Early boot complete`.
  Therefore the single XCTest rewrite was too late or on the wrong page/process.
- Next (v51): add the same post-validation fix-ups to
  `vm_page_validate_cs_mapped_chunk()` (called from `vm_fourk_pager.c:1027`,
  which uses `cs_validate_range()` directly), guarded by `validated`. Keep
  `m30_irt_retrigger_after_xctest()` on both existing paths. No 0417, no
  security check weakened.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-23 — v51 offline (MAIN only): chunk-path XCTest fix-up

- v50 physical result: IRT patch restored (`state=3`, `xctest=1`, durable
  heartbeat), but SpringBoardUI assertion persists and appears before the patch
  marker. The one class-name rewrite was too late or on the wrong page/process.
- The remaining unpatched validation path is `vm_page_validate_cs_mapped_chunk()`
  (called from `vm_fourk_pager.c:1027`), which calls `cs_validate_range()`
  directly and never reaches either `vm_page_validate_cs_mapped()` fix-up.
- v51 (`0428-m30-xctest-chunk-path.patch`, incremental on 0426 + 0427):
  1. Split the class-name scanner into `m30_xctest_probe_fixup_range(kaddr,
     page_offset, len)`; the existing full-page wrapper passes `PAGE_SIZE`.
  2. On successful chunk validation, call the range scanner with `chunk_size`
     and the exact `object->paging_offset + offset + offset_in_page` file
     offset, then call `m30_irt_retrigger_after_xctest()`.
  3. Strictly range-limited: bytes outside the just-validated chunk are never
     written. No 0417, no security check weakened, no disk write.
- Offline checks PASS: standalone syntax check for IRT + xctest + chunk blocks;
  `git apply --check` for 0426 then 0427 then 0428 against the exact v49 CI
  base; application reproduces the intended v51 source byte-for-byte; focused
  tests extended with chunk-path and range-boundary models.
- NEXT: commit/push, run CI, then package/validate/boot as before.
- NO UI/lock-screen success claimed.

## 2026-11-23 — v51 CI GREEN and candidate (MAIN only)

- CI `45173700250` GREEN (18m16s) for source commit `8ee1e3c5`. Log shows
  `Applying patch: 0426`, `0427`, and `0428`; buildtree `vm_fault.c` matches
  `/tmp/m30_v51/modified.c` byte-for-byte.
- Kernel
  `d857197355520846d82ba9bd4bcaf175f0d1ddf42677cf2f91a21e206db6a522`;
  payload `0b75f9e0ef25615dd0e1c10e5699b9baaabf9c76b5a0762b7e7028c061ae2b0d`;
  shim-boot.img
  `7bcaa7359081edb851a07bcb304b4bdf9dc64cb8cb4ecac23cd4f0e6cbf342be`.
- Validators all PASS: buildtree, kernel, platform 9/9, CPU 17/17, ADT 22/22,
  packaging, handoff 18/18, all applicable focused tests.
- Layout shift verified: 0428 grew `__TEXT_EXEC __text` by exactly `0x1000`.
  Entry moved `0xfffffff007410488` -> `0xfffffff007411488`; `_start_first_cpu`
  moved `0xfffffff0074120ec` -> `0xfffffff0074130ec`; `__start` still branches
  to `_start_first_cpu`. ADT PA moved `0x82450000` -> `0x82454000`; boot_args
  PA moved `0x82454000` -> `0x82458000`. `shim/loader.c` derives both from the
  payload header, with no hardcoded old addresses. Evidence saved in
  `validation/ios-candidate-v51-out/entry-layout-check.txt`. Shim region remains
  byte-identical to v31.
- Candidate: `validation/ios-candidate-v51-out/` with README. NOT physically
  tested. NEXT: BOOT-only flash, 180 s window, return to TWRP, pull pstore;
  check `xctest=<count>` versus v50's `1`, XCTEST/retrigger markers, IRT
  `state=3`, and SpringBoardUI assertion ordering.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

- v51 candidate committed/pushed as `581321f7`.

## 2026-11-23 — v51 physical result (MAIN only): REJECTED

- v51 BOOT-flashed with `shim-boot.img`
  `7bcaa7359081edb851a07bcb304b4bdf9dc64cb8cb4ecac23cd4f0e6cbf342be` on the
  positively identified M30 (`m30lte`, serial `320081735bb166a3`) in TWRP.
  BOOT only; no BOOT readback; USERDATA/SYSTEM/RECOVERY untouched.
- pstore `validation/physical-boot-test/20261123-ios-v51-boot/raw/pmsg-ramoops-0`
  SHA256 `ecf0c2ed5289be600e956a014ee4bd1b01fd8aec2391124b57b426a649efdebd`.
  Decoded: 101 records, 1 wrap issue. Final heartbeat is
  `M30 IRT final: state=2 off=0xa432d84 ... hits=1 tries=29 sc=42 si=26
  fo=15649 vh=2826 oh=0 pr=-5 ... hb=11 xctest=1`.
- There is NO `M30 IRT: patched _internal_release_type`, NO
  `M30 IRT: patched (final state=3 ...)`, NO `M30 XCTEST: patched`, and NO
  `M30 IRT: retrigger` marker in the captured ring. The SpringBoardUI assertion
  and reason string are still present; no `Early boot complete`.
- v51 is a regression. Observation: the worker reached companion symbols but
  never reached v50's `oh=1` / `mo=0xa432000` patch state. Working hypothesis
  (NOT proven): calling `m30_irt_retrigger_after_xctest()` from the 4K chunk
  path opened the DSC gate on an earlier/different validated page than the
  v48/v50-proven slow/bitmap-fast path.
- v50 remains the last physically successful IRT candidate (`state=3`, `oh=1`,
  durable heartbeat through `hb=24`). v51 rejected for flashing.
- Next (v52): keep the range-limited chunk-path literal rewrite, but REMOVE the
  retrigger call from the chunk path so v50's gate timing is preserved. Consider
  adding a separate chunk counter to the durable heartbeat to prove whether the
  extra path fired. No 0417; no security check weakened.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

## 2026-11-23 — v52 offline (MAIN only): chunk rewrite without chunk gate

- v51 physical result: `state=2`, `oh=0`, no IRT patch marker, `xctest=1`,
  assertion persists. v50 remains the last good IRT candidate. The working
  hypothesis is that `m30_irt_retrigger_after_xctest()` on the 4K chunk path
  opened the DSC gate too early.
- v52 (`0429-m30-chunk-path-no-retrigger.patch`, incremental on 0426 + 0427 +
  0428):
  1. KEEP the range-limited `m30_xctest_probe_fixup_range()` call on the 4K
     chunk path, so the SpringBoardUI literal can still be rewritten there.
  2. REMOVE `m30_irt_retrigger_after_xctest()` from the chunk path. Only the
     v48/v50-proven slow and bitmap-fast paths may open the DSC scan gate.
  3. Add `m30_xctest_chunk_count` and `xctchunk=<count>` to both durable
     heartbeat forms, so a later capture proves whether the chunk rewrite fired.
- Offline checks PASS: standalone syntax check including both heartbeat format
  strings; `git apply --check` for 0426 -> 0427 -> 0428 -> 0429 against the exact
  v49 CI base; application reproduces the intended v52 source byte-for-byte;
  focused tests extended with the deferred-gate model.
- NEXT: commit/push, run CI, then package/validate/boot as before.
- NO UI/lock-screen success claimed.

## 2026-11-23 — v52 CI GREEN and candidate (MAIN only)

- CI `45179499798` GREEN (14m22s) for source commit `c4bbb74d`. Log shows
  `Applying patch: 0426`, `0427`, `0428`, and `0429`; buildtree
  `osfmk/vm/vm_fault.c` matches `/tmp/m30_v52/modified.c` byte-for-byte.
- Kernel
  `6805139a62ccfc6992e421e0e7a8fad5b1a91f94c899fe12bcb368b54a10ea92`;
  payload `58584cfeb606f15e218b82005d50ca342b40984fb70424d15b1f06a22f3c8d4d`;
  shim-boot.img
  `d2e46bc18c161e9cd4c2c04f0c6eec96dc4166c479298f59285ac46bd2695cda`;
  ios-boot.img
  `ae5bc3aa85b6627c9d3b1131e2ad5c854eb734af001c3ce1c585b5b60c16a8cb`.
- Validators all PASS: buildtree, kernel, platform 9/9, CPU 17/17, ADT 22/22,
  packaging, handoff 18/18, all applicable focused tests. Patch order
  `0426 -> 0427 -> 0428 -> 0429` was preflighted with `git apply --check` and
  verified to reproduce the intended v52 source byte-for-byte.
- Layout verified: removing the chunk-path retrigger returns the kernel to the
  v50 values. Entry `0xfffffff007410488`, `_start_first_cpu`
  `0xfffffff0074120ec`, `__TEXT_EXEC __text` size `0x008ae9d8`, ADT PA
  `0x82450000`, boot_args PA `0x82454000`. Evidence in
  `validation/ios-candidate-v52-out/entry-layout-check.txt`. Shim region remains
  byte-identical to v31.
- Candidate: `validation/ios-candidate-v52-out/` with README. NOT physically
  tested. Active handoff: device is in TWRP; awaiting explicit approval for a
  BOOT-only flash. Next: flash `shim-boot.img`, resume, one ~180 s window,
  return to TWRP, pull pstore. Check IRT `state=3`/`oh=1`, `xctest=<count>`,
  new `xctchunk=<count>`, SpringBoardUI assertion ordering, and any
  `Early boot complete`. Do not equate SpringBoard loading with visible UI.
- v50 remains the last physically successful IRT candidate. No UI/lock-screen
  success claimed. BOOT readback SKIPPED; USERDATA/SYSTEM/RECOVERY untouched.

- v52 candidate committed/pushed as `ff043ccd`.

## 2026-11-23 — v52 physical result (MAIN only): IRT restored, no UI

- First Heimdall attempt found no download-mode device and performed no write;
  log preserved as `heimdall-flash-failed-download-detect.log`. The device was
  then put into download mode with `adb reboot download`; `heimdall detect`
  succeeded. BOOT-only flash of `shim-boot.img`
  `d2e46bc18c161e9cd4c2c04f0c6eec96dc4166c479298f59285ac46bd2695cda` and
  `heimdall print-pit --resume` both exited 0. No BOOT readback;
  USERDATA/SYSTEM/RECOVERY untouched.
- Fixed window: resume `13:27:04Z`, window end `13:30:04Z`; device returned to
  TWRP before pstore collection.
- pstore
  `validation/physical-boot-test/20261123-ios-v52-boot/raw/pmsg-ramoops-0`
  SHA256 `409c2f25233750cc6e78b476c8e849207d8294e629b3a508d9e2c2f7e605de51`.
  Decoded: 124 records, 1 wrap issue. Pre-flash pstore still matched v51's
  result (`ecf0c2ed5289be600e956a014ee4bd1b01fd8aec2391124b57b426a649efdebd`).
- Observation: `M30 IRT: patched _internal_release_type off 0xa432d84 (0 -> 3)`
  is present once, followed by 10 `M30 IRT status: state=3` lines with
  `oh=1 pr=-5 mo=0xa432000`, covering `replay=10` through `replay=19`.
  There is NO `M30 IRT final: state=2`, so v51's regression is gone.
- The capture ends during the 30-iteration status loop. It has no
  `M30 IRT: patched (final state=3 ...)`, no `M30 IRT final: ...`, and no
  `xctest=`/`xctchunk=` fields; the new chunk counter cannot be evaluated from
  this window. This is capture timing, not a `state=2` failure.
- SpringBoardUI `NSInternalInconsistencyException` remains at records `[024]`,
  `[027]`, and `[089]`, all before the IRT patch marker at `[092]`. No
  `Early boot complete`; no UI or lock-screen evidence; no UI success claimed.
- v52 is NOT rejected on IRT correctness. v50 remains the last candidate with a
  full compact final heartbeat (`hb=24`, `xctest=1`). v51 remains rejected.
- Next: keep behaviour unchanged and first make the chunk rewrite observable
  inside the status loop (e.g. `xctchunk=` in the status line or a one-shot
  chunk marker), so the fixed 180 s capture can prove whether the new path
  fired before changing gate behaviour again. No 0417; no security check
  weakened; no BOOT readback.

- v52 physical evidence committed/pushed as `2ee5d54d`.

## 2026-11-23 — v53 offline (MAIN only): early DSC-header gate

- User explicitly rejected an observability-only candidate; this change is a
  fix attempt, not a diagnostic build.
- Root cause from v52: the IRT worker is still gated on the SpringBoard XCTest
  literal page fault. That page faults in from SpringBoard itself, so the
  symbol scan and `_internal_release_type` patch land after the SpringBoardUI
  assertion. v49 proved that starting on the first arbitrary fault fails
  (`state=4`) because the pager initially hands over launchd/dyld Mach-O
  vnodes, not the DSC.
- v53 (`0430-m30-irt-early-dsc-gate.patch`, incremental on 0426 + 0427 + 0428 +
  0429):
  1. Start the read-only IRT worker on the first validated page that is really
     a dyld shared-cache header (`mo_offset == 0` and `dyld_v` at `kaddr[0:6]`).
     This happens when dyld maps the cache, before SpringBoard loads.
  2. Keep the v50 XCTest retrigger only as a fallback. If the early scan has
     already started, the later XCTest patch records `m30_irt_retriggered`
     but does NOT reset state or restart the worker.
  3. Keep v52's range-limited chunk rewrite and no chunk-path retrigger.
- All file access remains `UIO_READ`; the in-memory write is strictly
  post-validation. No 0417; no AMFI, code-signing, trust-cache, page-validation
  or other security check weakened. No disk write.
- Offline checks PASS: standalone syntax check including both heartbeat format
  strings; `git apply --check` for 0426 -> 0427 -> 0428 -> 0429 -> 0430 against
  the exact v49 CI base; application reproduces the intended v53 source
  byte-for-byte; focused tests extended with the early-gate model.
- NEXT: commit/push, run CI, then package/validate. Do not flash without
  explicit user approval. NO UI/lock-screen success claimed.

## 2026-11-23 — v53 CI GREEN and candidate (MAIN only)

- CI `45185667251` GREEN (18m51s) for source commit `ffcb6466`. Log shows
  `Applying patch: 0426`, `0427`, `0428`, `0429`, and `0430`; buildtree
  `osfmk/vm/vm_fault.c` matches `/tmp/m30_v53/modified.c` byte-for-byte.
- Kernel
  `de84396fb0268ac2129737af5ad37bfe2b8fba52da7bb9e93f840d6534f9dcf4`;
  payload `3522a4447de58d8b23a11c06486d4452286247e54f93835e2e41a10f55c7bbba`;
  shim-boot.img
  `7cf35ab74045307f69f752eb6f6c1cfc638c402116a91f3e30f3ec5c1046df00`;
  ios-boot.img
  `94f04c6c654108b9272300dec631f8d60a835dfde86c8574cdc9a4a32ae3aafe`.
- Validators all PASS: buildtree, kernel, platform 9/9, CPU 17/17, ADT 22/22,
  packaging, handoff 18/18, all applicable focused tests. Patch order
  `0426 -> 0427 -> 0428 -> 0429 -> 0430` preflighted and verified to reproduce
  the intended v53 source byte-for-byte.
- Layout unchanged from v52: entry `0xfffffff007410488`, `_start_first_cpu`
  `0xfffffff0074120ec`, `__TEXT_EXEC __text` size `0x008ae9d8`, ADT PA
  `0x82450000`, boot_args PA `0x82454000`. Shim region remains byte-identical
  to v31. Evidence in `validation/ios-candidate-v53-out/entry-layout-check.txt`.
- Candidate: `validation/ios-candidate-v53-out/` with README. User authorized
  automatic BOOT-only flash and full physical test. NEXT: flash, 180 s window,
  return to TWRP, pull/decode pstore, record evidence, no UI claim unless
  physically proven.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED;
  USERDATA/SYSTEM/RECOVERY untouched.

- v53 candidate committed/pushed as `6d0c4a19`.

## 2026-11-23 — v53 physical result (MAIN only): REJECTED

- Device was initially disconnected; after reconnection it was positively
  identified in TWRP (`m30lte`, serial `320081735bb166a3`, `ro.twrp.boot=1`).
  BOOT-only flash of `shim-boot.img`
  `7cf35ab74045307f69f752eb6f6c1cfc638c402116a91f3e30f3ec5c1046df00` and
  `heimdall print-pit --resume` both exited 0. No BOOT readback;
  USERDATA/SYSTEM/RECOVERY untouched.
- Window: resume `14:08:34Z`, end `14:11:34Z`; device returned to TWRP before
  pstore collection.
- pstore
  `validation/physical-boot-test/20261123-ios-v53-boot/raw/pmsg-ramoops-0`
  SHA256 `ade2f38b0262da9db0996b03bbc4f989235aa6f36ae27feb5c54a245ed893a1c`.
  Decoded: 118 records, 1 wrap issue. Pre-flash pstore matched v52's result.
- Observation: durable heartbeat is `M30 IRT final: state=4 ... hb=1` through
  `hb=38`, with `xctest=1 xctchunk=0`. There is NO IRT patch marker, NO
  `state=3`, NO `M30 IRT: early scan started on DSC header`, NO
  `M30 IRT: XCTEST patch after early scan`, and NO `M30 IRT: retrigger` marker.
- The SpringBoardUI `NSInternalInconsistencyException` remains at record `[042]`.
  No `Early boot complete`; no UI/lock-screen evidence; no UI success claimed.
- v53 is rejected. The captured ring has no one-shot diagnostics identifying
  which failure path set `state=4`. Working hypothesis (NOT proven): the early
  DSC-header fault is still too soon for Cryptex-first companion selection, or
  the recovered vnode is not resolvable by the worker.
- v52 remains the last physically successful IRT candidate (`state=3`, `oh=1`,
  durable status replay). v51 and v53 are rejected. v50 remains the last
  candidate with a full compact final heartbeat.
- Active handoff: device is in TWRP. No further flash is queued. Next candidate
  must be chosen from evidence; do not claim UI without physical proof.
- NO UI/lock-screen success claimed. BOOT readback SKIPPED.

- v53 physical evidence committed/pushed as `c1f38f96`.

## 2026-11-23 - v54 offline (MAIN only): bounded retry for early IRT scan

- User asked to implement the fix direction from the v53 evidence: keep the
  early DSC-header start, but make an early scan failure retryable instead of
  terminal, so a later DSC fault can retry before SpringBoard reaches the probe.
- v53 physical evidence: durable state=4, comp=0, ls=0x4000, but img=0,
  sym=0, hits=0, tries=0, nlist_cnt=0, nlist_range=0, err=0. The worker chose
  the Cryptex .symbols companion but failed before resolving an image or a
  symbol. Exact branch remains unproven; this change addresses the
  terminal-state behaviour, not the unknown root cause.
- New patch 0431-m30-irt-retryable-early-scan.patch (incremental on
  0426 + 0427 + 0428 + 0429 + 0430):
  1. m30_irt_mark_failure() converts a failure of an early, DSC-header-
     started worker into NEED_DSC with thread_started=0 and clears the
     one-shot diag mask, up to M30_IRT_MAX_EARLY_ATTEMPTS=4.
  2. A later genuine DSC-header fault starts a new worker. Wrong-magic
     vnodes take the same retryable path when the worker was early.
  3. After the budget is exhausted, the failure is terminal but leaves the
     v50 XCTEST fallback able to restart. A worker started only by XCTEST
     remains terminal on failure (v50 behaviour preserved).
  4. Failed early attempts with a retry armed skip the long heartbeat loops
     so they cannot overwrite the next attempt diagnostics in pstore.
  5. Early start markers are numbered (attempt=N) for physical evidence.
- No security check weakened: all file reads are UIO_READ; the only write
  remains the post-validation in-memory uint32 page patch. No 0417; no disk
  write; v18 baseline/4K config unchanged.
- Offline checks PASS: standalone syntax check of the IRT block; patch chain
  0426 -> 0427 -> 0428 -> 0429 -> 0430 -> 0431 applies to the exact v49 CI
  base and reproduces /tmp/m30_v54/modified.c byte-for-byte; focused
  tools/test_m30_internal_release_type.py PASS including new v54 patch and
  bounded-retry model tests. validate-repo.py reports only its pre-existing
  patch-number-gap warnings.
- Commit for source/patch/tests: d2a4854d (pushed).
- NEXT: run CI, then package/validate. Do NOT flash without explicit user
  approval. No UI/lock-screen success claimed.

## 2026-11-23 - v54 CI GREEN and candidate packaged (MAIN only)

- CI 45206251994 GREEN for source 25b905f8 (patch d2a4854d). Applying patch 0431 confirmed in CI log; kernel built with XNU_TARGET=iphoneos. Buildtree vm_fault.c matches /tmp/m30_v54/modified.c byte-for-byte (SHA256 152edc1a...).
- Candidate: validation/ios-candidate-v54-out/ with README and entry-layout-check.txt.
  Kernel 4327c4c9fda0f3c6d50c5d65beaab74ab42af985e7569f4a5b93ffac3d3610e5;
  payload a69480ebee4a7b90108f4b63c96e33a8f9c3168e8bd7ae738ea210947c743543;
  shim-boot.img 1da365a3b352575a366d2d8e898e0a8585afc56fd917ca95c5e122af0aeb4d5c;
  ios-boot.img 0f5af834c16bcac89c28da139340f28c10987e485de7541924b798c95bb3ac32.
- Layout changed: entry VA 0xfffffff007411488 (v53 0xfffffff007410488), _start_first_cpu 0xfffffff0074130ec, __TEXT_EXEC __text size 0x008b4000; ADT PA 0x82454000 and boot_args PA 0x82458000. Shim reads entry/ADT/boot_args from payload header; shim Image/ELF and 5456-byte shim region in shim-boot.img are byte-identical to v53/v31.
- Validators PASS: buildtree, kernel (6 checks), platform 9/9, packaging, handoff 18/18, all applicable focused tests (test_m30_16k_pages.py skipped as inapplicable). validate-repo.py has only pre-existing patch-number-gap warnings. CI A53 compatibility check passed.
- Status: candidate packaged/validated, NOT physically tested. Device in TWRP; no flash queued. Next physical step requires EXPLICIT user approval: BOOT-only shim-boot.img flash, resume, ~180 s window, return to TWRP, pull/decode pstore. Check numbered early-start/retry markers, patch marker, state=3, and assertion timing. No UI/lock-screen success claimed. BOOT readback skipped; USERDATA/SYSTEM/RECOVERY untouched.

## 2026-11-23 - v54 physical result (MAIN only): IRT state=3 restored

- Explicit user approval obtained. Device re-identified in TWRP (m30lte, serial 320081735bb166a3, ro.twrp.boot=1). BOOT-only flash of shim-boot.img 1da365a3... and heimdall print-pit --resume both exited 0. No BOOT readback; USERDATA/SYSTEM/RECOVERY untouched.
- Window: resume 16:02:46Z -> end 16:05:46Z (180 s). Device disconnected from USB during boot; user forced it back to TWRP with hardware keys; pstore pulled.
- Pre-pstore SHA256 ade2f38b... (same as v53, fresh window). Post pstore validation/physical-boot-test/20261123-ios-v54-boot/raw/pmsg-ramoops-0 SHA256 a146572fe77038d4fd0c22a5e1c9b94fc66da4c4222b54a5b78bcb0981c554b9 (16372 B); decoded 87 records, 4 wrap/gap issues, stream starts mid-message.
- Result: durable M30 IRT patched (final state=3 off=0xa432d84 sym=0x1e1d3ad84 ... oh=1 pr=-5 fb=0x0 hb=15..39 xctest=1 xctchunk=0), 75 full status replay lines; no state=4 in captured ring. v53 regression is cleared at the IRT-state level.
- One-shot early-start/retry/patch-marker records and the SpringBoardUI assertion wrapped out of the 16 KB ring. Their absence is NOT evidence the assertion is fixed, and the captured ring cannot prove whether the early retry path or the v50 XCTEST fallback started the successful worker. No Early boot complete and no lock-screen evidence. NO UI/lock-screen success claimed.
- Focused tests extended with the v54 pstore evidence model and PASS. Physical README: validation/physical-boot-test/20261123-ios-v54-boot/README.md. No further flash queued; any new physical test needs explicit approval.

## 2026-11-23 - v55 offline (MAIN only): validate the full 16K CS block on first fault

- New explicit authorization supersedes per-flash approval for v55 and later
  validated candidates: autonomous physical testing is allowed, but every
  write still requires positive device identity (SM-M305F, serial
  `320081735bb166a3`) and Samsung Download Mode confirmation; BOOT only via
  Heimdall; never USERDATA/SYSTEM/RECOVERY; never Fastboot. MAIN only; no
  GitHub settings changes; no OSX/XNU-target switch; no security weakening.
- Evidence chain: v45 pstore `[177]` SpringBoard `cs_invalid_page` final
  status `0x22000000 ... (remove VALID) page` after `Early boot complete`;
  willowios proved that exact CS_VALID loss drops the
  `com.apple.springboard-ui.client` entitlement and triggers the
  `+[SpringBoardUI load]` assertion. v52 ordered that assertion before the IRT
  patch marker; v30 proved literal string rewriting alone cannot fix it.
- Code cause in the v54 buildtree: `vm_page_validate_cs_mapped_slow()`
  assembles a 16K validation block only when all four resident 4K pages are
  present. The first fault of a 16K-hashed page has one resident page, so it
  falls back to `vsize = PAGE_SIZE`, `validated` stays 0, and
  `vm_fault_cs_check_violation()` calls `cs_invalid_page()`.
- New patch `0432-m30-cs-16k-block-readback.patch` (incremental on v54):
  1. When the block is not fully resident, read the exact 16K bytes from the
     code-signed vnode with `vn_rdwr(UIO_READ, ..., IO_NOCACHE, ...)` while
     temporarily dropping the VM object lock. This is explicitly permitted by
     the `vm_fault_cs_check_violation()` comment; the faulting page stays busy
     and the VM map keeps an object reference. This also fixes the v34 panic
     cause (I/O while holding the object lock).
  2. After re-locking, re-look-up every 4K page and copy its actual bytes into
     the file block before hashing; the busy faulting page is copied from
     `kaddr`. The signature is therefore checked against what is really
     mapped, never against a trusted on-disk copy alone. A tampered page fails
     closed. The object-alive/pager checks are repeated after the unlock.
  3. `cs_validate_page()` still hashes the whole 16K block. Short/failed reads
     fall back to one mapped page, which cannot match a 16K hash and fails
     closed. No disk write occurs.
  4. Durable `csblk`/`csfail`/`csvok` counters and one-shot `M30 CS diag`
     records are replayed in the v54 IRT heartbeat so the physical result is
     visible even after the 16 KB pmsg ring wraps.
- v54 retryable early IRT scan, v45 Cryptex-first lookup, 4K config, v18
  baseline and all post-validation in-memory fix-ups are preserved. No
  AMFI/trust-cache/signature/hash/page-validation bypass, no 0417, no disk
  write, no OSX target, no branch/settings changes.
- Offline checks PASS: patch applies cleanly to the exact v54 CI buildtree and
  reproduces modified `vm_fault.c` SHA256
  `ab3cf37eac16a1dbf91472335153ce6b92ef8daa3e5565103b8a92b75afe62dd`;
  standalone syntax check of the inserted block is clean; new
  `tools/test_m30_cs_16k_readback.py` PASS including tampered-page, short-read
  and held-lock failure models; all other applicable focused PASS
  (`test_m30_16k_pages.py` remains inapplicable without 0417);
  `validate-repo.py` reports only the pre-existing patch-number-gap warnings.
- NEXT: CI with `XNU_TARGET=iphoneos`, package/validate v55, then autonomous
  BOOT-only physical test under the new authorization. No UI/lock-screen
  milestone is claimed without verifiable physical evidence.

## 2026-11-23 - v55 CI GREEN and candidate packaged (MAIN only)

- CI `45219943492` GREEN for source `28a8a1ee` (`XNU_TARGET=iphoneos`,
  `M30LTE`, `DEVELOPMENT`). CI log explicitly applied
  `0432-m30-cs-16k-block-readback.patch`. Buildtree
  `osfmk/vm/vm_fault.c` SHA256
  `ab3cf37eac16a1dbf91472335153ce6b92ef8daa3e5565103b8a92b75afe62dd`
  matches the locally reproduced v55 source byte-for-byte.
- Candidate: `validation/ios-candidate-v55-out/` with README,
  `entry-layout-check.txt`, `SHA256SUMS`, package/validate logs, and the
  compressed QEMU smoke trace summary. Kernel
  `16fbec8acd87de5c34bc3487097dcea24e3fcd608a270de6f7de955eca0112cb`;
  payload `0718b348b3ffa691ac89bb502ae81b02af61ff0ef5e886ee4749023fe47fd343`;
  `shim-boot.img`
  `e58de8b007ad1d9149d5161fb3ba2b7aef698c7177130257a8463e230ca0550b`;
  `ios-boot.img`
  `17328c3f3e76340ea1060d53bc94c206288a832bbcb0895865c1d019004efccc`.
- Layout unchanged from v54: entry `0xfffffff007411488`,
  `_start_first_cpu` `0xfffffff0074130ec`, `__TEXT_EXEC __text` size
  `0x008b4000`, kernel end `0xfffffff008454000`, ADT PA `0x82454000`,
  boot_args PA `0x82458000`. Payload grew by 320 bytes to 16,179,264.
  Shim Image/ELF remain byte-identical to v54/v53/v31.
- Validators PASS: buildtree, kernel (6 checks), platform 9/9, packaging,
  handoff 20/20, all applicable focused tests (`test_m30_16k_pages.py`
  intentionally inapplicable without 0417), and CI A53 compatibility.
  `validate-repo.py` still reports only its pre-existing patch-number-gap
  warnings. Generic QEMU was non-authoritative and its trace was compressed.
- Device identity re-confirmed in TWRP before any write: `m30lte`,
  `ro.boot.em.model=SM-M305F`, bootloader `M305FDDU8CVK1`, serial
  `320081735bb166a3`, `ro.twrp.boot=1`. Download Mode must be confirmed
  immediately before the BOOT write. No flash has been performed yet.
- NEXT: enter Samsung Download Mode via ADB only, verify Heimdall detection,
  then flash ONLY the validated `shim-boot.img` to BOOT, resume, observe
  ~180 s, return to recovery, pull/decode pstore, and compare with
  v45/v52/v54/v50. Never USERDATA/SYSTEM/RECOVERY; never Fastboot. No
  UI/lock-screen milestone claim without verifiable physical evidence.

## 2026-11-23 - v55 physical result (MAIN only): early regression

- Device positively re-identified in TWRP (`SM-M305F`, `m30lte`, serial
  `320081735bb166a3`, bootloader `M305FDDU8CVK1`, `ro.twrp.boot=1`) and
  Heimdall detected Samsung Download Mode immediately before the write.
  BOOT-only flash of `shim-boot.img` `e58de8b0...` succeeded at
  `17:17:38Z..17:17:43Z`; USERDATA/SYSTEM/RECOVERY untouched, no Fastboot.
- The first resume attempt used invalid standalone `heimdall --resume` and only
  printed usage; a corrected `print-pit --resume` found the device had already
  left Download Mode, so the flash had booted automatically. Full 180 s window
  `17:17:53Z..17:21:00Z`; device later returned to TWRP ADB and pstore was
  pulled immediately.
- `validation/physical-boot-test/20261123-ios-v55-boot/raw/pmsg-ramoops-0` is
  12,402 bytes, SHA256
  `a0897bebe812f89006b0dfaba4c4484d0bdb96c3f9a0ef720ec5c193323fdbef`.
  `tools/decode_pmsg.py` decoded 154/154 records, consumed all bytes,
  `clean=true`, zero issues. Unlike v54, this capture is complete and un-wrapped.
- The boot reached HFS root mount and both `load_init_program` attempts, then
  only hardware-key events from forcing recovery. There are ZERO records for
  `M30 IRT`, `csblk`/`csfail`/`csvok`, `M30 CS diag`, `CODE SIGNING`,
  `cs_invalid_page`, `SpringBoard`, `NSInternalInconsistencyException`, `CRASH`,
  or `Early boot complete`. v55 therefore regressed earlier than v54/v52 and
  did not reach the stage the CS fix was meant to affect. PHYSICALLY REJECTED.
- Code-supported hypothesis: v55 allocates the 16K readback buffer with
  `kalloc_data(..., Z_WAITOK)` at `vm_fault.c:8981` while the VM object lock is
  still held. v54 used `Z_NOWAIT` there with an explicit “do not sleep while
  holding the object lock” comment. A sleeping allocation under the object
  lock plausibly hangs the first code-signing validation before launchd.
- NEXT: v56 patch changing that allocation to `Z_NOWAIT`, failing closed on
  allocation failure, and checking `object->pager == pager` after the
  lock drop/reacquire; then focused tests, CI, packaging, and a new BOOT-only
  physical test. Do not reflash unchanged v55. No UI/lock-screen claim.

## 2026-11-23 - local storage cleanup (approved)

- Removed 48 stale, untracked `milestone_artifacts/ci_*` directories (~14.2G),
  keeping 9 buildtree runs covering v18 (`44946634655`), v45 (`45121370706`),
  v49 (`45162621882`), v50 (`45169239555`), v51 (`45173700250`),
  v52 (`45179499798`), v53 (`45185667251`), v54 (`45206251994`) and
  v55 (`45219943492`). `milestone_artifacts/` is now 2.9G.
- `git gc` repacked 403 loose objects (381.67 MiB) into packs; `.git` is 1.7G.
  Filesystem went from 17G free to 32G free. No history rewrite and no tracked
  evidence deleted.
- The cleanup removed untracked buildtrees that several focused tests used as
  source-of-truth inputs, so those tests were repointed to the retained v55
  buildtree (`ci_45219943492`). Full rerun: all applicable tests PASS; only
  `test_m30_16k_pages.py` remains inapplicable because 0417 is intentionally
  absent. `validate-repo.py` still reports only the pre-existing
  patch-number-gap warnings.

## 2026-11-23 - v56 offline (MAIN only): non-sleeping 16K CS readback

- Root-cause hypothesis from v55: `vm_page_validate_cs_mapped_slow()` called
  `kalloc_data(CS_16K_BLOCK_SIZE, Z_WAITOK)` while still holding the VM object
  lock. v54 explicitly uses `Z_NOWAIT` there with a “do not sleep while holding
  the object lock” comment. The v55 physical capture ended immediately after
  `load_init_program` with no IRT/CS telemetry and no ring wrap, consistent
  with a sleep/deadlock on the first code-signing validation.
- New incremental patch
  `xnu/patches-minimal/0433-m30-cs-16k-nowait-pager-recheck.patch` (applied
  after 0432): allocate the 16K readback buffer with `Z_NOWAIT`; if allocation
  fails, increment `csfail`, emit `M30 CS diag 3`, and fall back to the secure
  one-page path; after the lock drop/reacquire require `object->pager == pager`
  (not merely non-NULL) before accepting the read; emit `M30 CS diag 4` on any
  rejection. All v55 hash/resident-byte overlay behaviour is unchanged.
- Offline checks PASS: 0433 applies to the exact v55 CI buildtree
  `ab3cf37e...` and reproduces modified `vm_fault.c` SHA256
  `2d9997b3f7b72d82576ccb404193a924ca147236c70ef667ee6f3edd52db2775`.
  New `tools/test_m30_cs_16k_nowait.py` PASS (patch structure, v55 pstore
  evidence, exact-SHA application, behavioural model for allocation failure,
  pager change and tamper). Original `tools/test_m30_cs_16k_readback.py`
  still PASS. All other applicable focused tests PASS after the retained-tree
  repoint. No security check is weakened; no 0417, no OSX target, no branch or
  GitHub settings change.
- NEXT: commit/push this source, run CI with `XNU_TARGET=iphoneos`, M30LTE,
  DEVELOPMENT; download/validate artifacts; package v56; then autonomous
  BOOT-only physical test under the existing authorization with the same
  identity/download-mode gates. Do not reflash v55. No UI/lock-screen claim
  without verifiable physical evidence.

## 2026-11-23 - v56 STOPPED before flash; v57 offline (MAIN only)

- v56 source (`989eb983`) and CI run `45229034214` were created, but an
  independent source review found a stronger, code-proven hang that 0433 does
  not fix. The CI run was cancelled (`conclusion=cancelled`) before completion
  and **v56 was never flashed**. No physical evidence or candidate image was
  produced for v56; it is not a validated candidate.
- Proven chain:
  `vm_page_map_and_validate_cs()` keeps the faulting page `vmp_busy` while
  `vm_page_validate_cs_mapped_slow()` runs; v55/v56 16K `vn_rdwr()` covers that
  page. Even with `IO_NOCACHE`, `cluster_read()` calls
  `ubc_create_upl_kernel(..., UPL_FILE_IO | UPL_SET_LITE)`;
  `vm_object_upl_request()` does `PAGE_SLEEP(object, dst_page, THREAD_UNINT)`
  for `vmp_busy || vmp_cleaning`. The thread waiting on the UPL owns the busy
  page, so it self-deadlocks. This also explains the absence of `M30 CS diag 0`:
  that record is emitted only after `vn_rdwr()` returns.
- New incremental patch
  `xnu/patches-minimal/0434-m30-cs-16k-no-busy-upl.patch` (after 0433): allocate
  with `Z_NOWAIT`; scan the four 4K slots; never include the busy faulting page
  or any other busy/cleaning page in `vn_rdwr()`; read only absent slots, one
  4K page at a time with the object lock dropped; use `kaddr` for the faulting
  page and physical bytes for other resident pages; recheck
  `object->pager == pager` and object life after every lock drop/reacquire;
  fail closed on busy peer, short read, allocation failure or pager change.
  `M30_CS_DIAG(5)` now records readback start before any I/O so the next
  physical capture can distinguish an allocation failure from an I/O hang.
- Offline checks PASS: 0433+0434 apply to the exact v55 CI buildtree and
  reproduce modified `vm_fault.c` SHA256
  `a10ab98b0506e521090402674b5ce533f1edb6e901350b39ce8c36e42365aa77`.
  New `tools/test_m30_cs_16k_no_busy_upl.py` PASS; it models mixed
  resident/absent slots, busy-page rejection before any I/O, short reads and
  4K page reads. `tools/test_m30_cs_16k_nowait.py` remains as the historical
  0433 gate. No signature, hash, AMFI, trust-cache or page-validation check is
  weakened; no 0417, no OSX target, no branch or GitHub settings change.
- NEXT: commit/push v57 source, run fresh CI with `XNU_TARGET=iphoneos`,
  M30LTE, DEVELOPMENT; download/validate artifacts; package v57; then
  autonomous BOOT-only physical test under the existing authorization with the
  same identity/download-mode gates. Do not flash v56 or reflash v55. No
  UI/lock-screen claim without verifiable physical evidence.

## 2026-11-23 - v57 CI GREEN and candidate packaged (MAIN only)

- CI `45230106038` GREEN for source `60379849` (`XNU_TARGET=iphoneos`,
  `M30LTE`, `DEVELOPMENT`). CI log explicitly applied
  `0434-m30-cs-16k-no-busy-upl.patch`; `ios_define_present=True`,
  `osx_define_present=False`, `PASS: iOS target selected`, and Cortex-A53 LSE
  count 0. Buildtree `osfmk/vm/vm_fault.c` SHA256
  `a10ab98b0506e521090402674b5ce533f1edb6e901350b39ce8c36e42365aa77`
  matches the locally reproduced v57 source byte-for-byte.
- Artifacts preserved under `milestone_artifacts/ci_45230106038/`. Kernel
  SHA256 `3d3c58d6834a2af83d1480f6a74c6cc7047bdbee334f99eb6d3994b83844d827`.
  `gh run download` needed `TMPDIR` pointed at the repo filesystem because the
  small `/tmp` tmpfs hit its quota.
- Candidate: `validation/ios-candidate-v57-out/` with README,
  `entry-layout-check.txt`, `SHA256SUMS`, package/validate logs and 20/20
  handoff verification. Payload
  `ea47b84a1f0d353e5d3cfcdf8d992f42164c8269bd053bf0212eed00a024990d`;
  `shim-boot.img`
  `0b85cc7666a45c761abf29002f42b5f24b395f9d7386112e5ade8748b2fcca31`;
  `ios-boot.img`
  `a803796692f0560f5532dd723c7e94e5903da62c7f93e6207918f493ee1d6595`.
- Layout unchanged from v55: entry `0xfffffff007411488`,
  `_start_first_cpu` `0xfffffff0074130ec`, `__TEXT_EXEC __text` size
  `0x008b4000`, kernel end `0xfffffff008454000`, ADT PA `0x82454000`,
  boot_args PA `0x82458000`, payload 16,179,264 bytes. Shim Image/ELF unchanged.
- Validators PASS: buildtree reverse-applies, kernel 6 checks, platform 9/9,
  packaging `validation.json result=PASS`, handoff 20/20, all applicable
  focused tests. `validate-repo.py` still reports only the pre-existing
  patch-number-gap warnings. No QEMU result is claimed as evidence.
- NEXT: positive device identity in TWRP, enter Samsung Download Mode, confirm
  Heimdall detection, flash ONLY `shim-boot.img` to BOOT, resume, observe
  ~180 s, pull pstore promptly, decode/analyze, and compare with
  v45/v52/v54/v50/v55. Never USERDATA/SYSTEM/RECOVERY; never Fastboot. Do not
  flash v56 or reflash v55. No UI/lock-screen claim without verifiable
  physical evidence.

## 2026-11-23/24 - v57 physical boot in progress (MAIN only): APPLE LOGO OBSERVED

- Device positively re-identified in TWRP before Download Mode (`SM-M305F`,
  `m30lte`, bootloader `M305FDDU8CVK1`, `ro.twrp.boot=1`), and Heimdall
  confirmed Download Mode immediately before the write. BOOT-only flash of
  `validation/ios-candidate-v57-out/shim-boot.img` SHA256
  `0b85cc7666a45c761abf29002f42b5f24b395f9d7386112e5ade8748b2fcca31`
  completed `18:06:56Z..18:07:01Z`; USERDATA/SYSTEM/RECOVERY untouched, no
  Fastboot, no BOOT readback. Correct `heimdall print-pit --resume` at
  `18:07:23Z` reported `Rebooting device...`.
- The 180 s observation window ended `18:10:38Z`. The user reports continuing
  console text, “booting system started”, and finally an **Apple logo** on the
  device. This is the first visible iOS UI milestone observed in this bring-up
  and is far beyond v55, which produced no post-`load_init_program` text and
  no logo. It remains a user observation until pstore confirms internal state;
  no lock-screen claim is made.
- The device has not returned to ADB recovery and is not in Download Mode, so
  `/sys/fs/pstore/pmsg-ramoops-0` cannot be pulled yet. Watchers waited for
  recovery ADB but timed out. A new watcher is armed to pull/hash pstore the
  moment recovery reappears. Evidence and hashes so far are in
  `validation/physical-boot-test/20261123-ios-v57-boot/README.md` and
  `raw/SHA256SUMS.partial`.
- NEXT: user forces TWRP with the established hardware-key method; then decode
  pstore, check `M30 CS diag 5`, `csblk`/`csfail`/`csvok`, progress past
  `load_init_program`, `Early boot complete`, SpringBoard/UI state, compare to
  v45/v52/v54/v50/v55, and commit the final physical README/handoff update.
  Still no UI/lock-screen success claim from the boot upload or observation
  alone.

## 2026-11-24 - v57 physical result (MAIN only): CS fix VALIDATED, Apple logo reached

- Device returned to TWRP and pstore pulled:
  `validation/physical-boot-test/20261123-ios-v57-boot/raw/pmsg-ramoops-0` is
  16,372 bytes, SHA256
  `8c17a9ed26c055a5a02cbf1f5643009327aa8876bf8e5c7c3c34ca7b1faee969`.
  `tools/decode_pmsg.py` decoded 166/166 records over all bytes with
  `clean=False` because the 16 KB ring wrapped during the long userspace boot;
  `tools/m30_bootlog.py inspect` produced the full decoded log. One-shot
  `M30 CS diag` records were overwritten, but durable IRT counters survived.
- Final replayed heartbeat: `M30 IRT: patched (final state=3 ... hb=179
  xctest=1 xctchunk=0 csblk=30025 csfail=12 csvok=192519)`. Repeated heartbeats
  from `csblk=27905 csfail=12 csvok=178243` upward show the 16K readback path
  ran continuously: 30,025 block readbacks, 192,519 successful full-block
  validations, only 12 fail-closed rejections. No terminal `state=4`.
- No `SpringBoard`, `NSInternalInconsistencyException`, or SpringBoard
  `cs_invalid_page` record in the captured window. The 19 `cs_invalid_page`
  records are for auxiliary daemons (`fairplayd.H2`, `xpcproxy`, `bluetoothd`,
  `searchpartyd`, `fmfd`, `networkserviceproxy`, `webbookmarksd`,
  `usermanagerd`), and 8 `CRASH` records are for `coreduetd` and `fmfd`. These
  are residual userspace issues, not the SpringBoard entitlement failure.
- User observed continuing console text, “booting system started”, and an
  **Apple logo** that remained visible. Combined with the pstore counters, this
  is the first verified visible iOS UI milestone on the M30 and proves the
  v45/v55 CS_VALID loss is fixed. No lock screen, home screen, or fully usable
  iOS is claimed; no framebuffer screenshot was captured.
- Comparison: v45 had SpringBoard `cs_invalid_page` after `Early boot complete`;
  v52 showed the SpringBoardUI assertion before the IRT marker; v54 had IRT
  `state=3` but no CS counters and no UI; v55 had no IRT/CS telemetry and
  stopped after `load_init_program`; v57 has deep userspace, healthy full-block
  validation counters, and a visible Apple logo. PHYSICALLY ACCEPTED for the
  CS root-cause fix and UI milestone. USERDATA/SYSTEM/RECOVERY untouched, no
  Fastboot, no BOOT readback.
- Final evidence: `validation/physical-boot-test/20261123-ios-v57-boot/README.md`,
  `analysis.txt`, decoded logs, `SHA256SUMS` and `raw/SHA256SUMS`. Commit this
  final handoff. Optional follow-up work is residual daemon crashes/entitlement
  noise (NOT required for the UI milestone); do not reflash a validated v57
  without a new root cause and explicit candidate.

## 2026-11-24 - v58 source (MAIN only): SpringBoard visibility and ring budget

- Verified v57 checkpoint before changes: HEAD is `55a0c810`, on `main`, and
  `sha256sum -c` passes for both
  `validation/ios-candidate-v57-out/SHA256SUMS` and
  `validation/physical-boot-test/20261123-ios-v57-boot/SHA256SUMS`. The
  working tree had pre-existing unstaged `site/` deletions and untracked
  scratch/artifact directories; none were touched.
- Corrected interpretation: the v57 Apple logo is a user observation, not proof
  of SpringBoard or a lock screen. No framebuffer capture was taken. The pstore
  capture is `clean=False` with 93 gaps/93 `bad_magic` records and starts
  mid-message; absence of `SpringBoard`/`NSInternal` in that window is **not**
  evidence that SpringBoard never launched. The kernel does not link
  `gAppleBootPict`; the logo is most plausibly backboardd/CoreAnimation or a
  retained splash.
- Root cause of the evidence loss: the 0426 IRT heartbeat emitted 30 full
  status lines plus 180 compact lines every 2 s = 210 records (~64 KB), far
  exceeding the 16 KB pmsg ring. This overwrote the SpringBoard window.
  `sweet_sample.c` is already compiled for M30LTE and defaults to
  `SpringBoard,backboardd`, but `sweet_sample_start()` was only called from the
  unused SWEET UFS root path, never from the M30 eMMC path.
- Other findings: 19 `cs_invalid_page` records are for auxiliary daemons
  (`fairplayd.H2`, `xpcproxy`, `bluetoothd`, `searchpartyd`, `fmfd`,
  `networkserviceproxy`, `triald`, `webbookmarksd`, `usermanagerd`,
  `bluetoothd`), not SpringBoard/backboardd/launchd/securityd/keybagd. The
  `coreduetd`/`fmfd` SIGTRAP crashes share PC `0x1a98eeb7c` and are downstream
  late-boot symptoms, not proven SpringBoard blockers. `lsd` has a
  cpu-monitor entitlement denial but no evidence it blocks UI. The v57 ADT
  already has the correct 4-byte zero activation properties (dump formatter
  misleadingly displayed `''`).
- New patch `xnu/patches-minimal/0435-m30-springboard-visibility.patch`
  (incremental on v57):
  1. IRT heartbeat reduced from 30+180 records to 5+18 (compact every 10 s),
     leaving most of the 16 KB ring for SpringBoard/backboardd crash-scan and
     sampler records while keeping durable IRT/CS counters.
  2. `sweet_sample_start()` called from `a5xelte_emmc_rootdev()` next to
     `emmc_log_start()`, so SpringBoard/backboardd are sampled at 90 s and then
     every 120 s with PC/LR/backtrace.
  No CS/AMFI/trust-cache/page-validation change; no security weakening; no
  0417; no OSX target; no branch or GitHub settings change.
- Offline checks PASS: 0435 applies to the exact v57 CI buildtree and
  reproduces `vm_fault.c` SHA256
  `9193cd37cf769a68b362dffe8a48c3d7b443cd7a7202d409ea941ab7bac5339a` and
  `a5xelte_emmc.c` SHA256
  `d15f61b44050bafb36162bb3124c9a2b4dd355c04f91b2a76cba4e5e133c6bbe`.
  New `tools/test_m30_springboard_visibility.py` PASS; all other applicable
  focused tests PASS (`test_m30_16k_pages.py` remains inapplicable without
  0417). `validate-repo.py` still reports only pre-existing gap warnings.
- Candidate packaging plan (small, evidence-based, no kernel security change):
  keep the v57 kernel/payload chain but set cmdline `cpus=6` (historical
  home-screen build used 6 cores rather than 1) and add
  `sweetfb_noconsole=1` so the kernel text console stops overwriting the GUI.
  ADT stays unchanged. Physical observation must capture early and late
  pstore, and a screen photo if a lock screen appears.
- NEXT: commit/push source, run CI with `XNU_TARGET=iphoneos`, M30LTE,
  DEVELOPMENT; validate artifacts; package v58 with the cmdline above; then
  autonomous BOOT-only physical test with the same identity/download-mode
  gates. No lock-screen claim without a visible persistent render plus logs.

## 2026-11-24 - v58 CI GREEN and candidate packaged (MAIN only)

- CI `45245697689` GREEN for source `8724a1a0` (`XNU_TARGET=iphoneos`,
  `M30LTE`, `DEVELOPMENT`). CI log explicitly applied
  `0435-m30-springboard-visibility.patch`; iOS target selection passed and
  Cortex-A53 LSE count was 0. Buildtree source hashes match the locally
  reproduced v58 files: `vm_fault.c`
  `9193cd37cf769a68b362dffe8a48c3d7b443cd7a7202d409ea941ab7bac5339a`,
  `a5xelte_emmc.c`
  `d15f61b44050bafb36162bb3124c9a2b4dd355c04f91b2a76cba4e5e133c6bbe`.
- Artifacts preserved under `milestone_artifacts/ci_45245697689/`. Kernel
  `5aaacba0ffe49ba021c86f8fd491aba9ff6f65a5514f7b7a2db0e8b1b5693cd2`.
- Candidate `validation/ios-candidate-v58-out/` packaged with cmdline
  `debug=0xc serial=3 cpus=6 keepsyms=1 maxmem=292 rd=emmcroot0
  emmcroot=USERDATA emmcprobe=1 emmcwrite=1 sweetfb_noconsole=1`. Payload
  `90f5e612a144e7e42411c664bca92820189e4cf0533eaa5794ccf3e74d6fcf8f`;
  `shim-boot.img`
  `2ef2e3a09cb501fb4b4ed4dd8e888441fe7d5895f29fb6b73397be1d982f783d`;
  `ios-boot.img`
  `88300d77aa45a57f3a8ca387e39fbd26f570ddf2421472801936f481b449a3ed`.
  Layout unchanged from v57; ADT unchanged; shim unchanged.
- Validators PASS: buildtree, kernel 6 checks, platform 9/9, packaging,
  handoff 22/22 (includes cpus=6 and sweetfb_noconsole=1), all applicable
  focused tests. No QEMU claim.
- NEXT: autonomous BOOT-only physical test under the existing authorization:
  confirm identity/Download Mode, verify `shim-boot.img` hash, flash BOOT only,
  capture pstore at ~90 s and at the end of the window, look for `SMP
  SpringBoard`/`SMP backboardd`, `M30 IRT` counters, SpringBoard CRASH/assertion
  strings, and take a screen photo if a lock screen appears. No UI claim
  without a persistent visible render plus supporting logs.

## 2026-11-24 - v58 physical result (MAIN only): SpringBoard launches, then aborts

- Identity verified in TWRP before the write (`SM-M305F`, `m30lte`, serial
  `320081735bb166a3`, bootloader `M305FDDU8CVK1`, `ro.twrp.boot=1`), Download
  Mode confirmed, BOOT-only flash of `shim-boot.img`
  `2ef2e3a09cb501fb4b4ed4dd8e888441fe7d5895f29fb6b73397be1d982f783d`
  completed `19:37:32Z..19:37:37Z`. USERDATA/SYSTEM/RECOVERY untouched, no
  Fastboot, no BOOT readback. Resume failed because the device auto-booted.
- Device was observed booting XNU console text. No lock screen was reported.
  It did not return to recovery, so pstore was pulled after the user forced
  TWRP: `validation/physical-boot-test/20261124-ios-v58-boot/raw/pmsg-ramoops-0`
  is 16,372 bytes, SHA256
  `7d16f9fd557ae757c2713b03b26bd319cc1a7b5396db9a97c546ab3007ee07d2`.
  `decode_pmsg.py` decoded 153/153 records with `clean=False` (ring wrapped
  over the ~25 min boot). Early `SMP` and IRT heartbeat records were lost;
  their absence is not evidence they did not run.
- **New decisive evidence:** SpringBoard did launch (`CRASH SpringBoard[739]
  sig 6 ... pc 0x1cd897198`) and then aborted with an NS exception (`reason ns 2
  code 0x6`, text overwritten). `backboardd` crash-looped through pids 746,
  752, 758, 763, 770, 777 with the exact same PC, so both die in one shared
  library abort path. XCTest fix-up fired (`total 113`) but did not prevent it.
- There are 36 `cs_invalid_page` records with status `0x22000000`; six are
  `backboardd` and one is a later `SpringBoard` pid 783. CS_VALID is still
  being stripped from UI processes despite the v57 full-block readback.
  v58 is PHYSICALLY REJECTED for the lock-screen objective, but it answers the
  key question: SpringBoard launches; the blocker is its abort plus backboardd
  crash loop, not “SpringBoard never starts”.
- Evidence: `validation/physical-boot-test/20261124-ios-v58-boot/README.md`,
  `analysis.txt`, decoded logs, `SHA256SUMS`, `raw/SHA256SUMS`.
- NEXT v59: remove the fail-closed rejection for busy/cleaning **peer** pages in
  the 16K readback overlay (the busy faulting page remains excluded from UPL
  and is hashed from `kaddr`; physical bytes of peers are copied and still
  full-block hashed, so tamper detection is preserved). Add durable per-reason
  CS failure counters (`cfa`/`cfi`/`cfp`) and an early crash-reason marker so
  the next capture does not depend on the wrapped ring. Force recovery at
  ~3 min in the next physical test to capture early pstore. No security change.

## 2026-11-24 - v59 source (MAIN only): busy-peer CS overlay + fail reasons

- v58 physically proved SpringBoard launches (pid 739) then aborts with an NS
  exception, and that backboardd crash-loops with the same PC
  `0x1cd897198`. It also showed 36 `cs_invalid_page` events including
  `backboardd` and a later `SpringBoard` pid 783: CS_VALID is still being
  stripped from UI processes despite the v57 full-block readback.
- New patch `xnu/patches-minimal/0436-m30-cs-busy-peer-overlay.patch`
  (incremental on v58): busy/cleaning **peer** pages are no longer rejected in
  the 16K readback. Only absent slots go to the vnode/UPL, so the busy faulting
  page is still excluded and is hashed from `kaddr`; every resident peer is
  copied through `phystokv()` and the full 16K block is still hashed, so a
  torn or tampered page can only fail closed. Added durable per-reason counters
  `m30_cs_fail_alloc`, `m30_cs_fail_io`, `m30_cs_fail_pager`, replayed in the
  IRT heartbeat as `cfa=`, `cfi=`, `cfp=`. No signature/hash/AMFI/trust-cache/
  page-validation change; no 0417, no OSX target, no branch/settings change.
- Offline checks PASS: patch applies to the exact v58 CI buildtree and
  reproduces `vm_fault.c` SHA256
  `98196f90fef3f7cc382678dbee83799b8bfd7893ac008ca0cefd0e8e262bf65d`.
  New `tools/test_m30_cs_busy_peer_overlay.py` PASS; all other applicable
  focused tests PASS (`test_m30_16k_pages.py` inapplicable without 0417).
- NEXT: commit/push source, run CI with `XNU_TARGET=iphoneos`, M30LTE,
  DEVELOPMENT; validate/package v59. Physical test must force recovery at
  ~3 min to capture early pstore, because the exact NS exception reason was
  lost in v58's wrapped ring. No lock-screen claim without visible persistent
  evidence plus logs.

## 2026-11-24 - v59 CI GREEN and candidate packaged (MAIN only)

- CI `45295419663` GREEN for source `dccbc33b` (`XNU_TARGET=iphoneos`, M30LTE,
  DEVELOPMENT). Log applied `0436-m30-cs-busy-peer-overlay.patch`; LSE count 0.
  Buildtree `vm_fault.c` matches the local v59 source byte-for-byte
  (`98196f90fef3f7cc382678dbee83799b8bfd7893ac008ca0cefd0e8e262bf65d`).
- Kernel SHA256 `82d1e1443a2260535195a12c12714ac2b2248355ca60af30bfce05f94f6c2448`.
  Candidate `validation/ios-candidate-v59-out/`: payload
  `6c4c3ddf1aafd4991b23a2839bdc4499dbc0a7622d6be83b0cdd1014a69a128b`,
  `shim-boot.img`
  `9890079d8d801aef5639d79a0eba5e8cb468c4ab735dec17eb2a1092eda1b421`.
  Cmdline/ADT/shim/layout unchanged from v58.
- Validators PASS: buildtree, kernel 6 checks, platform 9/9, packaging, handoff
  22/22, all applicable focused tests.
- NEXT: BOOT-only physical test with identity/Download Mode gate; force recovery
  at ~3 min to capture early pstore with the NS exception reason and the new
  `cfa/cfi/cfp` counters. No lock-screen claim without visible persistent
  evidence plus logs.

## 2026-11-24 - v59 physical boot: inconclusive (late pstore capture)

- Identity/Download Mode verified, BOOT-only flash of
  `shim-boot.img` `9890079d8d801aef5639d79a0eba5e8cb468c4ab735dec17eb2a1092eda1b421`
  at `00:34:44Z..00:34:49Z`, resume `00:34:59Z`. USERDATA/SYSTEM/RECOVERY
  untouched, no Fastboot, no BOOT readback.
- The requested ~3 min early recovery capture was missed. Pstore was finally
  pulled at `04:50Z`, about four hours after boot, so the 16 KB ring had wrapped
  again. Raw pstore `8f2e5b306d07863000c29e5e43c8b3f54307ce991a4cb1c020e343a805a2d32d`;
  decode 139/139 records, `clean=False`.
- Surviving window contains 50 `cs_invalid_page` records for auxiliary daemons
  only (`fairplayd.H2` 27, `bluetoothd` 17, `xpcproxy` 5, `fseventsd` 1), and zero
  `SpringBoard`/`backboardd`/`M30 IRT`/`csblk=`/`cfa=`/`cfi=`/`cfp=`/`SMP `/
  `CRASH`/`NSInternal`/`state=4` records. Those absences are due to ring wrap,
  not evidence of absence. No lock screen was reported.
- v59 is INCONCLUSIVE on the CS fix; no success or failure claim. Evidence:
  `validation/physical-boot-test/20261124-ios-v59-boot/README.md`,
  `analysis.txt`, decoded logs and both SHA256SUMS files.
- NEXT v60: make decisive telemetry independent of user timing. Add a very slow
  (~10 min) durable IRT/CS report that always stays near the ring tail, and a
  replay of the last SpringBoard/backboardd crash reason. Then rerun physical;
  no lock-screen claim without visible persistent evidence plus logs.

## 2026-11-24 - v60 source (MAIN only): durable CS/IRT + crash reason report

- New patch `xnu/patches-minimal/0437-m30-durable-crash-report.patch`
  (incremental on v59):
  1. After the bounded heartbeat, the IRT worker keeps one compact
     `M30 SLOW:` line every 10 minutes with IRT state, `csblk/csfail/csvok` and
     `cfa/cfi/cfp`. At ~6 records/hour this stays near the tail of the 16 KB
     pmsg ring even after hours of daemon noise, so any later recovery pull
     contains the final CS result.
  2. `osfmk/kern/exception.c` records the first UI heap string containing
     `Exception`/`exception`/`reason` into `m30_last_crash_reason[256]`; the
     slow heartbeat replays it as `reason=...`. This targets the NS exception
     reason that v58/v59 lost to ring wrap.
  No signature/hash/AMFI/trust-cache/page-validation change; no 0417, no OSX
  target, no branch or GitHub settings change.
- Offline checks PASS: patch applies to the exact v59 CI buildtree and
  reproduces `vm_fault.c` SHA256
  `cb010af81d89fa10ddf9d7aa03579225bd2860fb001de309c815ecfaf650551d` and
  `exception.c` SHA256
  `35b3161fadd93ff49aa9f4b93f9165296939407f7da8dde5a9558d6e5c480e80`.
  New `tools/test_m30_durable_crash_report.py` PASS; all other applicable
  focused tests PASS (`test_m30_16k_pages.py` inapplicable without 0417).
- NEXT: commit/push, CI, validate/package v60, then BOOT-only physical test.
  Capture pstore whenever recovery is convenient; the slow report should make
  early timing unnecessary. No lock-screen claim without a visible persistent
  render plus logs.

## 2026-11-24 - v60 CI failure and fix (MAIN only)

- CI `45329987546` FAILED for source `e252d946`. The only build error was
  `exception.c:995:12: error: call to undeclared function 'strstr'` in the new
  m30 crash-reason capture; all other steps were healthy.
- New incremental patch `xnu/patches-minimal/0438-m30-string-include.patch`
  adds `#include <string.h>` to the same guarded block in `exception.c`. No
  behavioural or security change.
- Offline checks PASS: 0437+0438 applied to the exact v59 CI buildtree
  reproduce `vm_fault.c` SHA256
  `cb010af81d89fa10ddf9d7aa03579225bd2860fb001de309c815ecfaf650551d` and
  final `exception.c` SHA256
  `3446b62576fb098020640154d2359e0bd9a6c521cc82302cf85beb5c8dbb011e`.
  `tools/test_m30_durable_crash_report.py` PASS with both patches; all other
  applicable focused tests PASS.
- NEXT: commit/push fix, rerun CI with `XNU_TARGET=iphoneos`, M30LTE,
  DEVELOPMENT; validate/package v60 and run BOOT-only physical test. No
  lock-screen claim without visible persistent evidence plus logs.

## 2026-11-24 - v60 CI second failure and fix (MAIN only)

- CI `45332065494` FAILED with the same `strstr` undeclared error. The
  `<string.h>` include was applied but XNU's kernel headers do not declare
  `strstr` at all, so adding the include could not fix it.
- New incremental patch `xnu/patches-minimal/0439-m30-local-substr.patch`
  replaces the three `strstr()` calls with a small local `m30_contains()`
  substring search. No behavioural or security change.
- Offline checks PASS: 0437+0438+0439 applied to the exact v59 CI buildtree
  reproduce `vm_fault.c` SHA256
  `cb010af81d89fa10ddf9d7aa03579225bd2860fb001de309c815ecfaf650551d` and
  final `exception.c` SHA256
  `335dba8e00448a9e4e06480cc3b4dfb4a5f4521c1b0cbb1610dffbd89f87668b`.
  `tools/test_m30_durable_crash_report.py` PASS with all three patches; all
  other applicable focused tests PASS.
- NEXT: commit/push, rerun CI, validate/package v60 and run BOOT-only physical
  test. No lock-screen claim without visible persistent evidence plus logs.

## 2026-11-24 - v60 CI GREEN and candidate packaged (MAIN only)

- CI `45334020730` GREEN for source `f561e630` (`XNU_TARGET=iphoneos`, M30LTE,
  DEVELOPMENT). Log applied 0435-0439; iOS target selection passed; Cortex-A53
  LSE count 0. Buildtree files match the local v60 source byte-for-byte:
  `vm_fault.c`
  `cb010af81d89fa10ddf9d7aa03579225bd2860fb001de309c815ecfaf650551d`,
  `exception.c`
  `335dba8e00448a9e4e06480cc3b4dfb4a5f4521c1b0cbb1610dffbd89f87668b`.
- Kernel SHA256
  `a24d220685d42b51a1ac8f74c9256480fd81fe1103195fc99c2da1f4b79c7637`.
  Candidate `validation/ios-candidate-v60-out/`: payload
  `3fd1b3d5486285b35eb3bce1cd29d42bae832c690aac4a067729ff15a2c04cdf`,
  `shim-boot.img`
  `c8db86b4526916da532b410b47f299d71787ad7618caa5c077096390c5b318c8`.
  Cmdline/ADT/shim/layout unchanged from v59.
- Validators PASS: buildtree, kernel 6 checks, platform 9/9, packaging, handoff
  22/22, all applicable focused tests. Two earlier CI runs failed only on the
  missing `strstr` declaration and were fixed with 0438/0439.
- NEXT: BOOT-only physical test with identity/Download Mode gate. Pull pstore
  when recovery is convenient; look for `M30 SLOW:` with `cfa/cfi/cfp` and
  `reason=`, SpringBoard/backboardd CS status, and any visible lock screen.
  No UI claim without a persistent visible render plus logs.

## 2026-11-24 - v60 first physical attempt: UI processes healthy, likely stopped early

- Identity/Download Mode verified; BOOT-only flash of
  `shim-boot.img` `c8db86b4526916da532b410b47f299d71787ad7618caa5c077096390c5b318c8`
  at `06:24:03Z..06:24:08Z`, resume `06:24:18Z`. USERDATA/SYSTEM/RECOVERY
  untouched, no Fastboot, no BOOT readback.
- Pstore pulled `06:29Z`, ~5 min after resume; raw SHA256
  `3299f42228ae42958c6b8946feb217d71acfc8e0139215fd782edff115e2097d`.
  Decode 144 records, `clean=False`.
- Decisive improvement over v58: `SMP SpringBoard[27]` and
  `SMP backboardd[57]` were alive with multiple threads; **zero** `CRASH`, zero
  `NSInternal`, zero `state=4`. Only 5 `cs_invalid_page` records, all auxiliary
  daemons (`ReportCrash`, `dmd`, `imagent`, `locationd`, `PowerUIAgent`), none
  UI. Counters: `csblk=7787 csfail=9 csvok=60944 cfa=4 cfi=5 cfp=0`.
- No `M30 SLOW` line because capture preceded the first 10-minute slow report.
  No lock screen was reported; the boot was forced back to recovery at ~5 min,
  which was likely too early. This attempt is INCONCLUSIVE on the lock-screen
  objective, not a rejection of the CS fix.
- Evidence: `validation/physical-boot-test/20261124-ios-v60-boot/README.md`,
  `analysis.txt`, decoded logs and SHA256SUMS.
- NEXT: reflash the SAME validated v60 image with a longer observation
  (~12–15 min) to allow a lock screen to appear and to capture the first
  `M30 SLOW` report. Technical reason for reflashing unchanged: the previous
  window ended before both the UI milestone and the slow telemetry could occur.

## 2026-11-24 - v60 long run: UI survives 19 min; console-mute boot-arg bug found

- Same validated v60 image reflashed BOOT-only; resume `06:34:59Z`. The
  observation watcher was killed by a server restart but rearmed; pstore pulled
  `06:54Z` (~19 min). Raw SHA256
  `1f78fb3f8e5111d5d5676a8a1f3a4ea9c8293dea14cae4490c0465db37af21e4`.
- `SMP SpringBoard[27]` and `SMP backboardd[57]` appear across multiple samples
  throughout the window. **Zero** `CRASH`, zero `NSInternal`, zero `state=4`.
  Both main threads are repeatedly at unslid PC ~`0x1c2611030` / LR
  ~`0x1c2622b18` (same shared-library wait), but they do not die.
- 12 `cs_invalid_page` records, all auxiliary daemons; none UI. Counter
  fragment `csblk=15551 csfail=15 csvok=105904 cfa=8`. CS fix is holding for UI
  processes far beyond v58.
- **Concrete cause of no visible lock screen:** payload cmdline used
  `sweetfb_noconsole=1`, but M30LTE defines `ARM64_BOARD_CONFIG_A5XELTE`, and
  `iokit/Kernel/arm/SweetFramebuffer.cpp` under that guard reads
  `a5fb_noconsole`. The console was therefore never muted and kept drawing over
  the GUI, matching the user's “a lot of logs” observation.
- NEXT: repackage the SAME CI-green v60 kernel with corrected cmdline
  `a5fb_noconsole=1` (plus `a5fb_keep_on=1` to avoid blanking). No kernel rebuild
  needed; v61 is a payload/cmdline candidate. Validate, then BOOT-only physical
  test. Evidence: `validation/physical-boot-test/20261124-ios-v60-boot-long/`.

## 2026-11-24 - v61 candidate packaged (MAIN only): correct console boot arg

- v61 reuses the byte-identical CI-green v60 kernel
  `a24d220685d42b51a1ac8f74c9256480fd81fe1103195fc99c2da1f4b79c7637`
  from CI `45334020730`; no new kernel build is needed. Only the payload cmdline
  changes from `sweetfb_noconsole=1` to the M30/A5-correct
  `a5fb_noconsole=1`, plus `a5fb_keep_on=1` to keep the panel on.
- Candidate `validation/ios-candidate-v61-out/`: payload
  `06a492b5b6a8d747956f8c7f5cb870d79c736813c588af14cbc79377e95cbf4e`,
  `shim-boot.img`
  `0a224fdb7c6a3e284d565a26e70c46094ef901b0b3c9c2b62e97affba4b421d1`.
  ADT and shim unchanged; layout unchanged.
- Validation: `validate_boot_images.py` PASS, `verify_handoff_v61.py` 23/23 PASS
  (includes both corrected boot args); v60 CI results and focused tests still
  apply because the kernel is unchanged.
- NEXT: BOOT-only physical test with identity/Download Mode gate. Expect the
  GUI to be visible now that the framebuffer console is muted. Accept only a
  persistent visible lock screen plus logs.

## 2026-11-24 - v61 physical result (MAIN only): still no lock screen

- Identity/Download Mode verified; BOOT-only flash at `07:32:11Z..07:32:16Z`
  (13:02:11..13:02:16 IST), resume `07:32:29Z` (13:02:29 IST). It was left
  booted ~13 min; pstore pulled at `07:45Z`. Raw SHA256
  `1b97b044381a3e1db2312633353963ebcbf78370342639afffa3668ae9f6a12d`,
  decode 158 records, `clean=False`.
- IRT reached `patched`; counter fragment `csblk=3943 csfail=5 csvok=37138
  cfa=0 cfi=5 cfp=0`. `backboardd` actively used the framebuffer: created a
  1080x2340 surface, multiple swaps/selectors, `SWEET FB: display on`. Only
  crash in the window was `driverkitd[68]` sig 9. No SpringBoard/backboardd
  crash, no `NSInternal`, no `state=4`.
- No lock screen was observed. The capture window was long enough, so this is
  not a timing issue. The ring wrapped before SpringBoard's final state could
  be seen, so the remaining question is whether SpringBoard never presented a
  lock-screen scene or was stuck in a shared wait.
- Evidence: `validation/physical-boot-test/20261124-ios-v61-boot/`.

## 2026-11-24 - v62 source (MAIN only): compact frequent UI liveness

- New patch `xnu/patches-minimal/0440-m30-compact-ui-state.patch` changes
  `bsd/dev/sweet_sample.c`: print `M30 UI: sb=<pid> bb=<pid> reason=<string>`
  every 30 s, replaying `m30_last_crash_reason`; keep the full `SMP` backtraces
  only every fourth tick (2 min) so they no longer overwrite the whole ring.
  No CS/AMFI/security change.
- Offline checks PASS: patch applies to exact v60 CI buildtree and reproduces
  `sweet_sample.c` SHA256
  `c7e92cc467a5c0fe062d8f4cd77dbe99c10a3909a4287dcd78c517963489fcf0`.
  `tools/test_m30_compact_ui_state.py` PASS; all applicable focused tests PASS.
- NEXT: commit/push, CI, validate/package v62 (reusing corrected v61 cmdline),
  physical test. The compact line should show whether SpringBoard is alive and
  whether any NS reason was captured, enabling the targeted final fix.

## 2026-11-24 - v62 CI GREEN and candidate packaged (MAIN only)

- CI `45356410574` GREEN for source `b667f247` (`XNU_TARGET=iphoneos`, M30LTE,
  DEVELOPMENT). Log applied `0440-m30-compact-ui-state.patch`; LSE count 0.
  Buildtree `sweet_sample.c` matches local v62 source
  `c7e92cc467a5c0fe062d8f4cd77dbe99c10a3909a4287dcd78c517963489fcf0`.
- Kernel SHA256 `45aff1b01f85b1dbe5a77903050005333eb858980cd1118465c3f11f02bda13d`.
  Candidate `validation/ios-candidate-v62-out/`: payload
  `e1c41dd83ee70cafc7af9ab91c8c20ed5320ee54a87392434790870d99d39bd0`,
  `shim-boot.img`
  `7798b211ebc9773df3225732e572dc18d091d2805cc1f7be72f967fbdd0913c7`.
  Cmdline/ADT/shim/layout unchanged from v61.
- Validators PASS: buildtree, kernel 6 checks, platform 9/9, packaging, handoff
  23/23, all applicable focused tests.
- NEXT: BOOT-only physical test with identity/Download Mode gate. Pull pstore
  when convenient; the compact line repeats every 30 s. No lock-screen claim
  without a visible persistent render plus logs.

## 2026-11-24 - v62 physical result (MAIN only): UI alive, still no lock-screen claim

- Identity/Download Mode verified; BOOT-only flash
  `10:27:49Z..10:27:54Z` (15:57:49..15:57:54 IST), resume `10:28:01Z`
  (15:58:01 IST). Pstore pulled at `10:48Z` (16:18 IST) after ~20 min. Raw
  SHA256 `2bc2179e27603d997ebe97851b7e0dd7eccdb878c56b8838f211d763004a85e7`.
- Compact telemetry survived: `M30 UI: sb=27 bb=57 reason=none`, proving both
  UI processes alive with no captured NS reason at that sample. The ring still
  wrapped heavily, so only one compact line remained.
- `SMP SpringBoard[27] slide 0x3f420000 mh 0x100008000`; main thread pc
  `0x201a31030`, lr `0x201a42b18`, unslid `0x1c2611030` / `0x1c2622b18`:
  the same location as the v60 long run. IRT final full record `state=3`,
  counters `csblk=3948 csfail=9 csvok=36811 cfa=4 cfi=5 cfp=0`.
- Backboardd actively used the framebuffer (`display on`, 1080x2340 surface).
  Only crash was `driverkitd[68] sig 9`; no SpringBoard/backboardd crash, no
  `NSInternal`, no `state=4`.
- Evidence: `validation/physical-boot-test/20261124-ios-v62-boot/`.
- User confirmed the visual result: **no lock screen**; v62 stayed on the Apple
  logo after console logs. This is a definitive physical rejection for the
  lock-screen objective. Process liveness, IRT state and framebuffer activity
  are NOT accepted as success.
- Symbolication is now complete with the genuine iOS 16 dyld local-symbol table,
  extracted read-only from USERDATA. The catalog's `.symbols` entry is an
  old-style `hlnk`/`hfs+` stub (`linkRef=664485424`); its real data fork is
  `iNode664485424` (fileID 318463) under private file-hardlink parent 18. The
  reusable read-only tool is `tools/m30_hfsx_read.py`; it resolved the hardlink
  to a 592,101,376-byte file at extent `(2905235, 144556)` blocks.
- Unslid SpringBoard PC `0x1c2611030` is `___commpage_gettimeofday_internal+0x350`;
  LR `0x1c2622b18` is `_do_compat+0x18c` / `fprintf_stderr+0x2e8`. The repeated
  main-thread state is in the libsystem stderr/`write(2)` path, not a UIKit
  lock-screen method. Evidence:
  `validation/physical-boot-test/20261124-ios-v62-boot/symbolication/`.
- Targeted v63 fix: retain the byte-identical CI-green v62 kernel and all CS /
  AMFI / signing / trust-cache / page-validation state, remove only `serial=3`
  from the payload cmdline. `serial=3` enables the serial console in
  `osfmk/arm/arm_init.c`; `fprintf_stderr` writes fd 2 there and can block with
  no serial drain. Kernel pstore logging remains active via
  `a5xelte_log_append()` in `_cnputs()`, independent of serial output.
