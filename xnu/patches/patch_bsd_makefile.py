#!/usr/bin/env python3
"""Patch bsd/Makefile to propagate SRCROOT and SETUP to sub-makes."""
import sys

with open('bsd/Makefile', 'r') as f:
    content = f.read()

# Find and modify the do_all target to add SRCROOT and SETUP after OBJPATH
lines = content.split('\n')
new_lines = []
i = 0
in_do_all = False
while i < len(lines):
    new_lines.append(lines[i])
    # Detect start of do_all target
    if lines[i].strip().startswith('do_all:') and '$(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile' in lines[i]:
        in_do_all = True
    # Detect end of do_all target (next target or blank line after build_all)
    if in_do_all and 'build_all' in lines[i] and not lines[i].strip().endswith('\\'):
        in_do_all = False
    # Inside do_all target, look for OBJPATH line and insert after it
    if in_do_all and 'OBJPATH=${OBJPATH}' in lines[i]:
        indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
        new_lines.append(indent + 'SRCROOT=${SRCROOT}					\\')
        new_lines.append(indent + 'SETUP=${SRCROOT}/SETUP					\\')
    i += 1

new_content = '\n'.join(new_lines)

if new_content != content:
    with open('bsd/Makefile', 'w') as f:
        f.write(new_content)
    print("Patched bsd/Makefile successfully!")
else:
    print("Could not find OBJPATH line in do_all target!")
    idx = content.find('do_all:')
    if idx >= 0:
        print(content[idx:idx+500])
    sys.exit(1)

# Verify the patch
with open('bsd/Makefile', 'r') as f:
    content = f.read()

if 'SRCROOT=${SRCROOT}' in content and 'SETUP=${SRCROOT}/SETUP' in content:
    print("Patched bsd/Makefile successfully!")
    idx = content.find('do_all:')
    if idx >= 0:
        print("=== Patched do_all target ===")
        print(content[idx:idx+400])
else:
    print("WARNING: SRCROOT/SETUP not found in patched content")
    idx = content.find('do_all:')
    if idx >= 0:
        print(content[idx:idx+500])
    sys.exit(1)