#!/usr/bin/env python3
"""Patch osfmk/mach/arm/Makefile to add VPATH at the very beginning."""
import sys
import os

target_dir = sys.argv[1] if len(sys.argv) > 1 else 'osfmk/mach/arm'
makefile_path = os.path.join(target_dir, 'Makefile')

with open(makefile_path, 'r') as f:
    content = f.read()

# Add VPATH at the very beginning of the file, before any includes
vpath_lines = '''# VPATH to find source files in the source directory
VPATH = $(SOURCE)/../../arm

'''

# Remove the existing VPATH line if present
content = content.replace('VPATH := $(VPATH):$(SOURCE)/../../arm\n', '')

new_content = vpath_lines + content

with open(makefile_path, 'w') as f:
    f.write(new_content)

print(f"Patched {makefile_path} with VPATH at the very beginning")

# Verify
with open(makefile_path, 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[:15]):
        print(f"  {i+1}: {line}")