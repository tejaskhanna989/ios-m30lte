#!/usr/bin/env python3
"""Patch bsd/Makefile to propagate SRCROOT and SETUP to sub-makes."""
import sys
import re

with open('bsd/Makefile', 'r') as f:
    content = f.read()

# Debug: print all targets
print("=== All targets in Makefile ===")
for match in re.finditer(r'^([a-zA-Z0-9_]+):', content, re.MULTILINE):
    print(f"  Target: {match.group(1)}")

# Debug: print all lines containing OBJPATH
print("\n=== Lines containing OBJPATH ===")
for i, line in enumerate(content.split('\n')):
    if 'OBJPATH' in line:
        print(f"  Line: {line}")

# Find and modify the do_all target to add SRCROOT and SETUP after OBJPATH
lines = content.split('\n')
new_lines = []
i = 0
in_do_all = False
found_do_all = False
while i < len(lines):
    new_lines.append(lines[i])
    # Detect start of do_all target (handle variations)
    stripped = lines[i].strip()
    if stripped.startswith('do_all') and ('do_all:' in stripped or 'do_all :' in stripped) and '$(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile' in lines[i]:
        in_do_all = True
        print(f"Found do_all start at line {i}: {lines[i]}")
    # Detect end of do_all target (next target or blank line after build_all)
    if in_do_all and 'build_all' in lines[i] and not lines[i].strip().endswith('\\'):
        in_do_all = False
        print(f"Found do_all end at line {i}: {lines[i]}")
    # Inside do_all target, look for OBJPATH line and insert after it
    if in_do_all and 'OBJPATH' in lines[i] and 'OBJPATH=' in lines[i]:
        indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
        new_lines.append(indent + 'SRCROOT=${SRCROOT}					\\')
        new_lines.append(indent + 'SETUP=${SRCROOT}/SETUP					\\')
        print(f"Inserted SRCROOT/SETUP after line {i}: {lines[i]}")
    i += 1

new_content = '\n'.join(new_lines)

if new_content != content:
    with open('bsd/Makefile', 'w') as f:
        f.write(new_content)
    print("Patched bsd/Makefile successfully!")
else:
    print("Could not find OBJPATH line in do_all target!")
    idx = content.find('do_all:')
    if idx >= 0:
        print(content[idx:idx+500])
    else:
        # Try to find any do_all variant
        for match in re.finditer(r'do_all', content):
            start = max(0, match.start() - 50)
            end = min(len(content), match.end() + 50)
            print(f"Found 'do_all' at {match.start()}: ...{content[start:end]}...")
    sys.exit(1)

# Verify the patch
with open('bsd/Makefile', 'r') as f:
    content = f.read()

if 'SRCROOT=${SRCROOT}' in content and 'SETUP=${SRCROOT}/SETUP' in content:
    print("Patched bsd/Makefile successfully!")
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