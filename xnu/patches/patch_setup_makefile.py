#!/usr/bin/env python3
"""Patch SETUP/Makefile to skip host tools during kernel build."""
import sys
import os

# Accept optional path argument, default to SETUP/Makefile
if len(sys.argv) > 1:
    path = sys.argv[1]
else:
    path = 'SETUP/Makefile'

if not os.path.exists(path):
    print(f"{path} not found!")
    sys.exit(1)

with open(path, 'r') as f:
    content = f.read()

# The original SETUP_SUBDIRS includes host tools
# We want to skip them when building for ARM64 (target kernel build)
# Host tools are already built separately for macOS (x86_64)
# Check RC_ARCHS for arm64 (target) vs x86_64 (host)

old_subdirs = """SETUP_SUBDIRS =		\\
	config		\\
	kextsymboltool	\\
	setsegname	\\
	decomment	\\
	installfile	\\
	replacecontents"""

new_subdirs = """ifeq ($(filter arm64,$(RC_ARCHS)),arm64)
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
    print(f"Patched {path} to skip host tools during kernel build")
else:
    print(f"Could not find SETUP_SUBDIRS pattern in {path}")
    print("Current content:")
    print(content[:2000])
    sys.exit(1)

with open(path, 'w') as f:
    f.write(content)

print(f"Patched {path}")
print("New content:")
with open(path, 'r') as f:
    print(f.read())
