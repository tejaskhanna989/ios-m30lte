#!/usr/bin/env python3
"""Patch security/Makefile to add kernel source includes and kernel private definitions."""
import sys

with open('security/Makefile', 'r') as f:
    content = f.read()

# 1. Add kernel source include paths at the beginning of INCFLAGS
# The file has: include $(MakeInc_dir) followed by INCDIR=...
# We'll add our includes right after the includes

# Find the line with "include $(MakeInc_dir)" and add our includes after it
old_include_dir = 'include $(MakeInc_dir)\n\nINCDIR=$(SDKHEADERSROOT)/usr/local/include'
new_include_dir = '''include $(MakeInc_dir)

#
# Kernel private include paths for security module
# Must come FIRST to ensure kernel-private headers are found before EXPORT_HDRS
#
INCFLAGS = -I$(SRCROOT)/bsd \\
	-I$(SRCROOT)/osfmk \\
	-I$(SRCROOT)/libkern \\
	-I$(SRCROOT)/iokit \\
	-I$(SRCROOT)/security

INCDIR=$(SDKHEADERSROOT)/usr/local/include'''

if old_include_dir not in content:
    # Try alternative pattern
    old_include_dir2 = 'include $(MakeInc_dir)\n\nINCDIR=$(SDKHEADERSROOT)/usr/local/include'
    if old_include_dir2 in content:
        content = content.replace(old_include_dir2, new_include_dir)
    else:
        # Try without newline
        old_include_dir3 = 'include $(MakeInc_dir)\nINCDIR=$(SDKHEADERSROOT)/usr/local/include'
        if old_include_dir3 in content:
            content = content.replace(old_include_dir3, new_include_dir)
        else:
            print("ERROR: Could not find include $(MakeInc_dir) pattern")
            sys.exit(1)
else:
    content = content.replace(old_include_dir, new_include_dir)

# 2. Add kernel private definitions to CFLAGS
old_cflags = 'CFLAGS+= -include meta_features.h -DBSD_KERNEL_PRIVATE'
new_cflags = '''CFLAGS+= -include meta_features.h -DBSD_KERNEL_PRIVATE -DMACH_KERNEL_PRIVATE -DKERNEL_PRIVATE -DKERNEL -DXNU_KERNEL_PRIVATE -DPRIVATE'''

if old_cflags not in content:
    print("ERROR: Could not find CFLAGS line with BSD_KERNEL_PRIVATE")
    sys.exit(1)

content = content.replace(old_cflags, new_cflags)

with open('security/Makefile', 'w') as f:
    f.write(content)

print("Patched security/Makefile with kernel source includes and kernel private definitions")

# Verify
with open('security/Makefile', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[:50]):
        print(f"  {i+1}: {line}")