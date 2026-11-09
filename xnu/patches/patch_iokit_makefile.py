#!/usr/bin/env python3
"""Patch iokit/Makefile to skip DriverKit when DRIVERKIT=0 - properly remove from subdirs."""
import sys

with open('iokit/Makefile', 'r') as f:
    content = f.read()

# Replace the INSTINC_SUBDIRS and EXPINC_SUBDIRS lines to conditionally exclude DriverKit
# Original:
# INSTINC_SUBDIRS = IOKit DriverKit System IOKitUser
# EXPINC_SUBDIRS = IOKit DriverKit
#
# New: conditionally exclude DriverKit when DRIVERKIT=0

old_instinc = 'INSTINC_SUBDIRS = IOKit DriverKit System IOKitUser'
new_instinc = '''ifeq ($(DRIVERKIT),0)
INSTINC_SUBDIRS = IOKit System IOKitUser
else
INSTINC_SUBDIRS = IOKit DriverKit System IOKitUser
endif'''

old_expinc = 'EXPINC_SUBDIRS = IOKit DriverKit'
new_expinc = '''ifeq ($(DRIVERKIT),0)
EXPINC_SUBDIRS = IOKit
else
EXPINC_SUBDIRS = IOKit DriverKit
endif'''

if old_instinc in content:
    content = content.replace(old_instinc, new_instinc)
    print("Patched INSTINC_SUBDIRS")
else:
    print("ERROR: Could not find INSTINC_SUBDIRS line")
    sys.exit(1)

if old_expinc in content:
    content = content.replace(old_expinc, new_expinc)
    print("Patched EXPINC_SUBDIRS")
else:
    print("ERROR: Could not find EXPINC_SUBDIRS line")
    sys.exit(1)

with open('iokit/Makefile', 'w') as f:
    f.write(content)

print("Patched iokit/Makefile to conditionally exclude DriverKit")

# Verify
with open('iokit/Makefile', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[:30]):
        if 'INSTINC' in line or 'EXPINC' in line or 'ifeq' in line or 'else' in line or 'endif' in line:
            print(f"  {i+1}: {line}")