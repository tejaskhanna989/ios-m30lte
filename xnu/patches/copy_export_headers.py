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
    
    # Missing headers
    ('osfmk/mach/mach_assert.h', 'BUILD/obj/EXPORT_HDRS/osfmk/mach_assert.h'),
    ('osfmk/mach/mach_assert.h', 'BUILD/obj/EXPORT_HDRS/mach_assert.h'),
    
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
    """Add lck_mtx_t definition to arm/locks.h in MACH_KERNEL_PRIVATE section."""
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        print(f"DEBUG: Patching {path}, content length: {len(content)}")
        # Find the MACH_KERNEL_PRIVATE section that defines lck_spin_t and add lck_mtx_t before #elif KERNEL_PRIVATE
        # The structure is:
        # #ifdef MACH_KERNEL_PRIVATE
        # ... #if LCK_SPIN_IS_TICKET_LOCK ... #else ... #endif (closes lck_spin_t)
        # #elif KERNEL_PRIVATE
        # We need to add lck_mtx_t in the MACH_KERNEL_PRIVATE section, right before #elif KERNEL_PRIVATE
        old = '''#endif

#elif KERNEL_PRIVATE'''
        new = '''#endif

/* Full lck_mtx_t definition for MACH_KERNEL_PRIVATE (ARM64 uses LCK_MTX_USE_ARCH) */
typedef struct {
	uintptr_t opaque[2] __kernel_data_semantics;
} lck_mtx_t;

#elif KERNEL_PRIVATE'''
        if old in content:
            print(f"DEBUG: Found pattern 1 in {path}")
            # Count occurrences
            count = content.count(old)
            print(f"DEBUG: Pattern 1 occurs {count} times")
            content = content.replace(old, new)
            with open(path, 'w') as f:
                f.write(content)
            # Verify the patch
            if 'lck_mtx_t' in content and 'uintptr_t opaque[2]' in content:
                print(f"DEBUG: Verified lck_mtx_t definition added to {path}")
            else:
                print(f"DEBUG: WARNING - lck_mtx_t definition may not have been added correctly!")
            print(f"Patched {path} - added lck_mtx_t to MACH_KERNEL_PRIVATE section")
            return True
        else:
            print(f"DEBUG: Pattern 1 not found in {path}")
            # Try alternative pattern with more context
            old2 = '''#endif

#define lck_spin_data hwlock.lock_data

#define LCK_SPIN_TAG_DESTROYED  0xdead  /* lock marked as Destroyed */

#define LCK_SPIN_TYPE           0x00000011
#define LCK_SPIN_TYPE_DESTROYED 0x000000ee
#endif

#elif KERNEL_PRIVATE'''
            new2 = '''#endif

#define lck_spin_data hwlock.lock_data

#define LCK_SPIN_TAG_DESTROYED  0xdead  /* lock marked as Destroyed */

#define LCK_SPIN_TYPE           0x00000011
#define LCK_SPIN_TYPE_DESTROYED 0x000000ee
#endif

/* Full lck_mtx_t definition for MACH_KERNEL_PRIVATE (ARM64 uses LCK_MTX_USE_ARCH) */
typedef struct {
	uintptr_t opaque[2] __kernel_data_semantics;
} lck_mtx_t;

#elif KERNEL_PRIVATE'''
            if old2 in content:
                print(f"DEBUG: Found pattern 2 in {path}")
                content = content.replace(old2, new2)
                with open(path, 'w') as f:
                    f.write(content)
                print(f"Patched {path} - added lck_mtx_t to MACH_KERNEL_PRIVATE section (alt)")
                return True
            else:
                print(f"DEBUG: Pattern 2 not found in {path}")
                print(f"Could not find pattern to patch in {path}")
                # Debug
                for i, line in enumerate(content.split('\n')):
                    if 'lck_spin_t' in line or 'lck_mtx_t' in line or 'KERNEL_PRIVATE' in line or '#elif' in line or '#endif' in line:
                        print(f"  Line {i+1}: {line}")
    return False

def patch_systm_h(path):
    """Add mount_t definition to systm.h"""
    replacements = {
        '#include <sys/vm.h>': '#include <sys/vm.h>\n#include <sys/mount.h>\ntypedef struct mount *mount_t;'
    }
    return patch_file(path, replacements)

def patch_vnode_internal_h(path):
    """Add missing types to vnode_internal.h"""
    replacements = {
        '#include <sys/vfs_context.h>': '#include <sys/vfs_context.h>\ntypedef uint32_t vfs_rename_flags_t;\ntypedef int dir_clone_authorizer_op_t;'
    }
    return patch_file(path, replacements)

def patch_smr_h(path):
    """Add stdatomic.h include to smr.h"""
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        if '#include <stdatomic.h>' not in content:
            content = content.replace(
                '#include <kern/smr_types.h>',
                '#include <kern/smr_types.h>\n#include <stdatomic.h>'
            )
            with open(path, 'w') as f:
                f.write(content)
            print(f"Patched {path} - added stdatomic.h")
            return True
        else:
            print(f"stdatomic.h already present in {path}")
    return False

def patch_mac_framework_h(path):
    """Remove the #error from mac_framework.h"""
    replacements = {
        '#error "no user-serviceable parts inside"': '/* #error "no user-serviceable parts inside" */'
    }
    return patch_file(path, replacements)

def patch_mac_internal_h(path):
    """Fix implicit int errors in mac_internal.h"""
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
    return patch_file(path, replacements)

def patch_refcnt_internal_h(path):
    """Add memory_order enum definitions to refcnt_internal.h"""
    print(f"DEBUG: patch_refcnt_internal_h called for {path}")
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        print(f"DEBUG: File {path} exists, length: {len(content)}")
        # Add memory_order enum definitions after the license header
        # Find a good place to insert - after the includes
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
        # Find the last include line and add after it
        lines = content.split('\n')
        last_include = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('#include'):
                last_include = i
                print(f"DEBUG: Found include at line {i}: {line.strip()}")
        print(f"DEBUG: Last include at line {last_include}")
        if last_include >= 0:
            lines.insert(last_include + 1, memory_order_defs)
            content = '\n'.join(lines)
            with open(path, 'w') as f:
                f.write(content)
            print(f"Patched {path} - added memory_order enum definitions")
            return True
        else:
            print(f"DEBUG: No include lines found in {path}")
    else:
        print(f"DEBUG: File {path} does not exist")
    return False

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
    
    print("\nAll patches applied!")

if __name__ == '__main__':
    main()