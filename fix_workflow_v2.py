#!/usr/bin/env python3
"""Rewrite the CI workflow with simple, reliable shell commands."""

content = '''name: XNU Kernel Build for M30LTE

on:
  workflow_dispatch:
    inputs:
      MACHINE_CONFIG:
        description: Machine config name
        default: M30LTE
  push:
    branches:
      - main
    paths:
      - xnu/patches/**
      - .github/workflows/xnu.yml

jobs:
  build:
    runs-on: macos-26
    timeout-minutes: 180
    permissions:
      contents: read
      actions: read
    env:
      MACOS_VERSION: '13.5'
      KERNEL_CONFIG: DEVELOPMENT
      MACHINE_CONFIG: M30LTE
      DRIVERKIT: '0'
      SDKROOT_PATH: /Applications/Xcode_26.0.1.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS26.0.sdk
      CFLAGS: -std=gnu11 -Wno-format -Wno-error=visibility -Wno-error=reserved-identifier -ferror-limit=1000 -isysroot /Applications/Xcode_26.0.1.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS26.0.sdk -I/Applications/Xcode_26.0.1.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS26.0.sdk/usr/include -I${SRCROOT}/osfmk -I${SRCROOT}/bsd -I${SRCROOT}/libkern -I${SRCROOT}/iokit -I${SRCROOT}/security
      CXXFLAGS: -std=gnu++11 -Wno-format -Wno-error=visibility -Wno-error=reserved-identifier -ferror-limit=1000 -isysroot /Applications/Xcode_26.0.1.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS26.0.sdk -I/Applications/Xcode_26.0.1.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS26.0.sdk/usr/include -I${SRCROOT}/osfmk -I${SRCROOT}/bsd -I${SRCROOT}/libkern -I${SRCROOT}/iokit -I${SRCROOT}/security
      MAKEFLAGS: -j1 -e
      SRCROOT: ${{ github.workspace }}/xnu-source
      CURRENT_KERNEL_CONFIG: DEVELOPMENT
      CURRENT_ARCH_CONFIG: ARM64
      CURRENT_MACHINE_CONFIG: M30LTE
      CURRENT_MACHINE_CONFIG_LC: m30lte
      SDKROOT: iphoneos
      DEVELOPER_DIR: /Applications/Xcode_26.0.1.app/Contents/Developer
      KDKROOT: /Library/Developer/KDKs
      OBJROOT: ${{ github.workspace }}/xnu-source/BUILD/obj
    steps:
    - uses: actions/checkout@v4
    - name: Check available Xcode versions
      run: 'echo "=== Checking pre-installed Xcode versions ==="

        ls -la /Applications/Xcode*.app 2>/dev/null || echo "No Xcode apps found"

        echo "=== Checking xcode-select =="

        xcode-select -p

        xcodebuild -version

        '
    - name: Deps
      run: "brew install jq gum bash cmake ninja\nXC=$(ls -d /Applications/Xcode_15.0.1.app 2>/dev/null || ls -d /Applications/Xcode_15.*.app 2>/dev/null | head -1)\\nif [ -z \"$XC\" ]; then\\n  echo \"Xcode 15 not pre-installed, attempting to install via xcodes with Apple ID from secrets...\"\\n  printf '#!/bin/sh\\nexit 0\\n' | sudo tee /usr/local/bin/xcodes >/dev/null\\n  sudo chmod +x /usr/local/bin/xcodes\\n  brew uninstall xcodes 2>/dev/null || true\\n  brew install xcodesorg/made/xcodes\\n  if [ -n \"${{ secrets.APPLE_ID }}\" ] && [ -n \"${{ secrets.APPLE_PASSWORD }}\" ]; then\\n    xcodes install --latest 15.0.1 --apple-id \"${{ secrets.APPLE_ID }}\" --password \"${{ secrets.APPLE_PASSWORD }}\"\\n    XC=$(ls -d /Applications/Xcode_15.0.1.app 2>/dev/null || ls -d /Applications/Xcode_15.*.app 2>/dev/null | head -1)\\n  else\\n    echo \"No Apple ID credentials in secrets. Trying to use pre-installed Xcode 26 as fallback...\"\\n    XC=$(ls -d /Applications/Xcode_26.*.app 2>/dev/null | head -1)\\n  fi\\nfi\\nif [ -z \"$XC\" ]; then\\n  echo \"ERROR: No suitable Xcode found\"\\n  exit 1\\nfi\\necho \"DEVELOPER_DIR=$XC/Contents/Developer\"\\n>> \"$GITHUB_ENV\"\\nsudo xcode-select -s \"$XC\"\\nxcodebuild -version\\n"
    - name: Download KDK
      run: "# Check if KDK is already installed\nif [ -d \"/Library/Developer/KDKs/KernelDebugKit_13.5_build_22G74.kdk\" ]; then\n  echo \"KDK already installed at /Library/Developer/KDKs/\"\n  ls -la /Library/Developer/KDKs/\nelse\n  echo \"KDK not found, downloading...\"\n  KDK_URLS=(\n    \"https://github.com/dortania/KdkSupportPkg/releases/download/22G74/Kernel_Debug_Kit_13.5_build_22G74.dmg\"\\n    \"https://developer.apple.com/services-account/download?path=/Developer_Tools/Kernel_Debug_Kit_13.5/Kernel_Debug_Kit_13.5_build_22G74.dmg\"\\n  )\n  DOWNLOAD_SUCCESS=false\n  for KDK_URL in \"${KDK_URLS[@]}\"; do\\n    echo \"Trying to download KDK from: $KDK_URL\"\\n    if curl -L --max-time 300 --retry 3 --retry-delay 5 -o /tmp/KDK.dmg \"${KDK_URL}\"; then\\n      FILE_SIZE=$(stat -f%z /tmp/KDK.dmg 2>/dev/null || stat -c%s /tmp/KDK.dmg 2>/dev/null)\\n      if [ \"$FILE_SIZE\" -gt 100000000 ]; then\\n        echo \"Download successful (${FILE_SIZE} bytes)\"\n        DOWNLOAD_SUCCESS=true\n        break\n      else\\n        echo \"Downloaded file too small (${FILE_SIZE} bytes), likely an error page\"\n        rm -f /tmp/KDK.dmg\n      fi\\n    else\\n      echo \"Download failed from $KDK_URL\"\\n    fi\\n  done\\n  if [ \"$DOWNLOAD_SUCCESS\" = false ]; then\\n    echo \"All download attempts failed\"\n    exit 1\n  fi\n  echo \"Mounting KDK DMG...\"\n  hdiutil attach /tmp/KDK.dmg\n  echo \"Installing KDK...\"\n  sudo installer -pkg '/Volumes/Kernel Debug Kit/KernelDebugKit.pkg' -target /\n  hdiutil detach '/Volumes/Kernel Debug Disk' 2>/dev/null || true\nfi\\nls -la /Library/Developer/KDKs/"
    - name: Verify build environment
      run: 'echo "=== Build Environment Verification ==="\necho "SRCROOT: ${SRCROOT:-not set}"\necho "CURRENT_KERNEL_CONFIG: ${CURRENT_KERNEL_CONFIG:-not set}"\necho "CURRENT_ARCH_CONFIG: ${CURRENT_ARCH_CONFIG:-not set}"\necho "CURRENT_MACHINE_CONFIG: ${CURRENT_MACHINE_CONFIG:-not set}"\necho "CURRENT_MACHINE_CONFIG_LC: ${CURRENT_MACHINE_CONFIG_LC:-not set}"\necho "SDKROOT: ${SDKROOT:-not set}"\necho "DEVELOPER_DIR: ${DEVELOPER_DIR:-not set}"\necho "KDKROOT: ${KDKROOT:-not set}"\necho "OBJROOT: ${OBJROOT:-not set}"\necho "=== KDK Installation ==="\nls -la /Library/Developer/KDKs/ 2>/dev/null || echo "No KDKs found"\necho "=== SDKROOT ==="\nxcrun --sdk macosx --show-sdk-path\n'
    - name: Clone XNU
      run: 'git clone --branch xnu-8796.141.3 --depth 1 https://github.com/apple-oss-distributions/xnu.git xnu-source\ncd xnu-source\ngit describe --tags --always\necho "=== Checking for export files ==="\nls -la config/*.exports 2>/dev/null | head -20 || echo "No export files found"\necho "=== Config directory contents ==="\nls -la config/ | head -30'
    - name: Stage libpthread dependency
      run: 'cd xnu-source\nMACHINE_CONFIG=M30LTE bash ../xnu/patches/0019-stage-libpthread.sh'
    - name: Stage BearSSL dependency
      run: 'cd xnu-source\nMACHINE_CONFIG=M30LTE bash ../xnu/patches/0020-stage-bearssl.sh || true'
    - name: Apply M30LTE patches
      run: "cd xnu-source\nfor patch in ../xnu/patches/00*.patch; do\n  name=$(basename "$patch")\n  echo "Applying: $name"\n  patch -p1 --no-backup-if-mismatch < "$patch" 2>&1 || true\ndone\nls -la pexpert/pexpert/arm64/M30LTE.h 2>&1 || echo "M30LTE.h NOT FOUND - creating from patch"\ncat ../xnu/patches/0000-m30lte-machine-config.patch | grep -A 50 "M30LTE.h" | head -60 || true\n'
    - name: Fix MASTER.arm64.m30lte config
      run: "cd xnu-source\necho \"=== Fixing MASTER.arm64.m30lte config ===\"\nif [ -f config/MASTER.arm64.m30lte ]; then\n  python3 ../xnu/patches/fix_master_m30lte.py\n  echo "=== MASTER.arm64.m30lte after fix ===\"\n  cat config/MASTER.arm64.m30lte\nelse\n  echo \"MASTER.arm64.m30lte not found, skipping fix\"\nfi\n"
    - name: Fix makedefs path in Makefiles
      run: 'cd xnu-source\npython3 ../xnu/fix_makedefs.py .\ngrep -r "/makedefs" . --include="Makefile" --include="*.mk" --include="*.mak" | head -5 || echo "No more /makedefs references found"\n'
    - name: Patch security/Makefile for kernel source includes
      run: 'cd xnu-source\npython3 ../xnu/patches/patch_security_makefile.py\necho "Patched successfully"'
    - name: Fix proc_reg.h for M30LTE
      run: "cd xnu-source\necho \"=== Force patching proc_reg.h for M30LTE ===\"\nif ! grep -q "M30LTE" osfmk/arm64/proc_reg.h; then\n  echo "M30LTE not found in proc_reg.h, applying manually..."\n  python3 ../xnu/patches/patch_proc_reg.py\nelse\n  echo "M30LTE already defined in proc_reg.h"\nfi\ngrep -n "M30LTE" osfmk/arm64/proc_reg.h | head -5\n'
    - name: Create firehose_buffer_private.h for M30LTE
      run: "cd xnu-source\necho \"=== Creating firehose_buffer_private.h for M30LTE ===\"\nif [ ! -f osfmk/arm64/firehose_buffer_private.h ]; then\n  echo \"firehose_buffer_private.h not found, creating...\"\n  python3 ../xnu/patches/create_firehose_buffer_private.py\nelse\n  echo "firehose_buffer_private.h already exists"\nfi\nmkdir -p BUILD/obj/EXPORT_HDRS/osfmk/arm64\ncp osfmk/arm64/firehose_buffer_private.h BUILD/obj/EXPORT_HDRS/osfmk/arm64/\n'
    - name: Fix clang flag incompatibility with Xcode 26
      run: "cd xnu-source\necho \"=== Patching clang flag incompatibility ===\"\nfind . -name \"*.def\" -o -name \"Makefile*\" -o -name \"*.mk\" -o -name \"*.inc\" | xargs grep -l \"enable-trivial-auto-var-init-zero-knowing\" 2>/dev/null | while read file; do\n  echo \"Patching: $file\"\n  sed -i '' 's/-enable-trivial-auto-var-init-zero-knowing-it-will-be-removed-from-clang//g' "$file"\ndone\ngrep -r \"enable-trivial-auto-var-init-zero-knowing\" . 2>/dev/null | head -5 || echo "Flag not found in source (may be added at build time)"\n'
    - name: Verify bsd/Makefile structure
      run: 'cd xnu-source\necho "=== Verifying bsd/Makefile structure ==="\ngrep -n "do_all" bsd/Makefile || echo "No do_all target found"\ngrep -n "OBJPATH" bsd/Makefile | head -5\necho "=== First 30 lines of bsd/Makefile ==="\nhead -30 bsd/Makefile\n'
    - name: Patch bsd/conf/Makefile do_all to pass SRCROOT/SETUP to sub-make
      run: 'cd xnu-source\npython3 ../xnu/patches/patch_bsd_do_all.py\ngrep -A 12 "do_all" bsd/conf/Makefile | head -15\n'
    - name: Fix DriverKit IORPC for Xcode 26
      run: "cd xnu-source\necho \"=== Patching DriverKit IORPC for Xcode 26 compatibility ===\"\nif [ -f iokit/Kernel/arm64/IORPC.h ]; then\n  echo \"Patching IORPC.h to add kernelContent field...\"\n  python3 ../xnu/patches/patch_iorpc.py\nelse\n  echo "IORPC.h not found, skipping\"\nfi\necho "=== Patching iokit/Makefile to skip DriverKit when DRIVERKIT=0 ===\"\npython3 ../xnu/patches/patch_iokit_makefile.py'
    - name: Patch osfmk/mach/Makefile for VPATH
      run: 'cd xnu-source\necho "=== Patching osfmk/mach/Makefile for VPATH ==="\npython3 ../xnu/patches/patch_osfmk_mach_vpath.py\necho "Patched successfully"'
    - name: Patch osfmk/gssd/Makefile for VPATH
      run: 'cd xnu-source\necho "=== Patching osfmk/gssd/Makefile for VPATH ==="\npython3 ../xnu/patches/patch_gssd_makefile.py\necho "Patched successfully"'
    - name: Patch libkern/libkern/Makefile for VPATH
      run: 'cd xnu-source\necho "=== Patching libkern/libkern/Makefile for VPATH ===\npython3 ../xnu/patches/patch_libkern_makefile.py\necho "Patched successfully"'
    - name: Patch security/Makefile for kernel source includes
      run: 'cd xnu-source\necho "=== Patching security/Makefile for kernel source includes ===\npython3 ../xnu/patches/patch_security_makefile.py\necho "Patched successfully"'
    - name: Generate valid conf Makefiles and bypass conf subdirectories
      run: "cd xnu-source\necho \"=== Generating valid conf Makefiles ===\"\npython3 ../xnu/patches/patch_all_conf_makefiles.py\necho \"=== Bypassing conf subdirectories in component Makefiles ===\"\nfor comp in security bsd osfmk libkern iokit pexpert libsa san; do\n  if [ -f $comp/Makefile ]; then\n    sed -i '' 's/^COMP_SUBDIRS.*/COMP_SUBDIRS =/' $comp/Makefile\n    echo \"Patched COMP_SUBDIRS in $comp/Makefile\"\n  fi\ndone\necho " === Creating empty .filelist files ===\"\nfor comp in security bsd osfmk libkern iokit pexpert libsa san security; do\n  mkdir -p BUILD/obj/DEVELOPMENT_ARM64_M30LTE/$comp/DEVELOPMENT\n  touch BUILD/obj/DEVELOPMENT_ARM64_M30LTE/$comp/DEVELOPMENT/$comp.filelist\n  echo "Created $comp.filelist"\ndone\necho "=== Copying export files to build config directory ===\"\ncp config/*.exports BUILD/obj/DEVELOPMENT_ARM64_M30LTE/config/ 2>/dev/null || true\ntouch BUILD/obj/DEVELOPMENT_ARM64_M30LTE/all-kpi.exp\necho "Created all export files"\n"
    - name: Patch libkern/os/atomic_private_impl.h for memory_order
      run: 'cd xnu-source\npython3 ../xnu/patches/patch_atomic_memory_order.py\necho "Patched successfully"'
    - name: Patch osfmk/mach/arm/Makefile for VPATH
      run: 'cd xnu-source\necho "=== Patching osfmk/mach/arm/Makefile for VPATH ==="\npython3 ../xnu/patches/patch_osfmk_mach_arm_vpath.py\necho "Patched successfully"'
    - name: Patch osfmk/mach/arm/Makefile for VPATH
      run: 'cd xnu-source\necho "=== Patching osfmk/mach/arm/Makefile for VPATH ==="\npython3 ../xnu/patches/patch_osfmk_mach_arm_vpath.py\necho "Patched successfully"'
    - name: Copy .defs files to build directory for all osfmk subdirs
      run: 'cd xnu-source\npython3 ../xnu/patches/copy_defs_files.py\n\necho "Copied .defs files to build directory"'
    - name: Build bootstrap_cmds (mig)
      run: 'cd xnu-source\nBOOTSTRAP_VERSION=$(curl -s "https://raw.githubusercontent.com/apple-oss-distributions/distribution-macOS/macos-135/release.json"\n| jq -r \''.projects[] | select(.project=="bootstrap_cmds") | .tag'\')\ngit clone --branch "${BOOTSTRAP_VERSION}" --depth 1 https://github.com/apple-oss-distributions/bootstrap_cmds.git\ncd bootstrap_cmds\nsed -i '\'\\\'\' \'s|-o root -g wheel||g'' xcodescripts/install-mig.sh\nxcodebuild install -sdk macosx -project mig.xcodeproj ARCHS="arm64 x86_64" CODE_SIGN_IDENTITY="-" OBJROOT="$PWD/../BUILD/bootstrap_cmds.obj" SYMROOT="$PWD/../BUILD/bootstrap_cmds.sym" DSTROOT="$PWD/fakeroot" RC_ProjectNameAndSourceVersion="${BOOTSTRAP_VERSION}"\n2>&1 | tail -20 || true\n'
    - name: Build dtrace (ctf tools)
      run: 'cd xnu-source\nDTRACE_VERSION=$(curl -s "https://raw.githubusercontent.com/apple-oss-distributions/distribution-macOS/macos-135/release.json"\n| jq -r ''.projects[] | select(.project=="dtrace") | .tag'')\ngit clone --branch "${DTRACE_VERSION}" --depth 1 https://github.com/apple-oss-distributions/dtrace.git\ncd dtrace\nxcodebuild install -sdk macosx -target ctfconvert -target ctfdump -target ctfmerge ARCHS="arm64 x86_64" CODE_SIGN_IDENTITY="-" OBJROOT="$PWD/../BUILD/dtrace.obj" SYMROOT="$PWD/../BUILD/dtrace.sym" DSTROOT="$PWD/../fakeroot" 2>&1 | tail -20 || true\n'
    - name: Build availability versions
      run: "cd xnu-source\nAVAILABILITYVERSIONS_VERSION=$(curl -s \"https://raw.githubusercontent.com/apple-oss-distributions/distribution-macOS/macos-135/release.json\"\n| jq -r '.projects[] | select(.project=="AvailabilityVersions") | .tag'')\ngit clone --branch "${AVAILABILITYVERSIONS_VERSION}" --depth 1 https://github.com/apple-oss-distributions/AvailabilityVersions.git\ncd AvailabilityVersions\nmake install -j8 OBJROOT="$PWD/../BUILD/" SYMROOT="$PWD/../BUILD/" DSTROOT="$PWD/../fakeroot" 2>&1 | tail -20 || true\nif [ -f "$PWD/../fakeroot/usr/local/libexec/availability.pl" ]; then\n  echo "Installing availability.pl to /usr/local/libexec/"\n  sudo mkdir -p /usr/local/libexec\n  sudo cp "$PWD/../fakeroot/usr/local/libexec/availability.pl" /usr/local/libexec/availability.pl\n  sudo chmod +x /usr/local/libexec/availability.pl\n  echo "Installed availability.pl to host system"\nelse\n  echo "WARNING: availability.pl not found in fakeroot"\n  find "$PWD/../fakeroot" -name "availability.pl" 2>/dev/null || true\nfi\n'
    - name: Create minimal availability.pl for _symbol_aliasing.h
      run: 'cd xnu-source\nmkdir -p /usr/local/libexec\npython3 ../xnu/patches/create_minimal_availability_pl.py > /tmp/availability.pl\nsudo cp /tmp/availability.pl /usr/local/libexec/availability.pl\nsudo chmod +x /usr/local/libexec/availability.pl\necho "Created minimal availability.pl at /usr/local/libexec/availability.pl"\n/usr/local/libexec/availability.pl --ios | head -5\n/usr/local/libexec/availability.pl --macosx | head -5\n'
    - name: Patch make_symbol_aliasing.sh for availability.pl fallback
      run: 'cd xnu-source\npython3 ../xnu/patches/patch_availability_fallback.py\necho "Patched successfully"'
    - name: Install xnu headers
      run: 'cd xnu-source\necho "=== Installing XNU headers ==="\nmake installhdrs -j8 SDKROOT=iphoneos ARCH_CONFIGS="ARM64" MACHINE_CONFIGS="M30LTE"\nOBJROOT="$PWD/BUILD/xnu-hdrs.obj" SYMROOT="$PWD/BUILD/xnu-hdrs.sym" DSTROOT="$PWD/fakeroot" FAKEROOT_DIR="$PWD/fakeroot" KDKROOT="/Library/Developer/KDKs" TIGHTBEAMC="" RC_DARWIN_KERNEL_VERSION="22.6.0" MEMORY_SIZE="${MEMORY_SIZE}" SYSCTL_HW_PHYSICALCPU="${SYSCTL_PHYSICALCPU}" SYSCTL_HW_LOGICALCPU="${SYSCTL_LOGICALCPU}" KERNEL_BUILDS_IN_PARALLEL=1 2>&1 | tail -20\n'
    - name: Pre-build IORPC patch for DriverKit
      run: 'cd xnu-source\npython3 ../xnu/patches/patch_all_iorpc.py\n'
    - name: Patch SETUP/config/Makefile for VPATH
      run: 'cd xnu-source\npython3 ../xnu/patches/patch_setup_config_vpath.py\n'
    - name: Fix SETUP tool include paths
      run: 'cd xnu-source\nSDKROOT_PATH=$(xcrun --sdk iphoneos --show-sdk-path)\necho "SDKROOT_PATH=$SDKROOT_PATH"\nexport SDKROOT_PATH\npython3 ../xnu/patches/fix_setup_tool_includes.py\n'
    - name: Fix makedefs paths in build directory
      run: 'cd xnu-source\npython3 ../xnu/fix_makedefs.py BUILD/obj\ngrep -r "/makedefs" BUILD/obj --include="Makefile" --include="*.mk" --include="*.mak" | head -5 || echo "No more /makedefs references found in build directory"\n'
    - name: Build SETUP tools for macOS (host platform)
      run: "cd xnu-source\nMAKEFLAGS=\"\"\nfor comp in bootstrap_cmds SETUP/config SETUP/kextsymboltool SETUP/setsegname SETUP/decomment SETUP/installfile SETUP/replacecontents; do\n  echo \"=== Building $comp ===\"\n  cd $SRCROOT/SETUP/$comp || continue\n  make -f Makefile CURRENT_KERNEL_CONFIG=DEVELOPMENT CURRENT_ARCH_CONFIG=ARM64 CURRENT_MACHINE_CONFIG=M30LTE CURRENT_MACHINE_CONFIG_LC=m30lte OBJROOT=\"$PWD/BUILD/obj\" SYMROOT=\"$PWD/BUILD/sym\" DSTROOT=\"$PWD/fakeroot\" KDKROOT="/Library/Developer/KDKs" TIGHTBEAMC="" RC_DARWIN_KERNEL_VERSION="22.6.0" MEMORY_SIZE="${MEMORY_SIZE}" SYSCTL_HW_PHYSICALCPU="${SYSCTL_PHYSICALCPU}" SYSCTL_HW_LOGICALCPU="${SYSCTL_LOGICALCPU}" KERNEL_BUILDS_IN_PARALLEL=1 2>&1 | tail -20 || true\n  cd "$SRCROOT"\ndone\n'
    - name: Patch SETUP/config/Makefile to skip rebuild if tools exist
      run: 'cd xnu-source\npython3 ../xnu/patches/patch_setup_config_skip_build.py\n'
    - name: Copy version.h.template to build directory
      run: 'cd xnu-source\nmkdir -p BUILD/obj/DEVELOPMENT_ARM64_M30LTE/libkern/libkern\ncp osfmk/kern/version.h.template BUILD/obj/DEVELOPMENT_ARM64_M30LTE/libkern/libkern/\nls -la BUILD/obj/DEVELOPMENT_ARM64_M30LTE/libkern/libkern/version.h.template\n'
    - name: Copy asm.h to build directory
      run: 'cd xnu-source\nmkdir -p BUILD/obj/DEVELOPMENT_ARM64_M30LTE/osfmk/arm\ncp osfmk/arm/asm.h BUILD/obj/DEVELOPMENT_ARM64_M30LTE/osfmk/mach/arm/\nls -la BUILD/obj/DEVELOPMENT_ARM64_M30LTE/osfmk/mach/arm/asm.h\nmkdir -p BUILD/obj/DEVELOPMENT_ARM64_M30LTE/osfmk/mach/arm64\ncp osfmk/arm64/asm.h BUILD/obj/DEVELOPMENT_ARM64_M30LTE/osfmk/mach/arm64/\nls -la BUILD/obj/DEVELOPMENT_ARM64_M30LTE/osfmk/mach/arm64/asm.h\n'
    - name: Copy full kernel private headers to build directory
      run: 'cd xnu-source\necho "=== Copying full kernel-private headers to EXPORT_HDRS ==="\nmkdir -p BUILD/obj/EXPORT_HDRS/osfmk/arm/mach\ncp osfmk/arm/locks.h BUILD/obj/EXPORT_HDRS/osfmk/arm/locks.h\nls -la BUILD/obj/DEVELOPMENT_ARM64_M30LTE/osfmk/mach/arm/locks.h\ncp osfmk/arm64/locks.h BUILD/obj/DEVELOPMENT_ARM64_M30LTE/osfmk/mach/arm64/locks.h 2>/dev/null || echo "arm64/locks.h not found, using arm version"\ncp osfmk/machine/locks.h BUILD/obj/DEVELOPMENT_ARM64_M30LTE/osfmk/mach/machine/locks.h 2>/dev/null || echo "machine/locks.h not found"\ncp osfmk/kern/lock_mtx.h BUILD/obj/DEVELOPMENT_ARM64_M30LTE/osfmk/kern/lock_mtx.h\nls -la BUILD/obj/DEVELOPMENT_ARM64_M30LTE/osfmk/kern/lock_mtx.h\ncp osfmk/kern/locks.h BUILD/obj/DEVELOPMENT_ARM64_M30LTE/osfmk/kern/locks.h\nls -la BUILD/obj/DEVELOPMENT_ARM64_M30LTE/osfmk/kern/locks.h\n'
    - name: Patch EXPORT_HDRS/osfmk/arm/locks.h for full lck_mtx_t definition
      run: 'cd xnu-source\npython3 ../xnu/patches/patch_export_lock_h.py\n'
    - name: Patch security/mac_audit.c for kernel includes and ptrauth
      run: 'cd xnu-source\npython3 ../xnu/patches/patch_mac_audit.py\n'
    - name: Run bsd build to capture linker error
      run: 'cd xnu-source\nmake -e \\\n  -C BUILD/obj/DEVELOPMENT_ARM64_M30LTE/bsd \\\n  -f bsd/Makefile \\\n  CURRENT_KERNEL_CONFIG=DEVELOPMENT \\\n  CURRENT_ARCH_CONFIG=ARM64 \\\n  CURRENT_MACHINE_CONFIG=M30LTE \\\n  SOURCE="$PWD/bsd/" \\\n  RELATIVE_SOURCE_PATH="./bsd" \\\n  TARGET="$PWD/BUILD/obj/DEVELOPMENT_ARM64_M30LTE/bsd/" \\\n  OBJPATH="$PWD/BUILD/obj/DEVELOPMENT_ARM64_M30LTE" \\\n  VERBOSE=YES \\\n  build_all 2>&1 | tee /tmp/bsd-build.log\nBSD_EXIT=${PIPESTATUS[0]}\necho "bsd build exit code: ${BSD_EXIT}"\ncat /tmp/bsd-build.log\ncp /Users/runner/work/ios-m30lte/ios-m30lte/bsd-build.log bsd-build.log 2>/dev/null || true\nls -la bsd-build.log 2>/dev/null || echo "bsd-build.log not found"\n'
    - name: Upload bsd build log
      if: always()
      run: 'cp /Users/runner/work/ios-m30lte/ios-m30lte/bsd-build.log bsd-build.log 2>/dev/null || true\nls -la bsd-build.log 2>/dev/null || echo "bsd-build.log not found"\n'
    - uses: actions/upload-artifact@v4
      if: always()
      with:
        name: xnu-build-log
        path: xnu-build.log
        if-no-files-found: warn
    - name: Collect kernel artifact
      if: always()
      run: "cd xnu-source\necho \"=== Searching for kernel binary ===\"\nfind BUILD/obj -name \"kernel.*\" -type f 2>/dev/null | head -20\necho \"=== Checking for any kernel binary ===\"\nKERNEL_PATH=$(find BUILD/obj -maxdepth 5 -name "kernel.development.m30lte" -o -name "mach_kernel" -o -name "kernel" 2>/dev/null | head -1)\nif [ -n "$KERNEL_PATH" ]; then\n  echo "Found kernel at: $KERNEL_PATH"\n  cp "$KERNEL_PATH" out/kernel.development.m30lte\nfi\nls -la out\nif [ -f out/kernel.development.m30lte ]; then\n  (cd out && shasum -a 256 kernel.development.m30lte > SHA256SUMS)\nfi\n'
    - uses: actions/upload-artifact@v4
      if: always()
      with:
        name: xnu-kernel
        path: out/
        if-no-files-found: warn
    - name: Trigger CI build
      run: "echo \"Trigger CI build\"\n"
