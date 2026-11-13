#!/usr/bin/env python3
"""Patch doconf.csh to fix argument parsing for flags that take arguments."""
import os
import re

with open('SETUP/config/doconf', 'r') as f:
    lines = f.readlines()

print("=== Patching doconf.csh (line by line) ===")

# Process line by line
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # Check if this line is a set VAR="$argv[2]" line
    # Look for patterns like: set MACHINE="$argv[2]"
    if 'set ' in line and '="$argv[2]"' in line:
        # Check if next line is shift and line after is breaksw
        if i + 2 < len(lines):
            next_line = lines[i + 1]
            next_next_line = lines[i + 2]
            if 'shift' in next_line and 'breaksw' in next_next_line:
                # Found the pattern - add extra shift
                print(f"Patching line {i+1}: {line.strip()}")
                new_lines.append(line)
                new_lines.append(lines[i + 1])  # first shift
                new_lines.append(lines[i + 1])  # extra shift
                new_lines.append(lines[i + 2])  # breaksw
                i += 3
                continue
    new_lines.append(line)
    i += 1

content = ''.join(new_lines)

# Initialize MASTER_CPU to prevent "Undefined variable" error
content = content.replace('unset PLATFORM', 'unset PLATFORM\nunset MASTER_CPU')

with open('SETUP/config/doconf', 'w') as f:
    f.write(''.join(new_lines))

print("Done patching doconf.csh")
