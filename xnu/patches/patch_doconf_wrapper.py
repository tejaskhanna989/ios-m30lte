#!/usr/bin/env python3
"""Replace doconf script with a wrapper that copies pre-generated Makefile.valid.

Instead of running doconf (which generates Makefiles with tab issues),
replace the doconf script with a wrapper that simply copies the pre-generated
Makefile.valid to the target location.
"""
import os
import shutil

DOCONF_PATH = 'SETUP/config/doconf'
BACKUP_PATH = 'SETUP/config/doconf.original'

DOCONF_WRAPPER = """#!/bin/csh -f
# Wrapper around doconf that copies pre-generated Makefile.valid
# instead of running the original doconf (which produces Makefiles with tab issues)
if ($#argv >= 1) then
    # Parse arguments to find -d (output dir) and -s (source dir)
    set output_dir = ""
    set source_dir = ""
    set i = 1
    while ($i <= $#argv)
        if ("$argv[$i]" == "-d") then
            set output_dir = "$argv[$((i + 1))]"
            set i = $((i + 2))
        else if ("$argv[$i]" == "-s") then
            set source_dir = "$argv[$((i + 1))]"
            set i = $((i + 2))
        else
            set i = $((i + 1))
        endif
    end

    if ("$output_dir" != "" && "$source_dir" != "") then
        # Copy pre-generated Makefile.valid to target
        if (-f "$source_dir/Makefile.valid") then
            mkdir -p "$output_dir"
            cp "$source_dir/Makefile.valid" "$output_dir/Makefile"
            echo "Copied Makefile.valid to $output_dir/Makefile"
        else
            echo "WARNING: $source_dir/Makefile.valid not found"
            exit 1
        endif
    else
        echo "Usage: doconf -d <output_dir> -s <source_dir> ..."
        exit 1
    endif
endif
"""

def main():
    # First, check if we already patched doconf
    if os.path.exists(BACKUP_PATH):
        print(f"{BACKUP_PATH} already exists, doconf already patched")
        return

    if not os.path.exists(DOCONF_PATH):
        print(f"ERROR: {DOCONF_PATH} not found")
        return False

    # Backup original doconf
    shutil.copy2(DOCONF_PATH, BACKUP_PATH)
    print(f"Backed up {DOCONF_PATH} to {BACKUP_PATH}")

    # Write wrapper
    with open(DOCONF_PATH, 'w') as f:
        f.write(DOCONF_WRAPPER)
    os.chmod(DOCONF_PATH, 0o755)
    print(f"Replaced {DOCONF_PATH} with wrapper script")

    print("Done")


if __name__ == '__main__':
    main()