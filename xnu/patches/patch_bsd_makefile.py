#!/usr/bin/env python3
"""Patch bsd/Makefile to propagate SRCROOT and SETUP to sub-makes."""
import re
import sys

with open('bsd/Makefile', 'r') as f:
    content = f.read()

# Find and modify the do_all target to add SRCROOT and SETUP
old_do_all = """do_all: $(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile
	$(_v)${MAKE} \\
		-C $(TARGET)/$(CURRENT_KERNEL_CONFIG)			\\
		-f $(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile		\\
		CURRENT_KERNEL_CONFIG=${CURRENT_KERNEL_CONFIG}		\\
		CURRENT_ARCH_CONFIG=${CURRENT_ARCH_CONFIG}		\\
		CURRENT_MACHINE_CONFIG=${CURRENT_MACHINE_CONFIG}	\\
		SOURCE=$(subst conf/,,$(SOURCE))			\\
		TARGET=${TARGET}					\\
		OBJPATH=${OBJPATH}					\\
		build_all"""

new_do_all = """do_all: $(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile
	$(_v)${MAKE} \\
		-C $(TARGET)/$(CURRENT_KERNEL_CONFIG)			\\
		-f $(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile		\\
		CURRENT_KERNEL_CONFIG=${CURRENT_KERNEL_CONFIG}		\\
		CURRENT_ARCH_CONFIG=${CURRENT_ARCH_CONFIG}		\\
		CURRENT_MACHINE_CONFIG=${CURRENT_MACHINE_CONFIG}	\\
		SOURCE=$(subst conf/,,$(SOURCE))			\\
		TARGET=${TARGET}					\\
		OBJPATH=${OBJPATH}					\\
		SRCROOT=${SRCROOT}					\\
		SETUP=${SRCROOT}/SETUP					\\
		build_all"""

if old_do_all in content:
    content = content.replace(old_do_all, new_do_all)
    with open('bsd/Makefile', 'w') as f:
        f.write(content)
    print("Patched bsd/Makefile successfully!")
else:
    print("Could not find do_all target!")
    idx = content.find('do_all:')
    if idx >= 0:
        print(content[idx:idx+500])
    sys.exit(1)

# Verify the patch
idx = content.find('SRCROOT=${SRCROOT}')
if idx >= 0:
    print("Patch verified: SRCROOT found in do_all target")
else:
    print("WARNING: SRCROOT not found in patched content")
