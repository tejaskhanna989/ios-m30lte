#!/usr/bin/env python3
"""Patch SETUP/Makefile to skip host tools during kernel build."""
import sys
import os

path = 'SETUP/Makefile'
if not os.path.exists(path):
    print(f"{path} not found!")
    sys.exit(1)

with open(path, 'r') as f:
    content = f.read()

# The original SETUP_SUBDIRS includes host tools
# We want to skip them when building for iPhoneOS (target)
# Check if we're building for iPhoneOS (target) vs macOS (host)

old_subdirs = """SETUP_SUBDIRS =		\\
	config		\\
	kextsymboltool	\\
	setsegname	\\
	decomment	\\
	installfile	\\
	replacecontents"""

new_subdirs = """ifeq ($(SDKROOT),iphoneos)
SETUP_SUBDIRS = config
else
SETUP_SUBDIRS =		\\
	config		\\
	kextsymboltool	\\
	setsegname	\\
	decomment	\\
	installfile	\\
	replacecontents
endif"""

if old_subdirs in content:
    content = content.replace(old_subdirs, new_subdirs)
    print("Patched SETUP/Makefile to skip host tools during kernel build")
else:
    print("Could not find SETUP_SUBDIRS pattern")
    sys.exit(1)

with open(path, 'w') as f:
    f.write(content)

print("Patched SETUP/Makefile")
