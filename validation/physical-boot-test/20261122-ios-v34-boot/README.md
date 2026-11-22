# iOS v34 physical boot — BOOT only, 2026-11-22 — KERNEL PANIC

Flashed only `validation/ios-candidate-v34-out/shim-boot.img` to BOOT, resumed,
booted once, forced back to TWRP, captured pstore immediately.
USERDATA/SYSTEM/RECOVERY untouched. BOOT readback skipped.

- Boot image SHA256: `24486a2652dbc9360da1caa6e747757a44aea111aef936e6b1b710ca88f66cf4`
- Fresh pstore: `13bd06ba44c5cd36d94ac657fa87f51246299f0c3315d2790a55b53720d7443b`
- 16,372 B, 209 records.

Result: kernel PANIC before userspace. Records 124-127:

```
load_init_program: attempting to load /usr/appleinternal/sbin/launchd.development
load_init_program: attempting to load /sbin/launchd
M30 IRT diag 0: enter state=0 vp=0xfffffff9cd646120 pager=0xfffffffab3babf80 mo=0x14000 kaddr[0:4]=e0010034
panic: lock_rw.c:877 Assertion failed: lock->lck_rw_owner != self->ctid : Lock already held
```

The 4 KB allocation succeeded, so `vn_rdwr()` ran in the page-fault path while
the `vm_object` lock was held and recursively acquired it. No further IRT
diagnostic was possible. This is a hard blocker for inline vnode reads.

v35 moves the read-only DSC symbol scan to a one-shot deferred kernel thread;
the fault path only patches an already-faulted in-memory page when the file
offset is known. No UI/lock-screen success claimed.
