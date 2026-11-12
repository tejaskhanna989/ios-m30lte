#!/usr/bin/env python3
"""Unified generator for manual component configs.

This script generates proper config files and Makefiles from source file lists,
with correct VPATH, unique OBJS, and proper CFILES/CXXFILES/SFILES separation.
"""

import os
import re
import sys

# ============================================================
# COMPONENT DEFINITIONS
# Each component defines its source files relative to xnu-source root
# Based on XNU 8796.141.3 source tree structure
# ============================================================

COMPONENTS = {
    'bsd': {
        'config_dir': 'bsd/conf',
        'source_files': [
            # kern
            'sys/kern/kern_clock.c',
            'sys/kern/kern_descrip.c',
            'sys/kern/kern_env.c',
            'sys/kern/kern_exec.c',
            'sys/kern/kern_exit.c',
            'sys/kern/kern_fork.c',
            'sys/kern/kern_init.c',
            'sys/kern/kern_jail.c',
            'sys/kern/kern_lock.c',
            'sys/kern/kern_malloc.c',
            'sys/kern/kern_man.c',
            'sys/kern/kern_module.c',
            'sys/kern/kern_monotonic.c',
            'sys/kern/kern_mutex.c',
            'sys/kern/kern_ntptime.c',
            'sys/kern/kern_pax.c',
            'sys/kern/kern_pgrp.c',
            'sys/kern/kern_proc.c',
            'sys/kern/kern_prot.c',
            'sys/kern/kern_prot2.c',
            'sys/kern/kern_pset.c',
            'sys/kern/kern_resource.c',
            'sys/kern/kern_rwlock.c',
            'sys/kern/kern_sched.c',
            'sys/kern/kern_sig.c',
            'sys/kern/kern_subr.c',
            'sys/kern/kern_syscall.c',
            'sys/kern/kern_sysctl.c',
            'sys/kern/kern_thread.c',
            'sys/kern/kern_time.c',
            'sys/kern/kern_timeout.c',
            'sys/kern/kern_umtx.c',
            'sys/kern/kern_xucred.c',
            'sys/kern/subr_autoconf.c',
            'sys/kern/subr_blist.c',
            'sys/kern/subr_bus.c',
            'sys/kern/subr_cpufreq.c',
            'sys/kern/subr_counter.c',
            'sys/kern/subr_cpuset.c',
            'sys/kern/subr_devicestat.c',
            'sys/kern/subr_disk.c',
            'sys/kern/subr_eventhandler.c',
            'sys/kern/subr_firmware.c',
            'sys/kern/subr_gtaskqueue.c',
            'sys/kern/subr_hhook.c',
            'sys/kern/subr_knote.c',
            'sys/kern/subr_kqueue.c',
            'sys/kern/subr_kobj.c',
            'sys/kern/subr_kthread.c',
            'sys/kern/subr_log.c',
            'sys/kern/subr_lro.c',
            'sys/kern/subr_mem.c',
            'sys/kern/subr_module.c',
            'sys/kern/subr_msgbuf.c',
            'sys/kern/subr_param.c',
            'sys/kern/subr_pcpu.c',
            'sys/kern/subr_power.c',
            'sys/kern/subr_prf.c',
            'sys/kern/subr_prof.c',
            'sys/kern/subr_rman.c',
            'sys/kern/subr_sbuf.c',
            'sys/kern/subr_sdt.c',
            'sys/kern/subr_sleepqueue.c',
            'sys/kern/subr_smp.c',
            'sys/kern/subr_turnstile.c',
            'sys/kern/subr_unit.c',
            'sys/kern/subr_witness.c',
            'sys/kern/sys_generic.c',
            'sys/kern/sys_process.c',
            # vfs
            'sys/kern/vfs_acl.c',
            'sys/kern/vfs_aio.c',
            'sys/kern/vfs_bio.c',
            'sys/kern/vfs_cache.c',
            'sys/kern/vfs_default.c',
            'sys/kern/vfs_export.c',
            'sys/kern/vfs_hash.c',
            'sys/kern/vfs_init.c',
            'sys/kern/vfs_lockf.c',
            'sys/kern/vfs_lookup.c',
            'sys/kern/vfs_mount.c',
            'sys/kern/vfs_mountroot.c',
            'sys/kern/vfs_subr.c',
            'sys/kern/vfs_syscalls.c',
            'sys/kern/vfs_vnops.c',
            # net (essential for networking symbols)
            'net/if.c',
            'net/if_arp.c',
            'net/if_dl.c',
            'net/if_ether.c',
            'net/if_media.c',
            'net/if_types.c',
            'net/netisr.c',
            'net/radix.c',
            'net/route.c',
            'net/rtsock.c',
            'netinet/in.c',
            'netinet/in_pcb.c',
            'netinet/in_proto.c',
            'netinet/ip_input.c',
            'netinet/ip_output.c',
            'netinet/ip_icmp.c',
            'netinet/ip_var.c',
            'netinet/tcp_input.c',
            'netinet/tcp_output.c',
            'netinet/tcp_subr.c',
            'netinet/tcp_timer.c',
            'netinet/tcp_var.c',
            'netinet/udp_usrreq.c',
            # mbuf (essential for mbuf symbols)
            'sys/kern/mbuf.c',
            'sys/kern/mbuf_ml.c',
            'sys/kern/mbuf_pkthdr.c',
            # ufs/ubc (for ubc_create_upl)
            'ufs/ubc_subr.c',
            'ufs/ubc_alloc.c',
            # arm64
            'arm64/arm64_mem.c',
            'arm64/atc.c',
            'arm64/locore.s',
            'arm64/machdep.c',
            'arm64/pmap.c',
            'arm64/pmap_data.c',
            'arm64/pmap_ppl.c',
            'arm64/sigtramp.s',
            'arm64/board_config.c',
        ]
    },
    'iokit': {
        'config_dir': 'iokit/conf',
        'source_files': [
            # Core IOKit
            'iokit/IOBSD/IOBSD.cpp',
            'iokit/IOBufferMemoryDescriptor.cpp',
            'iokit/IOCatalogue.cpp',
            'iokit/IOCommand.cpp',
            'iokit/IOCommandGate.cpp',
            'iokit/IOCommandPool.cpp',
            'iokit/IODataQueue.cpp',
            'iokit/IODeviceMemory.cpp',
            'iokit/IODeviceTreeSupport.cpp',
            'iokit/IODMACommand.cpp',
            'iokit/IODMAEventSource.cpp',
            'iokit/IODTMatching.cpp',
            'iokit/IODTNVRAM.cpp',
            'iokit/IOEventSource.cpp',
            'iokit/IOFilterInterruptEventSource.cpp',
            'iokit/IOFramebuffer.cpp',
            'iokit/IOGeneralMemoryDescriptor.cpp',
            'iokit/IOInterruptController.cpp',
            'iokit/IOInterruptEventSource.cpp',
            'iokit/IOIterator.cpp',
            # IOKit/ subdirectories (essential)
            'iokit/IOKit/IOLib.cpp',
            'iokit/IOKit/IOLog.cpp',
            'iokit/IOKit/IOPanic.cpp',
            'iokit/IOKit/IOService.cpp',
            'iokit/IOKit/IOUserClient.cpp',
            'iokit/IOKit/IOWorkLoop.cpp',
            'iokit/IOKit/OSSerialize.cpp',
            'iokit/IOKit/OSArray.cpp',
            'iokit/IOKit/OSData.cpp',
            'iokit/IOKit/OSDictionary.cpp',
            'iokit/IOKit/OSNumber.cpp',
            'iokit/IOKit/OSObject.cpp',
            'iokit/IOKit/OSString.cpp',
            'iokit/IOKit/notification/IONotificationRegistrar.cpp',
            'iokit/IOKit/notification/IONotifier.cpp',
            'iokit/IOKit/notification/IONotifierRegistry.cpp',
            # iokit/ root level (essential)
            'iokit/IOKitServer.cpp',
            'iokit/IOKitDiagnostics.cpp',
            'iokit/IOKitKeys.cpp',
            'iokit/IOLog.cpp',
            'iokit/IOMemoryDescriptor.cpp',
            'iokit/IOMapper.cpp',
            'iokit/IOMapperEndpoint.cpp',
            'iokit/IOMapperMemoryDescriptor.cpp',
            'iokit/IOMapperSpec.cpp',
            'iokit/IOMapperSpecArray.cpp',
            'iokit/IOMPAccess.cpp',
            'iokit/IOMPContainer.cpp',
            'iokit/IOMPDevice.cpp',
            'iokit/IOMPSDevice.cpp',
            'iokit/IOMPT.cpp',
            'iokit/IOPlatformDevice.cpp',
            'iokit/IOPlatformExpert.cpp',
            'iokit/IOPMPowerSource.cpp',
            'iokit/IOPMrootDomain.cpp',
            'iokit/IOPMScheduler.cpp',
            'iokit/IOPoller.cpp',
            'iokit/IOPolicy.cpp',
            'iokit/IOReport.cpp',
            'iokit/IOReportChannel.cpp',
            'iokit/IOReportGroup.cpp',
            'iokit/IOReportGroups.cpp',
            'iokit/IOReportLegend.cpp',
            'iokit/IOReportTypes.cpp',
            'iokit/IOResource.cpp',
            'iokit/IOResourceOwner.cpp',
            'iokit/IOService.cpp',
            'iokit/IOServiceGroup.cpp',
            'iokit/IOServiceMatching.cpp',
            'iokit/IOServiceOrdering.cpp',
            'iokit/IOSharedDataQueue.cpp',
            'iokit/IOSharedDataQueueClient.cpp',
            'iokit/IOStorage.cpp',
            'iokit/IOStorageController.cpp',
            'iokit/IOStorageFamily.cpp',
            'iokit/IOStorageRedundancyController.cpp',
            'iokit/IOStream.cpp',
            'iokit/IOStreamUserClient.cpp',
            'iokit/IOStreamUserClientInterface.cpp',
            'iokit/IOSystemReporter.cpp',
            'iokit/IOTime.cpp',
            'iokit/IOTimeStamp.cpp',
            'iokit/IOTransfer.cpp',
            'iokit/IOUserClient.cpp',
            'iokit/IOUserClientClass.cpp',
            'iokit/IOUserClientMethod.cpp',
            'iokit/IOUserClientNotification.cpp',
            'iokit/IOUserClientProperty.cpp',
            'iokit/IOWorkLoop.cpp',
            'iokit/IOWorkQueue.cpp',
        ]
    },
    'osfmk': {
        'config_dir': 'osfmk/conf',
        'source_files': [
            # kern (essential)
            'osfmk/kern/kern_clock.c',
            'osfmk/kern/kern_descrip.c',
            'osfmk/kern/kern_env.c',
            'osfmk/kern/kern_exec.c',
            'osfmk/kern/kern_exit.c',
            'osfmk/kern/kern_fork.c',
            'osfmk/kern/kern_init.c',
            'osfmk/kern/kern_jail.c',
            'osfmk/kern/kern_lock.c',
            'osfmk/kern/kern_malloc.c',
            'osfmk/kern/kern_man.c',
            'osfmk/kern/kern_module.c',
            'osfmk/kern/kern_monotonic.c',
            'osfmk/kern/kern_mutex.c',
            'osfmk/kern/kern_ntptime.c',
            'osfmk/kern/kern_pax.c',
            'osfmk/kern/kern_pgrp.c',
            'osfmk/kern/kern_proc.c',
            'osfmk/kern/kern_prot.c',
            'osfmk/kern/kern_prot2.c',
            'osfmk/kern/kern_pset.c',
            'osfmk/kern/kern_resource.c',
            'osfmk/kern/kern_rwlock.c',
            'osfmk/kern/kern_sched.c',
            'osfmk/kern/kern_sig.c',
            'osfmk/kern/kern_subr.c',
            'osfmk/kern/kern_syscall.c',
            'osfmk/kern/kern_sysctl.c',
            'osfmk/kern/kern_thread.c',
            'osfmk/kern/kern_time.c',
            'osfmk/kern/kern_timeout.c',
            'osfmk/kern/kern_umtx.c',
            'osfmk/kern/kern_xucred.c',
            'osfmk/kern/subr_autoconf.c',
            'osfmk/kern/subr_blist.c',
            'osfmk/kern/subr_bus.c',
            'osfmk/kern/subr_cpufreq.c',
            'osfmk/kern/subr_counter.c',
            'osfmk/kern/subr_cpuset.c',
            'osfmk/kern/subr_devicestat.c',
            'osfmk/kern/subr_disk.c',
            'osfmk/kern/subr_eventhandler.c',
            'osfmk/kern/subr_firmware.c',
            'osfmk/kern/subr_gtaskqueue.c',
            'osfmk/kern/subr_hhook.c',
            'osfmk/kern/subr_knote.c',
            'osfmk/kern/subr_kqueue.c',
            'osfmk/kern/subr_kobj.c',
            'osfmk/kern/subr_kthread.c',
            'osfmk/kern/subr_log.c',
            'osfmk/kern/subr_lro.c',
            'osfmk/kern/subr_mem.c',
            'osfmk/kern/subr_module.c',
            'osfmk/kern/subr_msgbuf.c',
            'osfmk/kern/subr_param.c',
            'osfmk/kern/subr_pcpu.c',
            'osfmk/kern/subr_power.c',
            'osfmk/kern/subr_prf.c',
            'osfmk/kern/subr_prof.c',
            'osfmk/kern/subr_rman.c',
            'osfmk/kern/subr_sbuf.c',
            'osfmk/kern/subr_sdt.c',
            'osfmk/kern/subr_sleepqueue.c',
            'osfmk/kern/subr_smp.c',
            'osfmk/kern/subr_turnstile.c',
            'osfmk/kern/subr_unit.c',
            'osfmk/kern/subr_witness.c',
            'osfmk/kern/sys_generic.c',
            'osfmk/kern/sys_process.c',
            # locks (essential for lck_mtx, lck_rw, lck_spin symbols)
            'osfmk/kern/lock.c',
            'osfmk/kern/lock_mtx.c',
            'osfmk/kern/lock_rw.c',
            'osfmk/kern/lock_spin.c',
            # vm (essential for vm_* symbols)
            'osfmk/vm/vm_map.c',
            'osfmk/vm/vm_page.c',
            'osfmk/vm/vm_pageout.c',
            'osfmk/vm/vm_object.c',
            'osfmk/vm/vm_kern.c',
            'osfmk/vm/vm_fault.c',
            # ipc (essential for task/port symbols)
            'osfmk/kern/ipc_kobject.c',
            'osfmk/kern/ipc_mqueue.c',
            'osfmk/kern/ipc_port.c',
            'osfmk/kern/ipc_pset.c',
            'osfmk/kern/ipc_space.c',
            'osfmk/kern/ipc_tt.c',
            'osfmk/kern/ipc_hash.c',
            'osfmk/kern/ipc_kmsg.c',
            'osfmk/kern/ipc_notify.c',
            'osfmk/kern/ipc_right.c',
            # task/thread (essential for task/port symbols)
            'osfmk/kern/task.c',
            'osfmk/kern/thread.c',
            'osfmk/kern/sched_prim.c',
            'osfmk/kern/turnstile.c',
            # clock/timer
            'osfmk/kern/clock.c',
            'osfmk/kern/clock_prim.c',
            'osfmk/kern/timer.c',
            # host/processor
            'osfmk/kern/host.c',
            'osfmk/kern/host_priv.c',
            'osfmk/kern/processor.c',
            'osfmk/kern/processor_set.c',
            'osfmk/kern/ledger.c',
        ]
    },
    'pexpert': {
        'config_dir': 'pexpert/conf',
        'source_files': [
            'pexpert/arm64/board_config.c',
            'pexpert/arm64/m30lte/board_config.c',
            'pexpert/arm64/machdep.c',
            'pexpert/arm64/pmap.c',
            'pexpert/arm64/startup.c',
            'pexpert/arm64/m30lte/machdep.c',
        ]
    },
    'libkern': {
        'config_dir': 'libkern/conf',
        'source_files': [
            'libkern/kern_bcops.c',
            'libkern/kern_kalloc.c',
            'libkern/kern_kalloc_vm.c',
            'libkern/kern_ktrace.c',
            'libkern/kern_lock.c',
            'libkern/kern_malloc.c',
            'libkern/kern_pcpu.c',
            'libkern/kern_pmap.c',
            'libkern/kern_quantize.c',
            'libkern/kern_sched.c',
            'libkern/kern_semaphore.c',
            'libkern/kern_turnstile.c',
            'libkern/kern_xmm.c',
            'libkern/libkern_c++abi.cpp',
            'libkern/libkern_c++.cpp',
            'libkern/libkern_exception.cpp',
            'libkern/libkern_init.cpp',
            'libkern/libkern_i386.cpp',
            'libkern/libkern_new.cpp',
            'libkern/libkern_os.cpp',
            'libkern/libkern_string.cpp',
            'libkern/libkern_time.cpp',
            'libkern/libkern_vm.cpp',
            'libkern/libkern_zalloc.c',
            'libkern/mach_vm.c',
            'libkern/obj.cpp',
            'libkern/os/atomic.c',
            'libkern/os/atomic_arm.c',
            'libkern/os/atomic_arm64.c',
            'libkern/os/block.c',
            'libkern/os/byte_order.c',
            'libkern/os/checksum.c',
            'libkern/os/contigmem.c',
            'libkern/os/cputype.c',
            'libkern/os/dispatch_queue.c',
            'libkern/os/fastpath.c',
            'libkern/os/fastpath_locks.c',
            'libkern/os/locks.c',
            'libkern/os/locks_cond.c',
            'libkern/os/locks_lck.c',
            'libkern/os/locks_mtx.c',
            'libkern/os/locks_rw.c',
            'libkern/os/malloc.c',
            'libkern/os/OSAtomic.c',
            'libkern/os/OSCompareAndSwap.c',
            'libkern/os/OSNumber.c',
            'libkern/os/OSObject.cpp',
            'libkern/os/OSQueue.cpp',
            'libkern/os/OSRuntime.cpp',
            'libkern/os/OSString.cpp',
            'libkern/os/refcnt.c',
            'libkern/os/thread_call.c',
            'libkern/os/tsd.c',
            'libkern/pool.c',
            'libkern/queue.c',
            'libkern/random.c',
            'libkern/section_data.c',
            'libkern/slab.c',
            'libkern/string.c',
            'libkern/vm/vm_map.c',
            'libkern/vm/vm_page.c',
            'libkern/vm/vm_pageout.c',
            'libkern/zalloc.c',
            # crypto (for SHA1 symbols)
            'libkern/crypto/sha1.c',
            'libkern/crypto/sha2.c',
            # ARM64 assembly
            'libkern/arm64/atomic.s',
            'libkern/arm64/libkern.s',
            'libkern/arm64/locore.s',
            'libkern/arm64/startup.s',
        ]
    },
    'libsa': {
        'config_dir': 'libsa/conf',
        'source_files': [
            'libsa/arm64/arm64_mem.c',
            'libsa/arm64/atc.c',
            'libsa/arm64/locore.s',
            'libsa/arm64/machdep.c',
            'libsa/arm64/pmap.c',
            'libsa/arm64/startup.s',
        ]
    },
    'san': {
        'config_dir': 'san/conf',
        'source_files': [
            'san/san.c',
            'san/san_policy.c',
        ]
    },
    'security': {
        'config_dir': 'security/conf',
        'source_files': [
            'security/mac_audit.c',
            'security/mac_base.c',
            'security/mac_data.c',
            'security/mac_label.c',
            'security/mac_necp.c',
            'security/mac_process.c',
            'security/mac_vfs.c',
            'security/mac_vfs_subr.c',
            'security/mac_system.c',
            'security/mac_sysv_sem.c',
            'security/mac_sysv_msg.c',
            'security/mac_sysv_shm.c',
            'security/mac_posix_sem.c',
            'security/mac_socket.c',
            'security/mac_posix_shm.c',
            'security/mac_pipe.c',
            'security/mac_priv.c',
            'security/mac_iokit.c',
            'security/mac_file.c',
            'security/mac_pty.c',
            'security/mac_kext.c',
            'security/mac_mach.c',
            'security/mac_skywalk.c',
        ]
    },
}

def generate_config_content(component_name, source_files):
    """Generate the config file content from source files."""
    lines = [
        f"# config file for {component_name}/conf",
        "# Generated manually to bypass doconf failure",
        "",
        "# Build directory",
        'builddir\t"."',
        "",
        "# Object directory",
        'objectdir\t"../../../../../../../BUILD/obj"',
        "",
        "# Source directory",
        'sourcedir\t"../../../../../../.."',
        "",
        f"# {component_name} files for M30LTE (ARM64)",
    ]
    for src in source_files:
        lines.append(src)
    return "\n".join(lines) + "\n"

def extract_vpath_dirs(source_files):
    """Extract unique directories from source file paths for VPATH."""
    dirs = set()
    for src in source_files:
        if '/' in src:
            dir_part = src.rsplit('/', 1)[0]
            dirs.add(dir_part)
    return sorted(dirs)

def generate_vpath(component_name, vpath_dirs):
    """Generate VPATH Makefile variable."""
    entries = []
    for d in vpath_dirs:
        entries.append(f"$(SOURCE)/../{d}")
    return "VPATH = " + ":".join(entries)

def generate_objs(source_files):
    """Generate unique OBJS list from source files."""
    objs = []
    seen = set()
    for src in source_files:
        base = os.path.basename(src)
        obj = base.rsplit('.', 1)[0] + '.o'
        if obj not in seen:
            seen.add(obj)
            objs.append(obj)
    return objs

def split_source_files(source_files):
    """Split source files into CFILES, CXXFILES, SFILES by extension."""
    cfiles = []
    cxxfiles = []
    sfiles = []
    for src in source_files:
        if src.endswith('.c'):
            cfiles.append(src)
        elif src.endswith('.cpp') or src.endswith('.cc') or src.endswith('.cxx'):
            cxxfiles.append(src)
        elif src.endswith('.s') or src.endswith('.S'):
            sfiles.append(src)
    return cfiles, cxxfiles, sfiles

def format_list(items, indent="\t"):
    """Format list for Makefile with proper line continuations."""
    if not items:
        return ""
    lines = []
    for i, item in enumerate(items):
        if i == len(items) - 1:
            lines.append(f"{indent}{item}")
        else:
            lines.append(f"{indent}{item} \\")
    return "\n".join(lines)

def generate_makefile_content(component_name, source_files):
    """Generate the complete Makefile content."""
    vpath_dirs = extract_vpath_dirs(source_files)
    vpath = generate_vpath(component_name, vpath_dirs)
    objs = generate_objs(source_files)
    cfiles, cxxfiles, sfiles = split_source_files(source_files)

    # Hardcode the CI source root path for reliability
    srcroot_path = '/Users/runner/work/ios-m30lte/ios-m30lte/xnu-source'

    makefile = f"""#
# This Makefile was generated by config
#
# DO NOT EDIT THIS FILE
#

# SRCROOT is the absolute path to the XNU source root (hardcoded for CI)
SRCROOT := {srcroot_path}
export SRCROOT

# makedefs is at $(SRCROOT)/makedefs
MakeInc_cmd = $(SRCROOT)/makedefs/MakeInc.cmd
MakeInc_def = $(SRCROOT)/makedefs/MakeInc.def
MakeInc_rule = $(SRCROOT)/makedefs/MakeInc.rule
MakeInc_dir = $(SRCROOT)/makedefs/MakeInc.dir
export MakeInc_cmd
export MakeInc_def
export MakeInc_rule
export MakeInc_dir

include $(MakeInc_cmd)
include $(MakeInc_def)

#
# XXX: CFLAGS
#
CFLAGS+= -include meta_features.h -DBSD_KERNEL_PRIVATE
SFLAGS+= -include meta_features.h

#
# INCFLAGS to include {component_name} prototypes
#
INCFLAGS_MAKEFILE= -I$(SOURCE)/..

#
# VPATH to find source files
#
{vpath}

#
# Directories for mig generated files
#
COMP_SUBDIRS =

#
#  Make sure we don't remove this by accident if interrupted at the wrong
#  time.
#
.PRECIOUS: Makefile


#
#  Theses macros are filled in by the config program depending on the
#  current configuration.  The MACHDEP macro is replaced by the
#  contents of the machine dependent makefile template and the others
#  are replaced by the corresponding symbol definitions for the
#  configuration.
#

OBJS = \\
{format_list(objs)}

LIBOBJS =

CFILES = \\
{format_list(cfiles)}

CXXFILES = \\
{format_list(cxxfiles)}

SFILES = \\
{format_list(sfiles)}

MACHDEP =

#
# Diagnostic opt-outs.  We need to make this list empty.
#
# DO NOT ADD MORE HERE.
#

# -Wno-cast-align
# -Wno-shorten-64-to-32
# -Wno-sign-conversion

# Rebuild if per-file overrides change
$(OBJS): $(firstword $(MAKEFILE_LIST))

# Rebuild if global compile flags change
$(COBJS): .CFLAGS
.CFLAGS: ALWAYS
\t$(_v)$(REPLACECONTENTS) $@ $(KCC) $(CFLAGS) $(INCFLAGS)
$(CXXOBJS): .CXXFLAGS
.CXXFLAGS: ALWAYS
\t$(_v)$(REPLACECONTENTS) $@ $(KC++) $(CXXFLAGS) $(INCFLAGS)
$(SOBJS): .SFLAGS
.SFLAGS: ALWAYS
\t$(_v)$(REPLACECONTENTS) $@ $(S_KCC) $(SFLAGS) $(INCFLAGS)

$(COMPONENT).filelist: $(OBJS)
\t@$(LOG_LDFILELIST) "$(COMPONENT)"
\t$(_v)for obj in $$(OBJS); do \\
\t\t $(ECHO) $(TARGET)/$(CURRENT_KERNEL_CONFIG)/$$(obj); \\
\tdone > $(COMPONENT).filelist

$(COMPONENT).libfilelist: $(LIBOBJS)
\t@$(LOG_LDFILELIST) "lib$(COMPONENT)"
\t$(_v)for obj in $$(LIBOBJS); do \\
\t\t $(ECHO) $(TARGET)/$(CURRENT_KERNEL_CONFIG)/$$(obj); \\
\tdone > $(COMPONENT).libfilelist

ifeq ($(RC_ProjectName),xnu_libraries)
do_all: $(COMPONENT).libfilelist
else
do_all: $(COMPONENT).filelist
endif

do_build_all:: do_all

include $(MakeInc_rule)
include $(MakeInc_dir)
"""
    return makefile

def write_component(component_name, info, dry_run=False):
    """Write config and Makefile for a component."""
    config_dir = info['config_dir']
    source_files = info['source_files']

    config_content = generate_config_content(component_name, source_files)
    makefile_content = generate_makefile_content(component_name, source_files)

    if dry_run:
        print(f"=== {component_name} ===")
        print(f"Config dir: {config_dir}")
        print(f"Source files: {len(source_files)}")
        print(f"VPATH dirs: {extract_vpath_dirs(source_files)}")
        print(f"Unique OBJS: {generate_objs(source_files)}")
        cfiles, cxxfiles, sfiles = split_source_files(source_files)
        print(f"C: {len(cfiles)}, C++: {len(cxxfiles)}, S: {len(sfiles)}")
        print()
        return

    # Write config file
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, 'DEVELOPMENT')
    with open(config_path, 'w') as f:
        f.write(config_content)
    print(f"Created {config_path}")

    # Write Makefile.valid
    makefile_path = os.path.join(config_dir, 'Makefile.valid')
    with open(makefile_path, 'w') as f:
        f.write(makefile_content)
    print(f"Created {makefile_path}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--dry-run':
        print("DRY RUN - showing what would be generated\n")
        for name, info in COMPONENTS.items():
            write_component(name, info, dry_run=True)
        return

    # Write all components
    for name, info in COMPONENTS.items():
        print(f"\n=== Processing {name} ===")
        write_component(name, info)

if __name__ == '__main__':
    main()