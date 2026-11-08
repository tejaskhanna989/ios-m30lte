#!/usr/bin/env python3
"""Patch bsd/Makefile do_all target to propagate SRCROOT and SETUP to sub-makes."""
import sys
import re

with open('bsd/Makefile', 'r') as f:
    content = f.read()

# Find the do_all target - it might be on multiple lines
# Pattern: do_all: $(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile
# The target might be on one line or split across lines

# First, let's find where do_all is defined
do_all_pattern = re.compile(r'^do_all\s*:', re.MULTILINE)
match = re.search(r'^do_all\s*:', content, re.MULTILINE)
if not match:
    print("No do_all target found!")
    # Try to find any target that contains do_all
    for match in re.finditer(r'^([a-zA-Z0-9_]+):', content, re.MULTILINE):
        print(f"  Target: {match.group(1)}")
    sys.exit(1)

print(f"Found do_all at position {match.start()}")

# Find the body of the do_all target
# The target body starts after the colon and continues until the next target or blank line
# The body contains a sub-make invocation with OBJPATH

# Find the sub-make invocation in the do_all target
# Look for the pattern: $(MAKE) ... OBJPATH=${OBJPATH} ... build_all
pattern = re.compile(
    r'(do_all\s*:[\s\S]*?OBJPATH\s*=\s*\$\{OBJPATH\}\s*\\\\\n\s*build_all)',
    re.MULTILINE | re.DOTALL
)

match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
if not match:
    print("Could not find do_all target with OBJPATH pattern!")
    # Debug: print context around do_all
    idx = content.find('do_all:')
    if idx >= 0:
        print(content[max(0, idx-100):idx+1000])
    sys.exit(1)

print("Found do_all target with OBJPATH pattern")

# Insert SRCROOT and SETUP after OBJPATH line
matched_text = match.group(0)
# Find the OBJPATH line and insert after it
new_text = re.sub(
    r'(OBJPATH\s*=\s*\$\{OBJPATH\}\s*\\\\\n)',
    r'\1SRCROOT=${SRCROOT}					\\\\nSETUP=${SRCROOT}/SETUP					\\\\n',
    matched_text
)

new_content = content[:content.index(matched_text)] + new_text + content[content.index(matched_text) + len(matched_text):]

with open('bsd/Makefile', 'w') as f:
    f.write(new_content)
print("Patched bsd/Makefile successfully!")

# Verify the patch
with open('bsd/Makefile', 'r') as f:
    content = f.read()

if 'SRCROOT=${SRCROOT}' in content and 'SETUP=${SRCROOT}/SETUP' in content:
    print("Patched bsd/Makefile successfully!")
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