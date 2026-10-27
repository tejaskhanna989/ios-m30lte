#!/usr/bin/env python3
"""Generate proper unified-diff patch for M30LTE kernel stubs.

Creates osfmk/arm64/m30_stubs.c with stub implementations for all undefined
board-specific symbols, and adds it to osfmk/conf/files.arm64.
"""

symbols_file = '/tmp/undefined_symbols.txt'

with open(symbols_file) as f:
    symbols = [line.strip() for line in f if line.strip()]


def categorize(name):
    """Return (return_type, params, body) for a stub."""
    void_pats = [
        'clean_dcache', 'flush_dcache', 'FlushPoC', 'CleanPoC', 'CleanPoU', 'FlushPoU',
        'fillPage', 'fill32', 'InvalidatePoU', 'invalidate_icache', 'invalidate_icache64',
        'set_mmu_ttb', 'set_mmu_ttb_alternate', 'set_tcr', '_m30_secondary_entry',
        'ml_enable_monitor', '__start', '_Shutdown_context', '_Idle_load_context',
        '_Idle_context', 'configure_misc_apple_boot_args', 'configure_misc_apple_regs',
        'configure_timer_apple_regs', 'consider_machine_adjust', 'consider_machine_collect',
        '_machine_switch_context', '_machine_stack_handoff', '_machine_stack_detach',
        '_machine_stack_attach', '_machine_set_current_thread', '_machine_load_context',
        '_machine_csv', '_machine_tecs', 'arm64_force_wfi_clock_gate',
        'arm64_prepare_for_sleep', 'arm64_replace_bootstack', 'arm64_thread_exception_return',
        'arm_debug_set', 'arm_fast_fault', 'flush_mmu_tlb_region',
    ]
    for pat in void_pats:
        if name.startswith(pat):
            return 'void', '', ''

    int_pats = [
        '__bcopy', '__copyin', '__copyout', 'copyinframe', 'copyio_recover',
        'copy_debug_state', 'copy_legacy_debug_state', 'dtrace_', 'kpc_',
        'compute_pmap_gc_throttle', 'cpu_tte', 'cpu_ttep', 'free_tt_count',
        'inuse_kernel_ptepages_count', 'inuse_kernel_ttepages_count',
        'free_page_size_tt_count', 'free_two_page_size_tt_count',
    ]
    for pat in int_pats:
        if name.startswith(pat):
            return 'int', '', 'return 0;'

    if name.startswith(('start_cpu', 'resume_idle_cpu', 'thread_bootstrap_return')):
        return 'kern_return_t', '', 'return KERN_FAILURE;'

    if name.startswith(('allow_', 'nx_enabled', 'coredumpok')):
        return 'boolean_t', '', 'return TRUE;'
    if name.startswith(('debug_',)):
        return 'boolean_t', '', 'return FALSE;'

    if name.startswith(('vm_first_phys', 'vm_last_phys', 'kvtophys')):
        return 'vm_offset_t', '', 'return 0;'

    uint_pats = [
        'arm_hardware_page_size', 'arm_pt_desc_size', 'arm_pt_root_size',
        'rawpmu_config_count', 'fixed_max', 'fixed_count', 'fixed_config_count',
        'configurable_max', 'configurable_count', 'configurable_config_count',
        'num_io_rgns', 'native_pt_attr',
    ]
    for pat in uint_pats:
        if name.startswith(pat):
            return 'unsigned int', '', 'return 0;'

    ptr_pats = [
        'ads_zone', 'io_attr_table', 'invalid_tte', 'invalid_ttep',
        'kernel_pmap', 'mapping_adjust', 'mapping_free_prime',
        'mapping_set_mod', 'mmu_kvtop', 'mmu_kvtop_wpreflight',
    ]
    for pat in ptr_pats:
        if name.startswith(pat):
            return 'void *', '', 'return NULL;'

    if name.startswith('pmap_'):
        return 'void', '', ''

    return 'void', '', ''


# Build stub definitions
stubs = []
for sym in symbols:
    name = sym.lstrip('_')
    ret, params, body = categorize(name)
    if params:
        decl = f'{ret} {name}({params}) {{'
    else:
        decl = f'{ret} {name}(void) {{'
    stubs.append(decl)
    if body:
        stubs.append(f'    {body}')
    stubs.append('}')
    stubs.append('')

# Build stub file content
stub_file_lines = []
stub_file_lines.append('/*')
stub_file_lines.append(' * M30LTE: stub implementations for low-level board-specific functions')
stub_file_lines.append(' * normally provided by Apple\'s closed per-SoC libraries.')
stub_file_lines.append(' * QEMU bring-up only needs these to exist at link time; real hardware')
stub_file_lines.append(' * bring-up will replace them with proper implementations.')
stub_file_lines.append(' */')
stub_file_lines.append('')
stub_file_lines.append('#include <pexpert/pexpert.h>')
stub_file_lines.append('#include <arm64/proc_reg.h>')
stub_file_lines.append('#include <vm/vm_map.h>')
stub_file_lines.append('#include <mach/kern_return.h>')
stub_file_lines.append('#include <mach/vm_types.h>')
stub_file_lines.append('#include <mach/boolean.h>')
stub_file_lines.append('#include <stddef.h>')
stub_file_lines.append('')
stub_file_lines.append('#if defined(M30LTE)')
stub_file_lines.append('')
stub_file_lines.extend(stubs)
stub_file_lines.append('#endif /* M30LTE */')
stub_file_lines.append('')

stub_file_line_count = len(stub_file_lines)

# ---- Build patch ----
patch_lines = []

# Part 1: New file m30_stubs.c
patch_lines.append('diff --git a/osfmk/arm64/m30_stubs.c b/osfmk/arm64/m30_stubs.c')
patch_lines.append('new file mode 100644')
patch_lines.append('--- /dev/null')
patch_lines.append('+++ b/osfmk/arm64/m30_stubs.c')
patch_lines.append(f'@@ -0,0 +1,{stub_file_line_count} @@')
for line in stub_file_lines:
    patch_lines.append('+' + line)

# Part 2: Modify files.arm64 - add m30_stubs.c after m30_early.c
# After patch 0010, files.arm64 has m30_early.c at line 44, arm64_hypercall.c at line 45
patch_lines.append('')
patch_lines.append('diff --git a/osfmk/conf/files.arm64 b/osfmk/conf/files.arm64')
patch_lines.append('--- a/osfmk/conf/files.arm64')
patch_lines.append('+++ b/osfmk/conf/files.arm64')
patch_lines.append('@@ -44,2 +44,3 @@')
patch_lines.append(' osfmk/arm64/m30_early.c	standard')
patch_lines.append('+osfmk/arm64/m30_stubs.c	standard')
patch_lines.append(' osfmk/arm64/arm64_hypercall.c	standard')

patch_text = '\n'.join(patch_lines) + '\n'

output_file = '/home/tejas/Projects/m30lte-ios/xnu/patches/0082-m30lte-lowlevel-stubs.patch'
with open(output_file, 'w') as f:
    f.write(patch_text)

print(f'Generated stubs for {len(symbols)} symbols')
print(f'Patch written to {output_file}')
print(f'Patch has {len(patch_lines)} lines')
