#!/usr/bin/env python3
"""Patch doconf.csh to fix argument parsing for flags that take arguments."""
import os
import re

with open('SETUP/config/doconf', 'r') as f:
    content = f.read()

print("=== Patching doconf.csh ===")

# Use regex with flexible whitespace to find and replace
# Pattern: set VAR="$argv[2]" followed by shift then breaksw
# We need to add an extra shift

# Match the pattern with flexible whitespace (spaces or tabs)
patterns = [
    (r'(^\s+set MACHINE=\$argv\[2\]"\s+\n\s+shift\s+\n\s+breaksw)', '    set MACHINE="$argv[2]"\n    shift\n    shift\n    breaksw'),
    (r'(^\s+set SOC_CONFIG=\$argv\[2\]"\s+\n\s+shift\s+\n\s+breaksw)', '    set SOC_CONFIG="$argv[2]"\n    shift\n    shift\n    breaksw'),
    (r'(^\s+set PLATFORM=\$argv\[2\]"\s+\n\s+shift\s+\n\s+breaksw)', '    set PLATFORM="$argv[2]"\n    shift\n    shift\n    breaksw'),
    (r'(^\s+set OBJDIR=\$argv\[2\]"\s+\n\s+shift\s+\n\s+breaksw)', '    set OBJDIR="$argv[2]"\n    shift\n    shift\n    breaksw'),
    (r'(^\s+set SOURCEDIR=\$argv\[2\]"\s+\n\s+shift\s+\n\s+breaksw)', '    set SOURCEDIR="$argv[2]"\n    shift\n    shift\n    breaksw'),
    (r'(^\s+set MASTER_CONF_DIR=\$argv\[2\]"\s+\n\s+shift\s+\n\s+breaksw)', '    set MASTER_CONF_DIR="$argv[2]"\n    shift\n    shift\n    breaksw'),
]

for pattern, replacement in patterns:
    matches = list(re.finditer(pattern, content, re.MULTILINE))
    if matches:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        print(f"Patched: {pattern}")
    else:
        print(f"WARNING: Pattern not found: {pattern}")

# Initialize MASTER_CPU to prevent "Undefined variable" error
if 'unset MASTER_CPU' not in content:
    if 'unset PLATFORM' in content:
        content = content.replace('unset PLATFORM', 'unset PLATFORM\nunset MASTER_CPU')
        print("Added MASTER_CPU initialization")
    else:
        print("WARNING: Could not find 'unset PLATFORM' to add MASTER_CPU init")

with open('SETUP/config/doconf', 'w') as f:
    f.write(content)

print("Done patching doconf.csh")
