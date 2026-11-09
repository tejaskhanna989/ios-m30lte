#!/usr/bin/env python3
"""Patch the copied locks.h to have full lck_mtx_t definition unconditionally."""
import sys
import os

target_file = 'BUILD/obj/EXPORT_HDRS/osfmk/arm/locks.h'

with open(target_file, 'r') as f:
    content = f.read()

# Replace the forward declaration with the full definition
# The forward declaration is:
# typedef struct __lck_mtx_t__            lck_mtx_t;
# We need to replace it with the full definition from the source

full_definition = '''#ifdef MACH_KERNEL_PRIVATE
/* Full definition for kernel private builds */
#ifndef LCK_SPIN_IS_TICKET_LOCK
#define LCK_SPIN_IS_TICKET_LOCK 0
#endif
#endif /* MACH_KERNEL_PRIVATE */

#include <kern/lock_types.h>
#ifdef  MACH_KERNEL_PRIVATE
#include <kern/sched_hygiene.h>
#include <kern/startup.h>
#if LCK_SPIN_IS_TICKET_LOCK
#include <kern/ticket_lock.h>
#endif
#endif

#ifdef  MACH_KERNEL_PRIVATE

#define enaLkDeb                0x00000001      /* Request debug in default attribute */
#define enaLkStat               0x00000002      /* Request statistic in default attribute */
#define disLkRWPrio             0x00000004      /* Disable RW lock priority promotion */
#define enaLkTimeStat           0x00000008      /* Request time statistics in default attribute */
#define disLkRWDebug            0x00000010      /* Disable RW lock best-effort debugging */

#define disLkType               0x80000000      /* Disable type checking */
#define disLktypeb              0
#define disLkThread             0x40000000      /* Disable ownership checking */
#define disLkThreadb            1
#define enaLkExtStck            0x20000000      /* Enable extended backtrace */
#define enaLkExtStckb           2
#define disLkMyLck              0x10000000      /* Disable recursive lock dectection */
#define disLkMyLckb             3

#endif

#ifdef  MACH_KERNEL_PRIVATE
#if LCK_SPIN_IS_TICKET_LOCK
typedef lck_ticket_t lck_spin_t;
#else
typedef struct {
	struct hslock   hwlock;
	unsigned long   type;
} lck_spin_t;

#define lck_spin_data hwlock.lock_data

#define LCK_SPIN_TAG_DESTROYED  0xdead  /* lock marked as Destroyed */

#define LCK_SPIN_TYPE           0x00000011
#define LCK_SPIN_TYPE_DESTROYED 0x000000ee
#endif

#elif KERNEL_PRIVATE

typedef struct {
	uintptr_t opaque[2] __kernel_data_semantics;
} lck_spin_t;

typedef struct {
	uintptr_t opaque[2] __kernel_data_semantics;
} lck_mtx_t;

typedef struct {
	uintptr_t opaque[16];
} lck_mtx_ext_t;

#else

typedef struct __lck_spin_t__           lck_spin_t;
typedef struct __lck_mtx_t__            lck_mtx_t;
typedef struct __lck_mtx_ext_t__        lck_mtx_ext_t;

#endif  /* !KERNEL_PRIVATE */

'''

# For the EXPORT_HDRS version, we need the KERNEL_PRIVATE version which has the full struct definition
# The issue is that the security module is built with KERNEL_PRIVATE but not MACH_KERNEL_PRIVATE
# So we need the KERNEL_PRIVATE version which has:
# typedef struct {
#     uintptr_t opaque[2] __kernel_data_semantics;
# } lck_mtx_t;

# Let's check what the current file has and replace the forward declaration
# The forward declaration is at the end under #else:
# typedef struct __lck_spin_t__           lck_spin_t;
# typedef struct __lck_mtx_t__            lck_mtx_t;
# typedef struct __lck_mtx_ext_t__        lck_mtx_ext_t;

# We need to replace the forward declaration of lck_mtx_t with the full definition

# Simple approach: replace the forward declaration with the KERNEL_PRIVATE definition
old_forward = '''#else

typedef struct __lck_spin_t__           lck_spin_t;
typedef struct __lck_mtx_t__            lck_mtx_t;
typedef struct __lck_mtx_ext_t__        lck_mtx_ext_t;

#endif  /* !KERNEL_PRIVATE */'''

new_kernel_private = '''#elif KERNEL_PRIVATE

typedef struct {
	uintptr_t opaque[2] __kernel_data_semantics;
} lck_spin_t;

typedef struct {
	uintptr_t opaque[2] __kernel_data_semantics;
} lck_mtx_t;

typedef struct {
	uintptr_t opaque[16];
} lck_mtx_ext_t;

#else

typedef struct __lck_spin_t__           lck_spin_t;
typedef struct __lck_mtx_t__            lck_mtx_t;
typedef struct __lck_mtx_ext_t__        lck_mtx_ext_t;

#endif  /* !KERNEL_PRIVATE */'''

if old_forward in content:
    content = content.replace(old_forward, new_kernel_private)
    print("Replaced forward declaration with KERNEL_PRIVATE definition")
else:
    print("Forward declaration not found, checking content...")
    # Debug: print the end of the file
    lines = content.split('\n')
    for i, line in enumerate(lines[-30:]):
        print(f"  {len(lines)-30+i+1}: {line}")

with open(target_file, 'w') as f:
    f.write(content)

print(f"Patched {target_file}")

# Verify
with open(target_file, 'r') as f:
    content = f.read()
    # Check for lck_mtx_t definition
    for i, line in enumerate(content.split('\n')):
        if 'lck_mtx_t' in line and 'typedef' in line:
            print(f"  Line {i+1}: {line}")