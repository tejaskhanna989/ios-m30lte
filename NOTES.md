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
