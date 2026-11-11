#!/usr/bin/env python3
"""Add C11 atomic function fallbacks using Clang builtins to atomic_private_impl.h"""
import sys

with open('libkern/os/atomic_private_impl.h', 'r') as f:
    content = f.read()

# Add fallback implementations before the final #endif
fallback_code = '''

/*
 * C11 atomic function fallbacks using Clang builtins.
 * These are needed when building with iPhoneOS SDK which doesn't provide
 * all C11 atomic functions in stdatomic.h when using -mkernel.
 */
#if !OS_ATOMIC_USES_CXX
#ifndef __OS_C11_ATOMIC_FALLBACKS_DEFINED__
#define __OS_C11_ATOMIC_FALLBACKS_DEFINED__

/* memory_order enum - should match stdatomic.h */
typedef enum {
    memory_order_relaxed = 0,
    memory_order_consume = 1,
    memory_order_acquire = 2,
    memory_order_release = 3,
    memory_order_acq_rel = 4,
    memory_order_seq_cst = 5
} memory_order;

/* atomic_init - initialize an atomic object */
#define atomic_init(obj, value) \
    do { \
        __typeof__(*(obj)) *___obj = (obj); \
        *___obj = (value); \
    } while (0)

/* atomic_load_explicit - load with memory order */
#define atomic_load_explicit(obj, mo) \
    __atomic_load_n((obj), (mo))

/* atomic_store_explicit - store with memory order */
#define atomic_store_explicit(obj, val, mo) \
    __atomic_store_n((obj), (val), (mo))

/* atomic_fetch_add_explicit - fetch and add with memory order */
#define atomic_fetch_add_explicit(obj, val, mo) \
    __atomic_fetch_add((obj), (val), (mo))

/* atomic_fetch_sub_explicit - fetch and subtract with memory order */
#define atomic_fetch_sub_explicit(obj, val, mo) \
    __atomic_fetch_sub((obj), (val), (mo))

/* atomic_fetch_and_explicit - fetch and bitwise AND with memory order */
#define atomic_fetch_and_explicit(obj, val, mo) \
    __atomic_fetch_and((obj), (val), (mo))

/* atomic_fetch_or_explicit - fetch and bitwise OR with memory order */
#define atomic_fetch_or_explicit(obj, val, mo) \
    __atomic_fetch_or((obj), (val), (mo))

/* atomic_fetch_xor_explicit - fetch and bitwise XOR with memory order */
#define atomic_fetch_xor_explicit(obj, val, mo) \
    __atomic_fetch_xor((obj), (val), (mo))

/* atomic_exchange_explicit - exchange with memory order */
#define atomic_exchange_explicit(obj, val, mo) \
    __atomic_exchange_n((obj), (val), (mo))

/* atomic_compare_exchange_strong_explicit - compare and exchange strong */
#define atomic_compare_exchange_strong_explicit(obj, expected, desired, success_mo, failure_mo) \
    __atomic_compare_exchange_n((obj), (expected), (desired), 0, (success_mo), (failure_mo))

/* atomic_compare_exchange_weak_explicit - compare and exchange weak */
#define atomic_compare_exchange_weak_explicit(obj, expected, desired, success_mo, failure_mo) \
    __atomic_compare_exchange_n((obj), (expected), (desired), 1, (success_mo), (failure_mo))

/* atomic_thread_fence - thread fence */
#define atomic_thread_fence(mo) \
    __atomic_thread_fence(mo)

/* atomic_signal_fence - signal fence */
#define atomic_signal_fence(mo) \
    __atomic_signal_fence(mo)

/* atomic_is_lock_free - check if atomic operations are lock-free */
#define atomic_is_lock_free(obj) \
    __atomic_is_lock_free(sizeof(*(obj)), (obj))

#endif /* __OS_C11_ATOMIC_FALLBACKS_DEFINED__ */
#endif /* !OS_ATOMIC_USES_CXX */

'''

# Insert before the final #endif
if '#endif /* __OS_ATOMIC_PRIVATE_IMPL_H__ */' not in content:
    print("ERROR: Could not find closing #endif")
    sys.exit(1)

content = content.replace(
    '#endif /* __OS_ATOMIC_PRIVATE_IMPL_H__ */',
    fallback_code + '\n#endif /* __OS_ATOMIC_PRIVATE_IMPL_H__ */'
)

with open('libkern/os/atomic_private_impl.h', 'w') as f:
    f.write(content)

print("Added C11 atomic fallbacks to atomic_private_impl.h")
