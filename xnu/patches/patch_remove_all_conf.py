#!/usr/bin/env python3
"""Remove conf from COMP_SUBDIRS in all component Makefiles to bypass doconf failure."""
import os

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
    
    # Remove conf from COMP_SUBDIRS - handle different formatting
    old_patterns = [
        'COMP_SUBDIRS = conf',
        'COMP_SUBDIRS =\t\\\n\tconf',
        'COMP_SUBDIRS = \\\n\tconf',
        'COMP_SUBDIRS =\\\n\tconf',
    ]
    
    replaced = False
    for old in old_patterns:
        if old in content:
            content = content.replace(old, 'COMP_SUBDIRS =')
            print(f"Patched {makefile}: removed conf from COMP_SUBDIRS")
            replaced = True
            break
    
    if not replaced:
        # Try regex
        import re
        new_content = re.sub(r'COMP_SUBDIRS\s*=\s*\\\s*\n\s*conf', 'COMP_SUBDIRS =', content)
        new_content = re.sub(r'COMP_SUBDIRS\s*=\s*conf', 'COMP_SUBDIRS =', new_content)
        if new_content != content:
            content = new_content
            print(f"Patched {makefile}: removed conf from COMP_SUBDIRS (regex)")
            replaced = True
    
    if not replaced:
        print(f"WARNING: Could not find COMP_SUBDIRS pattern in {makefile}")
    
    with open(makefile, 'w') as f:
        f.write(content)

print("Done")