#!/usr/bin/env python3
"""Add step to patch osfmk/mach/Makefile for VPATH."""
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

# New step to patch osfmk/mach/Makefile for VPATH
new_step = {
    'name': 'Patch osfmk/mach/Makefile for VPATH',
    'run': '''cd xnu-source
echo "=== Patching osfmk/mach/Makefile for VPATH ==="
python3 ../xnu/patches/patch_osfmk_mach_vpath.py
echo "Patched successfully"'''
}

# Insert after "Fix DriverKit IORPC for Xcode 26" step
steps.insert(fix_iorpc_idx + 1, new_step)

with open('.github/workflows/xnu.yml', 'w') as f:
    yaml.dump(workflow, f, sort_keys=False, default_style='')

print("Added osfmk/mach VPATH patch step")