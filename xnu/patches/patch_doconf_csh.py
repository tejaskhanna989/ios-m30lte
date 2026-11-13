#!/usr/bin/env python3
"""Patch doconf.csh to fix argument parsing for flags that take arguments."""
import os

with open('SETUP/config/doconf', 'r') as f:
    content = f.read()

# Fix each case that takes an argument by adding an extra shift
# The pattern is: set VAR="$argv[2]" followed by shift then breaksw
# We need to change "shift" to "shift; shift" for these cases

# Actual patterns from the doconf.csh source:
fixes = [
    # -cpu case
    ('set MACHINE="$argv[2]"\n    shift\n    breaksw', 'set MACHINE="$argv[2]"\n    shift\n    shift\n    breaksw'),
    # -soc case
    ('set SOC_CONFIG="$argv[2]"\n    shift\n    breaksw', 'set SOC_CONFIG="$argv[2]"\n    shift\n    shift\n    breaksw'),
    # -platform case
    ('set PLATFORM="$argv[2]"\n    shift\n    breaksw', 'set PLATFORM="$argv[2]"\n    shift\n    shift\n    breaksw'),
    # -d case
    ('set OBJDIR="$argv[2]"\n    shift\n    breaksw', 'set OBJDIR="$argv[2]"\n    shift\n    shift\n    breaksw'),
    # -s case
    ('set SOURCEDIR="$argv[2]"\n    shift\n    breaksw', 'set SOURCEDIR="$argv[2]"\n    shift\n    shift\n    breaksw'),
    # -m case
    ('set MASTER_CONF_DIR="$argv[2]"\n    shift\n    breaksw', 'set MASTER_CONF_DIR="$argv[2]"\n    shift\n    shift\n    breaksw'),
]

for old, new in fixes:
    if old in content:
        content = content.replace(old, new)
        print(f"Patched: {old.split(chr(10))[0]}")
    else:
        print(f"WARNING: Pattern not found: {old.split(chr(10))[0]}")
        # Try with 2-space indentation
        old2 = old.replace('    ', '  ')
        new2 = new.replace('    ', '  ')
        if old2 in content:
            content = content.replace(old2, new2)
            print(f"Patched (alt indent): {old2.split(chr(10))[0]}")
        else:
            print(f"  Still not found with alt indent")

# Initialize MASTER_CPU to prevent "Undefined variable" error
init_pattern = 'unset MASTER_CPU'
if init_pattern not in content:
    # Add after the other unsets
    old_unset = 'unset PLATFORM'
    new_unset = 'unset PLATFORM\nunset MASTER_CPU'
    if old_unset in content:
        content = content.replace(old_unset, new_unset)
        print("Added MASTER_CPU initialization")

with open('SETUP/config/doconf', 'w') as f:
    f.write(content)

print("Done patching doconf.csh")
