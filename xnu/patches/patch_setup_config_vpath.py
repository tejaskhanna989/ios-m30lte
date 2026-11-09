#!/usr/bin/env python3
"""Patch SETUP/config/Makefile to add VPATH at the very beginning for source file discovery."""
import sys
import re

with open('SETUP/config/Makefile', 'r') as f:
    content = f.read()

# Add VPATH at the very beginning, before any includes
vpath_lines = '''# VPATH to find source files in the source directory
VPATH = $(SOURCE)

'''
# Insert at the very beginning
new_content = vpath_lines + content

with open('SETUP/config/Makefile', 'w') as f:
    f.write(new_content)

print("Patched SETUP/config/Makefile with VPATH at the very beginning")

# Verify
with open('SETUP/config/Makefile', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[:10]):
        print(f"  {i+1}: {line}")