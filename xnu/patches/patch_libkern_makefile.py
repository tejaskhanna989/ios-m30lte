#!/usr/bin/env python3
"""Patch libkern/libkern/Makefile to add VPATH for source file discovery."""
import sys
import os

# Get target directory from command line argument, default to source
target_dir = sys.argv[1] if len(sys.argv) > 1 else 'libkern/libkern'
makefile_path = os.path.join(target_dir, 'Makefile')

with open(makefile_path, 'r') as f:
    content = f.read()

# Add VPATH at the very beginning of the file, before any includes
vpath_lines = '''# VPATH to find source files in the source directory
VPATH = $(SOURCE)

'''

new_content = vpath_lines + content

with open(makefile_path, 'w') as f:
    f.write(new_content)

print(f"Patched {makefile_path} with VPATH at the very beginning")

# Verify
with open(makefile_path, 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[:10]):
        print(f"  {i+1}: {line}")