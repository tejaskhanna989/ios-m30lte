#!/usr/bin/env python3
"""Disable security/conf module by removing it from COMP_SUBDIRS in security/Makefile."""
import os

with open('security/Makefile', 'r') as f:
    content = f.read()

# Remove conf from COMP_SUBDIRS
old = 'COMP_SUBDIRS = conf'
new = 'COMP_SUBDIRS ='

if old not in content:
    print("WARNING: Could not find COMP_SUBDIRS = conf")
else:
    content = content.replace(old, new)
    with open('security/Makefile', 'w') as f:
        f.write(content)
    print("Patched security/Makefile: removed conf from COMP_SUBDIRS")

print("Done")