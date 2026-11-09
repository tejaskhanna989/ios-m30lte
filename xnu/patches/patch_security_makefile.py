#!/usr/bin/env python3
"""Patch security/Makefile to add kernel source includes at the beginning."""
import sys

with open('security/Makefile', 'r') as f:
    content = f.read()

# Add kernel source include paths at the beginning of the file, after the includes
# Find the line with "include $(MakeInc_dir)" and add our includes after it
# But better: add after the includes and before COMP_SUBDIRS

# Find the line with "COMP_SUBDIRS = conf" and add our includes before it
old_comp_subdirs = 'COMP_SUBDIRS = conf'
new_comp_subdirs = '''#
# Kernel private include paths for security module
# Must come before EXPORT_HDRS to ensure kernel-private headers are found
#
INCFLAGS += -I$(SRCROOT)/bsd \\
	-I$(SRCROOT)/osfmk \\
	-I$(SRCROOT)/libkern \\
	-I$(SRCROOT)/iokit \\
	-I$(SRCROOT)/security

COMP_SUBDIRS = conf'''

if old_comp_subdirs not in content:
    print("ERROR: Could not find COMP_SUBDIRS line")
    sys.exit(1)

content = content.replace(old_comp_subdirs, new_comp_subdirs)

# Also add kernel private definitions to CFLAGS for this component
# Find the CFLAGS line or add it
if 'CFLAGS+=' not in content:
    # Add CFLAGS after the includes
    include_makeinc_dir = 'include $(MakeInc_dir)'
    if include_makeinc_dir in content:
        content = content.replace(
            include_makeinc_dir,
            include_makeinc_dir + '\n\nCFLAGS+= -DMACH_KERNEL_PRIVATE -DKERNEL_PRIVATE -DKERNEL -DXNU_KERNEL_PRIVATE -DPRIVATE'
        )
    else:
        print("WARNING: Could not find include $(MakeInc_dir) line")

with open('security/Makefile', 'w') as f:
    f.write(content)

print("Patched security/Makefile with kernel source includes and kernel private definitions")

# Verify
with open('security/Makefile', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[:50]):
        print(f"  {i+1}: {line}")