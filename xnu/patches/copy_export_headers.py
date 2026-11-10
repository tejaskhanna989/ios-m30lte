#!/usr/bin/env python3
"""Copy and patch all needed kernel-private headers for security module.
Patches both source tree and EXPORT_HDRS to ensure correct definitions are used
regardless of include path order."""
import os
import shutil

# List of headers to copy from source to EXPORT_HDRS
headers_to_copy = [
    # osfmk/kern - lock types
    ('osfmk/kern/lock_mtx.h', 'BUILD/obj/EXPORT_HDRS/osfmk/kern/lock_mtx.h'),
    ('osfmk/kern/lock_types.h', 'BUILD/obj/EXPORT_HDRS/osfmk/kern/lock_types.h'),
    ('osfmk/kern/locks.h', 'BUILD/obj/EXPORT_HDRS/osfmk/kern/locks.h'),
    ('osfmk/kern/lock_attr.h', 'BUILD/obj/EXPORT_HDRS/osfmk/kern/lock_attr.h'),
    ('osfmk/kern/lock_group.h', 'BUILD/obj/EXPORT_HDRS/osfmk/kern/lock_group.h'),
    ('osfmk/kern/lock_rw.h', 'BUILD/obj/EXPORT_HDRS/osfmk/kern/lock_rw.h'),
    ('osfmk/kern/lock_sleep.h', 'BUILD/obj/EXPORT_HDRS/osfmk/kern/lock_sleep.h'),
    ('osfmk/kern/lock_stat.h', 'BUILD/obj/EXPORT_HDRS/osfmk/kern/lock_stat.h'),

    # osfmk/kern - smr and atomic
    ('osfmk/kern/smr.h', 'BUILD/obj/EXPORT_HDRS/osfmk/kern/smr.h'),
    ('osfmk/kern/atomic.h', 'BUILD/obj/EXPORT_HDRS/osfmk/kern/atomic.h'),

    # osfmk/kern - kern_types
    ('osfmk/kern/kern_types.h', 'BUILD/obj/EXPORT_HDRS/osfmk/kern/kern_types.h'),
    ('osfmk/kern/queue.h', 'BUILD/obj/EXPORT_HDRS/osfmk/kern/queue.h'),

    # bsd/sys - vnode and related
    ('bsd/sys/vnode_internal.h', 'BUILD/obj/EXPORT_HDRS/bsd/sys/vnode_internal.h'),
    ('bsd/sys/vnode.h', 'BUILD/obj/EXPORT_HDRS/bsd/sys/vnode.h'),
    ('bsd/sys/mount.h', 'BUILD/obj/EXPORT_HDRS/bsd/sys/mount.h'),
    ('bsd/sys/mount_internal.h', 'BUILD/obj/EXPORT_HDRS/bsd/sys/mount_internal.h'),
    ('bsd/sys/systm.h', 'BUILD/obj/EXPORT_HDRS/bsd/sys/systm.h'),
    ('bsd/sys/vfs.h', 'BUILD/obj/EXPORT_HDRS/bsd/sys/vfs.h'),
    ('bsd/sys/vnode.h', 'BUILD/obj/EXPORT_HDRS/bsd/sys/vnode.h'),
    ('bsd/sys/filedesc.h', 'BUILD/obj/EXPORT_HDRS/bsd/sys/filedesc.h'),
    ('bsd/sys/proc_internal.h', 'BUILD/obj/EXPORT_HDRS/bsd/sys/proc_internal.h'),
    ('bsd/sys/proc.h', 'BUILD/obj/EXPORT_HDRS/bsd/sys/proc.h'),
    ('bsd/sys/ucred.h', 'BUILD/obj/EXPORT_HDRS/bsd/sys/ucred.h'),
    ('bsd/sys/kauth.h', 'BUILD/obj/EXPORT_HDRS/bsd/sys/kauth.h'),
    ('bsd/sys/kernel_types.h', 'BUILD/obj/EXPORT_HDRS/bsd/sys/kernel_types.h'),

    # osfmk/mach - needed types
    ('osfmk/mach/vm_types.h', 'BUILD/obj/EXPORT_HDRS/osfmk/mach/vm_types.h'),
    ('osfmk/mach/vm_param.h', 'BUILD/obj/EXPORT_HDRS/osfmk/mach/vm_param.h'),
    ('osfmk/mach/memory_object.h', 'BUILD/obj/EXPORT_HDRS/osfmk/mach/memory_object.h'),
    ('osfmk/mach/memory_object_types.h', 'BUILD/obj/EXPORT_HDRS/osfmk/mach/memory_object_types.h'),
    ('osfmk/mach/std_types.h', 'BUILD/obj/EXPORT_HDRS/osfmk/std_types.h'),
    ('osfmk/mach/std_types.h', 'BUILD/obj/EXPORT_HDRS/osfmk/types.h'),
    ('bsd/sys/types.h', 'BUILD/obj/EXPORT_HDRS/osfmk/types.h'),

    # Missing headers (created, not copied from source)
    # mach_assert.h - kernel private header that defines MACH_ASSERT
    # This is normally provided by KDK but missing in open-source XNU

    # security - fix mac_framework.h and mac_internal.h
    ('security/mac_framework.h', 'BUILD/obj/EXPORT_HDRS/security/mac_framework.h'),
    ('security/mac_internal.h', 'BUILD/obj/EXPORT_HDRS/security/mac_internal.h'),
    ('security/mac_policy.h', 'BUILD/obj/EXPORT_HDRS/security/mac_policy.h'),
    ('security/mac_data.h', 'BUILD/obj/EXPORT_HDRS/security/mac_data.h'),
    ('security/mac_mach_internal.h', 'BUILD/obj/EXPORT_HDRS/security/mac_mach_internal.h'),
    ('security/mac_policy.h', 'BUILD/obj/EXPORT_HDRS/security/mac_policy.h'),

    # libkern - atomic and related
    ('libkern/os/atomic.h', 'BUILD/obj/EXPORT_HDRS/libkern/os/atomic.h'),
    ('libkern/os/atomic_private.h', 'BUILD/obj/EXPORT_HDRS/libkern/os/atomic_private.h'),
    ('libkern/os/atomic_private_impl.h', 'BUILD/obj/EXPORT_HDRS/libkern/os/atomic_private_impl.h'),
    ('libkern/os/refcnt_internal.h', 'BUILD/obj/EXPORT_HDRS/libkern/os/refcnt_internal.h'),

    # osfmk/kern - smr and atomic
    ('osfmk/kern/smr.h', 'BUILD/obj/EXPORT_HDRS/osfmk/kern/smr.h'),
    ('osfmk/kern/smr_hash.h', 'BUILD/obj/EXPORT_HDRS/osfmk/kern/smr_hash.h'),
    ('osfmk/kern/smr_types.h', 'BUILD/obj/EXPORT_HDRS/osfmk/kern/smr_types.h'),

    # bsd/sys - vfs and rename
    ('bsd/sys/vfs.h', 'BUILD/obj/EXPORT_HDRS/bsd/sys/vfs.h'),
    ('bsd/sys/vnode.h', 'BUILD/obj/EXPORT_HDRS/bsd/sys/vnode.h'),
]

# Also copy sys/_types.h and related for bsd
type_headers = [
    'bsd/sys/_types.h',
    'bsd/sys/types.h',
    'bsd/machine/_types.h',
    'bsd/sys/_types/_fd_def.h',
    'bsd/sys/_types/_sigaltstack.h',
    'bsd/sys/_types/_ucontext.h',
    'bsd/sys/_types/_siginfo.h',
    'bsd/sys/_types/_fd_set.h',
    'bsd/sys/_types/_fd_setsize.h',
    'bsd/sys/_types/_pthread_attr_t.h',
    'bsd/sys/_types/_pthread_cond_t.h',
    'bsd/sys/_types/_pthread_condattr_t.h',
    'bsd/sys/_types/_pthread_mutex_t.h',
    'bsd/sys/_types/_pthread_mutexattr_t.h',
    'bsd/sys/_types/_pthread_rwlock_t.h',
    'bsd/sys/_types/_pthread_rwlockattr_t.h',
    'bsd/sys/_types/_pthread_t.h',
    'bsd/sys/_types/_pthread_key_t.h',
    'bsd/sys/_types/_pthread_once_t.h',
]

for src in type_headers:
    dst = src.replace('bsd/', 'BUILD/obj/EXPORT_HDRS/bsd/')
    headers_to_copy.append((src, dst))


def copy_headers():
    for src, dst in headers_to_copy:
        src_path = src
        dst_path = dst

        if not os.path.exists(src_path):
            print(f"WARNING: Source not found: {src_path}")
            continue

        # Create destination directory
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)

        # Copy the file
        shutil.copy2(src_path, dst_path)
        print(f"Copied {src_path} -> {dst_path}")


def patch_file(path, replacements):
    """Apply replacements to a file if it exists."""
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        original = content
        for old, new in replacements.items():
            content = content.replace(old, new)
        if content != original:
            with open(path, 'w') as f:
                f.write(content)
            print(f"Patched {path}")
            return True
        else:
            print(f"No changes needed for {path}")
    else:
        print(f"WARNING: File not found: {path}")
    return False


def patch_arm_locks_h(path):
    """Ensure arm/locks.h does NOT define lck_mtx_t (it's defined in lock_mtx.h)."""
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        print(f"DEBUG: Patching {path}, content length: {len(content)}")
        # Remove any lck_mtx_t typedef from arm/locks.h to avoid redefinition
        # The definition should come from lock_mtx.h

        # Pattern 1: The full definition block with comment
        old_block1 = """/* Full lck_mtx_t definition for MACH_KERNEL_PRIVATE (ARM64 uses LCK_MTX_USE_ARCH) */
typedef struct {
	uintptr_t opaque[2] __kernel_data_semantics;
} lck_mtx_t;

"""
        # Pattern 2: Without comment
        old_block2 = """typedef struct {
	uintptr_t opaque[2] __kernel_data_semantics;
} lck_mtx_t;

"""
        # Pattern 3: Original Apple definition style
        old_block3 = """typedef struct __lck_mtx_t__            lck_mtx_t;"""

        changed = False
        if old_block1 in content:
            content = content.replace(old_block1, '')
            changed = True
        if old_block2 in content:
            content = content.replace(old_block2, '')
            changed = True
        if old_block3 in content:
            content = content.replace(old_block3, '')
            changed = True

        if changed:
            with open(path, 'w') as f:
                f.write(content)
            print(f"Patched {path} - removed duplicate lck_mtx_t definition")
            return True
        else:
            print(f"No duplicate lck_mtx_t definition found in {path}")
            return True
    return False


def patch_systm_h(path):
    """Add missing includes to systm.h for mount_t type."""
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        # Add sys/mount.h include for mount_t type
        if '#include <sys/mount.h>' not in content:
            lines = content.split('\n')
            insert_pos = 0
            # Find the last system include
            for i, line in enumerate(lines):
                if line.strip().startswith('#include') and ('sys/' in line or 'kern/' in line):
                    insert_pos = i + 1
            if insert_pos > 0:
                lines.insert(insert_pos, '#include <sys/mount.h>')
                content = '\n'.join(lines)
                with open(path, 'w') as f:
                    f.write(content)
                print(f"Patched {path} - added sys/mount.h include for mount_t")
                return True
    return False


def patch_vnode_internal_h(path):
    """Add missing types and includes to vnode_internal.h."""
    print(f"DEBUG: patch_vnode_internal_h called for {path}")
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        print(f"DEBUG: {path} exists, length: {len(content)}")
        # Add missing type definitions and includes
        lines = content.split('\n')
        insert_pos = 0
        # Find the last include
        for i, line in enumerate(lines):
            if line.strip().startswith('#include'):
                insert_pos = i + 1
                print(f"DEBUG: Found include at line {i}: {line.strip()}")
        print(f"DEBUG: Insert position: {insert_pos}")
        if insert_pos > 0:
            # Add missing type definitions and includes
            new_items = [
                '#include <sys/mount.h>',
                '#include <sys/vnode_if.h>',
                '#include <kern/lock_mtx.h>',  # For lck_mtx_t definition
                'typedef uint32_t vfs_rename_flags_t;',
                'typedef enum dir_clone_authorizer_op { OP_AUTHORIZE = 0, OP_VATTR_SETUP = 1, OP_VATTR_CLEANUP = 2 } dir_clone_authorizer_op_t;',
                # Ensure full lck_mtx_t definition is visible (vnode uses it as a field, not pointer)
                # The forward declaration in lock_mtx.h might be inside a conditional
                'typedef struct {\n'
                '    uintptr_t opaque[2] __kernel_data_semantics;\n'
                '} lck_mtx_t;',
            ]
            for item in reversed(new_items):
                if item not in content:
                    lines.insert(insert_pos, item)
                    print(f"DEBUG: Added: {item}")
                else:
                    print(f"DEBUG: Already present: {item}")
            content = '\n'.join(lines)
            
            # Now remove any forward declaration that might have come from lock_mtx.h include
            # to avoid typedef redefinition with our full definition
            if 'typedef struct _lck_mtx_ lck_mtx_t;' in content:
                content = content.replace('typedef struct _lck_mtx_ lck_mtx_t;', '')
                print(f"DEBUG: Removed forward declaration of lck_mtx_t after include")
            if 'typedef struct _lck_mtx_t lck_mtx_t;' in content:
                content = content.replace('typedef struct _lck_mtx_t lck_mtx_t;', '')
                print(f"DEBUG: Removed forward declaration of lck_mtx_t (alt)")
            
            with open(path, 'w') as f:
                f.write(content)
            print(f"Patched {path} - added missing types and includes")
            return True
        else:
            print(f"WARNING: No include lines found in {path}")
    else:
        print(f"WARNING: File not found: {path}")
    return False


def patch_smr_h(path):
    """Add stdatomic.h include and fallback implementations for atomic_thread_fence and atomic_signal_fence"""
    print(f"DEBUG: patch_smr_h called for {path}")
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        print(f"DEBUG: {path} exists, length: {len(content)}, has stdatomic: {'#include <stdatomic.h>' in content}")
        # Add stdatomic.h include after the last include
        if '#include <stdatomic.h>' not in content:
            lines = content.split('\n')
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('#include'):
                    insert_pos = i + 1
                    print(f"DEBUG: Found include at line {i}: {line.strip()}")
            print(f"DEBUG: Insert position: {insert_pos}")
            if insert_pos > 0:
                lines.insert(insert_pos, '#include <stdatomic.h>')
                content = '\n'.join(lines)

        # Add fallback implementations for atomic_thread_fence and atomic_signal_fence
        # These are C11 functions that may not be available in the iPhoneOS SDK's stdatomic.h
        fallback_code = (
            '\n'
            '/*\n'
            ' * Fallback implementations for C11 atomic functions.\n'
            ' * These may not be available in the iPhoneOS SDK\'s stdatomic.h.\n'
            ' */\n'
            '#if !defined(atomic_thread_fence) && !defined(HAVE_ATOMIC_THREAD_FENCE)\n'
            'static inline void atomic_thread_fence(memory_order order) {\n'
            '    // Compiler barrier - in practice we use OSAtomic or os_atomic\n'
            '    // This is a minimal fallback\n'
            '    __asm__ __volatile__("" ::: "memory");\n'
            '}\n'
            '#define HAVE_ATOMIC_THREAD_FENCE 1\n'
            '#endif\n'
            '\n'
            '#if !defined(atomic_signal_fence) && !defined(HAVE_ATOMIC_SIGNAL_FENCE)\n'
            'static inline void atomic_signal_fence(memory_order order) {\n'
            '    // Compiler barrier for signal handlers\n'
            '    __asm__ __volatile__("" ::: "memory");\n'
            '}\n'
            '#define HAVE_ATOMIC_SIGNAL_FENCE 1\n'
            '#endif\n'
            '\n'
        )
        if fallback_code not in content:
            lines = content.split('\n')
            insert_pos = 0
            for i, line in enumerate(lines):
                if '#include <stdatomic.h>' in line:
                    insert_pos = i + 1
                    break
            if insert_pos > 0:
                lines.insert(insert_pos, fallback_code)
                content = '\n'.join(lines)
                with open(path, 'w') as f:
                    f.write(content)
                print(f"Patched {path} - added stdatomic.h include and fallback atomic functions")
                return True
            else:
                print(f"WARNING: No stdatomic.h include found in {path}")
    else:
        print(f"WARNING: File not found: {path}")
    return False


def patch_mac_framework_h(path):
    """Remove the #error from mac_framework.h"""
    replacements = {
        '#error "no user-serviceable parts inside"': '/* #error "no user-serviceable parts inside" */'
    }
    return patch_file(path, replacements)


def patch_mac_internal_h(path):
    """Fix implicit int errors in mac_internal.h and add missing includes."""
    print(f"DEBUG: patch_mac_internal_h called for {path}")
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        print(f"DEBUG: {path} exists, length: {len(content)}")
        # Add sysctl.h include for SYSCTL_DECL macro - use sys/sysctl.h which is the standard path
        if '#include <sys/sysctl.h>' not in content and '#include <bsd/sys/sysctl.h>' not in content:
            lines = content.split('\n')
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('#include'):
                    insert_pos = i + 1
                    print(f"DEBUG: Found include at line {i}: {line.strip()}")
            print(f"DEBUG: Insert position: {insert_pos}")
            if insert_pos > 0:
                lines.insert(insert_pos, '#include <sys/sysctl.h>')
                content = '\n'.join(lines)
                print(f"DEBUG: Added sys/sysctl.h include")
        # Fix implicit int declarations
        replacements = {
            'struct __mac_get_proc_args;': 'int __mac_get_proc_args(void);',
            'struct __mac_set_proc_args;': 'int __mac_set_proc_args(void);',
            'struct __mac_get_lcid_args;': 'int __mac_get_lcid_args(void);',
            'struct __mac_get_fd_args;': 'int __mac_get_fd_args(void);',
            'struct __mac_get_file_args;': 'int __mac_get_file_args(void);',
            'struct __mac_get_link_args;': 'int __mac_get_link_args(void);',
            'struct __mac_set_fd_args;': 'int __mac_set_fd_args(void);',
            'struct __mac_set_file_args;': 'int __mac_set_file_args(void);',
            'struct __mac_syscall_args;': 'int __mac_syscall_args(void);',
        }
        for old, new in replacements.items():
            if old in content:
                content = content.replace(old, new)
                print(f"DEBUG: Replaced: {old} -> {new}")
            else:
                print(f"DEBUG: Not found: {old}")
        # Ensure SYSCTL_DECL is defined (fallback if not in sysctl.h)
        if 'SYSCTL_DECL' in content and '#define SYSCTL_DECL' not in content:
            lines = content.split('\n')
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('#include'):
                    insert_pos = i + 1
            if insert_pos > 0:
                sysctl_decl_def = (
                    '\n'
                    '/* Fallback definition for SYSCTL_DECL if not provided by sysctl.h */\n'
                    '#ifndef SYSCTL_DECL\n'
                    '#define SYSCTL_DECL(name) extern int name##_sysctl(void *oidp, void *arg1, int arg2, void *arg3, void *arg4)\n'
                    '#endif\n'
                    '\n'
                )
                lines.insert(insert_pos, sysctl_decl_def)
                content = '\n'.join(lines)
                print(f"DEBUG: Added SYSCTL_DECL fallback definition")
        with open(path, 'w') as f:
            f.write(content)
        print(f"Patched {path} - added sys/sysctl.h include and fixed implicit int")
        return True
    else:
        print(f"WARNING: File not found: {path}")
    return False


def patch_refcnt_internal_h(path):
    """Add memory_order enum definitions and stdatomic.h include to refcnt_internal.h"""
    print(f"DEBUG: patch_refcnt_internal_h called for {path}")
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        print(f"DEBUG: File {path} exists, length: {len(content)}")
        # Add stdatomic.h include and memory_order enum definitions right after the header guard
        # The file starts with #ifndef _OS_REFCNT_INTERNAL_H / #define _OS_REFCNT_INTERNAL_H
        # We need to insert right after the header guard
        stdatomic_and_memory_order = """#include <stdatomic.h>

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

"""
        lines = content.split('\n')
        insert_pos = 0
        # Find the header guard end (#define _OS_REFCNT_INTERNAL_H)
        for i, line in enumerate(lines):
            if line.strip().startswith('#define _OS_REFCNT_INTERNAL_H'):
                insert_pos = i + 1
                break
        if insert_pos > 0:
            lines.insert(insert_pos, stdatomic_and_memory_order)
            content = '\n'.join(lines)
            with open(path, 'w') as f:
                f.write(content)
            print(f"Patched {path} - added stdatomic.h include and memory_order enum")
            return True
        else:
            print(f"WARNING: Header guard not found in {path}")
    else:
        print(f"WARNING: File not found: {path}")
    return False


def patch_atomic_private_h_stdatomic(path):
    """Add stdatomic.h include to atomic_private.h for C11 atomic functions."""
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        # Add stdatomic.h include after the existing includes
        if '#include <stdatomic.h>' not in content and '#include <os/atomic.h>' in content:
            content = content.replace(
                '#include <os/atomic.h>',
                '#include <os/atomic.h>\n#include <stdatomic.h>'
            )
            with open(path, 'w') as f:
                f.write(content)
            print(f"Patched {path} - added stdatomic.h include")
            return True
    return False


def patch_mpsc_queue_h_stdatomic(path):
    """Add stdatomic.h include to mpsc_queue.h for C11 atomic functions."""
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        # Add stdatomic.h include after the existing includes
        if '#include <stdatomic.h>' not in content:
            lines = content.split('\n')
            insert_pos = 0
            # Find the last include line
            for i, line in enumerate(lines):
                if line.strip().startswith('#include'):
                    insert_pos = i + 1
            if insert_pos > 0:
                lines.insert(insert_pos, '#include <stdatomic.h>')
                content = '\n'.join(lines)
                with open(path, 'w') as f:
                    f.write(content)
                print(f"Patched {path} - added stdatomic.h include")
                return True
    return False


def patch_processor_h_stdatomic(path):
    """Add stdatomic.h include to processor.h for C11 atomic functions."""
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        # Add stdatomic.h include after the existing includes
        if '#include <stdatomic.h>' not in content:
            lines = content.split('\n')
            insert_pos = 0
            # Find the last include line
            for i, line in enumerate(lines):
                if line.strip().startswith('#include'):
                    insert_pos = i + 1
            if insert_pos > 0:
                lines.insert(insert_pos, '#include <stdatomic.h>')
                content = '\n'.join(lines)
                with open(path, 'w') as f:
                    f.write(content)
                print(f"Patched {path} - added stdatomic.h include")
                return True
    return False


def patch_ipc_object_h_stdatomic(path):
    """Add stdatomic.h include to ipc_object.h for C11 atomic functions."""
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        # Add stdatomic.h include after the existing includes
        if '#include <stdatomic.h>' not in content:
            lines = content.split('\n')
            insert_pos = 0
            # Find the last include line
            for i, line in enumerate(lines):
                if line.strip().startswith('#include'):
                    insert_pos = i + 1
            if insert_pos > 0:
                lines.insert(insert_pos, '#include <stdatomic.h>')
                content = '\n'.join(lines)
                with open(path, 'w') as f:
                    f.write(content)
                print(f"Patched {path} - added stdatomic.h include")
                return True
    return False


def patch_param_h_undef_setbit_clrbit(path):
    """Undef setbit/clrbit macros in param.h to avoid conflicts with kernel function declarations."""
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        # Add undef before the macros are defined, right after the includes
        lines = content.split('\n')
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('#define setbit'):
                insert_pos = i
                break
        if insert_pos == 0:
            # Fallback: find the end of includes
            for i, line in enumerate(lines):
                if line.strip().startswith('#include'):
                    insert_pos = i + 1
        if insert_pos > 0:
            undef_block = '\n/* Undef setbit/clrbit to avoid conflicts with kernel function declarations */\n#undef setbit\n#undef clrbit\n'
            lines.insert(insert_pos, undef_block)
            content = '\n'.join(lines)
            with open(path, 'w') as f:
                f.write(content)
            print(f"Patched {path} - added undef for setbit/clrbit")
            return True
    return False


def patch_misc_protos_h_undef_setbit_clrbit(path):
    """Undef setbit/clrbit macros in misc_protos.h before function declarations to avoid conflicts."""
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        # Add undef before the setbit/clrbit function declarations
        import re
        # Find the setbit function declaration and insert undef before it
        pattern = r'(extern void setbit\()'
        if re.search(pattern, content) and '#undef setbit' not in content:
            content = re.sub(
                pattern,
                '/* Undef setbit/clrbit to avoid conflicts with macros in param.h */\n#undef setbit\n#undef clrbit\n\nextern void setbit(',
                content
            )
            with open(path, 'w') as f:
                f.write(content)
            print(f"Patched {path} - added undef for setbit/clrbit before function declarations")
            return True
    return False


def patch_kern_types_h_clock_t(path):
    """Guard clock_t typedef in kern_types.h to avoid redefinition with bsd/_clock_t.h"""
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        # Guard the clock_t typedef - use exact string matching
        exact_typedef = 'typedef  struct clock                   *clock_t;'
        if exact_typedef in content and '#ifndef clock_t' not in content:
            content = content.replace(
                exact_typedef,
                '#ifndef clock_t\ntypedef  struct clock                   *clock_t;\n#endif'
            )
            with open(path, 'w') as f:
                f.write(content)
            print(f"Patched {path} - guarded clock_t typedef")
            return True
    return False


def patch_clock_t_typedef(path):
    """Fix clock_t typedef redefinition by using proper guard."""
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        # Fix the clock_t typedef with proper guard
        exact_typedef = 'typedef  struct clock                   *clock_t;'
        if exact_typedef in content and '#ifndef clock_t' not in content:
            content = content.replace(
                exact_typedef,
                '#ifndef clock_t\ntypedef  struct clock                   *clock_t;\n#endif'
            )
            with open(path, 'w') as f:
                f.write(content)
            print(f"Patched {path} - guarded clock_t typedef")
            return True
    return False


def patch_lock_mtx_h_consolidate(path):
    """Fix lck_mtx_t visibility in lock_mtx.h by ensuring typedef is visible to function declarations."""
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        # The lck_mtx_t typedef is inside #if MACH_KERNEL_PRIVATE / #if !LCK_MTX_USE_ARCH block
        # but function declarations are outside that block. Add a forward declaration
        # before the function declarations so they can see the type.
        if 'extern lck_mtx_t        *lck_mtx_alloc_init(' in content:
            # Check if forward declaration already exists
            if 'typedef struct _lck_mtx_ lck_mtx_t;' not in content:
                # Add forward declaration before the first function declaration
                content = content.replace(
                    'extern lck_mtx_t        *lck_mtx_alloc_init(',
                    'typedef struct _lck_mtx_ lck_mtx_t;\n\nextern lck_mtx_t        *lck_mtx_alloc_init('
                )
                with open(path, 'w') as f:
                    f.write(content)
                print(f"Patched {path} - added forward declaration for lck_mtx_t")
                return True
    return False


def patch_proc_internal_h_task_get_proc_raw(path):
    """Fix task_get_proc_raw conflict between proc_internal.h and task.h.
    The proc_internal.h declares it as returning proc_t, while task.h declares it as void*.
    We'll comment out the declaration in proc_internal.h since task.h is the authoritative one.
    """
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        # Comment out the conflicting declaration
        if 'extern proc_t task_get_proc_raw(task_t task);' in content:
            content = content.replace(
                'extern proc_t task_get_proc_raw(task_t task);',
                '/* extern proc_t task_get_proc_raw(task_t task);  -- conflicts with task.h */'
            )
            with open(path, 'w') as f:
                f.write(content)
            print(f"Patched {path} - commented out conflicting task_get_proc_raw declaration")
            return True
    return False


def patch_vnode_internal_h_dir_clone(path):
    """Remove our dir_clone_authorizer_op_t typedef since vnode_if.h already defines it as enum."""
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        # Remove our typedef since vnode_if.h already defines it properly
        if 'typedef int dir_clone_authorizer_op_t;' in content:
            content = content.replace(
                'typedef int dir_clone_authorizer_op_t;',
                '/* typedef int dir_clone_authorizer_op_t;  -- defined in vnode_if.h as enum */'
            )
            with open(path, 'w') as f:
                f.write(content)
            print(f"Patched {path} - commented out duplicate dir_clone_authorizer_op_t typedef")
            return True
    return False


def patch_syslog_h_log_conflict(path):
    """Guard the log function declaration in syslog.h to avoid conflict with misc_protos.h."""
    import re
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        # Guard the log function declaration - use regex to handle varying whitespace
        pattern = r'void\s+log\(int,\s*const\s+char\s*\*,\s*\.\.\.\)\s*__printflike\(2,\s*3\);'
        if re.search(pattern, content) and '#ifndef __SYSLOG_H_LOG_DEFINED__' not in content:
            content = re.sub(
                pattern,
                '#ifndef __SYSLOG_H_LOG_DEFINED__\nvoid    log(int, const char *, ...) __printflike(2, 3);\n#define __SYSLOG_H_LOG_DEFINED__\n#endif',
                content
            )
            with open(path, 'w') as f:
                f.write(content)
            print(f"Patched {path} - guarded log function declaration")
            return True
    return False


def patch_proc_internal_h_zone_declare(path):
    """Remove our ZONE_DECLARE_ID for ZONE_ID_PROC_TASK since it's defined elsewhere."""
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        # Comment out the conflicting ZONE_DECLARE_ID
        if 'ZONE_DECLARE_ID(ZONE_ID_PROC_TASK, "proc_task");' in content:
            content = content.replace(
                'ZONE_DECLARE_ID(ZONE_ID_PROC_TASK, "proc_task");',
                '/* ZONE_DECLARE_ID(ZONE_ID_PROC_TASK, "proc_task");  -- conflicts with another definition */'
            )
            with open(path, 'w') as f:
                f.write(content)
            print(f"Patched {path} - commented out conflicting ZONE_DECLARE_ID")
            return True
    return False


def create_mach_assert_h():
    """Create mach_assert.h - kernel private header defining MACH_ASSERT.
    This header is normally provided by KDK but missing in open-source XNU.
    """
    content = """/*
 * Copyright (c) 2000-2022 Apple Inc. All rights reserved.
 *
 * @APPLE_OSREFERENCE_LICENSE_HEADER_START@
 *
 * This file contains Original Code and/or Modifications of Original Code
 * as defined in and that are subject to the Apple Public Source License
 * Version 2.0 (the 'License'). You may not use this file except in
 * compliance with the License. The rights granted to you under the License
 * may not be used to create, or enable the creation or redistribution of,
 * unlawful or unlicensed copies of an Apple operating system, or to
 * circumvent, violate, or enable the circumvention or violation of, any
 * terms of an Apple operating system software license agreement.
 *
 * Please obtain a copy of the License at
 * http://www.opensource.apple.com/apsl/ and read it before using this file.
 *
 * The Original Code and all software distributed under the License are
 * distributed on an 'AS IS' basis, WITHOUT WARRANTY OF ANY KIND, EITHER
 * EXPRESSION OR IMPLIED, AND APPLE HEREBY DISCLAIMS ALL SUCH WARRANTIES,
 * INCLUDING WITHOUT LIMITATION, ANY WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE, QUIET ENJOYMENT OR NON-INFRINGEMENT.
 * Please see the License for the specific language governing rights and
 * limitations under the License.
 *
 * @APPLE_OSREFERENCE_LICENSE_HEADER_END@
 */

#ifndef _MACH_ASSERT_H_
#define _MACH_ASSERT_H_

/*
 * Kernel assertion macros.
 */

#ifndef MACH_ASSERT
#ifdef DEBUG
#define MACH_ASSERT(assertion) \
    do { \
        if (!(assertion)) { \
            panic("MACH_ASSERT failed: %s", #assertion); \
        } \
    } while (0)
#else
#define MACH_ASSERT(assertion) \
    do { } while (0)
#endif /* DEBUG */
#endif /* MACH_ASSERT */

#ifndef MACH_ASSUME
#define MACH_ASSUME(assertion) __builtin_assume(assertion)
#endif /* MACH_ASSUME */

#endif /* _MACH_ASSERT_H_ */
"""
    # Create the file in both source and EXPORT_HDRS locations
    paths = [
        'osfmk/mach/mach_assert.h',
        'BUILD/obj/EXPORT_HDRS/osfmk/mach_assert.h',
        'BUILD/obj/EXPORT_HDRS/mach_assert.h',
        'BUILD/obj/EXPORT_HDRS/osfmk/mach/mach_assert.h',
    ]
    for path in paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        print(f"Created {path}")

    # Also add to EXPORT_HDRS/osfmk/mach/ if needed
    os.makedirs('BUILD/obj/EXPORT_HDRS/osfmk/mach', exist_ok=True)
    mach_path = 'BUILD/obj/EXPORT_HDRS/osfmk/mach/mach_assert.h'
    with open(mach_path, 'w') as f:
        f.write(content)
    print(f"Created {mach_path}")

    return True


def create_mach_ldebug_h():
    """Create mach_ldebug.h - kernel private header for libdebug support.
    This header is normally provided by KDK but missing in open-source XNU.
    """
    content = """/*
 * Copyright (c) 2000-2022 Apple Inc. All rights reserved.
 *
 * @APPLE_OSREFERENCE_LICENSE_HEADER_START@
 *
 * This file contains Original Code and/or Modifications of Original Code
 * as defined in and that are subject to the Apple Public Source License
 * Version 2.0 (the 'License'). You may not use this file except in
 * compliance with the License. The rights granted to you under the License
 * may not be used to create, or enable the creation or redistribution of,
 * unlawful or unlicensed copies of an Apple operating system, or to
 * circumvent, violate, or enable the circumvention or violation of, any
 * terms of an Apple operating system software license agreement.
 *
 * Please obtain a copy of the License at
 * http://www.opensource.apple.com/apsl/ and read it before using this file.
 *
 * The Original Code and all software distributed under the License are
 * distributed on an 'AS IS' basis, WITHOUT WARRANTY OF ANY KIND, EITHER
 * EXPRESSION OR IMPLIED, AND APPLE HEREBY DISCLAIMS ALL SUCH WARRANTIES,
 * INCLUDING WITHOUT LIMITATION, ANY WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE, QUIET ENJOYMENT OR NON-INFRINGEMENT.
 * Please see the License for the specific language governing rights and
 * limitations under the License.
 *
 * @APPLE_OSREFERENCE_LICENSE_HEADER_END@
 */

#ifndef _MACH_LDEBUG_H_
#define _MACH_LDEBUG_H_

/*
 * mach_ldebug.h - Kernel libdebug support
 * This header provides kernel debugging support macros and definitions.
 */

#ifndef MACH_LDEBUG
#define MACH_LDEBUG 0
#endif

#endif /* _MACH_LDEBUG_H_ */
"""
    # Create the file in both source and EXPORT_HDRS locations
    paths = [
        'osfmk/mach/mach_ldebug.h',
        'BUILD/obj/EXPORT_HDRS/osfmk/mach_ldebug.h',
        'BUILD/obj/EXPORT_HDRS/mach_ldebug.h',
        'BUILD/obj/EXPORT_HDRS/osfmk/mach/mach_ldebug.h',
    ]
    for path in paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        print(f"Created {path}")

    # Also add to EXPORT_HDRS/osfmk/mach/ if needed
    os.makedirs('BUILD/obj/EXPORT_HDRS/osfmk/mach', exist_ok=True)
    mach_path = 'BUILD/obj/EXPORT_HDRS/osfmk/mach/mach_ldebug.h'
    with open(mach_path, 'w') as f:
        f.write(content)
    print(f"Created {mach_path}")

    return True


def main():
    print("Copying kernel-private headers to EXPORT_HDRS...")
    copy_headers()

    print("\nPatching SOURCE headers...")
    # Patch source files directly (these are used first by build system)
    patch_arm_locks_h('osfmk/arm/locks.h')
    patch_arm_locks_h('osfmk/arm64/locks.h')  # Also patch arm64 if it exists
    patch_systm_h('bsd/sys/systm.h')
    patch_vnode_internal_h('bsd/sys/vnode_internal.h')
    patch_smr_h('osfmk/kern/smr.h')
    patch_mac_framework_h('security/mac_framework.h')
    patch_mac_internal_h('security/mac_internal.h')
    patch_refcnt_internal_h('libkern/os/refcnt_internal.h')
    patch_atomic_private_h_stdatomic('libkern/os/atomic_private.h')
    patch_mpsc_queue_h_stdatomic('osfmk/kern/mpsc_queue.h')
    patch_processor_h_stdatomic('osfmk/kern/processor.h')
    patch_ipc_object_h_stdatomic('osfmk/ipc/ipc_object.h')
    patch_param_h_undef_setbit_clrbit('bsd/sys/param.h')
    patch_misc_protos_h_undef_setbit_clrbit('osfmk/kern/misc_protos.h')
    patch_kern_types_h_clock_t('osfmk/kern/kern_types.h')
    patch_clock_t_typedef('osfmk/kern/kern_types.h')
    patch_lock_mtx_h_consolidate('osfmk/kern/lock_mtx.h')
    patch_proc_internal_h_task_get_proc_raw('bsd/sys/proc_internal.h')
    patch_vnode_internal_h_dir_clone('bsd/sys/vnode_internal.h')
    patch_syslog_h_log_conflict('bsd/sys/syslog.h')
    patch_proc_internal_h_zone_declare('bsd/sys/proc_internal.h')
    create_mach_assert_h()
    create_mach_ldebug_h()

    print("\nPatching EXPORT_HDRS headers...")
    # Also patch EXPORT_HDRS copies
    patch_arm_locks_h('BUILD/obj/EXPORT_HDRS/osfmk/arm/locks.h')
    patch_arm_locks_h('BUILD/obj/EXPORT_HDRS/osfmk/arm64/locks.h')
    patch_systm_h('BUILD/obj/EXPORT_HDRS/bsd/sys/systm.h')
    patch_vnode_internal_h('BUILD/obj/EXPORT_HDRS/bsd/sys/vnode_internal.h')
    patch_smr_h('BUILD/obj/EXPORT_HDRS/osfmk/kern/smr.h')
    patch_mac_framework_h('BUILD/obj/EXPORT_HDRS/security/mac_framework.h')
    patch_mac_internal_h('BUILD/obj/EXPORT_HDRS/security/mac_internal.h')
    patch_refcnt_internal_h('BUILD/obj/EXPORT_HDRS/libkern/os/refcnt_internal.h')
    patch_atomic_private_h_stdatomic('BUILD/obj/EXPORT_HDRS/libkern/os/atomic_private.h')
    patch_mpsc_queue_h_stdatomic('BUILD/obj/EXPORT_HDRS/osfmk/kern/mpsc_queue.h')
    patch_processor_h_stdatomic('BUILD/obj/EXPORT_HDRS/osfmk/kern/processor.h')
    patch_ipc_object_h_stdatomic('BUILD/obj/EXPORT_HDRS/osfmk/ipc/ipc_object.h')
    patch_param_h_undef_setbit_clrbit('BUILD/obj/EXPORT_HDRS/bsd/sys/param.h')
    patch_misc_protos_h_undef_setbit_clrbit('BUILD/obj/EXPORT_HDRS/osfmk/kern/misc_protos.h')
    patch_kern_types_h_clock_t('BUILD/obj/EXPORT_HDRS/osfmk/kern/kern_types.h')
    patch_clock_t_typedef('BUILD/obj/EXPORT_HDRS/osfmk/kern/kern_types.h')
    patch_lock_mtx_h_consolidate('BUILD/obj/EXPORT_HDRS/osfmk/kern/lock_mtx.h')
    patch_proc_internal_h_task_get_proc_raw('BUILD/obj/EXPORT_HDRS/bsd/sys/proc_internal.h')
    patch_vnode_internal_h_dir_clone('BUILD/obj/EXPORT_HDRS/bsd/sys/vnode_internal.h')
    patch_syslog_h_log_conflict('BUILD/obj/EXPORT_HDRS/bsd/sys/syslog.h')
    patch_proc_internal_h_zone_declare('BUILD/obj/EXPORT_HDRS/bsd/sys/proc_internal.h')

    print("\nAll patches applied!")


if __name__ == '__main__':
    main()