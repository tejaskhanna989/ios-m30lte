#!/usr/bin/env python3
"""Patch EXTERNAL_HEADERS/stdatomic.h to guard _Atomic with C11 version check."""
import sys
import os

path = 'EXTERNAL_HEADERS/stdatomic.h'
if not os.path.exists(path):
    # Try to find it
    import glob
    matches = glob.glob('**/stdatomic.h', recursive=True)
    if matches:
        path = matches[0]
    else:
        print("stdatomic.h not found!")
        sys.exit(1)

with open(path, 'r') as f:
    content = f.read()

# The issue: _Atomic is used without C11 version check
# We need to guard _Atomic typedefs with #if __STDC_VERSION__ >= 201112L || defined(__cplusplus)

# The atomic type definitions use _Atomic() - we need to guard them
# Find the section with atomic type definitions and wrap with C11 check

old_atomic_start = '''/* 7.17.6 Atomic integer types */

#ifdef __cplusplus
typedef _Atomic(bool)               atomic_bool;
#else
typedef _Atomic(_Bool)              atomic_bool;
#endif
typedef _Atomic(char)               atomic_char;'''

new_atomic_start = '''/* 7.17.6 Atomic integer types */

#if __STDC_VERSION__ >= 201112L || defined(__cplusplus)

#ifdef __cplusplus
typedef _Atomic(bool)               atomic_bool;
#else
typedef _Atomic(_Bool)              atomic_bool;
#endif
typedef _Atomic(char)               atomic_char;'''

# Find the atomic_flag section and close the guard before it
old_atomic_flag = '''/* 7.17.8 Atomic flag type and operations */

typedef struct atomic_flag { atomic_bool _Value; } atomic_flag;'''

new_atomic_flag = '''#endif /* __STDC_VERSION__ >= 201112L || defined(__cplusplus) */

/* 7.17.8 Atomic flag type and operations */

typedef struct atomic_flag { atomic_bool _Value; } atomic_flag;'''

if old_atomic_start in content:
    content = content.replace(old_atomic_start, new_atomic_start)
    print("Replaced atomic_start")
else:
    print("Could not find old_atomic_start pattern")
    sys.exit(1)

if old_atomic_flag in content:
    content = content.replace(old_atomic_flag, new_atomic_flag)
    print("Replaced atomic_flag")
else:
    print("Could not find old_atomic_flag pattern")
    sys.exit(1)

# Write the patched content
with open(path, 'w') as f:
    f.write(content)

print("Patched EXTERNAL_HEADERS/stdatomic.h")
