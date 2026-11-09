#!/usr/bin/env python3
"""Patch SETUP/config/Makefile to add VPATH at the beginning for source file discovery."""
import sys
import re

with open('SETUP/config/Makefile', 'r') as f:
    content = f.read()

# Add VPATH right after the includes, before any rules
# Find the line after the last include
lines = content.split('\n')
insert_idx = -1
for i, line in enumerate(lines):
    if line.strip().startswith('include $(MakeInc_dir)'):
        insert_idx = i + 1
        break

if insert_idx == -1:
    print("ERROR: Could not find include $(MakeInc_dir) line")
    sys.exit(1)

# Insert VPATH after the includes
vpath_lines = [
    '',
    '# VPATH to find source files in the source directory',
    'VPATH = $(SOURCE)',
    ''
]

new_lines = lines[:insert_idx] + vpath_lines + lines[insert_idx:]
new_content = '\n'.join(new_lines)

with open('SETUP/config/Makefile', 'w') as f:
    f.write(new_content)

print("Patched SETUP/config/Makefile with VPATH at the beginning")

# Verify
with open('SETUP/config/Makefile', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[:30]):
        if 'VPATH' in line or 'include' in line:
            print(f"  {i+1}: {line}")