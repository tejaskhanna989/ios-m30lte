#!/usr/bin/env python3
"""Generate a proper unified-diff patch for M30LTE kernel stubs.

Creates osfmk/arm64/m30_stubs.c with stub implementations for all 268
undefined board-specific symbols, and adds it to osfmk/conf/files.arm64.
"""

symbols_file = '/tmp/undefined_symbols.txt'

with open(symbols_file) as f:
    symbols = [line.strip() for line in f if line.strip()]


def categorize(name):
    """Return (return_type, params, body) for a stub."""
    # void functions (no return)
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

    # int returning 0
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

    # kern_return_t
    if name.startswith(('start_cpu', 'resume_idle_cpu', 'thread_bootstrap_return')):
        return 'kern_return_t', '', 'return KERN_FAILURE;'

    # boolean_t
    if name.startswith(('allow_', 'nx_enabled', 'coredumpok')):
        return 'boolean_t', '', 'return TRUE;'
    if name.startswith(('debug_',)):
        return 'boolean_t', '', 'return FALSE;'

    # vm_offset_t
    if name.startswith(('vm_first_phys', 'vm_last_phys', 'kvtophys')):
        return 'vm_offset_t', '', 'return 0;'

    # unsigned int
    uint_pats = [
        'arm_hardware_page_size', 'arm_pt_desc_size', 'arm_pt_root_size',
        'rawpmu_config_count', 'fixed_max', 'fixed_count', 'fixed_config_count',
        'configurable_max', 'configurable_count', 'configurable_config_count',
        'num_io_rgns', 'native_pt_attr',
    ]
    for pat in uint_pats:
        if name.startswith(pat):
            return 'unsigned int', '', 'return 0;'

    # void* returning NULL
    ptr_pats = [
        'ads_zone', 'io_attr_table', 'invalid_tte', 'invalid_ttep',
        'kernel_pmap', 'mapping_adjust', 'mapping_free_prime',
        'mapping_set_mod', 'mmu_kvtop', 'mmu_kvtop_wpreflight',
    ]
    for pat in ptr_pats:
        if name.startswith(pat):
            return 'void *', '', 'return NULL;'

    # _pmap_* -> void (most common)
    if name.startswith('pmap_'):
        return 'void', '', ''

    # Default: void
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

stub_text = '\n'.join(stubs)

# ---- Build the patch ----
patch = []

# Part 1: New file m30_stubs.c
patch.append('diff --git a/osfmk/arm64/m30_stubs.c b/osfmk/arm64/m30_stubs.c')
patch.append('new file mode 100644')
patch.append('--- /dev/null')
patch.append('+++ b/osfmk/arm64/m30_stubs.c')

# Count lines in the stub file content
stub_lines = stub_text.count('\n') + 1
header_lines = 9  # /* ... */ (5 lines) + blank + #if + blank + .text ... actually let me count precisely

# Content lines:
content_lines = []
content_lines.append('/*')
content_lines.append(' * M30LTE: stub implementations for low-level board-specific functions')
content_lines.append(' * normally provided by Apple\'s closed per-SoC libraries.')
content_lines.append(' * QEMU bring-up only needs these to exist at link time; real hardware')
content_lines.append(' * bring-up will replace them with proper implementations.')
content_lines.append(' */')
content_lines.append('')
content_lines.append('#include <pexpert/pexpert.h>')
content_lines.append('#include <arm64/proc_reg.h>')
content_lines.append('#include <vm/vm_map.h>')
content_lines.append('#include <mach/kern_return.h>')
content_lines.append('#include <mach/vm_types.h>')
content_lines.append('#include <mach/boolean.h>')
content_lines.append('#include <stddef.h>')
content_lines.append('')
content_lines.append('#if defined(M30LTE)')
content_lines.append('')
content_lines.extend(stubs)
content_lines.append('#endif /* M30LTE */')
content_lines.append('')

file_lines = len(content_lines)

patch.append(f'@@ -0,0 +1,{file_lines} @@')
for line in content_lines:
    patch.append('+' + line)

# Part 2: Modify files.arm64 - add m30_stubs.c after m30_early.c
patch.append('')
patch.append('diff --git a/osfmk/conf/files.arm64 b/osfmk/conf/files.arm64')
patch.append('index b0dad49..0000000 100644')
patch.append('--- a/osfmk/conf/files.arm64')
patch.append('+++ b/osfmk/conf/files.arm64')
patch.append('@@ -43,3 +43,4 @@ osfmk/arm64/arm_vm_init.c	optional config_pmap_ppl')
patch.append(' osfmk/arm64/m30_early.c	standard')
patch.append('+osfmk/arm64/m30_stubs.c	standard')
patch.append(' osfmk/arm64/arm64_hypercall.c	standard')

with open('/home/tejas/Projects/m30lte-ios/xnu/patches/0082-m30lte-lowlevel-stubs.patch', 'w') as f:
    f.write('\n'.join(patch) + '\n')

print(f'Generated stubs for {len(symbols)} symbols')
print(f'Patch written to xnu/patches/0082-m30lte-lowlevel-stubs.patch')
print(f'Stub file has {file_lines} lines')
