#!/usr/bin/env python3
"""Patch bsd/Makefile to propagate SRCROOT and SETUP to sub-makes using sed."""
import subprocess
import sys

# Use sed to patch the bsd/Makefile do_all target
# Add SRCROOT and SETUP after OBJPATH line in do_all target
sed_cmd = r'''sed -i '' '/^do_all: \$(TARGET)\/\$(CURRENT_KERNEL_CONFIG)\/Makefile/,/^[[:space:]]*build_all/ {
    /^[[:space:]]*OBJPATH=\$\${OBJPATH}/a\
\                SRCROOT=\${SRCROOT}                                        \\
\                SETUP=\$\${SRCROOT}/SETUP                                        \\
}' bsd/Makefile'''

result = subprocess.run(sed_cmd, shell=True, capture_output=True, text=True, cwd='bsd')

if result.returncode != 0:
    print(f"sed failed: {result.stderr}")
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
    # Debug: show what we have
    idx = content.find('do_all:')
    if idx >= 0:
        print(content[idx:idx+500])
    sys.exit(1)