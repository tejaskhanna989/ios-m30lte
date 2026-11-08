#!/usr/bin/env python3
"""Patch SETUP/config/Makefile to add VPATH at the end of the file."""
import sys

with open('SETUP/config/Makefile', 'r') as f:
    content = f.read()

# Append VPATH at the end of the file
if 'VPATH = $(SOURCE)' not in content:
    content = content.rstrip() + '\n\nVPATH = $(SOURCE)\n'
    with open('SETUP/config/Makefile', 'w') as f:
        f.write(content)
    print("Appended VPATH to SETUP/config/Makefile")
else:
    print("VPATH already present")

# Verify
with open('SETUP/config/Makefile', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[-5:]):
        print(f"  {line}")