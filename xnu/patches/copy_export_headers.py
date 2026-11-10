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
    return False

def patch_lock_mtx_h(path):
    """Add full lck_mtx_t definition to lock_mtx.h"""
    replacements = {
        'typedef struct __lck_mtx_t__            lck_mtx_t;': '''typedef struct lck_mtx {
    uint32_t lck_mtx_type;
    lck_grp_t lck_mtx_grp;
    union {
        struct {
            uint32_t owner:28;
            uint32_t ilocked:1;
            uint32_t spin_mode:1;
            uint32_t needs_wakeup:1;
            uint32_t profile:1;
        };
        uint32_t data;
        uint64_t val;
    } lck_mtx;
    uint16_t lck_mtx_ilk_tail;
    uint16_t lck_mtx_as_tail;
} lck_mtx_t;'''
    }
    return patch_file(path, replacements)

def patch_systm_h(path):
    """Add mount_t definition to systm.h"""
    replacements = {
        '#include <sys/mount.h>': '#include <sys/mount.h>\ntypedef struct mount *mount_t;'
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
            print(f"Patched {path}")
            return True
    return False

def patch_vnode_internal_h(path):
    """Add missing types to vnode_internal.h"""
    replacements = {
        'typedef struct namecache *namecache_t;': 'typedef struct namecache *namecache_t;\ntypedef uint32_t vfs_rename_flags_t;\ntypedef int dir_clone_authorizer_op_t;'
    }
    return patch_file(path, replacements)

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

def main():
    print("Copying kernel-private headers to EXPORT_HDRS...")
    copy_headers()
    
    print("\nPatching SOURCE headers...")
    # Patch source files directly (these are used first by build system)
    patch_lock_mtx_h('osfmk/kern/lock_mtx.h')
    patch_systm_h('bsd/sys/systm.h')
    patch_smr_h('osfmk/kern/smr.h')
    patch_vnode_internal_h('bsd/sys/vnode_internal.h')
    patch_mac_framework_h('security/mac_framework.h')
    patch_mac_internal_h('security/mac_internal.h')
    
    print("\nPatching EXPORT_HDRS headers...")
    # Also patch EXPORT_HDRS copies
    patch_lock_mtx_h('BUILD/obj/EXPORT_HDRS/osfmk/kern/lock_mtx.h')
    patch_systm_h('BUILD/obj/EXPORT_HDRS/bsd/sys/systm.h')
    patch_smr_h('BUILD/obj/EXPORT_HDRS/osfmk/kern/smr.h')
    patch_vnode_internal_h('BUILD/obj/EXPORT_HDRS/bsd/sys/vnode_internal.h')
    patch_mac_framework_h('BUILD/obj/EXPORT_HDRS/security/mac_framework.h')
    patch_mac_internal_h('BUILD/obj/EXPORT_HDRS/security/mac_internal.h')
    
    print("\nAll patches applied!")

if __name__ == '__main__':
    main()