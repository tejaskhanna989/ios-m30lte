#!/usr/bin/env python3
"""Patch libkern/os/atomic_private_impl.h to define memory_order enum."""
import sys

with open('libkern/os/atomic_private_impl.h', 'r') as f:
    content = f.read()

# Add memory_order enum definition after the includes
# Find the first non-include line after the header
lines = content.split('\n')
insert_idx = 0
for i, line in enumerate(lines):
    if line.startswith('#include') or line.startswith('//') or line.startswith('/*') or line.strip() == '':
        continue
    else:
        insert_idx = i
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

# Replace memory_order_* values with __ATOMIC_* constants (for any remaining uses)
content = content.replace('memory_order_relaxed', '__ATOMIC_RELAXED')
content = content.replace('memory_order_acquire', '__ATOMIC_ACQUIRE')
content = content.replace('memory_order_release', '__ATOMIC_RELEASE')
content = content.replace('memory_order_acq_rel', '__ATOMIC_ACQ_REL')
content = content.replace('memory_order_seq_cst', '__ATOMIC_SEQ_CST')
# Don't replace memory_order_consume as it's used in the enum

with open('libkern/os/atomic_private_impl.h', 'w') as f:
    f.write(content)

print("Patched libkern/os/atomic_private_impl.h")