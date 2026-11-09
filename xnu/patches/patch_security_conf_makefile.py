#!/usr/bin/env python3
"""Patch security/conf/Makefile.template to add kernel source include paths before EXPORT_HDRS."""
import sys

with open('security/conf/Makefile.template', 'r') as f:
    content = f.read()

# Find the INCFLAGS_MAKEFILE line and add kernel source directories
# The current line is: INCFLAGS_MAKEFILE= -I$(SOURCE)/..
# We need to add kernel source directories so they come before EXPORT_HDRS

old_line = 'INCFLAGS_MAKEFILE= -I$(SOURCE)/..'
new_lines = '''INCFLAGS_MAKEFILE= -I$(SOURCE)/.. \\
	-I$(SRCROOT)/bsd \\
	-I$(SRCROOT)/osfmk \\
	-I$(SRCROOT)/libkern \\
	-I$(SRCROOT)/iokit'''

if old_line not in content:
    print("ERROR: Could not find INCFLAGS_MAKEFILE line")
    sys.exit(1)

content = content.replace(old_line, new_lines)

with open('security/conf/Makefile.template', 'w') as f:
    f.write(content)

print("Patched security/conf/Makefile.template with kernel source include paths")

# Verify
with open('security/conf/Makefile.template', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[:30]):
        print(f"  {i+1}: {line}")