#!/usr/bin/env python3
"""
Switch darwin-xnu-build's XNU KERNEL compile to a genuine iOS target.

Target selection in xnu-8796.141.3 is driven ONLY by SDKROOT:
  SDKROOT=iphoneos -> PLATFORM=iPhoneOS (SDK platform path, MakeInc.cmd:144-151)
                   -> XNU_TARGET_OS_IOS + -miphoneos-version-min + -Wl,-ios_version_min
                   (MakeInc.def:91-93)

Scope (all narrowly scoped; no global SDK modification):
  1. XNU kernel make + JSONDB make: SDKROOT=iphoneos
  2. libfirehose_kernel (linked into kernel): -sdk iphoneos, ARCHS already arm64
     after patch_build_sh.py, so its LC_BUILD_VERSION platform matches the kernel.
  3. libfirehose xcconfig uses -nostdinc with a restricted HEADER_SEARCH_PATHS;
     the KDK-installed mach/arm/vm_types.h needs <Availability.h> from the SDK
     usr/include, which is not in that list. Append the macOS SDK usr/include
     path to HEADER_SEARCH_PATHS for this target only (a controlled compatibility
     include path; no SDK files modified or overwritten).

The KDK force-load in MakeInc.def applies only to T6000/T8101/VMAPPLE, not
M30LTE, so no iOS KDK is required.
"""
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text()

# --- 1. XNU kernel make invocations -----------------------------------------
kernel_make = 'make install -j8 VERBOSE=YES "${CTF_TOOL_OVERRIDES[@]}" SDKROOT=macosx TARGET_CONFIGS='
assert text.count(kernel_make) == 1, 'kernel make line not uniquely found'
text = text.replace(kernel_make,
                    'make install -j8 VERBOSE=YES "${CTF_TOOL_OVERRIDES[@]}" SDKROOT=iphoneos TARGET_CONFIGS=')

jsondb_make = 'make SDKROOT=macosx TARGET_CONFIGS="$KERNEL_CONFIG $ARCH_CONFIG $MACHINE_CONFIG" LOGCOLORS=y BUILD_WERROR=0 BUILD_LTO=0 BUILD_JSON_COMPILATION_DATABASE=1'
assert text.count(jsondb_make) == 1, 'jsondb make line not uniquely found'
text = text.replace(jsondb_make,
                    'make SDKROOT=iphoneos TARGET_CONFIGS="$KERNEL_CONFIG $ARCH_CONFIG $MACHINE_CONFIG" LOGCOLORS=y BUILD_WERROR=0 BUILD_LTO=0 BUILD_JSON_COMPILATION_DATABASE=1')

# --- 2. libfirehose target platform -----------------------------------------
libfh = 'xcodebuild install -target libfirehose_kernel -sdk macosx'
assert text.count(libfh) == 1, 'libfirehose_kernel xcodebuild line not found'
text = text.replace(libfh,
                    'xcodebuild install -target libfirehose_kernel -sdk iphoneos')

# --- 3. Controlled compatibility include path for <Availability.h> ----------
# Insert AFTER build.sh's existing xcconfig seds (which redirect Kernel.framework
# and usr/local/include to FAKEROOT_DIR), so append the macOS SDK usr/include to
# HEADER_SEARCH_PATHS. macOS SDK Availability.h is Apple's public SDK header;
# it defines only availability macros and does not alter iOS target selection
# (target comes from SDKROOT/-miphoneos-version-min, not this header).
anchor = ('        sed -i \'\' \'s|$(SDKROOT)/usr/local/include|$(FAKEROOT_DIR)/usr/local/include|g\' '
          '"${SRCROOT}/xcodeconfig/libfirehose_kernel.xcconfig"\n')
assert text.count(anchor) == 1, 'libfirehose xcconfig sed anchor not found'
compat = (
    '        # iOS target: fakeroot KDK headers include <Availability.h>; the\n'
    '        # libfirehose xcconfig uses -nostdinc, so add the SDK usr/include.\n'
    '        IOS_SDK=$(xcrun -sdk iphoneos --show-sdk-path)\n'
    '        sed -i \'\' "s|HEADER_SEARCH_PATHS = \\(.*\\)$|HEADER_SEARCH_PATHS = \\1 $IOS_SDK/usr/include|" '
    '"${SRCROOT}/xcodeconfig/libfirehose_kernel.xcconfig"\n'
)
text = text.replace(anchor, anchor + compat)

path.write_text(text)
print('iOS target: kernel/jsondb -> SDKROOT=iphoneos; libfirehose -sdk iphoneos; '
      'Availability.h via SDK usr/include path (no SDK files modified)')
