#!/usr/bin/env python3
"""
Fix /makedefs references in XNU Makefiles to use absolute path instead.
This avoids the need for a symlink at /makedefs which isn't possible on read-only root.
"""
import os
import re
import sys

def fix_file(filepath, makedefs_abs_path):
    """Fix /makedefs references in a single file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Pattern: match /makedefs at start of path component
    # Matches: /makedefs/..., /makedefs at end of line
    # After: whitespace, (, =, start of line
    # NOT in middle of expanded path like /Users/.../xnu-source/makedefs
    
    # First, protect existing absolute makedefs paths
    content = re.sub(re.escape(makedefs_abs_path), '__MAKEDEFS_ABS_PLACEHOLDER__', content)
    
    # Replace /makedefs at start of path component (after whitespace, (, =, or start of line)
    # Matches: " /makedefs/", " /makedefs\n", "(/makedefs/", "=/makedefs/", "^/makedefs/"
    content = re.sub(r'(?<=[\s(=])/makedefs(?=/|$)', makedefs_abs_path, content)
    # Also match at start of line
    content = re.sub(r'^/makedefs(?=/|$)', makedefs_abs_path, content, flags=re.MULTILINE)
    
    # Restore placeholder
    content = content.replace('__MAKEDEFS_ABS_PLACEHOLDER__', makedefs_abs_path)
    
    with open(filepath, 'w') as f:
        f.write(content)

def main():
    source_root = sys.argv[1] if len(sys.argv) > 1 else '.'
    source_root = os.path.abspath(source_root)
    makedefs_abs_path = os.path.join(source_root, 'makedefs')
    
    print(f"Source root: {source_root}")
    print(f"Makedefs absolute path: {makedefs_abs_path}")
    
    # Find all Makefiles
    for root, dirs, files in os.walk(source_root):
        for file in files:
            if file in ('Makefile', 'Makefile.inc', 'Makefile.def') or file.endswith('.mk') or file.endswith('.mak'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        if '/makedefs' in f.read():
                            print(f"Fixing: {filepath}")
                            fix_file(filepath, makedefs_abs_path)
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

if __name__ == '__main__':
    main()