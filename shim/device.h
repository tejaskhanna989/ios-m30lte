/*
 * Device abstraction for the boot shim.
 *
 * ios-m30 was written for the Galaxy M30 (m30, Samsung Exynos 7885).
 * This header adds a struct device_config so the same shim source can be
 * built for other devices (starting with the Galaxy M30 / m30lte).
 *
 * Each device provides a const struct device_config instance in
 * shim/devices/<name>.c. shim_main() selects one at runtime (later: from
 * the DTB or a build-time option).
 */
#pragma once
#include <stdint.h>

struct device_config {
	const char *name;

	/* Boot image format */
	int samsung_boot;	/* 1: Samsung Odin/Heimdall package, 0: Android boot.img v2 */

	/* Memory */
	uint64_t phys_base;
	uint64_t mem_size;

	/* Framebuffer (ABL / bootloader splash) */
	uint64_t fb_phys;
	uint64_t fb_size;
	int fb_w, fb_h, fb_stride;

	/* GICv3 */
	uint64_t gicd_base, gicd_size;
	uint64_t gicr_base, gicr_size;
	int vtimer_intid, ptimer_intid, sgi_intid;
	unsigned timebase;

	/* PSCI / SMC */
	uint64_t psci_version;
	uint64_t psci_cpu_on, psci_cpu_off, psci_cpu_suspend;
	uint64_t psci_system_reset, psci_features;

	/* Storage */
	int has_ufs;		/* 1: UFS host (m30), 0: eMMC (m30lte) */
	uint64_t ufs_base, ufs_size;	/* used when has_ufs */
	uint64_t emmc_base, emmc_size;	/* used when !has_ufs */

	/* Restart / power-off */
	uint64_t restart_reason;
	uint32_t restart_magic;
	uint64_t pshold;

	/* CPU topology */
	int nr_cpus;
	int nr_clusters;
	int cluster0_cpus, cluster1_cpus;
};

extern const struct device_config *dev;
