#!/usr/bin/env python3
"""Generate C stub implementations for all undefined M30LTE kernel symbols.

Symbols are categorized by name pattern and assigned C signatures that match
the likely calling convention. For QEMU testing, stubs just need to exist
and return safe defaults; real hardware bring-up will replace them.
"""

import sys
import os

symbols_file = sys.argv[1] if len(sys.argv) > 1 else '/tmp/undefined_symbols.txt'

with open(symbols_file) as f:
    symbols = [line.strip() for line in f if line.strip()]


def categorize(name):
    """Return (return_type, params, body) for a stub based on symbol name."""
    # void functions (no return value expected)
    void_patterns = [
        ('clean_dcache', 'void', '', ''),
        ('flush_dcache', 'void', '', ''),
        ('FlushPoC', 'void', '', ''),
        ('CleanPoC', 'void', '', ''),
        ('CleanPoU', 'void', '', ''),
        ('FlushPoU', 'void', '', ''),
        ('fillPage', 'void', '', ''),
        ('fill32', 'void', '', ''),
        ('InvalidatePoU', 'void', '', ''),
        ('invalidate_icache', 'void', '', ''),
        ('invalidate_icache64', 'void', '', ''),
        ('set_mmu_ttb', 'void', 'vm_offset_t ttb', ''),
        ('set_mmu_ttb_alternate', 'void', 'vm_offset_t ttb', ''),
        ('set_tcr', 'void', 'uint32_t tcr', ''),
        ('_m30_secondary_entry', 'void', '', ''),
        ('ml_enable_monitor', 'void', '', ''),
        ('__start', 'void', '', ''),
        ('_Shutdown_context', 'void', '', ''),
        ('_Idle_load_context', 'void', '', ''),
        ('_Idle_context', 'void', '', ''),
        ('configure_misc_apple_boot_args', 'void', '', ''),
        ('configure_misc_apple_regs', 'void', '', ''),
        ('configure_timer_apple_regs', 'void', '', ''),
        ('consider_machine_adjust', 'void', '', ''),
        ('consider_machine_collect', 'void', '', ''),
        ('_machine_switch_context', 'void', '', ''),
        ('_machine_stack_handoff', 'void', '', ''),
        ('_machine_stack_detach', 'void', '', ''),
        ('_machine_stack_attach', 'void', '', ''),
        ('_machine_set_current_thread', 'void', '', ''),
        ('_machine_load_context', 'void', '', ''),
        ('_machine_thread_on_core', 'void', '', ''),
        ('_machine_thread_on_core_allow_invalid', 'void', '', ''),
        ('_machine_thread_process_signature', 'void', '', ''),
        ('_machine_thread_set_tsd_base', 'void', '', ''),
        ('_machine_thread_template_init', 'void', '', ''),
        ('_machine_tecs', 'void', '', ''),
        ('_machine_csv', 'void', '', ''),
        ('arm64_force_wfi_clock_gate', 'void', '', ''),
        ('arm64_prepare_for_sleep', 'void', '', ''),
        ('arm64_replace_bootstack', 'void', '', ''),
        ('arm64_thread_exception_return', 'void', '', ''),
    ]
    for pat, ret, params, body in void_patterns:
        if name.startswith(pat):
            return ret, params, body

    # int/kern_return_t returning 0
    int_patterns = [
        ('__bcopy', 'int', 'void *dst, const void *src, size_t len', 'return 0;'),
        ('__copyin', 'int', 'const void *user_addr, void *kernel_addr, size_t len', 'return 0;'),
        ('__copyout', 'int', 'const void *kernel_addr, void *user_addr, size_t len', 'return 0;'),
        ('copyinframe', 'int', '', 'return 0;'),
        ('copyio_recover', 'int', '', 'return 0;'),
        ('copy_debug_state', 'int', '', 'return 0;'),
        ('copy_legacy_debug_state', 'int', '', 'return 0;'),
        ('dtrace_', 'int', '', 'return 0;'),
        ('kpc_', 'int', '', 'return 0;'),
        ('compute_pmap_gc_throttle', 'int', '', 'return 0;'),
        ('cpu_tte', 'int', '', 'return 0;'),
        ('cpu_ttep', 'int', '', 'return 0;'),
        ('free_tt_count', 'int', '', 'return 0;'),
        ('inuse_kernel_ptepages_count', 'int', '', 'return 0;'),
        ('inuse_kernel_ttepages_count', 'int', '', 'return 0;'),
        ('free_page_size_tt_count', 'int', '', 'return 0;'),
        ('free_two_page_size_tt_count', 'int', '', 'return 0;'),
        ('flush_mmu_tlb_region', 'int', '', 'return 0;'),
        ('_start_cpu', 'kern_return_t', 'cpu_data_t cpu, vm_offset_t entry, vm_offset_t arg', 'return KERN_FAILURE;'),
    ]
    for pat, ret, params, body in int_patterns:
        if name.startswith(pat):
            return ret, params, body

    # boolean_t returning TRUE/FALSE
    bool_patterns = [
        ('allow_', 'boolean_t', '', 'return TRUE;'),
        ('nx_enabled', 'boolean_t', '', 'return TRUE;'),
        ('coredumpok', 'boolean_t', '', 'return TRUE;'),
        ('debug_', 'boolean_t', '', 'return FALSE;'),
        ('debug_state_is_valid', 'boolean_t', '', 'return FALSE;'),
    ]
    for pat, ret, params, body in bool_patterns:
        if name.startswith(pat):
            return ret, params, body

    # vm_offset_t returning 0
    vmoff_patterns = [
        ('vm_first_phys', 'vm_offset_t', '', 'return 0;'),
        ('vm_last_phys', 'vm_offset_t', '', 'return 0;'),
        ('kvtophys', 'vm_offset_t', '', 'return 0;'),
    ]
    for pat, ret, params, body in vmoff_patterns:
        if name.startswith(pat):
            return ret, params, body

    # unsigned int returning 0
    uint_patterns = [
        ('arm_hardware_page_size', 'unsigned int', '', 'return 0;'),
        ('arm_pt_desc_size', 'unsigned int', '', 'return 0;'),
        ('arm_pt_root_size', 'unsigned int', '', 'return 0;'),
        ('rawpmu_config_count', 'unsigned int', '', 'return 0;'),
        ('fixed_max', 'unsigned int', '', 'return 0;'),
        ('fixed_count', 'unsigned int', '', 'return 0;'),
        ('fixed_config_count', 'unsigned int', '', 'return 0;'),
        ('configurable_max', 'unsigned int', '', 'return 0;'),
        ('configurable_count', 'unsigned int', '', 'return 0;'),
        ('configurable_config_count', 'unsigned int', '', 'return 0;'),
        ('num_io_rgns', 'unsigned int', '', 'return 0;'),
        ('native_pt_attr', 'unsigned int', '', 'return 0;'),
    ]
    for pat, ret, params, body in uint_patterns:
        if name.startswith(pat):
            return ret, params, body

    # void* returning NULL
    ptr_patterns = [
        ('ads_zone', 'void *', '', 'return NULL;'),
        ('io_attr_table', 'void *', '', 'return NULL;'),
        ('invalid_tte', 'void *', '', 'return NULL;'),
        ('invalid_ttep', 'void *', '', 'return NULL;'),
        ('kernel_pmap', 'void *', '', 'return NULL;'),
        ('mapping_adjust', 'void *', '', 'return NULL;'),
        ('mapping_free_prime', 'void *', '', 'return NULL;'),
        ('mapping_set_mod', 'void *', '', 'return NULL;'),
        ('mmu_kvtop', 'void *', '', 'return NULL;'),
        ('mmu_kvtop_wpreflight', 'void *', '', 'return NULL;'),
    ]
    for pat, ret, params, body in ptr_patterns:
        if name.startswith(pat):
            return ret, params, body

    # arm_debug_set variants
    if name.startswith('arm_debug_set'):
        return 'void', '', ''

    # _pmap_* functions - most return void, some return int/boolean_t/pointers
    if name.startswith('pmap_'):
        # Functions returning pointers
        pmap_ptr = [
            ('pmap_enter', 'void', '', ''),
            ('pmap_enter_options', 'void', '', ''),
            ('pmap_enter_options_addr', 'void', '', ''),
            ('pmap_insert_commpage', 'void', '', ''),
            ('pmap_map', 'void', '', ''),
            ('pmap_map_block', 'void', '', ''),
            ('pmap_map_block_addr', 'void', '', ''),
            ('pmap_map_bd', 'void', '', ''),
            ('pmap_map_bd_with_options', 'void', '', ''),
            ('pmap_map_compressor_page', 'void', '', ''),
            ('pmap_map_cpu_windows_copy', 'void', '', ''),
            ('pmap_map_globals', 'void', '', ''),
            ('pmap_map_high_window_bd', 'void', '', ''),
            ('pmap_next_page', 'void', '', ''),
            ('pmap_next_page_hi', 'void', '', ''),
            ('pmap_object_store', 'void', '', ''),
            ('pmap_page_protect', 'void', '', ''),
            ('pmap_page_protect_options', 'void', '', ''),
            ('pmap_protect', 'void', '', ''),
            ('pmap_protect_options', 'void', '', ''),
            ('pmap_query_page_info', 'void', '', ''),
            ('pmap_query_page_info_retries', 'void', '', ''),
            ('pmap_query_resident', 'void', '', ''),
            ('pmap_reference', 'void', '', ''),
            ('pmap_release_pages_fast', 'void', '', ''),
            ('pmap_remove', 'void', '', ''),
            ('pmap_remove_options', 'void', '', ''),
            ('pmap_ro_zone_atomic_op', 'void', '', ''),
            ('pmap_ro_zone_bzero', 'void', '', ''),
            ('pmap_ro_zone_memcpy', 'void', '', ''),
            ('pmap_require', 'void', '', ''),
            ('pmap_set_cache_attributes', 'void', '', ''),
            ('pmap_set_jit_entitled', 'void', '', ''),
            ('pmap_set_nested', 'void', '', ''),
            ('pmap_set_noencrypt', 'void', '', ''),
            ('pmap_set_process', 'void', '', ''),
            ('pmap_set_tpro', 'void', '', ''),
            ('pmap_set_vm_map_cs_enforced', 'void', '', ''),
            ('pmap_shared_region_size_min', 'void', '', ''),
            ('pmap_switch', 'void', '', ''),
            ('pmap_switch_user', 'void', '', ''),
            ('pmap_sync_page_attributes_phys', 'void', '', ''),
            ('pmap_sync_page_data_phys', 'void', '', ''),
            ('pmap_test', 'void', '', ''),
            ('pmap_test_text_corruption', 'void', '', ''),
            ('pmap_trim', 'void', '', ''),
            ('pmap_unmap_compressor_page', 'void', '', ''),
            ('pmap_unmap_cpu_windows_copy', 'void', '', ''),
            ('pmap_user_va_bits', 'void', '', ''),
            ('pmap_valid_address', 'void', '', ''),
            ('pmap_valid_page', 'void', '', ''),
            ('pmap_unnest', 'void', '', ''),
            ('pmap_unnest_options', 'void', '', ''),
            ('pmap_zero_page', 'void', '', ''),
            ('pmap_zero_part_page', 'void', '', ''),
            ('pmap_bootstrap', 'void', '', ''),
            ('pmap_destroy', 'void', '', ''),
            ('pmap_disable_NX', 'void', '', ''),
            ('pmap_disconnect', 'void', '', ''),
            ('pmap_disconnect_options', 'void', '', ''),
            ('pmap_dump_page_tables', 'void', '', ''),
            ('pmap_enforces_execute_only', 'void', '', ''),
            ('pmap_find_phys', 'void', '', ''),
            ('pmap_find_phys_nofault', 'void', '', ''),
            ('pmap_find_pa', 'void', '', ''),
            ('pmap_flush', 'void', '', ''),
            ('pmap_flush_context_init', 'void', '', ''),
            ('pmap_footprint_suspend', 'void', '', ''),
            ('pmap_fork_nest', 'void', '', ''),
            ('pmap_free_pages', 'void', '', ''),
            ('pmap_free_pages_span', 'void', '', ''),
            ('pmap_get_jit_entitled', 'void', '', ''),
            ('pmap_get_refmod', 'void', '', ''),
            ('pmap_get_tpro', 'void', '', ''),
            ('pmap_get_vm_map_cs_enforced', 'void', '', ''),
            ('pmap_has_managed_page', 'void', '', ''),
            ('pmap_has_prot_policy', 'void', '', ''),
            ('pmap_init', 'void', '', ''),
            ('pmap_init_pte_page', 'void', '', ''),
            ('pmap_in_ppl', 'void', '', ''),
            ('pmap_is_exotic', 'void', '', ''),
            ('pmap_is_modified', 'void', '', ''),
            ('pmap_is_noencrypt', 'void', '', ''),
            ('pmap_is_referenced', 'void', '', ''),
            ('pmap_kernel_va_bits', 'void', '', ''),
            ('pmap_ledger_alloc', 'void', '', ''),
            ('pmap_ledger_free', 'void', '', ''),
            ('pmap_ledger_verify_size', 'void', '', ''),
            ('pmap_lock_phys_page', 'void', '', ''),
            ('pmap_max_offset', 'void', '', ''),
            ('pmap_nest', 'void', '', ''),
            ('pmap_nop', 'void', '', ''),
        ]
        for pat, ret, params, body in pmap_ptr:
            if name.startswith(pat):
                return ret, params, body
        # Default pmap: void
        return 'void', '', ''

    # Default: void function
    return 'void', '', ''


# Generate stubs
stub_defs = []
for sym in symbols:
    name = sym.lstrip('_')
    ret, params, body = categorize(name)
    if params:
        decl = f'{ret} {name}({params}) {{'
    else:
        decl = f'{ret} {name}(void) {{'
    stub_defs.append(decl)
    if body:
        stub_defs.append(f'    {body}')
    stub_defs.append('}')
    stub_defs.append('')

# Write output
output = []
output.append('/*')
output.append(' * M30LTE: stub implementations for low-level board-specific functions')
output.append(' * normally provided by Apple\'s closed per-SoC libraries.')
output.append(' * QEMU testing only needs these to exist; real hardware bring-up will')
output.append(' * replace them with proper implementations.')
output.append(' */')
output.append('#include <pexpert/pexpert.h>')
output.append('#include <arm64/proc_reg.h>')
output.append('#include <vm/vm_map.h>')
output.append('#include <mach/kern_return.h>')
output.append('#include <mach/vm_types.h>')
output.append('#include <mach/boolean.h>')
output.append('#include <stddef.h>')
output.append('')
output.append('#if defined(M30LTE)')
output.append('')
output.extend(stub_defs)
output.append('#endif /* M30LTE */')
output.append('')

print(f'Generated {len(stub_defs)} stub lines for {len(symbols)} symbols')
print('\n'.join(output[:10]))
print('...')
print('\n'.join(output[-5:]))

# Write to file
with open('/tmp/stub_output.c', 'w') as f:
    f.write('\n'.join(output))
print('\nWritten to /tmp/stub_output.c')
