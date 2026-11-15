#!/usr/bin/env python3
"""Patch security/mac_audit.c to add required kernel includes and ptrauth macro BEFORE vnode_internal.h."""
import sys

with open('security/mac_audit.c', 'r') as f:
    content = f.read()

# Find the vnode_internal.h include line and insert our definitions BEFORE it
# The current includes include vnode_internal.h early:
# #include <sys/vnode_internal.h>

new_includes = '''/* Include kernel private headers for full type definitions used by vnode_internal.h */
#include <kern/lock_mtx.h>
#include <kern/locks.h>
#include <ptrauth.h>

/* Define XNU_PTRAUTH_SIGNED_PTR for pointer authentication on ARM64.
 * This macro is used by vnode_internal.h for pointer signing.
 * On ARM64 with ptrauth support, it applies the ptrauth attribute.
 * On other platforms or when disabled, it's a no-op. */
#if defined(__arm64__) && __has_feature(ptrauth)
#define XNU_PTRAUTH_SIGNED_PTR(_discriminator) \
    __ptrauth(ptrauth_key_process_independent_data, 1, ptrauth_string_discriminator(_discriminator))
#else
#define XNU_PTRAUTH_SIGNED_PTR(_discriminator)
#endif

/* Function prototypes for audit stub functions to avoid -Wmissing-prototypes */
int mac_system_check_audit(struct ucred *cred, void *record, int length);
int mac_system_check_auditon(struct ucred *cred, int cmd);
int mac_system_check_auditctl(struct ucred *cred, struct vnode *vp);
int mac_proc_check_getauid(struct proc *curp);
int mac_proc_check_setauid(struct proc *curp, uid_t auid);
int mac_proc_check_getaudit(struct proc *curp, struct auditinfo_addr *aip);
int mac_proc_check_setaudit(struct proc *curp, struct auditinfo_addr *aip);
int mac_proc_check_getaudit_addr(struct proc *curp, struct auditinfo_addr *aip, int *sizep);
int mac_proc_check_setaudit_addr(struct proc *curp, struct auditinfo_addr *aip);
int mac_system_check_auditctl(struct ucred *cred, struct vnode *vp);

'''

# Insert before #include <sys/vnode_internal.h>
new_content = content.replace(
    '#include <sys/vnode_internal.h>',
    new_includes + '#include <sys/vnode_internal.h>'
)

with open('security/mac_audit.c', 'w') as f:
    f.write(new_content)

print("Patched security/mac_audit.c with required includes and XNU_PTRAUTH_SIGNED_PTR macro BEFORE vnode_internal.h")

# Verify
with open('security/mac_audit.c', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[:55]):
        print(f"  {i+1}: {line}")
