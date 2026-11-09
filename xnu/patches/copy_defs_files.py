#!/usr/bin/env python3
"""Copy .defs files to build directory for osfmk/mach."""
import sys
import os
import shutil

src_dir = 'osfmk/mach'
build_dir = 'BUILD/obj/DEVELOPMENT_ARM64_M30LTE/osfmk/mach'

# Create build directory
os.makedirs(build_dir, exist_ok=True)

# Copy all .defs files
defs_files = [
    'clock.defs', 'clock_priv.defs', 'clock_reply.defs', 'clock_types.defs',
    'mach_types.defs', 'std_types.defs',
    'audit_triggers.defs', 'clock_reply.defs', 'exc.defs',
    'host_notify_reply.defs', 'host_priv.defs', 'host_security.defs',
    'mach_exc.defs', 'mach_host.defs', 'mach_port.defs', 'mach_vm.defs',
    'mach_voucher.defs', 'mach_voucher_attr_control.defs',
    'memory_entry.defs', 'memory_error_notification.defs',
    'notify.defs', 'processor.defs', 'processor_set.defs',
    'task.defs', 'task_access.defs', 'telemetry_notification.defs',
    'thread_act.defs', 'vm_map.defs',
    'audit_triggers.defs', 'clock_reply.defs', 'coalition_notification.defs',
    'exc.defs', 'fairplayd_notification.defs', 'arcade_upcall.defs',
    'host_notify_reply.defs', 'host_priv.defs', 'host_security.defs',
    'mach_exc.defs', 'mach_host.defs', 'mach_port.defs', 'mach_vm.defs',
    'mach_voucher.defs', 'mach_voucher_attr_control.defs',
    'memory_entry.defs', 'memory_error_notification.defs',
    'notify.defs', 'processor.defs', 'processor_set.defs',
    'task.defs', 'task_access.defs', 'telemetry_notification.defs',
    'thread_act.defs', 'vm_map.defs',
    'mach_eventlink.defs', 'restartable.defs', 'sysdiagnose_notification.defs',
    'coalition_notification.defs', 'fairplayd_notification.defs',
    'arcade_upcall.defs', 'ktrace_background.defs',
    'mach_notify.defs', 'mach_test_upcall.defs',
    'memory_error_notification.defs', 'upl.defs', 'vfs_nspace.defs',
    'vm32_map.defs', 'iocompressionstats_notification.defs',
]

# Get all .defs files from source
for f in os.listdir('osfmk/mach'):
    if f.endswith('.defs'):
        src = os.path.join('osfmk/mach', f)
        dst = os.path.join(build_dir, f)
        shutil.copy2(src, dst)
        print(f"Copied {f}")

print(f"Copied .defs files to {build_dir}")