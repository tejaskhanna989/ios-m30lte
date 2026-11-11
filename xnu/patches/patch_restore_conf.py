#!/usr/bin/env python3
"""Restore conf to COMP_SUBDIRS in all component Makefiles."""
import os
import re

makefiles = [
    'security/Makefile',
    'bsd/Makefile',
    'osfmk/Makefile',
    'libkern/Makefile',
    'iokit/Makefile',
    'pexpert/Makefile',
    'libsa/Makefile',
    'san/Makefile',
]

for makefile in makefiles:
    if not os.path.exists(makefile):
        print(f"WARNING: {makefile} not found")
        continue

    with open(makefile, 'r') as f:
        content = f.read()

    # Restore conf to COMP_SUBDIRS
    old = 'COMP_SUBDIRS ='
    new = 'COMP_SUBDIRS = \\\n\tconf'

    if old in content:
        content = content.replace(old, new, 1)
        with open(makefile, 'w') as f:
            f.write(content)
        print(f"Patched {makefile}: restored conf to COMP_SUBDIRS")
    else:
        print(f"WARNING: Could not find COMP_SUBDIRS = in {makefile}")

print("Done")