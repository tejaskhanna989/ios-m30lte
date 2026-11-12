#!/usr/bin/env python3
"""Write the complete CI workflow file."""

workflow_content = """name: XNU Kernel Build for M30LTE

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
      run: |
        echo "=== Checking pre-installed Xcode versions ==="
        ls -la /Applications/Xcode*.app 2>/dev/null || echo "No Xcode apps found"
        echo "=== Checking xcode-select ==="
        xcode-select -p
        xcodebuild -version
    - name: Deps
      run: |
        brew install jq gum bash cmake ninja
        XC=$(ls -d /Applications/Xcode_15.0.1.app 2>/dev/null || ls -d /Applications/Xcode_15.*.app 2>/dev/null | head -1)
        if [ -z "$XC" ]; then
          echo "Xcode 15 not pre-installed, attempting to install via xcodes with Apple ID from secrets..."
          printf '#!/bin/sh\nexit 0\n' | sudo tee /usr/local/bin/xcodes >/dev/null
          sudo chmod +x /usr/local/bin/xcodes
          brew uninstall xcodes 2>/dev/null || true
          brew install xcodesorg/made/xcodes
          if [ -n "${{ secrets.APPLE_ID }}" ] && [ -n "${{ secrets.APPLE_PASSWORD }}" ]; then
            xcodes install --latest 15.0.1 --apple-id "${{ secrets.APPLE_ID }}" --password "${{ secrets.APPLE_PASSWORD }}"
            XC=$(ls -d /Applications/Xcode_15.0.1.app 2>/dev/null || ls -d /Applications/Xcode_15.*.app 2>/dev/null | head -1)
          else
            echo "No Apple ID credentials in secrets. Trying to use pre-installed Xcode 26 as fallback..."
            XC=$(ls -d /Applications/Xcode_26.*.app 2>/dev/null | head -1)
          fi
        fi
        if [ -z "$XC" ]; then
          echo "ERROR: No suitable Xcode found"
          exit 1
        fi
        echo "DEVELOPER_DIR=$XC/Contents/Developer" >> "$GITHUB_ENV"
        sudo xcode-select -s "$XC"
        xcodebuild -version
    - name: Download KDK
      run: |
        echo "=== Checking if KDK is already installed ==="
        if [ -d "/Library/Developer/KDKs/KernelDebugKit_13.5_build_22G74.kdk" ]; then
          echo "KDK already installed at /Library/Developer/KDKs/"
          ls -la /Library/Developer/KDKs/
        else
          echo "KDK not found, downloading..."
          KDK_URLS=(
            "https://github.com/dortania/KdkSupportPkg/releases/download/22G74/Kernel_Debug_Kit_13.5_build_22G74.dmg"
            "https://developer.apple.com/services-account/download?path=/Developer_Tools/Kernel_Debug_Kit_13.5/Kernel_Debug_Kit_13.5_build_22G74.dmg"
          )
          DOWNLOAD_SUCCESS=false
          for KDK_URL in "${KDK_URLS[@]}"; do
            echo "Trying to download KDK from: $KDK_URL"
            if curl -L --max-time 300 --retry 3 --retry-delay 5 -o /tmp/KDK.dmg "$KDK_URL"; then
              FILE_SIZE=$(stat -f%z /tmp/KDK.dmg 2>/dev/null || stat -c%s /tmp/KDK.dmg 2>/dev/null)
              if [ "$FILE_SIZE" -gt 100000000 ]; then
                echo "Download successful (${FILE_SIZE} bytes)"
                DOWNLOAD_SUCCESS=true
                break
              else
                echo "Downloaded file too small (${FILE_SIZE} bytes), likely an error page"
                rm -f /tmp/KDK.dmg
              fi
            else
              echo "Download failed from $KDK_URL"
            fi
          done
          if [ "$DOWNLOAD_SUCCESS" = false ]; then
            echo "All download attempts failed"
            exit 1
          fi
          echo "Mounting KDK DMG..."
          hdiutil attach /tmp/KDK.dmg
          echo "Installing KDK..."
          sudo installer -pkg '/Volumes/Kernel Debug Kit/KernelDebugKit.pkg' -target /
          hdiutil detach '/Volumes/Kernel Debug Disk' 2>/dev/null || true
        fi
        echo "=== Verifying KDK installation ==="
        ls -la /Library/Developer/KDKs/
    - name: Clone XNU
      run: 'cd xnu-source
        git clone --branch xnu-8796.141.3 --depth 1 https://github.com/apple-oss-distributions/xnu.git xnu-source
        cd xnu-source
        git describe --tags --always'
    - name: Stage libpthread dependency
      run: 'cd xnu-source
        MACHINE_CONFIG=M30LTE bash ../xnu/patches/0019-stage-libpthread.sh'
    - name: Stage BearSSL dependency
      run: 'cd xnu-source
        MACHINE_CONFIG=M30LTE bash ../xnu/patches/0020-stage-bearssl.sh || true'
    - name: Apply M30LTE patches
      run: "cd xnu-source\nfor patch in ../xnu/patches/00*.patch; do\n  name=$(basename \"$patch\")\n  echo \"Applying: $name\"\n  patch -p1 --no-backup-if-mismatch < \"$patch\" 2>&1 || true\ndone\nls -la pexpert/pexpert/arm64/M30LTE.h 2>&1 || echo \"M30LTE.h NOT FOUND - creating from patch\"\ncat ../xnu/patches/0000-m30lte-machine-config.patch | grep -A 50 \"M30LTE.h\" | head -60 || true\n"
    - name: Fix MASTER.arm64.m30lte config
      run: "cd xnu-source\necho \"=== Fixing MASTER.arm64.m30lte config ===\"\nif [ -f config/MASTER.arm64.m30lte ]; then\n  python3 ../xnu/patches/fix_master_m30lte.py\n  echo \"=== MASTER.arm64.m30lte after fix ===\"\n  cat config/MASTER.arm64.m30lte\nelse\n  echo \"MASTER.arm64.m30lte not found, skipping fix\"\nfi\n"
    - name: Fix makedefs path in Makefiles
      run: 'cd xnu-source

        echo "=== Fixing /makedefs paths in Makefiles ==="

        python3 ../xnu/fix_makedefs.py .

        # Verify the changes

        grep -r "/makedefs" . --include="Makefile" --include="*.mk" --include="*.mak" | head -5 || echo "No more /makedefs references found"

        '
    - name: Patch security/Makefile for kernel source includes
      run: 'cd xnu-source\n\n        echo "=== Patching security/Makefile for kernel source includes ===\\"\n\n        python3 ../xnu/patches/patch_security_makefile.py\n\n        echo "Patched successfully"\n'
    - name: Bypass conf subdirectories and create build files
      run: "cd xnu-source\necho \"=== Bypassing conf subdirectories ===\"\nfor comp in security bsd osfmk libkern iokit pexpert libsa san security; do\n  if [ -f $comp/Makefile ]; then\n    sed -i '' 's/^COMP_SUBDIRS.*/COMP_SUBDIRS =/' $comp/Makefile\n    echo \"Patched COMP_SUBDIRS in $comp/Makefile\"\n  fi\ndone\necho \"=== Creating empty .filelist files ===\"\nfor comp in security bsd osfmk libkern iokit pexpert libsa san security; do\n  mkdir -p BUILD/obj/DEVELOPMENT_ARM64_M30LTE/$comp/DEVELOPMENT\\n  touch BUILD/obj/DEVELOPMENT_ARM64_M30LTE/$comp/DEVELOPMENT/$comp.filelist\\n  echo \"Created $comp.filelist\"\ndone\\necho \\"=== Copying export files to build config directory ===\\\"\\ncp config/*.exports BUILD/obj/DEVELOPMENT_ARM64_M30LTE/config/ 2>/dev/null || true\\ntouch BUILD/obj/DEVELOPMENT_ARM64_M30LTE/all-kpi.exp\\necho \\"Created all export files\\\"\n'
    - name: Patch libkern/os/atomic_private_impl.h for memory_order
      run: 'cd xnu-source\n\n        echo "=== Patching libkern/os/atomic_private_impl.h for memory_order ===\\\"\\n\\\\n        python3 ../xnu/patches/patch_atomic_memory_order.py\\\\n\\\\n        echo \\"Patched successfully\\\"\\\\n\'\\n    - name: Patch osfmk/mach/arm/Makefile for VPATH\\n      run: \'cd xnu-source\\\\n\\\\n        echo \\"=== Patching osfmk/mach/arm/Makefile for VPATH ===\\\\\\\\"\\\\n\\\\n        python3 ../xnu/patches/patch_osfmk_mach_arm_vpath.py\\\\n\\\\n        echo \\"Patched successfully\\\"\\\\n\'\\n    - name: Patch osfmk/mach/arm/Makefile for VPATH\\n      run: \'cd xnu-source\\\\n\\\\n        echo \\"=== Patching osfmk/mach/arm/Makefile for VPATH ===\\\\\\\"\\\\n\\\\n        python3 ../xnu/patches/patch_osfmk_mach_arm_vpath.py\\\\n\\\\n        echo \\"Patched successfully\\\"\\\\n\'\\n    - name: Copy .defs files to build directory for all osfmk subdirs\\n      run: \'cd xnu-source\\\\n\\\\n        echo \\"=== Copying .defs files to build directory for all osfmk subdirs ===\\\\\\\"\\\\n\\\\n        python3 ../xnu/patches/copy_defs_files.py\\\\n\\\\n        echo \\"Copied .defs files to build directory\\\"\\\\n\'\\n    - name: Build bootstrap_cmds (mig)\\n      run: \'cd xnu-source\\\\n\\\\n        BOOTSTRAP_VERSION=$(curl -s "https://raw.githubusercontent.com/apple-oss-distributions/distribution-macOS/macos-135/release.json"\n| jq -r \'.projects[] | select(.project=="bootstrap_cmds") | .tag\'\\\\\n\\\\n        git clone --branch "${BOOTSTRAP_VERSION}" --depth 1 https://github.com/apple-oss-distributions/bootstrap_cmds.git\\\\n        bootstrap_cmds\\\\n\\\\n        cd bootstrap_cmds\\\\n\\\\n        sed -i \'\'s|-o root -g wheel||g\\'\' xcodescripts/install-mig.sh\\\\n\\\\n        xcodebuild install -sdk macosx -project mig.xcodeproj ARCHS="arm64 x86_64" CODE_SIGN_IDENTITY="-" OBJROOT="$PWD/../BUILD/bootstrap_cmds.obj" SYMROOT="$PWD/../BUILD/bootstrap_cmds.sym" DSTROOT="$PWD/../fakeroot" RC_ProjectNameAndSourceVersion="${BOOTSTRAP_VERSION}"\\\\n\\\\n        2>&1 | tail -20 || true\\\\n        \\\\n        \'\\n    - name: Build dtrace (ctf tools)\\n      run: \'cd xnu-source\\\\n\\\\n        DTRACE_VERSION=$(curl -s "https://raw.githubusercontent.com/apple-oss-distributions/distribution-macOS/macos-135/release.json"\n| jq -r \'.projects[] | select(.project=="dtrace") | .tag\'\\\\\\\\n\\\\n        git clone --branch "${DTRACE_VERSION}" --depth 1 https://github.com/apple-oss-distributions/dtrace.git\\\\n        dtrace\\\\n\\\\n        cd dtrace\\\\n\\\\n        xcodebuild install -sdk macosx -target ctfconvert -target ctfdump -target ctfmerge ARCHS="arm64 x86_64" CODE_SIGN_IDENTITY="-" OBJROOT="$PWD/../BUILD/dtrace.obj" SYMROOT="$PWD/../BUILD/dtrace.sym" DSTROOT="$PWD/../fakeroot" 2>&1 | tail -20 || true\\\\n        \\\\\\\\n        \'\\n    - name: Build availability versions\\n      run: "cd xnu-source\\nAVAILABILITYVERSIONS_VERSION=$(curl -s \"https://raw.githubusercontent.com/apple-oss-distributions/distribution-macOS/macos-135/release.json\"\n| jq -r \'.projects[] | select(.project=="AvailabilityVersions") | .tag\')\\\\n\\\\ngit clone --branch "${AVAILABILITYVERSIONS_VERSION}" --depth 1 https://github.com/apple-oss-distributions/AvailabilityVersions.git\\\\ncd AvailabilityVersions\\\\nmake install -j8 OBJROOT="$PWD/../BUILD/" SYMROOT="$PWD/../BUILD/" DSTROOT="$PWD/../fakeroot" 2>&1 | tail -20 || true\\\\n# Also install availability.pl to host system location\\\\nfor make_symbol_aliasing.sh fallback\\\\nif [ -f "$PWD/../fakeroot/usr/local/libexec/availability.pl" ]; then\\\\n  echo \\"Installing availability.pl to /usr/local/libexec/\\\"\\\\n  sudo mkdir -p /usr/local/libexec\\\\n  sudo cp "$PWD/../fakeroot/usr/local/libexec/availability.pl" /usr/local/libexec/availability.pl\\\\n  sudo chmod +x /usr/local/libexec/availability.pl\\\\n  echo \\"Installed availability.pl to host system\\\"\\\\nelse\\\\n  echo \\"WARNING: availability.pl not found in fakeroot\\\"\\\\n  find "$PWD/../fakeroot" -name "availability.pl" 2>/dev/null || true\\\\nfi\\\\n\'\\n    - name: Create minimal availability.pl for _symbol_aliasing.h\\n      run: \'cd xnu-source\\\\n\\\\n        echo \\"=== Creating minimal availability.pl for _symbol_aliasing.h ===\\\\\\\"\\\\n\\\\n        sudo mkdir -p /usr/local/libexec\\\\n\\\\n        python3 ../xnu/patches/create_minimal_availability_pl.py > /tmp/availability.pl\\\\n\\\\n        sudo cp /tmp/availability.pl /usr/local/libexec/availability.pl\\\\n\\\\n        sudo chmod +x /usr/local/libexec/availability.pl\\\\n\\\\n        echo \\"Created minimal availability.pl at /usr/local/libexec/availability.pl\\\"\\\\n\\\\n        # Verify it works\\\\n\\\\n        /usr/local/libexec/availability.pl --ios | head -5\\\\n\\\\n        /usr/local/libexec/availability.pl --macosx | head -5\\\\n\\\\n        \\\\n\'\\n    - name: Patch make_symbol_aliasing.sh for availability.pl fallback\\n      run: \'cd xnu-source\\\\n\\\\n        echo \\"=== Patching make_symbol_aliasing.sh for availability.pl fallback ===\\\\\\\\\\\\\\\\"\\\\\\\\\\\\\\\\n\\\\\\\\\\\\\\\\n        python3 ../xnu/patches/patch_availability_fallback.py\\\\\\\\\\\\\\\\n\\\\\\\\\\\\\\\\n        echo \\\\\\\\\\\\\\\"Patched successfully\\\\\\\\\\\\\\\"\\\\\\\\\\\\\\\\n\\\\\\\\n\\\'\\n    - name: Install xnu headers\\n      run: \'cd xnu-source\\\\n\\\\n        echo \\\\\\\\\\\"=== Installing XNU headers ===\\\\\\\\\\\\\\\"\\\\\\\\\\\\\\\\n\\\\\\\\\\\\\\\\n        make installhdrs -j8 SDKROOT=iphoneos ARCH_CONFIGS="ARM64" MACHINE_CONFIGS="M30LTE" OBJROOT="$PWD/BUILD/obj" SYMROOT="$PWD/BUILD/sym" DSTROOT="$PWD/fakeroot" FAKEROOT_DIR="$PWD/fakeroot" KDKROOT="/Library/Developer/KDKs" TIGHTBEAMC="" RC_DARWIN_KERNEL_VERSION="22.6.0" MEMORY_SIZE="${MEMORY_SIZE}" SYSCTL_HW_PHYSICALCPU="${SYSCTL_PHYSICALCPU}" SYSCTL_HW_LOGICALCPU="${SYSCTL_LOGICALCPU}" KERNEL_BUILDS_IN_PARALLEL=1 2>&1 | tail -20\\\\\\\\\\\\\\\\n\\\\\\\\\\\\\\\\n        \'\\n    - name: Pre-build IORPC patch for DriverKit\\n      run: \'cd xnu-source\\\\n\\\\n        echo \\\\\\\\\\\\\\\"=== Pre-build IORPC patch for DriverKit ===\\\\\\\\\\\\\\\"\\\\\\\\\\\\\\\\n\\\\\\\\\\\\\\\\n        python3 ../xnu/patches/patch_all_iorpc.py\\\\\\\\\\\\\\\\n\\\\\\\\\\\\\\\\n        echo \\\\\\\\\\\\\\\"Patched successfully\\\\\\\\\\\\\\\"\\\\\\\\\\\\\\\\n\\\\\\\\n\\\'\\n    - name: Patch SETUP/config/Makefile for VPATH\\n      run: \'cd xnu-source\\\\n\\\\n        echo \\\\\\\\\\\\\\\"=== Patching SETUP/config/Makefile for VPATH ===\\\\\\\\\\\\\\\"\\\\\\\\\\\\\\\\n\\\\\\\\\\\\\\\\n        python3 ../xnu/patches/patch_setup_config_vpath.py\\\\\\\\\\\\\\\\n\\\\\\\\\\\\\\\\n        echo \\\\\\\\\\\\\\\"Patched successfully\\\\\\\\\\\\\\\"\\\\\\\\\\\\\\\\n\\\\\\\\n\\\'\\n    - name: Fix SETUP tool include paths\\n      run: \'cd xnu-source\\\\n\\\\n        echo \\\\\\\\\\\\\\\"=== Fixing SETUP tool include paths ===\\\\\\\\\\\\\\\"\\\\\\\\\\\\\\\\n\\\\\\\\\\\\\\\\n        SDKROOT_PATH=$(xcrun --sdk iphoneos --show-sdk-path)\\\\\\\\\\\\\\\\\n\\\\\\\\\\\\\\\\n        echo \\\\\\\\\\\\\\\"SDKROOT_PATH=$SDKROOT_PATH\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n\\\\\\\\\\\\\\\\n        export SDKROOT_PATH\\\\\\\\\\\\\\\\n\\\\\\\\\\\\\\\\n        python3 ../xnu/patches/fix_setup_tool_includes.py\\\\\\\\\\\\\\\\n\\\\\\\\\\\\\\\\n        echo \\\\\\\\\\\\\\\"Patched successfully\\\\\\\\\\\\\\\"\\\\\\\\\\\\\\\\n\\\\\\\\n\\\'\\n    - name: Fix makedefs paths in build directory\\n      run: \'cd xnu-source\\\\n\\\\n        python3 ../xnu/fix_makedefs.py BUILD/obj\\\\n\\\\n        \\\\\\\\\\\\\\\\n        # Verify the changes\\\\\\\\\\\\\\\\n\\\\\\\\\\\\\\\\n        grep -r \\\"/makedefs\\\" BUILD/obj --include=\\\"Makefile\\\" --include=\\\"*.mk\\\" --include=\\\"*.mak\\\" | head -5 || echo \\\"No more /makedefs references found in build directory\\\"\\\\\\\\\\\\\\\\n\\\\\\\\\\\\\\\\n        \\\\\\\\\\\\\\\\n    - name: Build XNU kernel\\\\\\\\n      id: build_kernel\\\\\\\\n      run: \\\"cd xnu-source\\\\\\\\\\\\\\\\n\\\\\\\\\\\\\\\\n      SDKROOT=iphoneos \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      HOST_SDKROOT=macosx \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      HOST_OS_VERSION=26.0 \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      TARGET_CONFIGS=\\\\\\\"DEVELOPMENT ARM64 M30LTE\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      CURRENT_KERNEL_CONFIG=DEVELOPMENT \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      CURRENT_ARCH_CONFIG=ARM64 \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      CURRENT_MACHINE_CONFIG=M30LTE \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      CURRENT_MACHINE_CONFIG_LC=m30lte \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      OBJROOT=\\\\\\"$PWD/BUILD/obj\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      SYMROOT=\\\\\\"$PWD/BUILD/sym\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      DSTROOT=\\\\\\\"$PWD/fakeroot\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      FAKEROOT_DIR=\\\\\\\"$PWD/fakeroot\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      KDKROOT=\\\\\\\"/Library/Developer/KDKs\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      TIGHTBEAMC=\\\\\\\"\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      RC_DARWIN_KERNEL_VERSION=\\\\\\\"22.6.0\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      MEMORY_SIZE=\\\\\\\"${MEMORY_SIZE}\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      SYSCTL_HW_PHYSICALCPU=\\\\\\\"${SYSCTL_PHYSICALCPU}\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      SYSCTL_HW_LOGICALCPU=\\\\\\\"${SYSCTL_LOGICALCPU}\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      KERNEL_BUILDS_IN_PARALLEL=1 \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      BUILD_WERROR=0 BUILD_LTO=0 CONCISE=0 \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      LOGCOLORS=y \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      DRIVERKIT=0 \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      SETUP_SUBDIRS=\\\\\\\"\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      MACH_KERNEL_PRIVATE=1 \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      RC_NONARCH_CFLAGS=\\\\\\\"-DKERNEL -DMACH_KERNEL_PRIVATE -DKERNEL_PRIVATE -DXNU_KERNEL_PRIVATE -DPRIVATE\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n      2>&1 | tee /tmp/xnu-build.log\\\\\\\\\\\\\\\\nBUILD_EXIT=${PIPESTATUS[0]}\\\\\\\\\\\\\\\\\necho \\\\\\\\\\\\\\\"make exit code: $BUILD_EXIT\\\\\\\\\\\\\\\"\\\\\\\\\\\\\\\\necho \\\\\\\\\\\\\\\"=== Errors in build log ===\\\\\\\\\\\\\\\\"\\\\\\\\\\\\\\\\ngrep -iE \\\\\\\\\\\\\\\"error:|error |make: \\\\\\\\\\\\\\\\\\*\\\\\\\\\\\\\\\\\\*\\\\\\\\\\\\\\\\*|No rule|syntax error|undefined reference|missing separator|command not found|ld:|symbol|library not found|collect2\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\" /tmp/xnu-build.log | head -50 || echo \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"No errors found in log\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"\\\\\\\\\\\\\\\\necho \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"=== Last 1000 lines of build log ===\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"\\\\\\\\\\\\\\\\ntail -1000 /tmp/xnu-build.log\\\\\\\\\\\\\\\\necho \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"=== Kernel artifacts ===\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\nfind BUILD/obj -name \\\\\\\\\\\\\\\"kernel.*\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\" -type f 2>/dev/null | head -10\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\nfind BUILD/obj/DEVELOPMENT_ARM64_M30LTE -maxdepth 3 \\( -name \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"kernel.development.m30lte\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\" -o -name \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"mach_kernel\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\" \\) 2>/dev/null | head -10\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\necho \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"BUILD_EXIT=$BUILD_EXIT\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\" >> $GITHUB_OUTPUT\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\nexit $BUILD_EXIT\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n\\"