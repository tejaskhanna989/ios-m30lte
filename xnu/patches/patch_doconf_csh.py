#!/usr/bin/env python3
"""Patch doconf.csh to fix argument parsing for flags that take arguments."""
import os

with open('SETUP/config/doconf', 'r') as f:
    lines = f.readlines()

print("=== Patching doconf.csh (line by line) ===")

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    if 'set ' in line and '="$argv[2]"' in line:
        j = i + 1
        shift_found = False
        while j < len(lines) and j < i + 20:
            if 'shift' in lines[j] and 'breaksw' not in lines[j]:
                shift_found = True
                break
            j += 1
        if shift_found:
            print(f"Patching line {i+1}: {line.strip()}")
            new_lines.append(line)
            k = i + 1
            while k <= j:
                new_lines.append(lines[k])
                k += 1
            new_lines.append(lines[j])
            i = j + 1
            continue
    new_lines.append(line)
    i += 1

content = ''.join(new_lines)

# Remove all unset commands for these variables and initialize them to empty string
# This prevents "Undefined variable" errors when referenced in foreach loops
content = content.replace('unset MASTER_CPU', '')
content = content.replace('unset SOC_CONFIG', '')
content = content.replace('unset PLATFORM', '')
content = content.replace('unset MACHINE', '')
content = content.replace('unset profile', '')

# Add initialization block after the existing variable initializations
# Find a good place to add the initialization
init_block = '''set MASTER_CPU = ""
set SOC_CONFIG = ""
set PLATFORM = ""
set MACHINE = ""
set profile = ""
'''
# Insert after the existing variable initializations
# Find the line with 'set OBJDIR=../BUILD' and insert before it
if 'set OBJDIR=../BUILD' in content:
    content = content.replace('set OBJDIR=../BUILD', 'set MASTER_CPU = ""\nset SOC_CONFIG = ""\nset PLATFORM = ""\nset MACHINE = ""\nset profile = ""\nset OBJDIR=../BUILD')
    print("Added variable initialization block")
else:
    print("WARNING: Could not find 'set OBJDIR=../BUILD' to insert initialization")

with open('SETUP/config/doconf', 'w') as f:
    f.write(content)

print("Done patching doconf.csh")
