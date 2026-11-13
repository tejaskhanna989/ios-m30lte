#!/usr/bin/env python3
"""Patch doconf.csh to fix argument parsing for flags that take arguments."""
import os

with open('SETUP/config/doconf', 'r') as f:
    content = f.read()

print("=== Patching doconf.csh ===")

# The actual patterns from the source (4-space indentation)
fixes = [
    # -cpu case
    ('    set MACHINE="$argv[2]"\n    shift\n    breaksw', '    set MACHINE="$argv[2]"\n    shift\n    shift\n    breaksw'),
    # -soc case
    ('    set SOC_CONFIG="$argv[2]"\n    shift\n    breaksw', '    set SOC_CONFIG="$argv[2]"\n    shift\n    shift\n    breaksw'),
    # -platform case
    ('    set PLATFORM="$argv[2]"\n    shift\n    breaksw', '    set PLATFORM="$argv[2]"\n    shift\n    shift\n    breaksw'),
    # -d case
    ('    set OBJDIR="$argv[2]"\n    shift\n    breaksw', '    set OBJDIR="$argv[2]"\n    shift\n    shift\n    breaksw'),
    # -s case
    ('    set SOURCEDIR="$argv[2]"\n    shift\n    breaksw', '    set SOURCEDIR="$argv[2]"\n    shift\n    shift\n    breaksw'),
    # -m case
    ('    set MASTER_CONF_DIR="$argv[2]"\n    shift\n    breaksw', '    set MASTER_CONF_DIR="$argv[2]"\n    shift\n    shift\n    breaksw'),
]

for old, new in fixes:
    if old in content:
        content = content.replace(old, new)
        print(f"Patched: {old.split(chr(10))[0]}")
    else:
        print(f"WARNING: Pattern not found: {old.split(chr(10))[0]}")
        # Try with tab indentation
        old2 = old.replace('    ', '\t')
        new2 = new.replace('    ', '\t')
        if old2 in content:
            content = content.replace(old2, new2)
            print(f"Patched (tab indent): {old2.split(chr(10))[0]}")
        else:
            print(f"  Still not found with tab indent")

# Initialize MASTER_CPU to prevent "Undefined variable" error
if 'unset MASTER_CPU' not in content:
    # Add after the other unsets
    if 'unset PLATFORM' in content:
        content = content.replace('unset PLATFORM', 'unset PLATFORM\nunset MASTER_CPU')
        print("Added MASTER_CPU initialization")
    else:
        print("WARNING: Could not find 'unset PLATFORM' to add MASTER_CPU init")

with open('SETUP/config/doconf', 'w') as f:
    f.write(content)

print("Done patching doconf.csh")
