#!/usr/bin/env python3
"""Patch doconf.csh to fix variable initialization and add debug output."""
import os

with open('SETUP/config/doconf', 'r') as f:
    content = f.read()

print("=== Patching doconf.csh ===")

# Fix 1: Initialize all variables that might be referenced but not set
init_block = '''set MASTER_CPU = ""
set SOC_CONFIG = ""
set PLATFORM = ""
set MACHINE = ""
set profile = ""
set DEF_AVP = ""
set DEF_SEED = ""
set SOURCE = ""
'''

if 'unset PLATFORM' in content:
    content = content.replace('unset PLATFORM', 'unset PLATFORM\n' + init_block)
    print("Added variable initialization block")
else:
    print("WARNING: Could not find 'unset PLATFORM' to insert initialization")

# Fix 2: Ensure MASTER file exists by copying the appropriate file
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
    import re
    pattern = re.escape('set MASTER_DIR=${MASTER_CONF_DIR}') + r'\s+' + re.escape('set MASTER =   ${MASTER_DIR}/MASTER') + r'\s*\n' + re.escape('foreach master_file (${MASTER}.${cpu}.${SOC_CONFIG}.${PLATFORM} ${MASTER}.${cpu}.${SOC_CONFIG} ${MASTER}.${cpu}.${PLATFORM} ${MASTER}.${cpu})')
    if re.search(pattern, content):
        content = re.sub(pattern, master_block, content)
        print("Patched with regex")
    else:
        print("Could not find pattern with regex either")

# Fix 3: Map SOURCEDIR to SOURCE
if 'set SOURCEDIR' in content:
    content = content.replace('set SOURCEDIR="$argv[2]"\n    shift\n    shift\n    breaksw', 'set SOURCEDIR="$argv[2]"\n    set SOURCE="$argv[2]"\n    shift\n    shift\n    breaksw')
    print("Added SOURCE = SOURCEDIR mapping")

# Fix 4: Add debug output before calling config binary
# Find the line that calls the config binary and add debug before it
debug_block = '''    echo "=== DEBUG: SYSCONF file content ==="
    cat $SYSCONF
    echo "=== END SYSCONF ==="
'''

# Find the config binary call pattern
config_call_pattern = '''if ($?profile) then
	    $CONFIG_DIR/config -c $SOURCEDIR -p $SYSCONF
	else
	    $CONFIG_DIR/config -c $SOURCEDIR $SYSCONF
	endif'''

new_config_call = '''if ($?profile) then
    echo "=== DEBUG: Calling config binary with profile ==="
    cat $SYSCONF
    echo "=== END SYSCONF ==="
	    $CONFIG_DIR/config -c $SOURCEDIR -p $SYSCONF
	else
    echo "=== DEBUG: Calling config binary without profile ==="
    cat $SYSCONF
    echo "=== END SYSCONF ==="
	    $CONFIG_DIR/config -c $SOURCEDIR $SYSCONF
	endif'''

if config_call_pattern in content:
    content = content.replace(config_call_pattern, new_config_call)
    print("Added debug output before config binary call")
else:
    print("WARNING: Could not find config binary call pattern")
    # Try with different indentation
    alt_pattern = config_call_pattern.replace('\t', '    ')
    if alt_pattern in content:
        content = content.replace(alt_pattern, new_config_call.replace('\t', '    '))
        print("Patched with alt indentation")
    else:
        print("Could not find with alt indentation either")

with open('SETUP/config/doconf', 'w') as f:
    f.write(content)

print("Done patching doconf.csh")
