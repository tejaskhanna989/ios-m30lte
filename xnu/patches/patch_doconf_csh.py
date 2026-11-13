#!/usr/bin/env python3
"""Patch doconf.csh to fix argument parsing for flags that take arguments.

The bug: when processing -cpu arm64, the script only shifts once (removing -cpu),
leaving arm64 in $argv. The while loop then breaks because arm64 doesn't start
with '-'. All subsequent flag values remain in $argv, causing SYS to be wrong.

Fix: shift twice for each flag that takes an argument (flag + value).
"""
import os
import re

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
    # Use regex to find the pattern with flexible whitespace
    # Pattern: set_line followed by shift then breaksw
    pattern = re.escape(set_line) + r'\s+shift\s+breaksw'
    replacement = set_line + '\n    shift\n    shift\n    breaksw'
    
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        print(f"Patched doconf: {flag} - added extra shift (regex)")
    else:
        print(f"WARNING: Could not find pattern for {flag} with regex")
        # Try to find just the set_line
        if set_line in content:
            print(f"  But set_line '{set_line}' found in content")
            # Show context around it
            idx = content.index(set_line)
            print(f"  Context: ...{content[max(0,idx-50):idx+100]}...")
        else:
            print(f"  set_line '{set_line}' NOT found in content")

with open('SETUP/config/doconf', 'w') as f:
    f.write(content)

print("Done")