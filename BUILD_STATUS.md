# XNU Kernel Build Status - Samsung Galaxy M30 (M30LTE) / Exynos 7904

## Current State: BLOCKED on iPhoneOS SDK C11 Atomic Functions

### ✅ FIXED (Major Progress)

1. **vnode_internal.h lck_mtx_t typedef redefinition** - FIXED
   - Removed custom lck_mtx_t typedef from vnode_internal.h
   - Now relies on lock_mtx.h full definition when MACH_KERNEL_PRIVATE=1
   - For ARM64, LCK_MTX_USE_ARCH=0 so full struct definition is available

2. **Security module kernel private defines** - FIXED
   - Added `override CFLAGS+=` to security/Makefile and security/conf/Makefile.template
   - Prevents environment CFLAGS override (MAKEFLAGS=-e)
   - mac_audit.c now compiles with -DKERNEL -DMACH_KERNEL_PRIVATE -DKERNEL_PRIVATE -DXNU_KERNEL_PRIVATE -DPRIVATE

3. **dir_clone_authorizer_op_t redefinition** - FIXED
   - Added `#ifndef dir_clone_authorizer_op_t` guard in vnode_internal.h patch
   - vnode_if.h already defines this enum

4. **stdatomic.h includes added** to multiple headers:
   - smr.h (with fallback atomic_thread_fence/atomic_signal_fence)
   - refcnt_internal.h
   - atomic_private.h
   - mpsc_queue.h
   - processor.h
   - ipc_object.h
   - ipc_space.h
   - ipc_port.h
   - thread.h

### ❌ REMAINING BLOCKERS

#### 1. C11 Atomic Functions Missing in iPhoneOS SDK (Critical)
**Error**: `call to undeclared function 'atomic_load_explicit'`, `atomic_fetch_or_explicit`, `atomic_init`, `atomic_store_explicit`, `atomic_exchange_explicit`, `atomic_signal_fence`, etc.

**Root Cause**: The iPhoneOS SDK's stdatomic.h doesn't declare all C11 atomic functions when compiling with `-mkernel` flag for arm64. This is an SDK limitation.

**Affected Headers**: refcnt_internal.h, mpsc_queue.h, processor.h, ipc_object.h, ipc_space.h, ipc_port.h, thread.h, smr.h

**Possible Solutions**:
- Implement missing atomic functions using compiler builtins (`__atomic_load`, `__atomic_store`, etc.) in a common header
- Modify headers to use kernel's os_atomic_* macros instead of direct C11 functions
- Use macOS SDK instead of iPhoneOS SDK for kernel build (but target is iOS)
- Patch SDK's stdatomic.h (not feasible in CI)

#### 2. clock_t Typedef Redefinition
**Error**: `typedef redefinition with different types ('struct clock *' vs '__darwin_clock_t')`
**File**: osfmk/kern/kern_types.h:221
**Fix**: Existing patch_kern_types_h_clock_t() should handle this - verify it's applied

#### 3. Scheduler Algorithm Not Enabled
**Error**: `Enable at least one scheduler algorithm in osfmk/conf/MASTER.XXX`
**Fix**: Need to configure scheduler in M30LTE machine config

#### 4. workq_threadreq_s Unknown Type
**Error**: `unknown type name 'workq_threadreq_s'` in bsd/sys/eventvar.h
**Fix**: Missing workqueue type definitions - need to include proper headers or define types

#### 5. copyinstr Conflicting Types
**Error**: `conflicting types for 'copyinstr'` in bsd/libkern/libkern.h:189
**Fix**: Declaration mismatch - need to check SDK vs kernel declarations

### Build Commands Tried
- Job-level CFLAGS with kernel defines → SDK header conflicts
- RC_NONARCH_CFLAGS in make command → Not picked up by security module Makefile
- override CFLAGS in security/Makefile → Works for security module, but other modules still fail

### Next Steps Required
1. **Implement C11 atomic function fallbacks** using compiler builtins in a common header (smr.h or new atomic_fallback.h)
2. **Fix clock_t typedef** - ensure patch_kern_types_h_clock_t is applied correctly
3. **Enable scheduler** in M30LTE machine config
4. **Add workqueue type definitions** for workq_threadreq_s
5. **Fix copyinstr declaration** mismatch

### CI Runs
- 42896464257: Fixed vnode_internal.h lck_mtx_t typedef
- 42898172840: Added MACH_KERNEL_PRIVATE to global CFLAGS (caused SDK conflicts)
- 42900262653: Added RC_NONARCH_CFLAGS to make command
- 42901635304: Used override directive for security module CFLAGS
- 42903697585: Added stdatomic.h to ipc_space.h, ipc_port.h, thread.h + dir_clone_authorizer_op_t guard

### Files Modified
- xnu/patches/copy_export_headers.py - Main patching script
- xnu/patches/patch_security_makefile.py - Security module CFLAGS
- xnu/patches/patch_security_conf_makefile.py - Security conf CFLAGS
- .github/workflows/xnu.yml - CI workflow

### Git Commits
- fdb587b: Add stdatomic.h includes to ipc_space.h, ipc_port.h, thread.h
- 6e59b93: Use override directive for CFLAGS in security module
- 9981da7: Add RC_NONARCH_CFLAGS to make command for kernel private defines
- 47c96cb: Add MACH_KERNEL_PRIVATE=1 to global CFLAGS/CXXFLAGS (reverted)
- e56f218: Fix vnode_internal.h: remove custom lck_mtx_t typedef to avoid redefinition