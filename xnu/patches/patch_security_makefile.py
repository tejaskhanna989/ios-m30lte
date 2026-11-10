#!/usr/bin/env python3
"""Patch security/Makefile to add kernel source includes and kernel private definitions."""
import sys

with open('security/Makefile', 'r') as f:
    content = f.read()

print("=== Original content ===")
for i, line in enumerate(content.split('\n')[:60]):
    print(f"  {i+1}: {repr(line)}")
print("=== End of content ===")

lines = content.split('\n')

# 1. Find COMP_SUBDIRS = conf line
comp_subdirs_idx = -1
for i, line in enumerate(lines):
    if line.strip() == 'COMP_SUBDIRS = conf':
        comp_subdirs_idx = i
        break

if comp_subdirs_idx == -1:
    print("ERROR: Could not find COMP_SUBDIRS = conf")
    sys.exit(1)

# Insert INCFLAGS before COMP_SUBDIRS = conf
incflags_lines = [
    '#',
    '# Kernel private include paths for security module',
    '# Must come FIRST to ensure kernel-private headers are found before EXPORT_HDRS',
    '#',
    'INCFLAGS = -I$(SRCROOT)/bsd \\',
    '	-I$(SRCROOT)/osfmk \\',
    '	-I$(SRCROOT)/libkern \\',
    '	-I$(SRCROOT)/iokit \\',
    '	-I$(SRCROOT)/security',
    ''
]

# Insert before COMP_SUBDIRS = conf
for i, line in enumerate([
    '#',
    '# Kernel private include paths for security module',
    '# Must come FIRST to ensure kernel-private headers are found before EXPORT_HDRS',
    '#',
    'INCFLAGS = -I$(SRCROOT)/bsd \\',
    '	-I$(SRCROOT)/osfmk \\',
    '	-I$(SRCROOT)/libkern \\',
    '	-I$(SRCROOT)/iokit \\',
    '	-I$(SRCROOT)/security',
    ''
]):
    lines.insert(comp_subdirs_idx + i, line)

# 2. Add kernel private definitions to CFLAGS after the last include
# Find the last include line
last_include_idx = -1
for i, line in enumerate(lines):
    if line.strip().startswith('include $(MakeInc_'):
        last_include_idx = i

if last_include_idx == -1:
    print("ERROR: Could not find include lines")
    sys.exit(1)

# Insert CFLAGS after the last include
cflags_lines = [
    '',
    'CFLAGS+= -include meta_features.h -DBSD_KERNEL_PRIVATE -DMACH_KERNEL_PRIVATE -DKERNEL_PRIVATE -DKERNEL -DXNU_KERNEL_PRIVATE -DPRIVATE',
    ''
]

for i, line in enumerate(['', 'CFLAGS+= -include meta_features.h -DBSD_KERNEL_PRIVATE -DMACH_KERNEL_PRIVATE -DKERNEL_PRIVATE -DKERNEL -DXNU_KERNEL_PRIVATE -DPRIVATE', '']):
    lines.insert(last_include_idx + 1 + i, line)

# Join and write
new_content = '\n'.join(lines)

with open('security/Makefile', 'w') as f:
    f.write(new_content)

print("Patched security/Makefile with kernel source includes and kernel private definitions")

# Verify
with open('security/Makefile', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[:70]):
        print(f"  {i+1}: {line}")