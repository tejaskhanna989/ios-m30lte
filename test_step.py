#!/usr/bin/env python3

import yaml
import sys

# Read the workflow file
with open('.github/workflows/xnu.yml', 'r') as f:
    data = yaml.safe_load(f)

# Print the job structure
job = data['jobs']['build']
print('Job steps:')
for i, step in enumerate(job['steps']):
    print(f'{i}: {step.get("name", "Unnamed step")}')

# Check if our step is properly defined
our_step = None
for step in job['steps']:
    if 'Create installfile replacement' in step.get('name', ''):
        our_step = step
        break

print(f'\nOur step found: {our_step is not None}')
if our_step:
    print('Step keys:', list(our_step.keys()))
    print('Step run content:', repr(our_step.get('run', '')[:100]))
    print('Step run content length:', len(our_step.get('run', '')))

# Check for any potential issues
print('\nChecking for potential issues...')
for i, step in enumerate(job['steps']):
    if 'run' in step:
        run_content = step['run']
        if len(run_content) > 0 and run_content[-1] != '\n':
            print(f'Warning: Step {i} ({step.get("name", "Unnamed")}) run content does not end with newline')
        if '\r' in run_content:
            print(f'Warning: Step {i} ({step.get("name", "Unnamed")}) run content contains Windows line endings')