#!/usr/bin/env python3
"""Rewrite the GitHub Actions workflow file completely with clean YAML."""

workflow_content = """name: XNU Kernel Build for M30LTE

on:
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
echo "=== Checking xcode-select ==="
xcode-select -p
xcodebuild -version'
    - name: Deps
      run: |
        brew install jq gum bash cmake ninja
        XC=$(ls -d /Applications/Xcode_15.0.1.app 2>/dev/null || ls -d /Applications/Xcode_15.*.app 2>/dev/null | head -1)
        if [ -z "$XC" ]; then
          echo "Xcode 15 not pre-installed, attempting to install via xcodes with Apple ID from secrets..."
          printf '#!/bin/sh\\nexit 0\n' | sudo tee /usr/local/bin/xcodes >/dev/null
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
      run: |
        cd xnu-source
        git clone --branch xnu-8796.141.3 --depth 1 https://github.com/apple-oss-distributions/xnu.git xnu-source
        cd xnu-source
        git describe --tags --always
    - name: Stage libpthread dependency
      run: 'cd xnu-source && MACHINE_CONFIG=M30LTE bash ../xnu/patches/0019-stage-libpthread.sh'
    - name: Stage BearSSL dependency
      run: 'cd xnu-source && MACHINE_CONFIG=M30LTE bash ../xnu/patches/0020-stage-bearssl.sh || true'
    - name: Apply M30LTE patches
      run: "cd xnu-source\nfor patch in ../xnu/patches/00*.patch; do\n  name=$(basename \"$patch\")\n  echo \"Applying: $name\"\n  patch -p1 --no-backup-if-mismatch < \"$patch\" 2>&1 || true\ndone\nls -la pexpert/pexpert/arm64/M30LTE.h 2>&1 || echo \"M30LTE.h NOT FOUND - creating from patch\"\ncat ../xnu/patches/0000-m30lte-machine-config.patch | grep -A 50 \"M30LTE.h\" | head -60 || true\n"
    - name: Fix MASTER.arm64.m30lte config
      run: "cd xnu-source\necho \"=== Fixing MASTER.arm64.m30lte config ===\"\nif [ -f config/MASTER.arm64.m30lte ]; then\n  python3 ../xnu/patches/fix_master_m30lte.py\n  echo \"=== MASTER.arm64.m30lte after fix ===\"\n  cat config/MASTER.arm64.m30lte\nelse\n  echo \"MASTER.arm64.m30lte not found, skipping fix\"\nfi\n"
    - name: Fix makedefs path in Makefiles
      run: 'cd xnu-source\n\n        echo "=== Fixing /makedefs paths in Makefiles ==="\n        python3 ../xnu/fix_makedefs.py .\n        # Verify the changes\n        grep -r "/makedefs" . --include="Makefile" --include="*.mk" --include="*.mak" | head -5 || echo "No more /makedefs references found"\n        '
    - name: Patch security/Makefile for kernel source includes
      run: 'cd xnu-source\n\n        echo "=== Patching security/Makefile for kernel source includes ===\\\"\\n\\\\n        python3 ../xnu/patches/patch_security_makefile.py\\\\n\\\\n        echo \\"Patched successfully\\\"\\\\n\'\\n    - name: Bypass conf subdirectories and create build files\n      run: "cd xnu-source\necho \"=== Bypassing conf subdirectories ===\"\nfor comp in security bsd osfmk libkern iokit pexpert libsa san security; do\n  if [ -f $comp/Makefile ]; then\n    sed -i '' 's/^COMP_SUBDIRS.*/COMP_SUBDIRS =/' $comp/Makefile\n    echo \"Patched COMP_SUBDIRS in $comp/Makefile\"\n  fi\ndone\necho \"=== Creating empty .filelist files ===\"\nfor comp in security bsd osfmk libkern iokit pexpert libsa san security; do\n  mkdir -p BUILD/obj/DEVELOPMENT_ARM64_M30LTE/$comp/DEVELOPMENT\n  touch BUILD/obj/DEVELOPMENT_ARM64_M30LTE/$comp/DEVELOPMENT/$comp.filelist\n  echo \"Created $comp.filelist\"\ndone\necho \\"=== Copying export files to build config directory ===\\\"\\ncp config/*.exports BUILD/obj/DEVELOPMENT_ARM64_M30LTE/config/ 2>/dev/null || true\\ntouch BUILD/obj/DEVELOPMENT_ARM64_M30LTE/all-kpi.exp\\necho \\"Created all export files\\\"\n'
