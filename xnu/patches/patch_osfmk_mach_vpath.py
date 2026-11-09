#!/usr/bin/env python3
"""Patch osfmk/mach/Makefile to add VPATH for source files."""
import sys

with open('osfmk/mach/Makefile', 'r') as f:
    content = f.read()

# Add VPATH after the MODULEMAPFILES section, before the DATAFILES section
# Find a good place to insert VPATH - after the includes
lines = content.split('\n')
insert_idx = -1
for i, line in enumerate(lines):
    if 'include $(MakeInc_dir)' in line:
        insert_idx = i + 1
        break

if insert_idx == -1:
    print("ERROR: Could not find 'include $(MakeInc_dir)' line")
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