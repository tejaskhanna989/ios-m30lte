#!/usr/bin/env python3
"""Fix MASTER.arm64.m30lte config file - replace #define with options, enable LIBKERN, fix KERNEL_BASE."""
import sys
import re

with open('config/MASTER.arm64.m30lte', 'r') as f:
    content = f.read()

# Replace #define with options
content = content.replace('#define nos_arm_asm 1\n', 'options\tNOS_ARM_ASM\t\t# <nos_arm_asm>\n')
content = content.replace('#define nos_arm_pmap 1\n', 'options\tNOS_ARM_PMAP\t\t# <nos_arm_pmap>\n')

# Fix KERNEL_BASE: remove config_pmap_ppl (conflicts with nos_arm_pmap), add missing standard options
content = content.replace(
    'KERNEL_BASE =    [ arm64 config_pmap_ppl medium msgb_large config_requires_u32_munging config_delay_idle_sleep config_proc_udata_storage config_uexc config_darkboot ARM_EXTRAS_BASE nos_arm_asm nos_arm_pmap ]',
    'KERNEL_BASE =    [ arm64 medium msgb_large config_embedded config_enforce_signed_code config_code_signature_reconstitution config_requires_u32_munging config_delay_idle_sleep config_proc_udata_storage config_uexc config_darkboot ARM_EXTRAS_BASE nos_arm_asm nos_arm_pmap config_amcc ]'
)

# Fix BSD_BASE: add config_imageboot_img4 and config_embedded for filelist generation
content = content.replace(
    'BSD_BASE =       [ mach_bsd sysv_sem sysv_msg sysv_shm config_netboot config_imageboot psynch config_proc_uuid_policy config_coredump pgo config_personas ]',
    'BSD_BASE =       [ mach_bsd sysv_sem sysv_msg sysv_shm config_netboot config_imageboot config_imageboot_img4 config_embedded psynch config_proc_uuid_policy config_coredump pgo config_personas ]'
)

# Uncomment PERF_DBG_BASE (without kpc, which is disabled for M30LTE)
content = content.replace(
    '#  PERF_DBG_BASE =  [ config_dtrace mach_kdp config_serial_kdp kdp_interactive_debugging config_kdp_coredump_encryption config_pervasive_energy PERFMON_BASE kperf ]',
    '  PERF_DBG_BASE =  [ config_dtrace mach_kdp config_serial_kdp kdp_interactive_debugging config_kdp_coredump_encryption config_pervasive_energy PERFMON_BASE kperf ]'
)

content = content.replace(
    '#  PERF_DBG_RELEASE=[ PERF_DBG_BASE ist_kdebug ]',
    '  PERF_DBG_RELEASE=[ PERF_DBG_BASE ist_kdebug ]'
)

content = content.replace(
    '#  PERF_DBG_DEV =   [ PERF_DBG_BASE lock_stats zleaks alternate_debugger sched_hygiene_debug config_debug_syscall_rejection config_iotrace ]',
    '  PERF_DBG_DEV =   [ PERF_DBG_BASE lock_stats zleaks alternate_debugger sched_hygiene_debug config_debug_syscall_rejection config_iotrace ]'
)

content = content.replace(
    '#  PERF_DBG_DEBUG = [ PERF_DBG_BASE lock_stats zleaks alternate_debugger sched_hygiene_debug config_debug_syscall_rejection config_iotrace ]',
    '  PERF_DBG_DEBUG = [ PERF_DBG_BASE lock_stats zleaks alternate_debugger sched_hygiene_debug config_debug_syscall_rejection config_iotrace ]'
)

# Uncomment MACH_BASE, SCHED_BASE, VM_BASE, SECURITY, BASE
content = content.replace(
    '#  MACH_BASE =      [ mach config_ecc_logging vc_progress_white importance_inheritance config_atm config_coalitions config_iosched config_sysdiagnose config_telemetry config_mach_bridge_recv_time config_quiesce_counter config_arm_pfz config_user_notification phys_write_acct config_service_port_info config_voucher_deprecated PARAVIRT_BASE config_ledger_interval_max ]',
    '  MACH_BASE =      [ mach config_ecc_logging vc_progress_white importance_inheritance config_atm config_coalitions config_iosched config_sysdiagnose config_telemetry config_mach_bridge_recv_time config_quiesce_counter config_arm_pfz config_user_notification phys_write_acct config_service_port_info config_voucher_deprecated PARAVIRT_BASE config_ledger_interval_max ]'
)

content = content.replace(
    '#  MACH_RELEASE =   [ MACH_BASE ]',
    '  MACH_RELEASE =   [ MACH_BASE ]'
)

content = content.replace(
    '#  MACH_DEV =       [ MACH_BASE config_io_accounting importance_trace ]',
    '  MACH_DEV =       [ MACH_BASE config_io_accounting importance_trace ]'
)

content = content.replace(
    '#  MACH_DEBUG =     [ MACH_BASE config_io_accounting importance_trace importance_debug ]',
    '  MACH_DEBUG =     [ MACH_BASE config_io_accounting importance_trace importance_debug ]'
)

content = content.replace(
    '#  SCHED_BASE =     [ config_sched_traditional config_sched_multiq config_sched_deferred_ast config_clutch config_sched_sfi config_sched_auto_join config_preadopt_tg ]',
    '  SCHED_BASE =     [ config_sched_traditional config_sched_multiq config_sched_deferred_ast config_clutch config_sched_sfi config_sched_auto_join config_preadopt_tg ]'
)

content = content.replace(
    '#  SCHED_RELEASE =  [ SCHED_BASE ]',
    '  SCHED_RELEASE =  [ SCHED_BASE ]'
)

content = content.replace(
    '#  SCHED_DEV =      [ SCHED_BASE ]',
    '  SCHED_DEV =      [ SCHED_BASE ]'
)

content = content.replace(
    '#  SCHED_DEBUG =    [ SCHED_BASE config_sched_grrr config_sched_proto ]',
    '  SCHED_DEBUG =    [ SCHED_BASE config_sched_grrr config_sched_proto ]'
)

content = content.replace(
    '#  VM_BASE =        [ vm_pressure_events memorystatus config_code_decryption encrypted_swap config_deferred_reclaim ]',
    '  VM_BASE =        [ vm_pressure_events memorystatus config_code_decryption encrypted_swap config_deferred_reclaim ]'
)

content = content.replace(
    '#  VM_RELEASE =     [ VM_BASE ]',
    '  VM_RELEASE =     [ VM_BASE ]'
)

content = content.replace(
    '#  VM_DEV =         [ VM_BASE dynamic_codesigning pgzalloc ]',
    '  VM_DEV =         [ VM_BASE dynamic_codesigning pgzalloc ]'
)

content = content.replace(
    '#  VM_DEBUG =       [ VM_BASE dynamic_codesigning pgzalloc ]',
    '  VM_DEBUG =       [ VM_BASE dynamic_codesigning pgzalloc ]'
)

content = content.replace(
    '#  VM_KASAN =       [ VM_BASE dynamic_codesigning config_kasan config_ubsan config_kcov config_ksancov kernel_tbi ]',
    '  VM_KASAN =       [ VM_BASE dynamic_codesigning config_kasan config_ubsan config_kcov config_ksancov kernel_tbi ]'
)

content = content.replace(
    '#  SECURITY =       [ config_macf config_audit kernel_integrity config_csr config_csr_from_dt config_setuid config_kas_info config_secure_bsd_root config_arcade config_supplemental_signatures second_static_trust_cache reslide_shared_cache ]',
    '  SECURITY =       [ config_macf config_audit kernel_integrity config_csr config_csr_from_dt config_setuid config_kas_info config_secure_bsd_root config_arcade config_supplemental_signatures second_static_trust_cache reslide_shared_cache ]'
)

content = content.replace(
    '#  BASE =           [ PF VPN SECURITY NFS ]',
    '  BASE =           [ PF VPN SECURITY NFS ]'
)

# Uncomment RELEASE, DEVELOPMENT, DEBUG, KASAN configs
content = content.replace(
    '#  RELEASE =        [ BASE KERNEL_RELEASE BSD_RELEASE FILESYS_RELEASE SKYWALK_RELEASE NETWORKING_RELEASE IOKIT_RELEASE LIBKERN_RELEASE    PERF_DBG_RELEASE MACH_RELEASE SCHED_RELEASE VM_RELEASE ]',
    '  RELEASE =        [ BASE KERNEL_RELEASE BSD_RELEASE FILESYS_RELEASE SKYWALK_RELEASE NETWORKING_RELEASE IOKIT_RELEASE LIBKERN_RELEASE    PERF_DBG_RELEASE MACH_RELEASE SCHED_RELEASE VM_RELEASE ]'
)

content = content.replace(
    '#  DEVELOPMENT =    [ BASE KERNEL_DEV     BSD_DEV     FILESYS_DEV     SKYWALK_DEV     NETWORKING_DEV     IOKIT_DEV     LIBKERN_DEV        PERF_DBG_DEV     MACH_DEV     SCHED_DEV     VM_DEV     ]',
    '  DEVELOPMENT =    [ BASE KERNEL_DEV     BSD_DEV     FILESYS_DEV     SKYWALK_DEV     NETWORKING_DEV     IOKIT_DEV     LIBKERN_DEV        PERF_DBG_DEV     MACH_DEV     SCHED_DEV     VM_DEV     ]'
)

content = content.replace(
    '#  DEBUG =          [ BASE KERNEL_DEBUG   BSD_DEBUG   FILESYS_DEBUG   SKYWALK_DEBUG   NETWORKING_DEBUG   IOKIT_DEBUG   LIBKERN_DEBUG      PERF_DBG_DEBUG   MACH_DEBUG   SCHED_DEBUG   VM_DEBUG   ]',
    '  DEBUG =          [ BASE KERNEL_DEBUG   BSD_DEBUG   FILESYS_DEBUG   SKYWALK_DEBUG   NETWORKING_DEBUG   IOKIT_DEBUG   LIBKERN_DEBUG      PERF_DBG_DEBUG   MACH_DEBUG   SCHED_DEBUG   VM_DEBUG   ]'
)

content = content.replace(
    '#  KASAN =          [ BASE KERNEL_DEV     BSD_DEV     FILESYS_DEV     SKYWALK_DEV     NETWORKING_DEV     IOKIT_DEV     LIBKERN_DEV        PERF_DBG_DEV     MACH_DEV     SCHED_DEV     VM_KASAN   ]',
    '  KASAN =          [ BASE KERNEL_DEV     BSD_DEV     FILESYS_DEV     SKYWALK_DEV     NETWORKING_DEV     IOKIT_DEV     LIBKERN_DEV        PERF_DBG_DEV     MACH_DEV     SCHED_DEV     VM_KASAN   ]'
)

# Uncomment LIBKERN lines
content = re.sub(r'^#\s*(LIBKERN_BASE\s*=)', r'  \1', content, flags=re.MULTILINE)
content = re.sub(r'^#\s*(LIBKERN_RELEASE\s*=)', r'  \1', content, flags=re.MULTILINE)
content = re.sub(r'^#\s*(LIBKERN_DEV\s*=)', r'  \1', content, flags=re.MULTILINE)
content = re.sub(r'^#\s*(LIBKERN_DEBUG\s*=)', r'  \1', content, flags=re.MULTILINE)

# Fix KERNEL_BASE: remove config_pmap_ppl (conflicts with nos_arm_pmap), add missing standard options
content = content.replace(
    'KERNEL_BASE =    [ arm64 config_pmap_ppl medium msgb_large config_requires_u32_munging config_delay_idle_sleep config_proc_udata_storage config_uexc config_darkboot ARM_EXTRAS_BASE nos_arm_asm nos_arm_pmap ]',
    'KERNEL_BASE =    [ arm64 medium msgb_large config_embedded config_enforce_signed_code config_code_signature_reconstitution config_requires_u32_munging config_delay_idle_sleep config_proc_udata_storage config_uexc config_darkboot ARM_EXTRAS_BASE nos_arm_asm nos_arm_pmap config_amcc ]'
)

# Fix BSD_BASE: add config_imageboot_img4 and config_embedded for filelist generation
content = content.replace(
    'BSD_BASE =       [ mach_bsd sysv_sem sysv_msg sysv_shm config_netboot config_imageboot psynch config_proc_uuid_policy config_coredump pgo config_personas ]',
    'BSD_BASE =       [ mach_bsd sysv_sem sysv_msg sysv_shm config_netboot config_imageboot config_imageboot_img4 config_embedded psynch config_proc_uuid_policy config_coredump pgo config_personas ]'
)

# Uncomment PERF_DBG_BASE (without kpc, which is disabled for M30LTE)
content = content.replace(
    '#  PERF_DBG_BASE =  [ config_dtrace mach_kdp config_serial_kdp kdp_interactive_debugging config_kdp_coredump_encryption config_pervasive_energy PERFMON_BASE kperf ]',
    '  PERF_DBG_BASE =  [ config_dtrace mach_kdp config_serial_kdp kdp_interactive_debugging config_kdp_coredump_encryption config_pervasive_energy PERFMON_BASE kperf ]'
)

content = content.replace(
    '#  PERF_DBG_RELEASE=[ PERF_DBG_BASE ist_kdebug ]',
    '  PERF_DBG_RELEASE=[ PERF_DBG_BASE ist_kdebug ]'
)

content = content.replace(
    '#  PERF_DBG_DEV =   [ PERF_DBG_BASE lock_stats zleaks alternate_debugger sched_hygiene_debug config_debug_syscall_rejection config_iotrace ]',
    '  PERF_DBG_DEV =   [ PERF_DBG_BASE lock_stats zleaks alternate_debugger sched_hygiene_debug config_debug_syscall_rejection config_iotrace ]'
)

content = content.replace(
    '#  PERF_DBG_DEBUG = [ PERF_DBG_BASE lock_stats zleaks alternate_debugger sched_hygiene_debug config_debug_syscall_rejection config_iotrace ]',
    '  PERF_DBG_DEBUG = [ PERF_DBG_BASE lock_stats zleaks alternate_debugger sched_hygiene_debug config_debug_syscall_rejection config_iotrace ]'
)

# Evaluate C preprocessor directives for M30LTE:
# SOC_CONFIG_t8020 = false (not defined)
# SOC_IS_VIRTUALIZED = false (not defined, -U)
# So: #if SOC_CONFIG_t8020 || SOC_IS_VIRTUALIZED -> FALSE, take #else branch
#     #if SOC_IS_VIRTUALIZED -> FALSE, take #else branch

# HIBERNATION block: #if SOC_CONFIG_t8020 || SOC_IS_VIRTUALIZED -> FALSE -> take #else (empty [ ])
hib_pattern = r'#if SOC_CONFIG_t8020 \|\| SOC_IS_VIRTUALIZED\n#\s*HIBERNATION\s*=\s*\[\s*\]\n#else /\*!\(SOC_CONFIG_t8020 \|\| SOC_IS_VIRTUALIZED\)\*/\n#\s*HIBERNATION\s*=\s*\[\s*\]\n#endif /\*SOC_CONFIG_t8020 \|\| SOC_IS_VIRTUALIZED\*/\n'
hib_replacement = '  HIBERNATION =    [ ]\n'
content = re.sub(hib_pattern, hib_replacement, content)

# PARAVIRT_BASE block: #if SOC_IS_VIRTUALIZED -> FALSE -> take #else (empty [ ])
pv_pattern = r'#if SOC_IS_VIRTUALIZED\n#\s*PARAVIRT_BASE\s*=\s*\[\s*config_pv_ticket\s*\]\n#else\n#\s*PARAVIRT_BASE\s*=\s*\[\s*\]\n#endif /\*SOC_IS_VIRTUALIZED\*/\n'
pv_replacement = '  PARAVIRT_BASE =  [ ]\n'
content = re.sub(pv_pattern, pv_replacement, content)

# Remove any remaining #define that aren't options
content = re.sub(r'^#define\s+\w+\s+.*\n', '', content, flags=re.MULTILINE)

# Keep preprocessor directives for doconf syntax - don't remove them
# content = re.sub(r'^#if.*\n', '', content, flags=re.MULTILINE)
# content = re.sub(r'^#else.*\n', '', content, flags=re.MULTILINE)
# content = re.sub(r'^#endif.*\n', '', content, flags=re.MULTILINE)

with open('config/MASTER.arm64.m30lte', 'w') as f:
    f.write(content)

print("Fixed MASTER.arm64.m30lte config file")

with open('config/MASTER.arm64.m30lte', 'r') as f:
    content = f.read()
    print("=== Fixed config file ===")
    print(content)