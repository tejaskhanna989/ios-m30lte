#!/usr/bin/env python3
"""Patch bsd/conf/Makefile do_all target to propagate SRCROOT and SETUP to sub-makes."""
import sys
import re

with open('bsd/conf/Makefile', 'r') as f:
    content = f.read()

# Find the do_all target in bsd/conf/Makefile
# Pattern: do_all: $(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile
# The target body contains a sub-make invocation with OBJPATH

pattern = re.compile(
    r'(do_all\s*:\s*\$\(TARGET\)/\$\(CURRENT_KERNEL_CONFIG\)/Makefile\s*\\n'
    r'(?:\s.*?\\\\\n)*'
    r'\s+OBJPATH\s*=\s*\$\{OBJPATH\}\s*\\\\\n'
    r'(?:\s.*?\\\\\n)*'
    r'\s+build_all)',
    re.MULTILINE | re.DOTALL
)

match = pattern.search(content)
if not match:
    print("Could not find do_all target with OBJPATH pattern in bsd/conf/Makefile!")
    # Debug: print context around do_all
    idx = content.find('do_all:')
    if idx >= 0:
        print(content[max(0, idx-100):idx+1000])
    sys.exit(1)

print("Found do_all target with OBJPATH pattern in bsd/conf/Makefile")

# Insert SRCROOT and SETUP after OBJPATH line
matched_text = match.group(0)
new_text = re.sub(
    r'(OBJPATH\s*=\s*\$\{OBJPATH\}\s*\\\\\n)',
    r'\1SRCROOT=${SRCROOT}\t\t\t\t\t\\\\\nSETUP=${SRCROOT}/SETUP\t\t\t\t\t\\\\\n',
    matched_text
)

new_content = content[:content.index(matched_text)] + new_text + content[content.index(matched_text) + len(matched_text):]

with open('bsd/conf/Makefile', 'w') as f:
    f.write(new_content)
print("Patched bsd/conf/Makefile successfully!")

# Verify the patch
with open('bsd/conf/Makefile', 'r') as f:
    content = f.read()

if 'SRCROOT=${SRCROOT}' in content and 'SETUP=${SRCROOT}/SETUP' in content:
    print("Patched bsd/conf/Makefile successfully!")
    idx = content.find('do_all')
    if idx >= 0:
        print("=== Patched do_all target ===")
        print(content[idx:idx+800])
else:
    print("WARNING: SRCROOT/SETUP not found in patched content")
    idx = content.find('do_all')
    if idx >= 0:
        print(content[idx:idx+800])
    sys.exit(1)