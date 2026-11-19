/*
 * Galaxy M30 (m30lte, Samsung Exynos 7885) device configuration.
 *
 * This is the ONLY device this port targets. The shim, the XNU machine
 * config (M30LTE) and the Apple Device Tree generator all follow the
 * Exynos 7885 layout.
 *
 * Values come from the phone's live device tree (/proc/device-tree on
 * Android) and must be verified against the real hardware. Those still
 * marked TBD are filled in as the port progresses; see PORTING.md.
 */
#include "../device.h"

const struct device_config m30lte_config = {
	.name = "m30lte",
	.samsung_boot = 1,	/* Samsung Odin/Heimdall package, not an Android boot.img */

	/* Memory (from /proc/device-tree/memory@*) */
	.phys_base = 0x0000000080000000UL,	/* memory@80000000 */
	.mem_size = 0x000000003da00000UL,	/* ~986 MB, plus upper bank */

	/* Framebuffer (from /proc/device-tree/reserved-memory/framebuffer@0xEC000000) */
	.fb_phys = 0x00000000ec000000UL,	/* framebuffer@0xEC000000 */
	.fb_size = 0x0000000001400000UL,	/* 20 MiB */
	.fb_w = 1080,
	.fb_h = 2340,
	.fb_stride = 1080 * 4,

	/* GICv3 (from /proc/device-tree/interrupt-controller@123001000) */
	.gicd_base = 0x0000000012301000UL,	/* GIC distributor */
	.gicd_size = 0x00010000UL,
	.gicr_base = 0x0000000012302000UL,	/* GIC redistributor */
	.gicr_size = 0x00100000UL,
	.vtimer_intid = 27,		/* ARM architected timer virtual PPI */
	.ptimer_intid = 26,		/* ARM architected timer physical PPI */
	.sgi_intid = 1,			/* SGI1 for cross-CPU signals */
	.timebase = 26000000,		/* 26 MHz CNTFRQ_EL0 */

	/* PSCI / SMC (Samsung SMC calling convention) */
	.psci_version = 0x84000000UL,
	.psci_cpu_on = 0xc4000003UL,
	.psci_cpu_off = 0x84000002UL,
	.psci_cpu_suspend = 0xc4000001UL,
	.psci_system_reset = 0x84000009UL,
	.psci_features = 0x8400000aUL,

	/* Storage (from /proc/device-tree/dwmmc0@13500000) */
	.has_ufs = 0,			/* the M30 has eMMC, not UFS */
	.ufs_base = 0, .ufs_size = 0,
	.emmc_base = 0x0000000013500000UL,	/* Exynos DWMC host controller */
	.emmc_size = 0x0000000000020000UL,

	/* Restart / power-off (TBD: Samsung-specific registers) */
	.restart_reason = 0x00000000UL,
	.restart_magic = 0x00000000UL,
	.pshold = 0x00000000UL,

	/* CPU topology (from /proc/device-tree/cpus/) */
	.nr_cpus = 8,			/* 2x Cortex-A73 + 6x Cortex-A53 */
	.nr_clusters = 2,
	.cluster0_cpus = 6,		/* A53 little cluster */
	.cluster1_cpus = 2,		/* A73 big cluster */
};

const struct device_config *dev = &m30lte_config;
