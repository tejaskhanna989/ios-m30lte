#!/usr/bin/env python3
"""Patch security/conf/Makefile.template to add kernel private definitions and source includes."""
import sys

with open('security/conf/Makefile.template', 'r') as f:
    content = f.read()

# 1. Add kernel source include paths to INCFLAGS_MAKEFILE
old_incflags = 'INCFLAGS_MAKEFILE= -I$(SOURCE)/..'
new_incflags = '''INCFLAGS_MAKEFILE= -I$(SOURCE)/.. \\
	-I$(SRCROOT)/bsd \\
	-I$(SRCROOT)/osfmk \\
	-I$(SRCROOT)/libkern \\
	-I$(SRCROOT)/iokit \\
	-I$(SRCROOT)/security'''

if old_incflags not in content:
    print("ERROR: Could not find INCFLAGS_MAKEFILE line")
    sys.exit(1)

content = content.replace(old_incflags, new_incflags)

# 2. Add kernel private definitions to CFLAGS
old_cflags = 'CFLAGS+= -include meta_features.h -DBSD_KERNEL_PRIVATE'
new_cflags = '''CFLAGS+= -include meta_features.h -DBSD_KERNEL_PRIVATE -DMACH_KERNEL_PRIVATE -DKERNEL_PRIVATE -DKERNEL -DXNU_KERNEL_PRIVATE -DPRIVATE

# Use override to prevent environment CFLAGS from overriding (MAKEFLAGS=-e)
override CFLAGS+= -DMACH_KERNEL_PRIVATE -DKERNEL_PRIVATE -DKERNEL -DXNU_KERNEL_PRIVATE -DPRIVATE'''

if old_cflags not in content:
    print("ERROR: Could not find CFLAGS line with BSD_KERNEL_PRIVATE")
    sys.exit(1)

content = content.replace(old_cflags, new_cflags)

with open('security/conf/Makefile.template', 'w') as f:
    f.write(content)

print("Patched security/conf/Makefile.template with kernel source includes and kernel private definitions")

# Verify
with open('security/conf/Makefile.template', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[:50]):
        print(f"  {i+1}: {line}")