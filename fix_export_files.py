#!/usr/bin/env python3
"""
Fix CI workflow: Copy export files to each component's DEVELOPMENT directory
"""

import os

workflow_path = '/home/tejas/Projects/m30lte-ios/.github/workflows/xnu.yml'

with open(workflow_path, 'r') as f:
    content = f.read()

# Find the exact step from the workflow file
old_step = '''    - name: Create all export files and filelists for kernel build
      run: "cd xnu-source\necho \"=== Copying all export files to build config directory ===\"\nmkdir -p BUILD/obj/DEVELOPMENT_ARM64_M30LTE/config\ncp config/*.exports BUILD/obj/DEVELOPMENT_ARM64_M30LTE/config/ 2>/dev/null || true\necho \"=== Creating empty .filelist files ===\"\nfor comp in security bsd osfmk libkern iokit pexpert libsa san security; do\n  mkdir -p BUILD/obj/DEVELOPMENT_ARM64_M30LTE/$comp/DEVELOPMENT\n  touch BUILD/obj/DEVELOPMENT_ARM64_M30LTE/$comp/DEVELOPMENT/$comp.filelist\n  echo \"Created $comp.filelist\"\ndone\necho \"=== Creating empty all-kpi.exp ===\"\ntouch BUILD/obj/DEVELOPMENT_ARM64_M30LTE/all-kpi.exp\necho \"Created all-kpi.exp\"\n"'''

# Replace with a step that copies export files to each component's DEVELOPMENT directory
new_step = '''    - name: Copy export files to each component's DEVELOPMENT directory
      run: "cd xnu-source\necho \"=== Copying export files to each component's DEVELOPMENT directory ===\"\n# Copy export files to config directory first\nmkdir -p BUILD/obj/DEVELOPMENT_ARM64_M30LTE/config\ncp config/*.exports BUILD/obj/DEVELOPMENT_ARM64_M30LTE/config/ 2>/dev/null || true\necho \"=== Copying export files to each component's DEVELOPMENT directory ===\"\nfor comp in security bsd osfmk libkern iokit pexpert libsa san security; do\n  mkdir -p BUILD/obj/DEVELOPMENT_ARM64_M30LTE/$comp/DEVELOPMENT\n  # Copy export files to each component's DEVELOPMENT directory\n  if [ -f config/$comp.exports ]; then\n    cp config/$comp.exports BUILD/obj/DEVELOPMENT_ARM64_M30LTE/$comp/DEVELOPMENT/\n    echo \"Copied $comp.exports to $comp/DEVELOPMENT/\"\n  fi\n  # Create empty .filelist for each component\n  touch BUILD/obj/DEVELOPMENT_ARM64_M30LTE/$comp/DEVELOPMENT/$comp.filelist\n  echo \"Created $comp.filelist\"\ndone\necho \"=== Creating empty all-kpi.exp ===\"\ntouch BUILD/obj/DEVELOPMENT_ARM64_M30LTE/all-kpi.exp\necho \"Created all-kpi.exp\"\n"'''

if old_step in content:
    content = content.replace(old_step, new_step, 1)
    with open(workflow_path, 'w') as f:
        f.write(content)
    print('Successfully updated workflow to copy export files to each component\'s DEVELOPMENT directory')
else:
    print('ERROR: Could not find the step to update')
    # Let's try a different approach - find the line number and replace it
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'Create all export files and filelists for kernel build' in line:
            print(f'Found step at line {i+1}')
            # Replace the next few lines (the run command)
            end_idx = i + 1
            while end_idx < len(lines) and not lines[end_idx].strip().startswith('- name:'):
                end_idx += 1
            
            # Replace the entire step
            new_lines = lines[:i] + [new_step] + lines[end_idx:]
            with open(workflow_path, 'w') as f:
                f.write('\n'.join(new_lines))
            print('Successfully updated workflow using line-based approach')
            break