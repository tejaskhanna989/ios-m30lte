#!/usr/bin/env python3
"""Patch make_symbol_aliasing.sh to find availability.pl in host system or build output."""
import sys

with open('bsd/sys/make_symbol_aliasing.sh', 'r') as f:
    content = f.read()

# Find the AVAILABILITY_PL line and the exit block, replace with fallback logic
old_block = '''AVAILABILITY_PL="${SDKROOT}/${DRIVERKITROOT}/usr/local/libexec/availability.pl"

if [ ! -x "${AVAILABILITY_PL}" ] ; then
    echo "Unable to locate ${AVAILABILITY_PL} (or not executable)" >&2
    exit 1
fi'''
new_block = '''AVAILABILITY_PL="${SDKROOT}/${DRIVERKITROOT}/usr/local/libexec/availability.pl"

# M30LTE: Fallback locations for availability.pl (not in SDK for non-DriverKit builds)
if [ ! -x "${AVAILABILITY_PL}" ] ; then
    # Try host system installation (from AvailabilityVersions build)
    if [ -x "/usr/local/libexec/availability.pl" ] ; then
        AVAILABILITY_PL="/usr/local/libexec/availability.pl"
    # Try build output directory (DSTROOT from AvailabilityVersions build)
    elif [ -n "${DSTROOT}" ] && [ -x "${DSTROOT}/usr/local/libexec/availability.pl" ] ; then
        AVAILABILITY_PL="${DSTROOT}/usr/local/libexec/availability.pl"
    # Try FAKEROOT_DIR (alternative build output)
    elif [ -n "${FAKEROOT_DIR}" ] && [ -x "${FAKEROOT_DIR}/usr/local/libexec/availability.pl" ] ; then
        AVAILABILITY_PL="${FAKEROOT_DIR}/usr/local/libexec/availability.pl"
    else
        echo "Unable to locate ${AVAILABILITY_PL} (or not executable) and no fallback found" >&2
        exit 1
    fi
fi'''

if old_block in content:
    content = content.replace(old_block, new_block)
    with open('bsd/sys/make_symbol_aliasing.sh', 'w') as f:
        f.write(content)
    print("Patched make_symbol_aliasing.sh with fallback locations")
else:
    print("ERROR: Could not find target line to patch")
    sys.exit(1)