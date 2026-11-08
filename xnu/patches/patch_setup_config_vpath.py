#!/usr/bin/env python3
"""Patch SETUP/config/Makefile to add VPATH for source files."""
import sys

with open('SETUP/config/Makefile', 'r') as f:
    content = f.read()

# Add VPATH after the CFLAGS line
old = 'CFLAGS = -isysroot $(HOST_SDKROOT) -mmacosx-version-min=$(HOST_OS_VERSION) -g -O0 -I$(SOURCE) -I.'
new = 'CFLAGS = -isysroot $(HOST_SDKROOT) -mmacosx-version-min=$(HOST_OS_VERSION) -g -O0 -I$(SOURCE) -I.\nVPATH = $(SOURCE)'

if old in content:
    content = content.replace(old, new)
    with open('SETUP/config/Makefile', 'w') as f:
        f.write(content)
    print("Patched SETUP/config/Makefile with VPATH")
else:
    print("ERROR: Could not find CFLAGS line to patch")
    sys.exit(1)