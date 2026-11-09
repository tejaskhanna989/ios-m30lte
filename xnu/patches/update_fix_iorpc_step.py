#!/usr/bin/env python3
"""Update the Fix DriverKit IORPC step to use Python script for patching iokit/Makefile."""
import yaml

with open('.github/workflows/xnu.yml', 'r') as f:
    workflow = yaml.safe_load(f)

steps = workflow['jobs']['build']['steps']

# Find the "Fix DriverKit IORPC for Xcode 26" step index
fix_iorpc_idx = None
for i, step in enumerate(steps):
    if step.get('name') == 'Fix DriverKit IORPC for Xcode 26':
        fix_iorpc_idx = i
        break

if fix_iorpc_idx is None:
    print("ERROR: Could not find 'Fix DriverKit IORPC for Xcode 26' step")
    sys.exit(1)

# Update the step to use Python script for patching iokit/Makefile
steps[fix_iorpc_idx]['run'] = '''cd xnu-source
echo "=== Patching DriverKit IORPC for Xcode 26 compatibility ==="
if [ -f iokit/DriverKit/IORPC.h ]; then
  echo "Patching IORPC.h to add kernelContent field..."
  python3 ../xnu/patches/patch_iorpc.py
else
  echo "IORPC.h not found, skipping"
fi
grep -n "kernelContent" iokit/DriverKit/IORPC.h 2>/dev/null | head -5 || echo "kernelContent not found in IORPC.h"

echo "=== Patching iokit/Makefile to skip DriverKit when DRIVERKIT=0 ==="
python3 ../xnu/patches/patch_iokit_makefile.py'''

import sys
with open('.github/workflows/xnu.yml', 'w') as f:
    yaml.dump(workflow, f, sort_keys=False, default_style='')

print("Updated Fix DriverKit IORPC step to use Python script for patching iokit/Makefile")