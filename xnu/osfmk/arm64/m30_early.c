/*
 * Galaxy M30 bootstrap console. No allocation, locks, ADT parsing or
 * per-CPU state: panic() can reach this before a current thread exists.
 * start.s maps the splash framebuffer VA=PA as Normal Non-Cacheable memory.
 * Stop using that mapping before arm_vm_init tears down bootstrap TTBR0.
 */
#include <arm64/m30_early.h>

#if defined(M30LTE)
#include <stdint.h>
#include <kern/misc_protos.h>

#define EARLY_FB ((volatile uint32_t *)(uintptr_t)0x9c000000)
#define EARLY_WIDTH 1080u
#define EARLY_HEIGHT 2400u
#define EARLY_STRIDE (4320u / 4)
#define EARLY_SCALE 2u
#define EARLY_CELL_W (8u * EARLY_SCALE)
#define EARLY_CELL_H (16u * EARLY_SCALE)
#define EARLY_ROWS ((EARLY_HEIGHT - 32u) / EARLY_CELL_H)
#define EARLY_COLS (EARLY_WIDTH / EARLY_CELL_W)

extern unsigned char iso_font[256 * 16];

/* Initialized data must remain writable until disable, including panics. */
static unsigned int early_row, early_col;
static unsigned int early_started, early_disabled, early_panicking;

static void
m30_early_clear_row(void)
{
	for (unsigned int y = 0; y < EARLY_CELL_H; y++) {
		volatile uint32_t *line = EARLY_FB + (early_row * EARLY_CELL_H + y) * EARLY_STRIDE;
		for (unsigned int x = 0; x < EARLY_WIDTH; x++)
			line[x] = 0xff000000u;
	}
}

void
m30_early_putc(char c)
{
	if (early_disabled)
		return;
	if (!early_started) {
		early_started = 1;
		m30_early_clear_row();
	}
	if (c == '\r') {
		early_col = 0;
		return;
	}
	if (c == '\n' || early_col == EARLY_COLS) {
		early_col = 0;
		early_row = (early_row + 1) % EARLY_ROWS;
		m30_early_clear_row();
		if (c == '\n')
			return;
	}
	const unsigned char *glyph = iso_font + (unsigned char)c * 16;
	for (unsigned int gy = 0; gy < 16; gy++) {
		for (unsigned int sy = 0; sy < EARLY_SCALE; sy++) {
			volatile uint32_t *line = EARLY_FB +
			    (early_row * EARLY_CELL_H + gy * EARLY_SCALE + sy) * EARLY_STRIDE +
			    early_col * EARLY_CELL_W;
			for (unsigned int gx = 0; gx < 8; gx++) {
				uint32_t pixel = (glyph[gy] & (1u << gx)) ? 0xffffffffu : 0xff000000u;
				for (unsigned int sx = 0; sx < EARLY_SCALE; sx++)
					line[gx * EARLY_SCALE + sx] = pixel;
			}
		}
	}
	early_col++;
}

static void
m30_early_string(const char *s)
{
	while (*s)
		m30_early_putc(*s++);
}

void
m30_early_mark(unsigned int stage, const char *label)
{
	if (early_disabled || stage > 8) {
		return;
	}
	uint32_t color = 0xff00ff00u | (stage * 28u << 16);
	for (unsigned int y = EARLY_HEIGHT - 32; y < EARLY_HEIGHT; y++) {
		for (unsigned int x = stage * 64; x < (stage + 1) * 64; x++) {
			EARLY_FB[y * EARLY_STRIDE + x] = color;
		}
	}
	__asm__ volatile("dsb sy" ::: "memory");
	m30_early_string("M30LTE EARLY ");
	m30_early_putc((char)('0' + stage));
	m30_early_string(": ");
	m30_early_string(label);
	m30_early_putc('\n');
}

void
m30_early_panic(const char *fmt, va_list *args)
{
	if (early_disabled || early_panicking) {
		return;
	}
	early_panicking = 1;
	m30_early_string("\nM30LTE EARLY PANIC: ");
	va_list copy;
	va_copy(copy, *args);
	_doprnt(fmt, &copy, m30_early_putc, 16);
	va_end(copy);
	m30_early_putc('\n');
	__asm__ volatile("dsb sy" ::: "memory");
}

void
m30_early_disable(void)
{
	m30_early_mark(8, "leaving bootstrap TTBR0");
	early_disabled = 1;
	__asm__ volatile("dsb sy" ::: "memory");
}
#endif /* M30LTE */

/* M30LTE: stub implementations for low-level board-specific functions
 * normally provided by Apple's closed per-SoC libraries. QEMU bring-up
 * only needs these to exist at link time; real hardware bring-up will
 * replace them with proper implementations. */
void *ads_zone(void) { return NULL; }
boolean_t allow_data_exec(void) { return TRUE; }
boolean_t allow_stack_exec(void) { return TRUE; }
void arm64_force_wfi_clock_gate(void) {}
void arm64_prepare_for_sleep(void) {}
void arm64_replace_bootstack(void) {}
void arm64_thread_exception_return(void) {}
void arm_debug_set(void) {}
void arm_debug_set32(void) {}
void arm_debug_set64(void) {}
void arm_fast_fault(void) {}
unsigned int arm_hardware_page_size(void) { return 0; }
unsigned int arm_pt_desc_size(void) { return 0; }
unsigned int arm_pt_root_size(void) { return 0; }
void __bcopyin(void *dst, const void *src, unsigned long len) { return; }
void __bcopyinstr(const void *src, void *dst, unsigned long len, size_t *len_res) { return; }
void __bcopyout(const void *src, void *dst, unsigned long len) { return; }
void __call_continuation(void) {}
void clean_dcache64(void) {}
void CleanPoC_Dcache(void) {}
void CleanPoC_DcacheRegion(unsigned long va, unsigned long size) {}
void CleanPoC_DcacheRegion_Force(unsigned long va, unsigned long size) {}
void CleanPoU_Dcache(void) {}
void CleanPoU_DcacheRegion(unsigned long va, unsigned long size) {}
unsigned int compute_pmap_gc_throttle(void) { return 0; }
void configure_misc_apple_boot_args(void) {}
void configure_misc_apple_regs(void) {}
void configure_timer_apple_regs(void) {}
void consider_machine_adjust(void) {}
void consider_machine_collect(void) {}
int copy_debug_state32(void) { return 0; }
int copy_debug_state64(void) { return 0; }
int __copyin_atomic32(void) { return 0; }
int __copyin_atomic32_wait_if_equals(void) { return 0; }
int __copyin_atomic64(void) { return 0; }
void copyinframe(void) {}
void copyio_recover_table(void) {}
void copyio_recover_table_end(void) {}
void copy_legacy_debug_state(void) {}
int __copyout_atomic32(void) { return 0; }
int __copyout_atomic64(void) { return 0; }
boolean_t coredumpok(void) { return TRUE; }
unsigned int cpu_tte(void) { return 0; }
unsigned int cpu_ttep(void) { return 0; }
boolean_t debug_legacy_state_is_valid(void) { return FALSE; }
boolean_t debug_state_is_valid32(void) { return FALSE; }
boolean_t debug_state_is_valid64(void) { return FALSE; }
int dtrace_copyio_postflight(void) { return 0; }
int dtrace_copyio_preflight(void) { return 0; }
int dtrace_nofault_copy16(void) { return 0; }
int dtrace_nofault_copy32(void) { return 0; }
int dtrace_nofault_copy64(void) { return 0; }
int dtrace_nofault_copy8(void) { return 0; }
void fill32_dczva(void) {}
void fill32_nt(void) {}
void fillPage(void) {}
void flush_dcache64(void) {}
void flush_mmu_tlb_region(void) {}
void FlushPoC_Dcache(void) {}
void FlushPoC_DcacheRegion(unsigned long va, unsigned long size) {}
void FlushPoU_Dcache(void) {}
void FlushPoU_DcacheRegion(unsigned long va, unsigned long size) {}
void InvalidatePoU_Icache(void) {}
void InvalidatePoU_IcacheRegion(unsigned long va, unsigned long size) {}
unsigned int inuse_kernel_ptepages_count(void) { return 0; }
unsigned int inuse_kernel_ttepages_count(void) { return 0; }
unsigned int inuse_kernel_tteroot_count(void) { return 0; }
unsigned int inuse_user_ptepages_count(void) { return 0; }
unsigned int inuse_user_ttepages_count(void) { return 0; }
unsigned int inuse_user_tteroot_count(void) { return 0; }
void Idle_context(void) {}
void Idle_load_context(void) {}
unsigned int hw_lck_ticket_reserve_orig_allow_invalid(void) { return 0; }
unsigned int kpc_arch_init(void) { return 0; }
unsigned int kpc_configurable_config_count(void) { return 0; }
unsigned int kpc_configurable_count(void) { return 0; }
unsigned int kpc_configurable_max(void) { return 0; }
unsigned int kpc_fixed_config_count(void) { return 0; }
unsigned int kpc_fixed_count(void) { return 0; }
unsigned int kpc_fixed_max(void) { return 0; }
unsigned int kpc_get_all_cpus_counters(void) { return 0; }
unsigned int kpc_get_classes(void) { return 0; }
unsigned int kpc_get_configurable_config(void) { return 0; }
unsigned int kpc_get_configurable_counters(void) { return 0; }
unsigned int kpc_get_fixed_config(void) { return 0; }
unsigned int kpc_get_fixed_counters(void) { return 0; }
unsigned int kpc_get_pmu_version(void) { return 0; }
unsigned int kpc_get_rawpmu_config(void) { return 0; }
unsigned int kpc_idle(void) { return 0; }
unsigned int kpc_idle_exit(void) { return 0; }
unsigned int kpc_is_running_configurable(void) { return 0; }
unsigned int kpc_is_running_fixed(void) { return 0; }
unsigned int kpc_pc_capture(void) { return 0; }
unsigned int kpc_rawpmu_config_count(void) { return 0; }
unsigned int kpc_set_config_arch(void) { return 0; }
unsigned int kpc_set_period_arch(void) { return 0; }
unsigned int kpc_set_running_arch(void) { return 0; }
unsigned int kpc_set_sw_inc(void) { return 0; }
unsigned long kvtophys(void) { return 0; }
void m30_secondary_entry(void) {}
void machine_csv(void) {}
void machine_load_context(void) {}
void machine_set_current_thread(void) {}
void machine_stack_attach(void) {}
void machine_stack_detach(void) {}
void machine_stack_handoff(void) {}
void machine_switch_context(void) {}
void machine_tecs(void) {}
void machine_thread_create(void) {}
void machine_thread_destroy(void) {}
void machine_thread_init(void) {}
void machine_thread_on_core(void) {}
void machine_thread_on_core_allow_invalid(void) {}
void machine_thread_process_signature(void) {}
void machine_thread_set_tsd_base(void) {}
void machine_thread_template_init(void) {}
void machine_tecs(void) {}
void mapping_adjust(void) {}
void mapping_free_prime(void) {}
void mapping_set_mod(void) {}
void *mmu_kvtop(void) { return NULL; }
void *mmu_kvtop_wpreflight(void) { return NULL; }
void ml_panic_trap_to_debugger(void) {}
unsigned int native_pt_attr(void) { return 0; }
boolean_t nx_enabled(void) { return TRUE; }
unsigned int num_io_rgns(void) { return 0; }
void pmap_advise_pagezero_range(void) {}
void pmap_adjust_unnest_parameters(void) {}
void pmap_assert_free(void) {}
void pmap_attribute_cache_sync(void) {}
void pmap_asid_flushes(void) {}
void pmap_asid_hits(void) {}
void pmap_asid_misses(void) {}
void pmap_attribute_cache_sync(void) {}
void pmap_batch_set_cache_attributes(void) {}
void pmap_bootstrap(void) {}
void pmap_bootloader_page(void) {}
void pmap_cache_attributes(void) {}
void pmap_change_wiring(void) {}
void pmap_clear_modify(void) {}
void pmap_clear_noencrypt(void) {}
void pmap_clear_reference(void) {}
void pmap_clear_refmod(void) {}
void pmap_clear_refmod_options(void) {}
void pmap_clear_refmod_range_options(void) {}
void pmap_clear_user_ttb(void) {}
void pmap_copy_page(void) {}
void pmap_copy_part_page(void) {}
void pmap_cpu_data_init(void) {}
void pmap_cpu_windows_copy_addr(void) {}
void pmap_create_commpages(void) {}
void pmap_create_options(void) {}
void pmap_disable_NX(void) {}
void pmap_disconnect(void) {}
void pmap_disconnect_options(void) {}
void pmap_dump_page_tables(void) {}
void pmap_enforces_execute_only(void) {}
void pmap_enter(void) {}
void pmap_enter_options(void) {}
void pmap_enter_options_addr(void) {}
void pmap_find_pa(void) {}
void pmap_find_phys(void) {}
void pmap_find_phys_nofault(void) {}
void pmap_flush(void) {}
void pmap_flush_context_init(void) {}
void pmap_footprint_suspend(void) {}
void pmap_fork_nest(void) {}
void pmap_free_pages(void) {}
void pmap_free_pages_span(void) {}
void pmap_get_jit_entitled(void) {}
void pmap_get_refmod(void) {}
void pmap_get_tpro(void) {}
void pmap_get_vm_map_cs_enforced(void) {}
void pmap_has_managed_page(void) {}
void pmap_has_prot_policy(void) {}
void pmap_init(void) {}
void pmap_init_pte_page(void) {}
void pmap_in_ppl(void) {}
void pmap_insert_commpage(void) {}
void pmap_is_exotic(void) {}
void pmap_is_modified(void) {}
void pmap_is_noencrypt(void) {}
void pmap_is_referenced(void) {}
void pmap_kernel_va_bits(void) {}
void pmap_ledger_alloc(void) {}
void pmap_ledger_free(void) {}
void pmap_ledger_verify_size(void) {}
void pmap_lock_phys_page(void) {}
void pmap_max_offset(void) {}
void pmap_next_page(void) {}
void pmap_next_page_hi(void) {}
void pmap_nest(void) {}
void pmap_nop(void) {}
void pmap_object_store(void) {}
void pmap_page_protect(void) {}
void pmap_page_protect_options(void) {}
void pmap_protect(void) {}
void pmap_protect_options(void) {}
void pmap_query_page_info(void) {}
void pmap_query_page_info_retries(void) {}
void pmap_query_resident(void) {}
void pmap_reference(void) {}
void pmap_release_pages_fast(void) {}
void pmap_remove(void) {}
void pmap_remove_options(void) {}
void pmap_require(void) {}
void pmap_ro_zone_atomic_op(void) {}
void pmap_ro_zone_bzero(void) {}
void pmap_ro_zone_memcpy(void) {}
void pmap_set_cache_attributes(void) {}
void pmap_set_jit_entitled(void) {}
void pmap_set_nested(void) {}
void pmap_set_noencrypt(void) {}
void pmap_set_process(void) {}
void pmap_set_tpro(void) {}
void pmap_set_vm_map_cs_enforced(void) {}
void pmap_shared_region_size_min(void) {}
void pmap_switch(void) {}
void pmap_switch_user(void) {}
void pmap_sync_page_attributes_phys(void) {}
void pmap_sync_page_data_phys(void) {}
void pmap_test(void) {}
void pmap_test_text_corruption(void) {}
void pmap_trim(void) {}
void pmap_unmap_compressor_page(void) {}
void pmap_unmap_cpu_windows_copy(void) {}
void pmap_user_va_bits(void) {}
void pmap_valid_address(void) {}
void pmap_valid_page(void) {}
void pmap_virtual_region(void) {}
void pmap_virtual_space(void) {}
void pmap_zero_page(void) {}
void pmap_zero_part_page(void) {}
void resume_idle_cpu(void) {}
void set_mmu_ttb(unsigned long ttb) {}
void set_mmu_ttb_alternate(unsigned long ttb) {}
void set_tcr(unsigned long tcr) {}
kern_return_t start_cpu(void) { return 0; }
kern_return_t thread_bootstrap_return(void) { return 0; }
unsigned long vm_first_phys(void) { return 0; }
unsigned long vm_last_phys(void) { return 0; }
void vm_footprint_suspend(void) {}
#endif /* M30LTE */
