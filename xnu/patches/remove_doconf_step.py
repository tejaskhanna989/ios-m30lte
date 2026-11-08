#!/usr/bin/env python3
"""Remove the Generate kernel configs step from workflow."""

import yaml

with open('.github/workflows/xnu.yml', 'r') as f:
    workflow = yaml.safe_load(f)

# Find and remove the "Generate kernel configs" step
steps = workflow['jobs']['build']['steps']
new_steps = []
for step in steps:
    if step.get('name') == 'Generate kernel configs (run doconf for all components)':
        print("Removing Generate kernel configs step")
        continue
    new_steps.append(step)

workflow['jobs']['build']['steps'] = new_steps

with open('.github/workflows/xnu.yml', 'w') as f:
    yaml.dump(workflow, f, sort_keys=False)

print("Removed Generate kernel configs step")