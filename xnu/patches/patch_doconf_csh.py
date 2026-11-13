#!/usr/bin/env python3
"""Patch doconf.csh to fix argument parsing for flags that take arguments.

The bug: when processing -cpu arm64, the script only shifts once (removing -cpu),
leaving arm64 in $argv. The while loop then breaks because arm64 doesn't start
with '-'. All subsequent flag values remain in $argv, causing SYS to be wrong.

Fix: shift twice for each flag that takes an argument (flag + value).
"""
import os

with open('SETUP/config/doconf', 'r') as f:
    content = f.read()

# Fix each case that takes an argument by adding an extra shift
# The pattern is: case "-X": ... set VAR="$argv[2]" ... shift; breaksw
# We need to change "shift" to "shift; shift" for these cases

# Note: The script uses MASTER_CPU not MACHINE for -cpu flag
cases_to_fix = [
    ('-cpu', 'set MASTER_CPU="$argv[2]"'),
    ('-soc', 'set SOC_CONFIG="$argv[2]"'),
    ('-platform', 'set PLATFORM="$argv[2]"'),
    ('-d', 'set OBJDIR="$argv[2]"'),
    ('-s', 'set SOURCEDIR="$argv[2]"'),
    ('-m', 'set MASTER_CONF_DIR="$argv[2]"'),
]

for flag, set_line in cases_to_fix:
    # Find the pattern: set VAR="$argv[2]" followed by shift
    old = f'{set_line}\n    shift\n    breaksw'
    new = f'{set_line}\n    shift\n    shift\n    breaksw'
    if old in content:
        content = content.replace(old, new)
        print(f"Patched doconf: {flag} - added extra shift")
    else:
        print(f"WARNING: Could not find pattern for {flag}")
        # Try alternative pattern with different spacing
        old2 = f'{set_line}\n  shift\n  breaksw'
        new2 = f'{set_line}\n  shift\n  shift\n  breaksw'
        if old2 in content:
            content = content.replace(old2, new2)
            print(f"Patched doconf (alt spacing): {flag} - added extra shift")
        else:
            print(f"  Could not find alternative pattern either")

with open('SETUP/config/doconf', 'w') as f:
    f.write(content)

print("Done")