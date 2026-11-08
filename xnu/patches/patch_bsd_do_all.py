#!/usr/bin/env python3
"""Patch bsd/conf/Makefile do_all target to propagate SRCROOT and SETUP to sub-makes."""
import sys

with open('bsd/conf/Makefile', 'r') as f:
    lines = f.readlines()

# Find the do_all target and insert SRCROOT/SETUP after OBJPATH line
in_do_all = False
patched = False
new_lines = []

for i, line in enumerate(lines):
    new_lines.append(line)
    
    # Detect start of do_all target
    if line.strip().startswith('do_all:') and '$(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile' in line:
        in_do_all = True
        continue
    
    # Detect end of do_all target (next target or include)
    if in_do_all and (line.strip().startswith('do_build_all') or line.strip().startswith('include ')):
        in_do_all = False
        continue
    
    # Inside do_all target, look for OBJPATH line
    if in_do_all and 'OBJPATH=${OBJPATH}' in line and line.rstrip().endswith('\\'):
        # Insert SRCROOT and SETUP after this line
        indent = line[:len(line) - len(line.lstrip())]
        new_lines.append(indent + 'SRCROOT=${SRCROOT}\t\t\t\t\t\\\n')
        new_lines.append(indent + 'SETUP=${SRCROOT}/SETUP\t\t\t\t\t\\\n')
        print(f"Inserted SRCROOT/SETUP after line {i}: {line.rstrip()}")
        patched = True

if not patched:
    print("Could not find OBJPATH line in do_all target!")
    # Debug: print the do_all area
    for i, line in enumerate(lines):
        if 'do_all:' in line:
            print("=== Found do_all at line", i, "===")
            for j in range(i, min(i+30, len(lines))):
                print(f"  {j}: {repr(lines[j])}")
            break
    sys.exit(1)

new_content = ''.join(new_lines)

with open('bsd/conf/Makefile', 'w') as f:
    f.write(new_content)
print("Patched bsd/conf/Makefile successfully!")

# Verify the patch
with open('bsd/conf/Makefile', 'r') as f:
    content = f.read()

if 'SRCROOT=${SRCROOT}' in content and 'SETUP=${SRCROOT}/SETUP' in content:
    print("Patched bsd/conf/Makefile successfully!")
    idx = content.find('do_all')
    if idx >= 0:
        print("=== Patched do_all target ===")
        print(content[idx:idx+800])
else:
    print("WARNING: SRCROOT/SETUP not found in patched content")
    idx = content.find('do_all')
    if idx >= 0:
        print(content[idx:idx+800])
    sys.exit(1)