/*
 * Milestone 4: act as iBoot for xnu.
 * Minimal: find payload, copy segments, build boot_args, jump to entry.
 */
#include <stdint.h>
#include "fdt.h"
#include "loader.h"
#include "device.h"

#define BOOT_LINE_LENGTH	608
#define PAGE_16K		0x4000UL

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

_Static_assert(__builtin_offsetof(struct payload, segs) == 0x2a8, "payload header layout");
_Static_assert(__builtin_offsetof(struct boot_args, Video) == 40, "boot_args layout");
_Static_assert(__builtin_offsetof(struct boot_args, CommandLine) == 108, "boot_args layout");
_Static_assert(sizeof(struct boot_args) == 736, "boot_args layout");

static void copy64(uintptr_t dst, uintptr_t src, uint64_t n)
{
	volatile uint64_t *d = (volatile uint64_t *)dst;
	volatile const uint64_t *s = (volatile const uint64_t *)src;
	for (uint64_t i = 0; i < (n + 7) / 8; i++)
		d[i] = s[i];
}

void *memcpy(void *dst, const void *src, uint64_t n)
{
	uint8_t *d = (uint8_t *)dst;
	const uint8_t *s = (const uint8_t *)src;
	for (uint64_t i = 0; i < n; i++)
		d[i] = s[i];
	return dst;
}

static void zero64(uintptr_t dst, uint64_t n)
{
	volatile uint64_t *d = (volatile uint64_t *)dst;
	for (uint64_t i = 0; i < n / 8; i++)
		d[i] = 0;
}

static int magic_ok(const char *m)
{
	static const char want[] = "M30LTXNU";
	for (int i = 0; i < 8; i++)
		if (m[i] != want[i])
			return 0;
	return 1;
}

typedef void (*xnu_entry_t)(uint64_t boot_args_pa);

const char *loader_boot(uintptr_t dtb)
{
	uint64_t rd_start, rd_end;

	/* Scan RAM for M30LTXNU magic - payload could be anywhere */
	uintptr_t scan_addrs[] = {
		0x11000000UL, 0x12000000UL, 0x13000000UL, 0x14000000UL,
		0x15000000UL, 0x16000000UL, 0x17000000UL, 0x18000000UL,
		0x41000000UL, 0x42000000UL, 0x43000000UL, 0x44000000UL,
		0x45000000UL, 0x46000000UL, 0x47000000UL, 0x48000000UL,
		0x49000000UL, 0x4A000000UL, 0x4B000000UL, 0x4C000000UL,
		0x50000000UL, 0x60000000UL, 0x70000000UL, 0x80000000UL,
		0x90000000UL, 0xA0000000UL, 0xB0000000UL, 0xC0000000UL,
	};
	int found = 0;
	for (int s = 0; s < 28; s++) {
		const struct payload *probe = (const struct payload *)scan_addrs[s];
		if (magic_ok(probe->magic)) {
			rd_start = scan_addrs[s];
			rd_end   = scan_addrs[s] + 0x1000000UL;
			found = 1;
			break;
		}
	}
	if (!found)
		return "no initrd payload found";

	const struct payload *p = (const struct payload *)rd_start;
	if (!magic_ok(p->magic))
		return "no M30LTXNU payload";
	if (p->version != 1 || (p->adt_off & 7) || (rd_start & 7))
		return "bad payload header";

	uint64_t pa_of_va_base = p->phys_base - p->virt_base;

	if (rd_end > p->phys_base && rd_start < p->phys_base + p->mem_size)
		return "ramdisk overlaps kernel memory";

	for (uint32_t i = 0; i < p->nsegs; i++) {
		const struct payload_seg *s = &p->segs[i];
		uintptr_t dst = s->vmaddr + pa_of_va_base;
		copy64(dst, rd_start + s->file_off, s->file_size);
		if (s->vmsize > s->file_size)
			zero64(dst + ((s->file_size + 7) & ~7UL),
			       s->vmsize - ((s->file_size + 7) & ~7UL));
	}

	uintptr_t adt_pa = p->kernel_end + pa_of_va_base;
	copy64(adt_pa, rd_start + p->adt_off, p->adt_size);
	uintptr_t ba_pa = (adt_pa + p->adt_size + PAGE_16K - 1) & ~(PAGE_16K - 1);
	uintptr_t top = ba_pa + PAGE_16K;

	zero64(ba_pa, PAGE_16K);
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
	((xnu_entry_t)entry_pa)(ba_pa);
	return "xnu returned";
}
