#!/usr/bin/env python3
"""Add explicit DRIVERKIT=0 export to build command."""
import yaml
import sys

with open('.github/workflows/xnu.yml', 'r') as f:
    workflow = yaml.safe_load(f)

steps = workflow['jobs']['build']['steps']

# Find the "Build XNU kernel" step index
build_kernel_idx = None
for i, step in enumerate(steps):
    if step.get('name') == 'Build XNU kernel':
        build_kernel_idx = i
        break

if build_kernel_idx is None:
    print("ERROR: Could not find 'Build XNU kernel' step")
    sys.exit(1)

# Get the current run command
run_cmd = steps[build_kernel_idx]['run']

# Find the make command - it's split across lines in YAML
# Search for "make -e VERBOSE=YES" without the backslashes
if 'make -e VERBOSE=YES' in run_cmd:
    run_cmd = run_cmd.replace('make -e VERBOSE=YES', 'export DRIVERKIT=0\nmake -e VERBOSE=YES')
    steps[build_kernel_idx]['run'] = run_cmd
    print("Added explicit export DRIVERKIT=0 before make command")
else:
    print("ERROR: Could not find 'make -e VERBOSE=YES' in run_cmd")
    sys.exit(1)

with open('.github/workflows/xnu.yml', 'w') as f:
    yaml.dump(workflow, f, sort_keys=False, default_style='')

print("Updated Build XNU kernel step to export DRIVERKIT=0")