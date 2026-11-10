#!/usr/bin/env python3
"""Patch security/Makefile to add kernel source includes and kernel private definitions."""
import sys

with open('security/Makefile', 'r') as f:
    content = f.read()

print("=== Original content ===")
print(content[:2000])
print("=== End of content ===")

# 1. Add kernel source include paths at the beginning of INCFLAGS
# Find the right place - after the includes, before COMP_SUBDIRS
# The file has include $(MakeInc_dir) then INCDIR

# First, let's see the exact content around the include
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'include $(MakeInc_dir)' in line:
        print(f"Found include at line {i}: {line}")
    if 'INCDIR=' in line:
        print(f"Found INCDIR at line {i}: {line}")
    if 'COMP_SUBDIRS = conf' in line:
        print(f"Found COMP_SUBDIRS at line {i}: {line}")

# Find the right place to insert - after include $(MakeInc_dir) and before INCDIR
# The file has:
# include $(MakeInc_dir)
# 
# INCDIR=$(SDKHEADERSROOT)/usr/local/include

# We need to insert after include $(MakeInc_dir) and before INCDIR
old_pattern = '''include $(MakeInc_dir)

INCDIR=$(SDKHEADERSROOT)/usr/local/include'''

new_pattern = '''include $(MakeInc_dir)

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

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    print("Replaced include pattern")
else:
    # Try alternative with single newline
    old_pattern2 = 'include $(MakeInc_dir)\nINCDIR=$(SDKHEADERSROOT)/usr/local/include'
    if old_pattern2 in content:
        content = content.replace(old_pattern2, '''include $(MakeInc_dir)

#
# Kernel private include paths for security module
# Must come FIRST to ensure kernel-private headers are found before EXPORT_HDRS
#
INCFLAGS = -I$(SRCROOT)/bsd \\
	-I$(SRCROOT)/osfmk \\
	-I$(SRCROOT)/libkern \\
	-I$(SRCROOT)/iokit \\
	-I$(SRCROOT)/security

INCDIR=$(SDKHEADERSROOT)/usr/local/include''')
        print("Replaced with single newline pattern")
    else:
        print("ERROR: Could not find include pattern")
        # Print the first 50 lines to debug
        for i, line in enumerate(content.split('\n')[:30]):
            print(f"  {i+1}: {line}")
        sys.exit(1)

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
    for i, line in enumerate(content.split('\n')[:60]):
        print(f"  {i+1}: {line}")