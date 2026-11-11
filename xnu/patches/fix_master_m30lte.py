#!/usr/bin/env python3
"""Fix MASTER.arm64.m30lte config file - convert #define to options, uncomment sections."""
import sys
import re

with open('config/MASTER.arm64.m30lte', 'r') as f:
    content = f.read()

# Convert #define to options (doconf syntax)
content = content.replace('#define nos_arm_asm 1\n', 'options\tNOS_ARM_ASM\t\t# <nos_arm_asm>\n')
content = content.replace('#define nos_arm_pmap 1\n', 'options\tNOS_ARM_PMAP\t\t# <nos_arm_pmap>\n')

# Uncomment KERNEL_BASE and fix it
content = content.replace(
    '#  KERNEL_BASE =    [ arm64 config_pmap_ppl medium msgb_large config_requires_u32_munging config_delay_idle_sleep config_proc_udata_storage config_uexc config_darkboot ARM_EXTRAS_BASE nos_arm_asm nos_arm_pmap ]',
    '  KERNEL_BASE =    [ arm64 medium msgb_large config_embedded config_enforce_signed_code config_code_signature_reconstitution config_requires_u32_munging config_delay_idle_sleep config_proc_udata_storage config_uexc config_darkboot ARM_EXTRAS_BASE nos_arm_asm nos_arm_pmap config_amcc ]'
)

# Uncomment KERNEL_RELEASE, KERNEL_DEV, KERNEL_DEBUG
content = content.replace('#  KERNEL_RELEASE = [ KERNEL_BASE ]', '  KERNEL_RELEASE = [ KERNEL_BASE ]')
content = content.replace('#  KERNEL_DEV =     [ KERNEL_BASE development mach_assert config_xnupost proc_ref_debug config_proc_resource_limits ]', '  KERNEL_DEV =     [ KERNEL_BASE development mach_assert config_xnupost proc_ref_debug config_proc_resource_limits ]')
content = content.replace('#  KERNEL_DEBUG =   [ KERNEL_BASE debug mach_assert config_xnupost config_waitq_stats config_workloop_debug config_proc_resource_limits ]', '  KERNEL_DEBUG =   [ KERNEL_BASE debug mach_assert config_xnupost config_waitq_stats config_workloop_debug config_proc_resource_limits ]')

# Uncomment BSD_BASE and fix it
content = content.replace(
    '#  BSD_BASE =       [ mach_bsd sysv_sem sysv_msg sysv_shm config_netboot config_imageboot psynch config_proc_uuid_policy config_coredump pgo config_personas ]',
    '  BSD_BASE =       [ mach_bsd sysv_sem sysv_msg sysv_shm config_netboot config_imageboot config_imageboot_img4 config_embedded psynch config_proc_uuid_policy config_coredump pgo config_personas ]'
)
content = content.replace('#  BSD_RELEASE =    [ BSD_BASE ]', '  BSD_RELEASE =    [ BSD_BASE ]')
content = content.replace('#  BSD_DEV =        [ BSD_BASE config_vnguard ]', '  BSD_DEV =        [ BSD_BASE config_vnguard ]')
content = content.replace('#  BSD_DEBUG =      [ BSD_BASE config_vnguard ]', '  BSD_DEBUG =      [ BSD_BASE config_vnguard ]')

# Uncomment FILESYS_BASE, etc.
content = content.replace('#  FILESYS_BASE =   [', '  FILESYS_BASE =   [')
content = content.replace('#  FILESYS_RELEASE= [ FILESYS_BASE ]', '  FILESYS_RELEASE= [ FILESYS_BASE ]')
content = content.replace('#  FILESYS_DEV =    [ FILESYS_BASE config_iocount_trace ]', '  FILESYS_DEV =    [ FILESYS_BASE config_iocount_trace ]')
content = content.replace('#  FILESYS_DEBUG =  [ FILESYS_BASE config_iocount_trace ]', '  FILESYS_DEBUG =  [ FILESYS_BASE config_iocount_trace ]')

# Uncomment NFS, SKYWALK, NETWORKING, VPN, PF, MULTIPATH
content = content.replace('#  NFS =            [ nfsserver ]', '  NFS =            [ nfsserver ]')
content = content.replace('#  SKYWALK_BASE =   [ skywalk config_nexus_user_pipe config_nexus_kernel_pipe config_nexus_monitor config_nexus_flowswitch config_nexus_netif ]', '  SKYWALK_BASE =   [ skywalk config_nexus_user_pipe config_nexus_kernel_pipe config_nexus_monitor config_nexus_flowswitch config_nexus_netif ]')
content = content.replace('#  SKYWALK_RELEASE = [ SKYWALK_BASE ]', '  SKYWALK_RELEASE = [ SKYWALK_BASE ]')
content = content.replace('#  SKYWALK_DEV =    [ SKYWALK_BASE ]', '  SKYWALK_DEV =    [ SKYWALK_BASE ]')
content = content.replace('#  SKYWALK_DEBUG =  [ SKYWALK_BASE ]', '  SKYWALK_DEBUG =  [ SKYWALK_BASE ]')
content = content.replace('#  NETWORKING =     [ inet bpfilter dummynet traffic_mgt sendfile ah_all_crypto bond vlan gif stf ifnet_input_chk config_mbuf_jumbo if_bridge MULTIPATH if_fake remote_vif ]', '  NETWORKING =     [ inet bpfilter dummynet traffic_mgt sendfile ah_all_crypto bond vlan gif stf ifnet_input_chk config_mbuf_jumbo if_bridge MULTIPATH if_fake remote_vif ]')
content = content.replace('#  NETWORKING_RELEASE = [ NETWORKING ]', '  NETWORKING_RELEASE = [ NETWORKING ]')
content = content.replace('#  NETWORKING_DEV = [ NETWORKING_RELEASE packet_mangler if_headless ]', '  NETWORKING_DEV = [ NETWORKING_RELEASE packet_mangler if_headless ]')
content = content.replace('#  NETWORKING_DEBUG = [ NETWORKING_DEV ]', '  NETWORKING_DEBUG = [ NETWORKING_DEV ]')
content = content.replace('#  VPN =            [ ipsec flow_divert necp content_filter ]', '  VPN =            [ ipsec flow_divert necp content_filter ]')
content = content.replace('#  PF =             [ pf pflog ]', '  PF =             [ pf pflog ]')
content = content.replace('#  MULTIPATH =      [ multipath mptcp ]', '  MULTIPATH =      [ multipath mptcp ]')

# Handle HIBERNATION preprocessor block - simplify to empty
content = re.sub(
    r'#if SOC_CONFIG_t8020 \|\| SOC_IS_VIRTUALIZED\n#\s*HIBERNATION\s*=\s*\[\s*\]\n#else /\*!\(SOC_CONFIG_t8020 \|\| SOC_IS_VIRTUALIZED\)\*/\n#\s*HIBERNATION\s*=\s*\[\s*\]\nendif /\*SOC_CONFIG_t8020 \|\| SOC_IS_VIRTUALIZED\*/\n',
    '  HIBERNATION =    [ ]\n',
    content,
    flags=re.MULTILINE
)

# Handle PARAVIRT_BASE preprocessor block - simplify to empty
content = re.sub(
    r'#if SOC_IS_VIRTUALIZED\n#\s*PARAVIRT_BASE\s*=\s*\[\s*config_pv_ticket\s*\]\n#else\n#\s*PARAVIRT_BASE\s*=\s*\[\s*\]\nendif /\*SOC_IS_VIRTUALIZED\*/\n',
    '  PARAVIRT_BASE =  [ ]\n',
    content,
    flags=re.MULTILINE
)

# Uncomment IOKIT_BASE, etc.
content = content.replace('#  IOKIT_BASE =     [ iokit iokitcpp no_kernel_hid config_sleep iokitstats HIBERNATION ]', '  IOKIT_BASE =     [ iokit iokitcpp no_kernel_hid config_sleep iokitstats HIBERNATION ]')
content = content.replace('#  IOKIT_RELEASE =  [ IOKIT_BASE ]', '  IOKIT_RELEASE =  [ IOKIT_BASE ]')
content = content.replace('#  IOKIT_DEV =      [ IOKIT_BASE iotracking ]', '  IOKIT_DEV =      [ IOKIT_BASE iotracking ]')
content = content.replace('#  IOKIT_DEBUG =    [ IOKIT_BASE iotracking ]', '  IOKIT_DEBUG =    [ IOKIT_BASE iotracking ]')

# Uncomment LIBKERN_BASE
content = content.replace('#  LIBKERN_BASE =   [ libkerncpp config_blocks config_kec_fips crypto_sha2 config_img4 ]', '  LIBKERN_BASE =   [ libkerncpp config_blocks config_kec_fips crypto_sha2 config_img4 ]')
content = content.replace('#  LIBKERN_RELEASE =[ LIBKERN_BASE zlib ]', '  LIBKERN_RELEASE =[ LIBKERN_BASE zlib ]')
content = content.replace('#  LIBKERN_DEV =    [ LIBKERN_BASE zlib iotracking ]', '  LIBKERN_DEV =    [ LIBKERN_BASE zlib iotracking ]')
content = content.replace('#  LIBKERN_DEBUG =  [ LIBKERN_BASE zlib iotracking ]', '  LIBKERN_DEBUG =  [ LIBKERN_BASE zlib iotracking ]')

# Uncomment PERF_DBG_BASE (without kpc)
content = content.replace('#  PERF_DBG_BASE =  [ config_dtrace mach_kdp config_serial_kdp kdp_interactive_debugging config_kdp_coredump_encryption config_pervasive_energy PERFMON_BASE kperf ]', '  PERF_DBG_BASE =  [ config_dtrace mach_kdp config_serial_kdp kdp_interactive_debugging config_kdp_coredump_encryption config_pervasive_energy PERFMON_BASE kperf ]')
content = content.replace('#  PERF_DBG_RELEASE=[ PERF_DBG_BASE ist_kdebug ]', '  PERF_DBG_RELEASE=[ PERF_DBG_BASE ist_kdebug ]')
content = content.replace('#  PERF_DBG_DEV =   [ PERF_DBG_BASE lock_stats zleaks alternate_debugger sched_hygiene_debug config_debug_syscall_rejection config_iotrace ]', '  PERF_DBG_DEV =   [ PERF_DBG_BASE lock_stats zleaks alternate_debugger sched_hygiene_debug config_debug_syscall_rejection config_iotrace ]')
content = content.replace('#  PERF_DBG_DEBUG = [ PERF_DBG_BASE lock_stats zleaks alternate_debugger sched_hygiene_debug config_debug_syscall_rejection config_iotrace ]', '  PERF_DBG_DEBUG = [ PERF_DBG_BASE lock_stats zleaks alternate_debugger sched_hygiene_debug config_debug_syscall_rejection config_iotrace ]')

# Uncomment MACH_BASE
content = content.replace('#  MACH_BASE =      [ mach config_ecc_logging vc_progress_white importance_inheritance config_atm config_coalitions config_iosched config_sysdiagnose config_telemetry config_mach_bridge_recv_time config_quiesce_counter config_arm_pfz config_user_notification phys_write_acct config_service_port_info config_voucher_deprecated PARAVIRT_BASE config_ledger_interval_max ]', '  MACH_BASE =      [ mach config_ecc_logging vc_progress_white importance_inheritance config_atm config_coalitions config_iosched config_sysdiagnose config_telemetry config_mach_bridge_recv_time config_quiesce_counter config_arm_pfz config_user_notification phys_write_acct config_service_port_info config_voucher_deprecated PARAVIRT_BASE config_ledger_interval_max ]')
content = content.replace('#  MACH_RELEASE =   [ MACH_BASE ]', '  MACH_RELEASE =   [ MACH_BASE ]')
content = content.replace('#  MACH_DEV =       [ MACH_BASE config_io_accounting importance_trace ]', '  MACH_DEV =       [ MACH_BASE config_io_accounting importance_trace ]')
content = content.replace('#  MACH_DEBUG =     [ MACH_BASE config_io_accounting importance_trace importance_debug ]', '  MACH_DEBUG =     [ MACH_BASE config_io_accounting importance_trace importance_debug ]')

# Uncomment SCHED_BASE - THIS IS CRITICAL FOR SCHEDULER
content = content.replace('#  SCHED_BASE =     [ config_sched_traditional config_sched_multiq config_sched_deferred_ast config_clutch config_sched_sfi config_sched_auto_join config_preadopt_tg ]', '  SCHED_BASE =     [ config_sched_traditional config_sched_multiq config_sched_deferred_ast config_clutch config_sched_sfi config_sched_auto_join config_preadopt_tg ]')
content = content.replace('#  SCHED_RELEASE =  [ SCHED_BASE ]', '  SCHED_RELEASE =  [ SCHED_BASE ]')
content = content.replace('#  SCHED_DEV =      [ SCHED_BASE ]', '  SCHED_DEV =      [ SCHED_BASE ]')
content = content.replace('#  SCHED_DEBUG =    [ SCHED_BASE config_sched_grrr config_sched_proto ]', '  SCHED_DEBUG =    [ SCHED_BASE config_sched_grrr config_sched_proto ]')

# Uncomment VM_BASE
content = content.replace('#  VM_BASE =        [ vm_pressure_events memorystatus config_code_decryption encrypted_swap config_deferred_reclaim ]', '  VM_BASE =        [ vm_pressure_events memorystatus config_code_decryption encrypted_swap config_deferred_reclaim ]')
content = content.replace('#  VM_RELEASE =     [ VM_BASE ]', '  VM_RELEASE =     [ VM_BASE ]')
content = content.replace('#  VM_DEV =         [ VM_BASE dynamic_codesigning pgzalloc ]', '  VM_DEV =         [ VM_BASE dynamic_codesigning pgzalloc ]')
content = content.replace('#  VM_DEBUG =       [ VM_BASE dynamic_codesigning pgzalloc ]', '  VM_DEBUG =       [ VM_BASE dynamic_codesigning pgzalloc ]')
content = content.replace('#  VM_KASAN =       [ VM_BASE dynamic_codesigning config_kasan config_ubsan config_kcov config_ksancov kernel_tbi ]', '  VM_KASAN =       [ VM_BASE dynamic_codesigning config_kasan config_ubsan config_kcov config_ksancov kernel_tbi ]')

# Uncomment SECURITY
content = content.replace('#  SECURITY =       [ config_macf config_audit kernel_integrity config_csr config_csr_from_dt config_setuid config_kas_info config_secure_bsd_root config_arcade config_supplemental_signatures second_static_trust_cache reslide_shared_cache ]', '  SECURITY =       [ config_macf config_audit kernel_integrity config_csr config_csr_from_dt config_setuid config_kas_info config_secure_bsd_root config_arcade config_supplemental_signatures second_static_trust_cache reslide_shared_cache ]')

# Uncomment BASE
content = content.replace('#  BASE =           [ PF VPN SECURITY NFS ]', '  BASE =           [ PF VPN SECURITY NFS ]')

# Uncomment RELEASE, DEVELOPMENT, DEBUG, KASAN
content = content.replace('#  RELEASE =        [ BASE KERNEL_RELEASE BSD_RELEASE FILESYS_RELEASE SKYWALK_RELEASE NETWORKING_RELEASE IOKIT_RELEASE LIBKERN_RELEASE    PERF_DBG_RELEASE MACH_RELEASE SCHED_RELEASE VM_RELEASE ]', '  RELEASE =        [ BASE KERNEL_RELEASE BSD_RELEASE FILESYS_RELEASE SKYWALK_RELEASE NETWORKING_RELEASE IOKIT_RELEASE LIBKERN_RELEASE    PERF_DBG_RELEASE MACH_RELEASE SCHED_RELEASE VM_RELEASE ]')
content = content.replace('#  DEVELOPMENT =    [ BASE KERNEL_DEV     BSD_DEV     FILESYS_DEV     SKYWALK_DEV     NETWORKING_DEV     IOKIT_DEV     LIBKERN_DEV        PERF_DBG_DEV     MACH_DEV     SCHED_DEV     VM_DEV     ]', '  DEVELOPMENT =    [ BASE KERNEL_DEV     BSD_DEV     FILESYS_DEV     SKYWALK_DEV     NETWORKING_DEV     IOKIT_DEV     LIBKERN_DEV        PERF_DBG_DEV     MACH_DEV     SCHED_DEV     VM_DEV     ]')
content = content.replace('#  DEBUG =          [ BASE KERNEL_DEBUG   BSD_DEBUG   FILESYS_DEBUG   SKYWALK_DEBUG   NETWORKING_DEBUG   IOKIT_DEBUG   LIBKERN_DEBUG      PERF_DBG_DEBUG   MACH_DEBUG   SCHED_DEBUG   VM_DEBUG   ]', '  DEBUG =          [ BASE KERNEL_DEBUG   BSD_DEBUG   FILESYS_DEBUG   SKYWALK_DEBUG   NETWORKING_DEBUG   IOKIT_DEBUG   LIBKERN_DEBUG      PERF_DBG_DEBUG   MACH_DEBUG   SCHED_DEBUG   VM_DEBUG   ]')
content = content.replace('#  KASAN =          [ BASE KERNEL_DEV     BSD_DEV     FILESYS_DEV     SKYWALK_DEV     NETWORKING_DEV     IOKIT_DEV     LIBKERN_DEV        PERF_DBG_DEV     MACH_DEV     SCHED_DEV     VM_KASAN   ]', '  KASAN =          [ BASE KERNEL_DEV     BSD_DEV     FILESYS_DEV     SKYWALK_DEV     NETWORKING_DEV     IOKIT_DEV     LIBKERN_DEV        PERF_DBG_DEV     MACH_DEV     SCHED_DEV     VM_KASAN   ]')

# Remove #define lines (already converted to options above)
# Keep preprocessor directives for doconf/unifdef

with open('config/MASTER.arm64.m30lte', 'w') as f:
    f.write(content)

print("Fixed MASTER.arm64.m30lte config file")

# Print for verification
with open('config/MASTER.arm64.m30lte', 'r') as f:
    print(f.read())
