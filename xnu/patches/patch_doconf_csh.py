#!/usr/bin/env python3
"""Patch doconf.csh to fix argument parsing for flags that take arguments."""
import os
import re

with open('SETUP/config/doconf', 'r') as f:
    content = f.read()

# Use regex to fix each case that takes an argument by adding an extra shift
# The pattern: set VAR="$argv[2]" followed by shift then breaksw
# We need to add an extra shift after the first shift

patterns = [
    (r'(set MACHINE=\$argv\[2\"]\s+shift\s+breaksw)', r'set MACHINE="$argv[2]"\n    shift\n    shift\n    breaksw'),
    (r'(set SOC_CONFIG=\$argv\[2\"]\s+shift\s+breaksw)', r'set SOC_CONFIG="$argv[2]"\n    shift\n    shift\n    breaksw'),
    (r'(set PLATFORM=\$argv\[2\"]\s+shift\s+breaksw)', r'set PLATFORM="$argv[2]"\n    shift\n    shift\n    breaksw'),
    (r'(set OBJDIR=\$argv\[2\"]\s+shift\s+breaksw)', r'set OBJDIR="$argv[2]"\n    shift\n    shift\n    breaksw'),
    (r'(set SOURCEDIR=\$argv\[2\"]\s+shift\s+breaksw)', r'set SOURCEDIR="$argv[2]"\n    shift\n    shift\n    breaksw'),
    (r'(set MASTER_CONF_DIR=\$argv\[2\"]\s+shift\s+breaksw)', r'set MASTER_CONF_DIR="$argv[2]"\n    shift\n    shift\n    breaksw'),
]

for pattern, replacement in patterns:
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        print(f"Patched: {pattern}")
    else:
        print(f"WARNING: Pattern not found: {pattern}")

# Initialize MASTER_CPU to prevent "Undefined variable" error
# Find where variables are unset and add MASTER_CPU initialization
if 'unset MASTER_CPU' not in content:
    # Add after the other unsets - find 'unset PLATFORM' and add after it
    content = content.replace('unset PLATFORM', 'unset PLATFORM\nunset MASTER_CPU')
    print("Added MASTER_CPU initialization")

with open('SETUP/config/doconf', 'w') as f:
    f.write(content)

print("Done patching doconf.csh")
