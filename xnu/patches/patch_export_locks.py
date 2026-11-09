#!/usr/bin/env python3
"""Patch the copied locks.h to have full lck_mtx_t definition."""
import sys
import os

target_file = 'BUILD/obj/EXPORT_HDRS/osfmk/arm/locks.h'

with open(target_file, 'r') as f:
    content = f.read()

# Simple approach: replace the forward declaration line with the full definition
# Find and replace the forward declaration line
old_line = 'typedef struct __lck_mtx_t__            lck_mtx_t;'
new_definition = '''typedef struct {
	uintptr_t opaque[2] __kernel_data_semantics;
} lck_mtx_t;'''

if old_line in content:
    content = content.replace(old_line, new_definition)
    print("Replaced forward declaration with full definition")
else:
    print("Forward declaration not found, trying alternative patterns...")
    # Try alternative patterns
    alt_patterns = [
        'typedef struct __lck_mtx_t__ lck_mtx_t;',
        'typedef struct __lck_mtx_t__  lck_mtx_t;',
        'typedef struct __lck_mtx_t__    lck_mtx_t;',
    ]
    for pattern in alt_patterns:
        if pattern in content:
            content = content.replace(pattern, new_definition)
            print(f"Replaced using alternative pattern: {pattern}")
            break
    else:
        print("ERROR: Could not find forward declaration pattern")
        # Debug: show lines containing lck_mtx_t
        for i, line in enumerate(content.split('\n')):
            if 'lck_mtx_t' in line:
                print(f"  Line {i+1}: {line}")
        sys.exit(1)

with open(target_file, 'w') as f:
    f.write(content)

print(f"Patched {target_file}")

# Verify
with open(target_file, 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')):
        if 'lck_mtx_t' in line and 'typedef' in line:
            print(f"  Line {i+1}: {line}")