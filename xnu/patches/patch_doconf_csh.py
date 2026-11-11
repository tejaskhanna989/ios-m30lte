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

cases_to_fix = [
    ('-cpu', 'set MACHINE="$argv[2]"'),
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

with open('SETUP/config/doconf', 'w') as f:
    f.write(content)

print("Done")