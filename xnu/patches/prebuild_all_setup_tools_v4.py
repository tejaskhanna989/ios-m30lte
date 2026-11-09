#!/usr/bin/env python3
"""Pre-build ALL SETUP tools for macOS - use absolute SRCROOT path."""
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

# Update the step to use absolute paths
steps[build_setup_idx]['run'] = '''cd xnu-source
echo "=== Building ALL SETUP tools for macOS (host platform) ==="
# List of SETUP tools to pre-build
SETUP_TOOLS="config kextsymboltool setsegname decomment installfile replacecontents"

# Use SRCROOT for absolute paths
SRCROOT="$PWD"
echo "SRCROOT=$SRCROOT"

for tool in $SETUP_TOOLS; do
  echo "Building $tool..."
  mkdir -p BUILD/obj/SETUP/$tool
  cd BUILD/obj/SETUP/$tool
  # Copy source files AND Makefile using absolute path
  echo "Copying source files for $tool from $SRCROOT/SETUP/$tool..."
  cp -v "$SRCROOT/SETUP/$tool"/*.c "$SRCROOT/SETUP/$tool"/*.h "$SRCROOT/SETUP/$tool"/*.y "$SRCROOT/SETUP/$tool"/*.l "$SRCROOT/SETUP/$tool/Makefile" . 2>&1 || echo "Copy failed for $tool"
  ls -la
  # Build with macOS SDK (host platform)
  if [ -f "Makefile" ]; then
    echo "Makefile found, building $tool..."
    make -f Makefile \\\\
      SDKROOT=macosx \\\\
      HOST_SDKROOT=macosx \\\\
      HOST_OS_VERSION=26.0 \\\\
      OBJROOT="$SRCROOT/BUILD/obj" \\\\
      SYMROOT="$SRCROOT/BUILD/sym" \\\\
      DSTROOT="$SRCROOT/fakeroot" \\\\
      FAKEROOT_DIR="$SRCROOT/fakeroot" \\\\
      KDKROOT="/Library/Developer/KDKs" \\\\
      SRCROOT="$SRCROOT" \\\\
      CURRENT_KERNEL_CONFIG=DEVELOPMENT \\\\
      CURRENT_ARCH_CONFIG=ARM64 \\\\
      CURRENT_MACHINE_CONFIG=M30LTE \\\\
      CURRENT_MACHINE_CONFIG_LC=m30lte \\\\
      do_build_setup 2>&1 | tail -20
    # Touch all output files to prevent rebuild
    touch $tool
    touch *.o 2>/dev/null || true
  else
    echo "ERROR: Makefile not found for $tool"
    exit 1
  fi
  cd "$SRCROOT"
done

echo "ALL SETUP tools built in build directory for macOS"'''

import sys
with open('.github/workflows/xnu.yml', 'w') as f:
    yaml.dump(workflow, f, sort_keys=False, default_style='')

print("Updated Build SETUP tools step to use absolute paths")