#!/usr/bin/env python3
"""Create filelists for kernel build - minimal version."""
import os
import sys

def main():
    srcroot = sys.argv[1] if len(sys.argv) > 1 else "."
    print(f"Creating filelists in {srcroot}")
    
    # Create filelist directories
    os.makedirs(os.path.join(srcroot, "EXPORT_HDRS"), exist_ok=True)
    
    # Create minimal filelist files
    filelists = [
        "EXPORT_HDRS/bsd.filelist",
        "EXPORT_HDRS/osfmk.filelist",
        "EXPORT_HDRS/iokit.filelist",
        "EXPORT_HDRS/libkern.filelist",
    ]
    
    for fl in filelists:
        path = os.path.join(srcroot, fl)
        with open(path, "w") as f:
            f.write("# Minimal filelist
")
        print(f"Created {fl}")
    
    print("Filelists created successfully")

if __name__ == "__main__":
    main()
