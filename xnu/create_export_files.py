#!/usr/bin/env python3
"""Create export files for kernel build - minimal version."""
import os
import sys
import shutil

def main():
    srcroot = sys.argv[1] if len(sys.argv) > 1 else "."
    print(f"Creating export files in {srcroot}")
    
    # Create EXPORT_HDRS directory structure
    export_dirs = [
        "EXPORT_HDRS/osfmk/arm",
        "EXPORT_HDRS/osfmk/arm64",
        "EXPORT_HDRS/osfmk/kern",
        "EXPORT_HDRS/osfmk/vm",
        "EXPORT_HDRS/osfmk/ipc",
        "EXPORT_HDRS/bsd",
        "EXPORT_HDRS/bsd/sys",
        "EXPORT_HDRS/bsd/kern",
        "EXPORT_HDRS/bsd/dev",
        "EXPORT_HDRS/bsd/net",
        "EXPORT_HDRS/bsd/netinet",
        "EXPORT_HDRS/iokit",
        "EXPORT_HDRS/iokit/IOKit",
        "EXPORT_HDRS/libkern",
        "EXPORT_HDRS/libkern/c++",
        "EXPORT_HDRS/libkern/os",
    ]
    
    for d in export_dirs:
        os.makedirs(os.path.join(srcroot, d), exist_ok=True)
    
    # Copy export files from config directory
    config_dir = os.path.join(srcroot, "config")
    if os.path.exists(config_dir):
        for f in os.listdir(config_dir):
            if f.endswith(".exports"):
                dst = os.path.join(srcroot, "EXPORT_HDRS", f)
                shutil.copy2(os.path.join(config_dir, f), dst)
                print(f"Copied {f} to EXPORT_HDRS")
    
    print("Export files created successfully")

if __name__ == "__main__":
    main()
