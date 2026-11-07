#!/usr/bin/env python3
"""Patch bsd/Makefile to propagate SRCROOT and SETUP to sub-makes."""
import re
import sys

with open('bsd/Makefile', 'r') as f:
    content = f.read()

# Use regex to find and modify the do_all target to add SRCROOT and SETUP
# The pattern matches the do_all target and its sub-make invocation
pattern = re.compile(
    r'(do_all:\s*\$\(TARGET\)/\$\(CURRENT_KERNEL_CONFIG\)/Makefile\s*\n'
    r'(?:\s*\$\(_v\)\$\{MAKE\} \\\n'
    r'\s+-C \$\$\(TARGET\)/\$\$\(CURRENT_KERNEL_CONFIG\).*?\\\n'
    r'\s+-f \$\$\(TARGET\)/\$\$\(CURRENT_KERNEL_CONFIG\)/Makefile\s+.*?\\\n'
    r'\s+CURRENT_KERNEL_CONFIG=\$\{CURRENT_KERNEL_CONFIG\}\s+.*?\\\n'
    r'\s+CURRENT_ARCH_CONFIG=\$\{CURRENT_ARCH_CONFIG\}\s+.*?\\\n'
    r'\s+CURRENT_MACHINE_CONFIG=\$\{CURRENT_MACHINE_CONFIG\}\s+.*?\\\n'
    r'\s+SOURCE=\$\$\(subst conf/,,\$\{SOURCE\}\)\s+.*?\\\n'
    r'\s+TARGET=\$\{TARGET\}\s+.*?\\\n'
    r'\s+OBJPATH=\$\{OBJPATH\}\s+.*?\\\n'
    r'\s+build_all)',
    re.DOTALL | re.MULTILINE
)

replacement = r'''do_all: $(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile
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
		build_all'''

new_content = pattern.sub(replacement, content)

if new_content != content:
    with open('bsd/Makefile', 'w') as f:
        f.write(new_content)
    print("Patched bsd/Makefile successfully!")
else:
    print("Could not find do_all target pattern!")
    # Debug: show what we have around do_all
    idx = content.find('do_all:')
    if idx >= 0:
        print(content[idx:idx+500])
    sys.exit(1)

# Verify the patch
if 'SRCROOT=${SRCROOT}' in new_content and 'SETUP=${SRCROOT}/SETUP' in new_content:
    print("Patch verified: SRCROOT and SETUP found in do_all target")
else:
    print("WARNING: SRCROOT/SETUP not found in patched content")
    sys.exit(1)