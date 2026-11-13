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
    # Check if this line is a set VAR="$argv[2]" line
    if 'set ' in line and '="$argv[2]"' in line:
        # Look ahead to find the next 'shift' followed by 'breaksw'
        # There might be intermediate lines (like if/else blocks)
        j = i + 1
        shift_found = False
        while j < len(lines) and j < i + 20:  # Look ahead up to 20 lines
            if 'shift' in lines[j] and 'breaksw' not in lines[j]:
                shift_found = True
                break
            j += 1
        if shift_found:
            # Found the pattern - add extra shift after the first shift
            print(f"Patching line {i+1}: {line.strip()}")
            new_lines.append(line)
            # Add all lines up to and including the first shift
            k = i + 1
            while k <= j:
                new_lines.append(lines[k])
                k += 1
            # Add extra shift
            new_lines.append(lines[j])
            # Add remaining lines
            i = j + 1
            continue
    new_lines.append(line)
    i += 1

content = ''.join(new_lines)

# Initialize MASTER_CPU to prevent "Undefined variable" error
content = content.replace('unset PLATFORM', 'unset PLATFORM\nunset MASTER_CPU')
content = content.replace('unset SOC_CONFIG', 'unset SOC_CONFIG\nunset MASTER_CPU')

with open('SETUP/config/doconf', 'w') as f:
    f.write(content)

print("Done patching doconf.csh")
