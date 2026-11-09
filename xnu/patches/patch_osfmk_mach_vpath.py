#!/usr/bin/env python3
"""Patch osfmk/mach/Makefile to add VPATH at the very beginning for source file discovery."""
import sys

with open('osfmk/mach/Makefile', 'r') as f:
    content = f.read()

# Add VPATH at the very beginning of the file, before any includes
vpath_lines = '''# VPATH to find source files in the source directory
VPATH = $(SOURCE)

'''

new_content = vpath_lines + content

with open('osfmk/mach/Makefile', 'w') as f:
    f.write(new_content)

print("Patched osfmk/mach/Makefile with VPATH at the very beginning")

# Verify
with open('osfmk/mach/Makefile', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[:10]):
        print(f"  {i+1}: {line}")