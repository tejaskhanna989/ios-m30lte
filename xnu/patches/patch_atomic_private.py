#!/usr/bin/env python3
"""Patch libkern/os/atomic_private_impl.h to define memory_order enum."""
import sys
import re

with open('libkern/os/atomic_private_impl.h', 'r') as f:
    content = f.read()

# Check if memory_order enum is already defined
if 'typedef enum memory_order' in content:
    print("memory_order enum already defined")
else:
    # Define memory_order enum - add after the license header
    # Find the end of the license header (look for the first non-comment line after the header)
    lines = content.split('\n')
    insert_idx = 0
    in_header = True
    for i, line in enumerate(lines):
        stripped = line.strip()
        if in_header:
            # Skip license header comments and blank lines
            if stripped == '' or stripped.startswith('/*') or stripped.startswith('*') or stripped.startswith('//') or stripped.startswith('#'):
                continue
            else:
                insert_idx = i
                in_header = False
                break
    
    # Define memory_order enum
    enum_def = '''// memory_order enum for C11 atomic operations
typedef enum memory_order {
    memory_order_relaxed = __ATOMIC_RELAXED,
    memory_order_consume = __ATOMIC_CONSUME,
    memory_order_acquire = __ATOMIC_ACQUIRE,
    memory_order_release = __ATOMIC_RELEASE,
    memory_order_acq_rel = __ATOMIC_ACQ_REL,
    memory_order_seq_cst = __ATOMIC_SEQ_CST
} memory_order;

'''
    
    lines.insert(insert_idx, enum_def)
    content = '\n'.join(lines)
    print(f"Inserted memory_order enum at line {insert_idx}")

# Replace memory_order_* values with __ATOMIC_* constants (for any remaining uses)
# But be careful not to replace the enum values we just added
# Use regex with negative lookahead to avoid replacing enum values
content = re.sub(r'\bmemory_order_relaxed\b(?!\s*=)', '__ATOMIC_RELAXED', content)
content = re.sub(r'\bmemory_order_acquire\b(?!\s*=)', '__ATOMIC_ACQUIRE', content)
content = re.sub(r'\bmemory_order_release\b(?!\s*=)', '__ATOMIC_RELEASE', content)
content = re.sub(r'\bmemory_order_acq_rel\b(?!\s*=)', '__ATOMIC_ACQ_REL', content)
content = re.sub(r'\bmemory_order_seq_cst\b(?!\s*=)', '__ATOMIC_SEQ_CST', content)
# Don't replace memory_order_consume as it's used in the enum

print("Replaced memory_order_* values")

with open('libkern/os/atomic_private_impl.h', 'w') as f:
    f.write(content)

print("Patched libkern/os/atomic_private_impl.h")

# Verify the patch
with open('libkern/os/atomic_private_impl.h', 'r') as f:
    content = f.read()
    
if 'typedef enum memory_order' in content:
    print("SUCCESS: memory_order enum is defined")
else:
    print("ERROR: memory_order enum NOT defined!")
    sys.exit(1)
    
if 'memory_order' in content and '__ATOMIC_' in content:
    print("SUCCESS: __ATOMIC_* constants are used")
else:
    print("WARNING: __ATOMIC_* constants may not be used")
    
# Show the first 30 lines to verify
lines = content.split('\n')
print("First 30 lines of patched file:")
for i, line in enumerate(lines[:30]):
    print(f"{i+1:3}: {line}")