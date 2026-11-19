#!/usr/bin/env python3
"""
Switch darwin-xnu-build's XNU KERNEL compile to a genuine iOS target.

Target selection in xnu-8796.141.3 is driven ONLY by SDKROOT:
  SDKROOT=iphoneos -> PLATFORM=iPhoneOS (from SDK platform path)
                   -> XNU_TARGET_OS_IOS + -miphoneos-version-min + -Wl,-ios_version_min
  (verified in makedefs/MakeInc.cmd:144-151 and MakeInc.def:91-93)

Scope: change ONLY the two XNU kernel `make` invocations:
  * the JSON-compilation-database make (JSONDB mode)
  * the real `make install` kernel build
Leave host-side `make installhdrs` and `xnu_libraries` on macosx: those feed
other host tooling and are not part of the linked kernel's target selection.

The KDK force-load in MakeInc.def applies only to T6000/T8101/VMAPPLE, not
M30LTE, so no iOS KDK is required.
"""
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text()

# The real kernel build make invocation (unique: "make install -j8 VERBOSE=YES" + CTF overrides)
kernel_make = 'make install -j8 VERBOSE=YES "${CTF_TOOL_OVERRIDES[@]}" SDKROOT=macosx TARGET_CONFIGS='
assert text.count(kernel_make) == 1, 'kernel make line not uniquely found'
text = text.replace(kernel_make,
                    'make install -j8 VERBOSE=YES "${CTF_TOOL_OVERRIDES[@]}" SDKROOT=iphoneos TARGET_CONFIGS=')

# The JSON compilation database make (JSONDB mode) — same kernel target
jsondb_make = 'make SDKROOT=macosx TARGET_CONFIGS="$KERNEL_CONFIG $ARCH_CONFIG $MACHINE_CONFIG" LOGCOLORS=y BUILD_WERROR=0 BUILD_LTO=0 BUILD_JSON_COMPILATION_DATABASE=1'
assert text.count(jsondb_make) == 1, 'jsondb make line not uniquely found'
text = text.replace(jsondb_make,
                    'make SDKROOT=iphoneos TARGET_CONFIGS="$KERNEL_CONFIG $ARCH_CONFIG $MACHINE_CONFIG" LOGCOLORS=y BUILD_WERROR=0 BUILD_LTO=0 BUILD_JSON_COMPILATION_DATABASE=1')

path.write_text(text)
print('iOS target: kernel make + jsondb make -> SDKROOT=iphoneos (XNU_TARGET_OS_IOS)')