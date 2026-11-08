#!/usr/bin/env python3
"""Patch bsd/conf/Makefile to ensure SRCROOT is set early and propagated to sub-makes."""
import sys

with open('bsd/conf/Makefile', 'r') as f:
    lines = f.readlines()

# Patch 1: Add SRCROOT fallback at the VERY TOP of the file (before any includes)
# Find the first non-comment, non-empty line
patched_srcroot = False
patched_do_all = False
new_lines = []

for i, line in enumerate(lines):
    # Add SRCROOT fallback at the very beginning, right after any initial comments
    if not patched_srcroot and i == 0:
        # Add at the very top
        new_lines.append('# Ensure SRCROOT is set early (fallback to environment)\n')
        new_lines.append('ifndef SRCROOT\n')
        new_lines.append('  SRCROOT := $(shell printenv SRCROOT 2>/dev/null)\n')
        new_lines.append('endif\n')
        new_lines.append('export SRCROOT\n\n')
        patched_srcroot = True
        print("Added SRCROOT fallback at top of file")
    
    new_lines.append(line)
    
    # Patch 2: Find do_all target and add SRCROOT/SETUP to sub-make
    if not patched_do_all and line.strip().startswith('do_all:') and '$(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile' in line:
        in_do_all = True
        continue
    
    if not patched_do_all and 'in_do_all' in locals() and in_do_all:
        # Detect end of do_all target
        if line.strip().startswith('do_build_all') or line.strip().startswith('include '):
            in_do_all = False
            continue
        
        # Look for OBJPATH line
        if 'OBJPATH=${OBJPATH}' in line and line.rstrip().endswith('\\'):
            indent = line[:len(line) - len(line.lstrip())]
            new_lines.append(indent + 'SRCROOT=${SRCROOT}\t\t\t\t\t\\\n')
            new_lines.append(indent + 'SETUP=${SRCROOT}/SETUP\t\t\t\t\t\\\n')
            print(f"Inserted SRCROOT/SETUP after OBJPATH line {i}")
            patched_do_all = True

if not patched_srcroot:
    print("WARNING: Could not add SRCROOT fallback at top")
    
if not patched_do_all:
    print("Could not find OBJPATH line in do_all target!")
    sys.exit(1)

new_content = ''.join(new_lines)

with open('bsd/conf/Makefile', 'w') as f:
    f.write(new_content)
print("Patched bsd/conf/Makefile successfully!")

# Verify the patches
with open('bsd/conf/Makefile', 'r') as f:
    content = f.read()

if 'ifndef SRCROOT' in content and 'export SRCROOT' in content:
    print("SRCROOT fallback patch verified!")
    # Show first 20 lines
    print("=== First 20 lines ===")
    print(content[:500])
else:
    print("WARNING: SRCROOT fallback not found in patched content")

if 'SRCROOT=${SRCROOT}' in content and 'SETUP=${SRCROOT}/SETUP' in content:
    print("do_all patch verified!")
    idx = content.find('do_all')
    if idx >= 0:
        print("=== Patched do_all target ===")
        print(content[idx:idx+800])
else:
    print("WARNING: do_all patch not found in patched content")
    idx = content.find('do_all')
    if idx >= 0:
        print(content[idx:idx+800])
    sys.exit(1)