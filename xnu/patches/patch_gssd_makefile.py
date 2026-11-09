#!/usr/bin/env python3
"""Patch osfmk/gssd/Makefile to add VPATH for source file discovery."""
import sys

with open('osfmk/gssd/Makefile', 'r') as f:
    content = f.read()

# Add VPATH at the very beginning of the file, before any includes
vpath_lines = '''# VPATH to find source files in the source directory
VPATH = $(SOURCE)

'''

new_content = vpath_lines + content

with open('osfmk/gssd/Makefile', 'w') as f:
    f.write(new_content)

print("Patched osfmk/gssd/Makefile with VPATH at the very beginning")

# Verify
with open('osfmk/gssd/Makefile', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[:10]):
        print(f"  {i+1}: {line}")