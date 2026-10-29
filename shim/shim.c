/*
 * Milestone 2: boot XNU kernel on M30LTE.
 * Scans RAM for M30LTXNU payload magic, then loads and jumps.
 */
#include <stdint.h>
#include <stddef.h>
#include "device.h"

#define PAGE_16K		0x4000UL
#define BOOT_LINE_LENGTH	608

struct payload_seg {
	uint64_t vmaddr, vmsize, file_off, file_size;
};

struct payload {
	char magic[8];
	uint32_t version, nsegs;
	uint64_t virt_base, entry_va, adt_off, adt_size, kernel_end;
	uint64_t phys_base, mem_size;
	char cmdline[BOOT_LINE_LENGTH];
	struct payload_seg segs[];
};

struct boot_video {
	uint64_t v_baseAddr, v_display, v_rowBytes, v_width, v_height, v_depth;
};

struct boot_args {
	uint16_t Revision, Version;
	uint64_t virtBase, physBase, memSize, topOfKernelData;
	struct boot_video Video;
	uint32_t machineType;
	uint64_t deviceTreeP;
	uint32_t deviceTreeLength;
	char CommandLine[BOOT_LINE_LENGTH];
	uint64_t bootFlags, memSizeActual;
};

static int magic_ok(const char *m)
{
	static const char want[] = "M30LTXNU";
	for (int i = 0; i < 8; i++)
		if (m[i] != want[i])
			return 0;
	return 1;
}

#define rsr(r) ({ uint64_t _v; __asm__ volatile("mrs %0, " r : "=r"(_v)); _v; })
#define wsr(r, v) __asm__ volatile("msr " r ", %0" : : "r"((uint64_t)(v)))
#define isb() __asm__ volatile("isb" ::: "memory")

static inline uint32_t rd32(uintptr_t a) { return *(volatile uint32_t *)a; }
static inline uint64_t rd64(uintptr_t a) { return *(volatile uint64_t *)a; }
static inline void wr32(uintptr_t a, uint32_t v) { *(volatile uint32_t *)a = v; }
static inline void wr8(uintptr_t a, uint8_t v) { *(volatile uint8_t *)a = v; }

extern char secondary_entry[];
extern char _data_end[];

static uint64_t smc(uint64_t fn, uint64_t a1, uint64_t a2, uint64_t a3)
{
	register uint64_t x0 __asm__("x0") = fn;
	register uint64_t x1 __asm__("x1") = a1;
	register uint64_t x2 __asm__("x2") = a2;
	register uint64_t x3 __asm__("x3") = a3;
	__asm__ volatile("smc #0"
			 : "+r"(x0), "+r"(x1), "+r"(x2), "+r"(x3)
			 : : "x4", "x5", "x6", "x7", "x8", "x9", "x10", "x11",
			     "x12", "x13", "x14", "x15", "x16", "x17", "memory");
	return x0;
}

static void delay_ms(unsigned ms)
{
	for (unsigned i = 0; i < ms * 1000; i++)
		__asm__ volatile("nop");
}

static void __attribute__((noreturn)) reset(unsigned after_s)
{
	wr32(dev->restart_reason, dev->restart_magic);
	__asm__ volatile("dsb sy" ::: "memory");
	smc(dev->psci_system_reset, 0, 0, 0);
	wr32(dev->pshold, 0);
	for (;;)
		__asm__ volatile("wfe");
}

static void irq_handler(void)
{
	uint64_t iar = rsr("icc_iar1_el1");
	uint32_t id = iar & 0xffffff;
	if (id >= 1020 && id <= 1023)
		return;
	wsr("icc_eoir1_el1", iar);
	isb();
}

void exc_handler(uint64_t slot, uint64_t *regs)
{
	if (slot == 5) {
		irq_handler();
		return;
	}
	for (;;) {
		__asm__ volatile("wfe");
	}
}

void secondary_main(void)
{
	for (;;)
		__asm__ volatile("wfe");
}

#define GICD_BASE		0x12301000UL
#define GICR_BASE		0x12302000UL
#define GICR_PE_SIZE		0x20000UL
#define GICR_TYPER		0x08
#define GICR_WAKER		0x14
#define GICR_SGI		0x10000
#define GICR_ISENABLER0		(GICR_SGI + 0x100)
#define GICR_ICENABLER0		(GICR_SGI + 0x180)
#define GICR_IPRIORITYR		(GICR_SGI + 0x400)
#define GICR_IGROUPR0		(GICR_SGI + 0x080)

static uintptr_t find_gicr(void)
{
	uint64_t aff = rsr("mpidr_el1");
	uint32_t want = (aff & 0xffffff) | ((aff >> 8) & 0xff000000);

	for (uintptr_t off = 0; off < 0x100000; off += GICR_PE_SIZE) {
		uint64_t typer = rd64(GICR_BASE + off + GICR_TYPER);
		if ((uint32_t)(typer >> 32) == want)
			return GICR_BASE + off;
		if (typer & (1 << 4))
			break;
	}
	return 0;
}

static void gicd_wait_rwp(void)
{
	for (int i = 0; i < 1000000 && (rd32(GICD_BASE) & (1U << 31)); i++)
		;
}

static void test_gic(void)
{
	uint32_t dctlr = rd32(GICD_BASE);
	wr32(GICD_BASE, dctlr | 0x1);
	gicd_wait_rwp();

	uintptr_t r = find_gicr();
	if (!r)
		return;

	uint32_t waker = rd32(r + GICR_WAKER);
	if (waker & 2) {
		wr32(r + GICR_WAKER, waker & ~2U);
		for (int i = 0; i < 100000 && (rd32(r + GICR_WAKER) & 4); i++)
			;
	}

	wr32(r + GICR_IGROUPR0, 0xffffffff);
	for (int id = 0; id < 32; id++)
		wr8(r + GICR_IPRIORITYR + id, 0xa0);
	wr32(r + GICR_ISENABLER0, (1U << 27) | (1U << 26) | (1U << 1));

	uint64_t ctlr = rsr("icc_ctlr_el1");
	wsr("icc_ctlr_el1", ctlr & ~2ULL);
	wsr("icc_pmr_el1", 0xf0);
	wsr("icc_bpr1_el1", 0);
	wsr("icc_igrpen1_el1", 1);
	isb();

	wsr("cntv_tval_el0", rsr("cntfrq_el0") / 100);
	wsr("cntv_ctl_el0", 1);
	delay_ms(100);
	wsr("cntv_ctl_el0", 0);
}

void shim_main(uint64_t dtb)
{
	(void)dtb;

	/* Samsung Exynos watchdog: kick to prevent reset during early boot. */
	volatile uint32_t *wdt = (volatile uint32_t *)0x10160000UL;
	*wdt = 0x1;

	volatile uint32_t *fb = (volatile uint32_t *)dev->fb_phys;
	/* red = running */
	for (int i = 0; i < 2048; i++) fb[i] = 0xFF0000FF;

	const struct payload *p = NULL;

	/* Try all possible locations */
	uintptr_t spots[] = {
		0x11000000UL,
		0x10010000UL,
		0x10008000UL + 0x4000UL,
		0x10008000UL + 0x8000UL,
		0x10008000UL + 0x10000UL,
		0x10020000UL,
		0x12000000UL,
		0x10800000UL,
	};
	for (int s = 0; s < 8 && !p; s++) {
		if (magic_ok((const char *)spots[s])) {
			p = (const struct payload *)spots[s];
			break;
		}
	}

	if (!p) {
		for (uintptr_t addr = 0x10000000UL; addr < 0x15000000UL; addr += 4) {
			if (magic_ok((const char *)addr)) {
				p = (const struct payload *)addr;
				break;
			}
		}
	}

	if (!p) {
		for (int i = 2048; i < 4096; i++) fb[i] = 0xFFFF0000;
		for (;;) __asm__ volatile("wfe");
	}

	for (int i = 4096; i < 6144; i++) fb[i] = 0xFF00FF00;

	if (p->version != 1 || (p->adt_off & 7))
		for (;;) __asm__ volatile("wfe");

	uint64_t pa_of_va_base = p->phys_base - p->virt_base;

	/* Copy kernel segments. */
	for (uint32_t i = 0; i < p->nsegs; i++) {
		const struct payload_seg *s = &p->segs[i];
		uintptr_t dst = s->vmaddr + pa_of_va_base;
		const uint8_t *src = (const uint8_t *)p + s->file_off;
		for (uint64_t j = 0; j < (s->file_size + 7) / 8; j++)
			((volatile uint64_t *)dst)[j] = ((const volatile uint64_t *)src)[j];
		if (s->vmsize > s->file_size)
			for (uint64_t j = 0; j < (s->vmsize - ((s->file_size + 7) & ~7UL)) / 8; j++)
				((volatile uint64_t *)(dst + ((s->file_size + 7) & ~7UL)))[j] = 0;
	}

	/* Place ADT and boot_args behind kernel. */
	uintptr_t adt_pa = p->kernel_end + pa_of_va_base;
	const uint8_t *adt_src = (const uint8_t *)p + p->adt_off;
	for (uint64_t j = 0; j < p->adt_size / 8; j++)
		((volatile uint64_t *)adt_pa)[j] = ((const volatile uint64_t *)adt_src)[j];
	uintptr_t ba_pa = (adt_pa + p->adt_size + PAGE_16K - 1) & ~(PAGE_16K - 1);
	uintptr_t top = ba_pa + PAGE_16K;

	for (uint64_t j = 0; j < PAGE_16K / 8; j++)
		((volatile uint64_t *)ba_pa)[j] = 0;

	volatile struct boot_args *ba = (volatile struct boot_args *)ba_pa;
	ba->Revision = 2;
	ba->Version = 2;
	ba->virtBase = p->virt_base;
	ba->physBase = p->phys_base;
	ba->memSize = p->mem_size;
	ba->topOfKernelData = top;
	ba->Video.v_baseAddr = dev->fb_phys;
	ba->Video.v_display = 1;
	ba->Video.v_rowBytes = dev->fb_stride;
	ba->Video.v_width = dev->fb_w;
	ba->Video.v_height = dev->fb_h;
	ba->Video.v_depth = 32;
	ba->deviceTreeP = adt_pa - pa_of_va_base;
	ba->deviceTreeLength = (uint32_t)p->adt_size;
	for (int i = 0; i < BOOT_LINE_LENGTH; i++)
		ba->CommandLine[i] = p->cmdline[i];
	ba->memSizeActual = p->mem_size;

	uintptr_t entry_pa = p->entry_va + pa_of_va_base;

	__asm__ volatile("dsb sy; ic iallu; dsb sy; isb" ::: "memory");
	((void (*)(uint64_t))entry_pa)(ba_pa);

	for (;;)
		__asm__ volatile("wfe");
}
