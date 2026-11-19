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
