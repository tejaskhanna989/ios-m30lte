#!/usr/bin/env python3
"""Patch osfmk/mach/Makefile to add VPATH for source files."""
import sys

with open('osfmk/mach/Makefile', 'r') as f:
    content = f.read()

# Find the line after the last include
lines = content.split('\n')
insert_idx = -1
for i, line in enumerate(lines):
    if line.strip() == 'include $(MakeInc_dir)':
        insert_idx = i + 1
        break

if insert_idx == -1:
    # Try alternative pattern
    for i, line in enumerate(lines):
        if 'include $(MakeInc_dir)' in line:
            insert_idx = i + 1
            break

if insert_idx == -1:
    print("ERROR: Could not find 'include $(MakeInc_dir)' line")
    print("First 30 lines of Makefile:")
    for i, line in enumerate(lines[:30]):
        print(f"  {i+1}: {line}")
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

with open('osfmk/mach/Makefile', 'w') as f:
    f.write(new_content)

print("Patched osfmk/mach/Makefile with VPATH")

# Verify
with open('osfmk/mach/Makefile', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[:30]):
        if 'VPATH' in line or 'include' in line:
            print(f"  {i+1}: {line}")