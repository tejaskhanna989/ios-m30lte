#!/usr/bin/env python3
"""Patch doconf.csh to fix variable initialization and MASTER file handling."""
import os

with open('SETUP/config/doconf', 'r') as f:
    content = f.read()

print("=== Patching doconf.csh ===")

# Fix 1: Initialize all variables that might be referenced but not set
# The script uses MASTER_CPU, SOC_CONFIG, PLATFORM, MACHINE, profile, DEF_AVP, DEF_SEED, SOURCE
# but they might not be set if the corresponding flags are not provided

# Add initialization after the existing unset commands
init_block = '''set MASTER_CPU = ""
set SOC_CONFIG = ""
set PLATFORM = ""
set MACHINE = ""
set profile = ""
set DEF_AVP = ""
set DEF_SEED = ""
set SOURCE = ""
'''

# Insert after the existing unset commands
if 'unset PLATFORM' in content:
    content = content.replace('unset PLATFORM', 'unset PLATFORM\n' + init_block)
    print("Added variable initialization block")
else:
    print("WARNING: Could not find 'unset PLATFORM' to insert initialization")

# Fix 2: Ensure MASTER file exists by copying the appropriate file
# The doconf script expects a base MASTER file in the MASTER_CONF_DIR
# We'll add a step to copy MASTER.arm64 to MASTER if MASTER doesn't exist
# This should be done after MASTER_DIR is set but before the foreach loop

# Find the location where MASTER is set and add the copy command
master_block = '''set MASTER_DIR=${MASTER_CONF_DIR}
set MASTER =   ${MASTER_DIR}/MASTER

# Ensure base MASTER file exists (copy from architecture-specific if needed)
if (! -f $MASTER) then
    if (-f ${MASTER_DIR}/MASTER.${cpu}) then
        cp ${MASTER_DIR}/MASTER.${cpu} $MASTER
    else if (-f ${MASTER_DIR}/MASTER.${cpu}.${SOC_CONFIG}) then
        cp ${MASTER_DIR}/MASTER.${cpu}.${SOC_CONFIG} $MASTER
    else
        echo "${prog}: no base MASTER file found in $MASTER_DIR"
        exit 1
    endif
endif

foreach master_file (${MASTER}.${cpu}.${SOC_CONFIG}.${PLATFORM} ${MASTER}.${cpu}.${SOC_CONFIG} ${MASTER}.${cpu}.${PLATFORM} ${MASTER}.${cpu})
'''

old_master_block = '''set MASTER_DIR=${MASTER_CONF_DIR}
set MASTER =   ${MASTER_DIR}/MASTER

foreach master_file (${MASTER}.${cpu}.${SOC_CONFIG}.${PLATFORM} ${MASTER}.${cpu}.${SOC_CONFIG} ${MASTER}.${cpu}.${PLATFORM} ${MASTER}.${cpu})'''

if old_master_block in content:
    content = content.replace(old_master_block, master_block)
    print("Added MASTER file existence check and copy")
else:
    print("WARNING: Could not find MASTER block to patch")
    # Try with different whitespace
    import re
    pattern = re.escape('set MASTER_DIR=${MASTER_CONF_DIR}') + r'\s+' + re.escape('set MASTER =   ${MASTER_DIR}/MASTER') + r'\s*\n' + re.escape('foreach master_file (${MASTER}.${cpu}.${SOC_CONFIG}.${PLATFORM} ${MASTER}.${cpu}.${SOC_CONFIG} ${MASTER}.${cpu}.${PLATFORM} ${MASTER}.${cpu})')
    if re.search(pattern, content):
        content = re.sub(pattern, master_block, content)
        print("Patched with regex")
    else:
        print("Could not find pattern with regex either")

# Fix 3: Also map SOURCEDIR to SOURCE since the script uses $SOURCE but -s sets SOURCEDIR
# Add after the SOURCEDIR is set
if 'set SOURCEDIR' in content:
    # Find where SOURCEDIR is set and add SOURCE = $SOURCEDIR after it
    # The pattern is: set SOURCEDIR=... followed by shift breaksw
    content = content.replace('set SOURCEDIR="$argv[2]"\n    shift\n    shift\n    breaksw', 'set SOURCEDIR="$argv[2]"\n    set SOURCE="$argv[2]"\n    shift\n    shift\n    breaksw')
    print("Added SOURCE = SOURCEDIR mapping")

with open('SETUP/config/doconf', 'w') as f:
    f.write(content)

print("Done patching doconf.csh")
