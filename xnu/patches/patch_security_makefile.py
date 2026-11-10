#!/usr/bin/env python3
"""Patch security/Makefile to add kernel private definitions."""
import sys

with open('security/Makefile', 'r') as f:
    content = f.read()

# Add kernel private definitions after the includes
# Find the line with "include $(MakeInc_def)" and add CFLAGS after it
# Use 'override' to prevent environment CFLAGS from overriding (due to MAKEFLAGS=-e)
old_text = 'include $(MakeInc_def)'
new_text = '''include $(MakeInc_def)

# Kernel private definitions for security module
# Use override to prevent environment CFLAGS from overriding (MAKEFLAGS=-e)
override CFLAGS+= -DMACH_KERNEL_PRIVATE -DKERNEL_PRIVATE -DKERNEL -DXNU_KERNEL_PRIVATE -DPRIVATE'''

if old_text not in content:
    print("ERROR: Could not find 'include $(MakeInc_def)' line")
    sys.exit(1)

content = content.replace(old_text, new_text)

with open('security/Makefile', 'w') as f:
    f.write(content)

print("Patched security/Makefile with kernel private definitions")

# Verify
with open('security/Makefile', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[:30]):
        print(f"  {i+1}: {line}")