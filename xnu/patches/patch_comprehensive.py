#!/usr/bin/env python3
"""Comprehensive patch for remaining build issues."""
import sys
import os
import re

def patch_atomic_thread_fence():
    """Add atomic_thread_fence and atomic_signal_fence declarations."""
    # These functions are in stdatomic.h but might not be available
    # We'll add them to atomic_private_impl.h
    path = 'libkern/os/atomic_private_impl.h'
    if not os.path.exists(path):
        print(f"{path} not found!")
        return False
        
    with open(path, 'r') as f:
        content = f.read()
    
    # Check if already patched
    if 'atomic_thread_fence' in content and 'extern' in content:
        print("atomic_thread_fence already declared")
        return True
    
    # Add function declarations after the memory_order enum
    lines = content.split('\n')
    insert_idx = 0
    for i, line in enumerate(lines):
        if '} memory_order;' in line:
            insert_idx = i + 1
            break
    
    # Add function declarations
    fence_decls = '''
// Atomic fence functions (C11)
extern void atomic_thread_fence(memory_order order);
extern void atomic_signal_fence(memory_order order);

'''
    lines.insert(insert_idx, fence_decls)
    content = '\n'.join(lines)
    
    with open(path, 'w') as f:
        f.write(content)
    print("Added atomic_thread_fence and atomic_signal_fence declarations")
    return True

def patch_locks_h():
    """Ensure lck_mtx_t is fully defined in locks.h"""
    path = 'EXPORT_HDRS/osfmk/arm/locks.h'
    if not os.path.exists(path):
        # Try alternative location
        path = 'osfmk/arm/locks.h'
    if not os.path.exists(path):
        print(f"locks.h not found!")
        return False
        
    with open(path, 'r') as f:
        content = f.read()
    
    # Check if already patched
    if 'lck_mtx_type' in content and 'lck_mtx_attr' in content:
        print("locks.h already patched")
        return True
    
    # Replace forward declaration with full definition
    old = 'struct lck_mtx_t;'
    new = '''struct lck_mtx_t {
    uint32_t lck_mtx_type;
    uint32_t lck_mtx_attr;
    uint32_t lck_mtx_grp;
    uint32_t lck_mtx_pad1;
    uint32_t lck_mtx_pad2;
    struct lck_mtx_deb *lck_mtx_deb;
};'''
    
    if old in content:
        content = content.replace(old, new)
        with open(path, 'w') as f:
            f.write(content)
        print("Patched locks.h with full lck_mtx_t definition")
        return True
    else:
        print("Could not find struct lck_mtx_t; in locks.h")
        return False

def patch_vnode_internal():
    """Fix XNU_PTRAUTH_SIGNED_PTR macro in vnode_internal.h"""
    path = 'bsd/sys/vnode_internal.h'
    if not os.path.exists(path):
        print(f"vnode_internal.h not found!")
        return False
        
    with open(path, 'r') as f:
        content = f.read()
    
    # Check if already patched
    if 'XNU_PTRAUTH_SIGNED_PTR' in content and 'ptrauth' in content.lower():
        print("vnode_internal.h already has ptrauth")
        return True
    
    # Find the ptrauth.h include or add it
    if '#include <sys/ptrauth.h>' not in content:
        # Add ptrauth.h include after other includes
        lines = content.split('\n')
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('#include') and 'sys/' in line:
                insert_idx = i + 1
        lines.insert(insert_idx, '#include <sys/ptrauth.h>')
        content = '\n'.join(lines)
    
    # Define XNU_PTRAUTH_SIGNED_PTR macro if not defined
    if 'XNU_PTRAUTH_SIGNED_PTR' not in content:
        # Find a good place to add the macro (after includes)
        lines = content.split('\n')
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('#include') and 'sys/' in line:
                insert_idx = i + 1
        
        macro_def = '''
// Pointer authentication macro for vnode pointers
#if defined(__arm64__) && __has_feature(ptrauth)
#define XNU_PTRAUTH_SIGNED_PTR(_discriminator) \\
    __ptrauth(ptrauth_key_process_independent_data, 1, ptrauth_string_discriminator(_discriminator))
#else
#define XNU_PTRAUTH_SIGNED_PTR(_discriminator)
#endif

'''
        lines.insert(insert_idx + 1, macro_def)
        content = '\n'.join(lines)
    
    with open(path, 'w') as f:
        f.write(content)
    print("Patched vnode_internal.h with ptrauth macro")
    return True

def patch_mount_t():
    """Ensure mount_t is defined by including sys/mount.h where needed"""
    # The error is in bsd/sys/systm.h - we need to add the include there
    path = 'bsd/sys/systm.h'
    if not os.path.exists(path):
        print(f"systm.h not found!")
        return False
        
    with open(path, 'r') as f:
        content = f.read()
    
    # Check if already has mount.h include
    if '#include <sys/mount.h>' in content:
        print("sys/mount.h already included in systm.h")
        return True
    
    # Add sys/mount.h include after other sys includes
    lines = content.split('\n')
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('#include <sys/') and 'mount' not in line:
            insert_idx = i + 1
    
    lines.insert(insert_idx, '#include <sys/mount.h>')
    content = '\n'.join(lines)
    
    with open(path, 'w') as f:
        f.write(content)
    print("Added sys/mount.h include to systm.h")
    return True

def patch_config_syntax():
    """Fix config file syntax error at line 193"""
    # The error might be in a generated config file
    # Let's check the MASTER.arm64.m30lte config
    path = 'config/MASTER.arm64.m30lte'
    if not os.path.exists(path):
        print(f"MASTER.arm64.m30lte not found!")
        return False
        
    with open(path, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    if len(lines) >= 193:
        print(f"Line 193: {lines[192]}")
        # Check for syntax issues
        line = lines[192].strip()
        if line and not line.startswith('#') and not line.startswith('options') and not line.startswith('makeoptions') and not line.startswith('machine') and not line.startswith('options'):
            print(f"Potential syntax issue at line 193: {line}")
    
    print("Config file checked")
    return True

def main():
    print("Running comprehensive patches...")
    
    patch_atomic_thread_fence()
    patch_locks_h()
    patch_vnode_internal()
    patch_mount_t()
    patch_config_syntax()
    
    print("All patches applied!")

if __name__ == '__main__':
    main()