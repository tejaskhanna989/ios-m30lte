#!/usr/bin/env python3
"""Patch security/Makefile to add kernel source includes at the VERY beginning."""
import sys

with open('security/Makefile', 'r') as f:
    content = f.read()

# Add kernel source include paths at the VERY beginning of the file, right after the header
# This ensures kernel source paths come before EXPORT_HDRS paths
header_end = '''include $(MakeInc_dir)

INCDIR=$(SDKHEADERSROOT)/usr/local/include'''

new_content = '''include $(MakeInc_dir)

#
# Kernel private include paths for security module
# Must come FIRST to ensure kernel-private headers are found before EXPORT_HDRS
#
INCFLAGS = -I$(SRCROOT)/bsd \\
	-I$(SRCROOT)/osfmk \\
	-I$(SRCROOT)/libkern \\
	-I$(SRCROOT)/iokit \\
	-I$(SRCROOT)/security \\
	-I$(SOURCE)/..

INCDIR=$(SDKHEADERSROOT)/usr/local/include'''

if header_end not in content:
    print("ERROR: Could not find header_end pattern")
    sys.exit(1)

content = content.replace(header_end, new_content)

# Also add kernel private definitions to CFLAGS
old_cflags = 'CFLAGS+= -include meta_features.h -DBSD_KERNEL_PRIVATE'
new_cflags = '''CFLAGS+= -include meta_features.h -DBSD_KERNEL_PRIVATE -DMACH_KERNEL_PRIVATE -DKERNEL_PRIVATE -DKERNEL -DXNU_KERNEL_PRIVATE -DPRIVATE'''

if old_cflags not in content:
    print("ERROR: Could not find CFLAGS line with BSD_KERNEL_PRIVATE")
    sys.exit(1)

content = content.replace(old_cflags, new_cflags)

with open('security/Makefile', 'w') as f:
    f.write(content)

print("Patched security/Makefile with kernel source includes at the beginning and kernel private definitions")

# Verify
with open('security/Makefile', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[:50]):
        print(f"  {i+1}: {line}")