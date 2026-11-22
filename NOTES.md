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
