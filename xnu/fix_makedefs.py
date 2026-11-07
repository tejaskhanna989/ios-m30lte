#!/usr/bin/env python3
"""
Fix /makedefs references in XNU Makefiles to use $(SRCROOT)/makedefs instead.
This avoids the need for a symlink at /makedefs which isn't possible on read-only root.
"""
import os
import re
import sys

def fix_file(filepath):
    """Fix /makedefs references in a single file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Pattern to match /makedefs but not $(SRCROOT)/makedefs
    # We need to be careful not to double-replace
    # First, protect existing $(SRCROOT)/makedefs
    content = re.sub(r'\$\(SRCROOT\)/makedefs', '__SRCROOT_MAKEDEFS_PLACEHOLDER__', content)
    
    # Replace remaining /makedefs with $(SRCROOT)/makedefs
    content = re.sub(r'(?<!\$\(SRCROOT\))/makedefs', '$(SRCROOT)/makedefs', content)
    
    # Restore placeholder
    content = content.replace('__SRCROOT_MAKEDEFS_PLACEHOLDER__', '$(SRCROOT)/makedefs')
    
    with open(filepath, 'w') as f:
        f.write(content)

def main():
    source_root = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    # Find all Makefiles
    for root, dirs, files in os.walk(source_root):
        for file in files:
            if file in ('Makefile', 'Makefile.inc', 'Makefile.def') or file.endswith('.mk') or file.endswith('.mak'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        if '/makedefs' in f.read():
                            print(f"Fixing: {filepath}")
                            fix_file(filepath)
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

if __name__ == '__main__':
    main()