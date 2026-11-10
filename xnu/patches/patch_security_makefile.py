#!/usr/bin/env python3
"""Patch security/Makefile to add kernel source includes and kernel private definitions."""
import sys

with open('security/Makefile', 'r') as f:
    content = f.read()

# 1. Add kernel source include paths before COMP_SUBDIRS
# The file has:
# COMP_SUBDIRS = conf
# 
# include $(MakeInc_rule)
# include $(MakeInc_dir)
# 
# We need to add INCFLAGS before COMP_SUBDIRS

old_comp_subdirs = 'COMP_SUBDIRS = conf\n\ninclude $(MakeInc_rule)\ninclude $(MakeInc_dir)'
new_comp_subdirs = '''#
# Kernel private include paths for security module
# Must come FIRST to ensure kernel-private headers are found before EXPORT_HDRS
#
INCFLAGS = -I$(SRCROOT)/bsd \\
	-I$(SRCROOT)/osfmk \\
	-I$(SRCROOT)/libkern \\
	-I$(SRCROOT)/iokit \\
	-I$(SRCROOT)/security

COMP_SUBDIRS = conf

include $(MakeInc_rule)
include $(MakeInc_dir)'''

if old_comp_subdirs in content:
    content = content.replace(old_comp_subdirs, new_comp_subdirs)
    print("Replaced COMP_SUBDIRS pattern")
else:
    print("ERROR: Could not find COMP_SUBDIRS pattern")
    # Print the end of the file to debug
    lines = content.split('\n')
    for i, line in enumerate(lines[-20:]):
        print(f"  {len(lines)-20+i+1}: {line}")
    sys.exit(1)

# 2. Add kernel private definitions to CFLAGS
# The security Makefile doesn't have CFLAGS, so we need to add it
# Add after the includes
old_include_dir = 'include $(MakeInc_rule)\ninclude $(MakeInc_dir)'
new_include_dir = '''include $(MakeInc_rule)
include $(MakeInc_dir)

CFLAGS+= -include meta_features.h -DBSD_KERNEL_PRIVATE -DMACH_KERNEL_PRIVATE -DKERNEL_PRIVATE -DKERNEL -DXNU_KERNEL_PRIVATE -DPRIVATE'''

if old_include_dir in content:
    content = content.replace(old_include_dir, new_include_dir)
    print("Added CFLAGS after includes")
else:
    print("ERROR: Could not find include pattern")
    sys.exit(1)

with open('security/Makefile', 'w') as f:
    f.write(content)

print("Patched security/Makefile with kernel source includes and kernel private definitions")

# Verify
with open('security/Makefile', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[:70]):
        print(f"  {i+1}: {line}")