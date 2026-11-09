#!/usr/bin/env python3
"""Copy .defs files to build directory for all osfmk subdirectories."""
import sys
import os
import shutil

# List of osfmk subdirectories that have .defs files
osfmk_subdirs = [
    'mach',
    'UserNotification',
    'gssd',
    'kextd',
    # Add more as needed
]

for subdir in osfmk_subdirs:
    src_dir = os.path.join('osfmk', subdir)
    build_dir = os.path.join('BUILD', 'obj', 'DEVELOPMENT_ARM64_M30LTE', 'osfmk', subdir)
    
    if not os.path.exists(src_dir):
        print(f"WARNING: Source directory {src_dir} does not exist, skipping")
        continue
    
    # Create build directory
    os.makedirs(build_dir, exist_ok=True)
    
    # Copy all .defs files
    count = 0
    for f in os.listdir(src_dir):
        if f.endswith('.defs'):
            src = os.path.join(src_dir, f)
            dst = os.path.join(build_dir, f)
            shutil.copy2(src, dst)
            count += 1
            print(f"  Copied {subdir}/{f}")
    
    if count > 0:
        print(f"Copied {count} .defs files from {src_dir} to {build_dir}")
    else:
        print(f"WARNING: No .defs files found in {src_dir}")
        # Debug: list all files in the directory
        all_files = os.listdir(src_dir)
        print(f"  Files in {src_dir}: {all_files}")

print("Done copying .defs files")