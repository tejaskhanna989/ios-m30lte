#!/usr/bin/env python3
"""Patch libkern/os/atomic_private_impl.h to define memory_order enum before use."""
import sys

with open('libkern/os/atomic_private_impl.h', 'r') as f:
    content = f.read()

# Add memory_order enum definitions after the license header and before the implementation
# Find the line with "#pragma mark - implementation details"
insert_marker = '#pragma mark - implementation details'

memory_order_defs = '''
/*
 * Memory order definitions for C11 atomics.
 * These are normally provided by <stdatomic.h> but we define them here
 * for kernel use where stdatomic.h may not be available.
 */
#ifndef __OS_MEMORY_ORDER_DEFINED__
#define __OS_MEMORY_ORDER_DEFINED__

typedef enum {
    memory_order_relaxed = 0,
    memory_order_consume = 1,
    memory_order_acquire = 2,
    memory_order_release = 3,
    memory_order_acq_rel = 4,
    memory_order_seq_cst = 5
} memory_order;

#endif /* __OS_MEMORY_ORDER_DEFINED__ */

'''

new_content = content.replace(insert_marker, memory_order_defs + insert_marker)

with open('libkern/os/atomic_private_impl.h', 'w') as f:
    f.write(new_content)

print("Patched libkern/os/atomic_private_impl.h with memory_order enum definitions")

# Verify
with open('libkern/os/atomic_private_impl.h', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[:50]):
        print(f"  {i+1}: {line}")