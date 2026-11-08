#!/usr/bin/env python3
"""Patch SETUP/config/Makefile to add VPATH for source files - robust version."""
import sys
import re

with open('SETUP/config/Makefile', 'r') as f:
    content = f.read()

# Find the CFLAGS line and add VPATH after it
# The CFLAGS line: CFLAGS = -isysroot $(HOST_SDKROOT) -mmacosx-version-min=$(HOST_OS_VERSION) -g -O0 -I$(SOURCE) -I.
# In regex, we need to escape $ (only at end), ( and )
pattern = r'(^CFLAGS = -isysroot \$\(HOST_SDKROOT\) -mmacosx-version-min=\$\(HOST_OS_VERSION\) -g -O0 -I\$\(SOURCE\) -I\.\n)'
replacement = r'\1VPATH = $(SOURCE)\n'

new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

if new_content == content:
    # Try a more flexible pattern - match start of CFLAGS line
    pattern2 = r'(^CFLAGS = -isysroot)'
    replacement2 = r'VPATH = $(SOURCE)\n\1'
    new_content = re.sub(pattern2, replacement2, content, flags=re.MULTILINE)
    
    if new_content == content:
        print("ERROR: Could not find CFLAGS line to patch")
        print("First 30 lines of Makefile:")
        for i, line in enumerate(content.split('\n')[:30]):
            print(f"  {i+1}: {line}")
        sys.exit(1)
    else:
        print("Patched with flexible pattern (start of CFLAGS)")

with open('SETUP/config/Makefile', 'w') as f:
    f.write(new_content)

print("Patched SETUP/config/Makefile with VPATH")
# Verify
with open('SETUP/config/Makefile', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')):
        if 'VPATH' in line or 'CFLAGS' in line:
            print(f"  {i+1}: {line}")