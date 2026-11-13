#!/usr/bin/env python3
"""Patch doconf.csh to fix argument parsing for flags that take arguments.

The bug: when processing -cpu arm64, the script only shifts once (removing -cpu),
leaving arm64 in $argv. The while loop then breaks because arm64 doesn't start
with '-'. All subsequent flag values remain in $argv, causing SYS to be wrong.

Fix: shift twice for each flag that takes an argument (flag + value).
Also initialize MASTER_CPU to prevent "Undefined variable" error.
"""
import os

with open('SETUP/config/doconf', 'r') as f:
    content = f.read()

# Fix each case that takes an argument by adding an extra shift
# The pattern is: set VAR="$argv[2]" followed by shift then breaksw
# We need to change "shift" to "shift; shift" for these cases

# Actual patterns from the doconf.csh source:
fixes = [
    # -cpu case
    ('set MACHINE="$argv[2]"
    shift
    breaksw', 'set MACHINE="$argv[2]"
    shift
    shift
    breaksw'),
    # -soc case
    ('set SOC_CONFIG="$argv[2]"
    shift
    breaksw', 'set SOC_CONFIG="$argv[2]"
    shift
    shift
    breaksw'),
    # -platform case
    ('set PLATFORM="$argv[2]"
    shift
    breaksw', 'set PLATFORM="$argv[2]"
    shift
    shift
    breaksw'),
    # -d case
    ('set OBJDIR="$argv[2]"
    shift
    breaksw', 'set OBJDIR="$argv[2]"
    shift
    shift
    breaksw'),
    # -s case
    ('set SOURCEDIR="$argv[2]"
    shift
    breaksw', 'set SOURCEDIR="$argv[2]"
    shift
    shift
    breaksw'),
    # -m case
    ('set MASTER_CONF_DIR="$argv[2]"
    shift
    breaksw', 'set MASTER_CONF_DIR="$argv[2]"
    shift
    shift
    breaksw'),
]

for old, new in fixes:
    if old in content:
        content = content.replace(old, new)
        print(f"Patched: {old.split(chr(10))[0]}")
    else:
        print(f"WARNING: Pattern not found: {old.split(chr(10))[0]}")
        # Try with different indentation
        old2 = old.replace('    ', '  ')
        new2 = new.replace('    ', '  ')
        if old2 in content:
            content = content.replace(old2, new2)
            print(f"Patched (alt indent): {old2.split(chr(10))[0]}")
        else:
            print(f"  Still not found with alt indent")

# Initialize MASTER_CPU to prevent "Undefined variable" error
# Find where variables are unset and add MASTER_CPU initialization
init_pattern = 'unset MASTER_CPU'
if init_pattern not in content:
    # Add after the other unsets
    old_unset = 'unset PLATFORM'
    new_unset = 'unset PLATFORM
unset MASTER_CPU'
    if old_unset in content:
        content = content.replace(old_unset, new_unset)
        print("Added MASTER_CPU initialization")

with open('SETUP/config/doconf', 'w') as f:
    f.write(content)

print("Done patching doconf.csh")
