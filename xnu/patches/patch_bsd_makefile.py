#!/usr/bin/env python3
"""Patch bsd/Makefile to propagate SRCROOT and SETUP to sub-makes."""
import sys

with open('bsd/Makefile', 'r') as f:
    content = f.read()

# Find the do_all target and add SRCROOT and SETUP after OBJPATH
# We need to find the exact line with OBJPATH and add two lines after it

# Look for the pattern: OBJPATH=${OBJPATH} followed by a newline and then build_all
# The structure is:
# do_all: $(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile
# 	$(_v)${MAKE} \
# 		-C $(TARGET)/$(CURRENT_KERNEL_CONFIG)			\
# 		-f $(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile		\
# 		CURRENT_KERNEL_CONFIG=${CURRENT_KERNEL_CONFIG}		\
# 		CURRENT_ARCH_CONFIG=${CURRENT_ARCH_CONFIG}		\
# 		CURRENT_MACHINE_CONFIG=${CURRENT_MACHINE_CONFIG}	\
# 		SOURCE=$(subst conf/,,$(SOURCE))			\
# 		TARGET=${TARGET}					\
# 		OBJPATH=${OBJPATH}					\
# 		build_all

# We need to insert after: OBJPATH=${OBJPATH}					\
# The two new lines:
# 		SRCROOT=${SRCROOT}					\
# 		SETUP=${SRCROOT}/SETUP					\

# Simple approach: find the OBJPATH line and insert after it
lines = content.split('\n')
new_lines = []
i = 0
while i < len(lines):
    new_lines.append(lines[i])
    # Check if this line contains OBJPATH and is in the do_all context
    if 'OBJPATH=${OBJPATH}' in lines[i] and i + 1 < len(lines):
        # Check if next line is the build_all line (or continuation)
        next_line = lines[i + 1] if i + 1 < len(lines) else ''
        if 'build_all' in next_line or '\\' in lines[i]:
            # Insert the two new lines after this one
            indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
            new_lines.append(indent + 'SRCROOT=${SRCROOT}					\\')
            new_lines.append(indent + 'SETUP=${SRCROOT}/SETUP					\\')
    i += 1

new_content = '\n'.join(new_lines)

if new_content != content:
    with open('bsd/Makefile', 'w') as f:
        f.write(new_content)
    print("Patched bsd/Makefile successfully!")
else:
    print("Could not find OBJPATH line in do_all target!")
    # Debug: show what we have around do_all
    idx = content.find('do_all:')
    if idx >= 0:
        print(content[idx:idx+500])
    sys.exit(1)

# Verify the patch
with open('bsd/Makefile', 'r') as f:
    content = f.read()

if 'SRCROOT=${SRCROOT}' in content and 'SETUP=${SRCROOT}/SETUP' in content:
    print("Patched bsd/Makefile successfully!")
    # Verify the patch
    idx = content.find('do_all:')
    if idx >= 0:
        print("=== Patched do_all target ===")
        print(content[idx:idx+400])
else:
    print("WARNING: SRCROOT/SETUP not found in patched content")
    idx = content.find('do_all:')
    if idx >= 0:
        print(content[idx:idx+500])
    sys.exit(1)