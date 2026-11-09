#!/usr/bin/env python3
"""Add step to patch osfmk/gssd/Makefile for VPATH."""
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

# New step to patch osfmk/gssd/Makefile for VPATH
new_step = {
    'name': 'Patch osfmk/gssd/Makefile for VPATH',
    'run': '''cd xnu-source
echo "=== Patching osfmk/gssd/Makefile for VPATH ==="
python3 ../xnu/patches/patch_gssd_makefile.py
echo "Patched successfully"'''
}

# Insert after "Patch osfmk/mach/Makefile for VPATH" step
steps.insert(patch_vpath_idx + 1, new_step)

with open('.github/workflows/xnu.yml', 'w') as f:
    yaml.dump(workflow, f, sort_keys=False, default_style='')

print("Added osfmk/gssd VPATH patch step")