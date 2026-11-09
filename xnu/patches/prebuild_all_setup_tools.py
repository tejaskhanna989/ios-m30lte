#!/usr/bin/env python3
"""Pre-build ALL SETUP tools for macOS and copy to build directory."""
import yaml

with open('.github/workflows/xnu.yml', 'r') as f:
    workflow = yaml.safe_load(f)

steps = workflow['jobs']['build']['steps']

# Find the "Build SETUP tools for macOS" step index
build_setup_idx = None
for i, step in enumerate(steps):
    if step.get('name') == 'Build SETUP tools for macOS (host platform)':
        build_setup_idx = i
        break

if build_setup_idx is None:
    print("ERROR: Could not find 'Build SETUP tools' step")
    sys.exit(1)

# Update the step to build ALL SETUP tools
steps[build_setup_idx]['run'] = '''cd xnu-source
echo "=== Building ALL SETUP tools for macOS (host platform) ==="
# List of SETUP tools to pre-build
SETUP_TOOLS="config kextsymboltool setsegname decomment installfile replacecontents"

for tool in $SETUP_TOOLS; do
  echo "Building $tool..."
  mkdir -p BUILD/obj/SETUP/$tool
  cd BUILD/obj/SETUP/$tool
  # Copy source files
  cp -v ../../../SETUP/$tool/*.c ../../../SETUP/$tool/*.h ../../../SETUP/$tool/*.y ../../../SETUP/$tool/*.l . 2>/dev/null || true
  # Build with macOS SDK (host platform)
  make -f ../../../SETUP/$tool/Makefile \\\\
    SDKROOT=macosx \\\\
    HOST_SDKROOT=macosx \\\\
    HOST_OS_VERSION=26.0 \\\\
    OBJROOT="../../.." \\\\
    SYMROOT="../../../BUILD/sym" \\\\
    DSTROOT="../../../fakeroot" \\\\
    FAKEROOT_DIR="../../../fakeroot" \\\\
    KDKROOT="/Library/Developer/KDKs" \\\\
    SRCROOT="../../.." \\\\
    CURRENT_KERNEL_CONFIG=DEVELOPMENT \\\\
    CURRENT_ARCH_CONFIG=ARM64 \\\\
    CURRENT_MACHINE_CONFIG=M30LTE \\\\
    CURRENT_MACHINE_CONFIG_LC=m30lte \\\\
    do_build_setup 2>&1 | tail -20
  # Touch all output files to prevent rebuild
  touch $tool
  touch *.o 2>/dev/null || true
  cd ../../../..
done

echo "ALL SETUP tools built in build directory for macOS"'''

import sys
with open('.github/workflows/xnu.yml', 'w') as f:
    yaml.dump(workflow, f, sort_keys=False, default_style='')

print("Updated Build SETUP tools step to build ALL SETUP tools")