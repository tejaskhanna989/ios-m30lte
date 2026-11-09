#!/usr/bin/env python3
"""Patch iokit/Makefile to skip DriverKit when DRIVERKIT=0 using Python."""
import sys

with open('iokit/Makefile', 'r') as f:
    content = f.read()

# Find the line after the last include MakeInc.dir and add the DRIVERKIT check
lines = content.split('\n')
insert_idx = -1
for i, line in enumerate(lines):
    if 'include $(MakeInc_dir)' in line:
        insert_idx = i + 1
        break

if insert_idx == -1:
    # Try alternative pattern
    for i, line in enumerate(lines):
        if 'include $(MakeInc_dir' in line:
            insert_idx = i + 1
            break

if insert_idx == -1:
    print("ERROR: Could not find 'include $(MakeInc_dir)' line")
    print("First 30 lines of Makefile:")
    for i, line in enumerate(lines[:30]):
        print(f"  {i+1}: {line}")
    sys.exit(1)

# Insert the DRIVERKIT check after the includes
new_lines = lines[:insert_idx] + [
    '',
    'ifeq ($(DRIVERKIT),0)',
    'SKIP_DRIVERKIT=1',
    'endif',
    ''
] + lines[insert_idx:]

new_content = '\n'.join(new_lines)

with open('iokit/Makefile', 'w') as f:
    f.write(new_content)

print("Patched iokit/Makefile to skip DriverKit when DRIVERKIT=0")

# Verify
with open('iokit/Makefile', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[:30]):
        if 'DRIVERKIT' in line or 'SKIP_DRIVERKIT' in line or 'ifeq' in line or 'endif' in line or 'include' in line:
            print(f"  {i+1}: {line}")