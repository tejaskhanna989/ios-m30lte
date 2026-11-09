#!/usr/bin/env python3
"""Add step to copy .defs files to build directory."""
import yaml

with open('.github/workflows/xnu.yml', 'r') as f:
    workflow = yaml.safe_load(f)

steps = workflow['jobs']['build']['steps']

# Find the "Patch osfmk/mach/Makefile for VPATH" step index
patch_vpath_idx = None
for i, step in enumerate(steps):
    if step.get('name') == 'Patch osfmk/mach/Makefile for VPATH':
        patch_vpath_idx = i
        break

if patch_vpath_idx is None:
    print("ERROR: Could not find 'Patch osfmk/mach/Makefile for VPATH' step")
    sys.exit(1)

# New step to copy .defs files
new_step = {
    'name': 'Copy .defs files to build directory for osfmk/mach',
    'run': '''cd xnu-source
echo "=== Copying .defs files to build directory for osfmk/mach ==="
mkdir -p BUILD/obj/DEVELOPMENT_ARM64_M30LTE/osfmk/mach
cp -v osfmk/mach/*.defs BUILD/obj/DEVELOPMENT_ARM64_M30LTE/osfmk/mach/ 2>/dev/null || true
ls -la BUILD/obj/DEVELOPMENT_ARM64_M30LTE/osfmk/mach/*.defs | head -20
echo "Copied .defs files to build directory"'''
}

import sys
# Insert after "Patch osfmk/mach/Makefile for VPATH" step
steps.insert(patch_vpath_idx + 1, new_step)

with open('.github/workflows/xnu.yml', 'w') as f:
    yaml.dump(workflow, f, sort_keys=False, default_style='')

print("Added copy .defs files step")