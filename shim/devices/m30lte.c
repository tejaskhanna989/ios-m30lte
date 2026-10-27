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

	.phys_base = 0x00000000UL,	/* TBD: from the live FDT memory node */
	.mem_size = 0x00000000UL,	/* TBD: from the live FDT memory node */

	.fb_phys = 0x00000000UL,	/* TBD: where Samsung's bootloader leaves the panel */
	.fb_size = 0x00000000UL,	/* TBD */
	.fb_w = 1080,
	.fb_h = 2340,
	.fb_stride = 1080 * 4,

	.gicd_base = 0x00000000UL,	/* TBD: from /proc/device-tree/interrupt-controller */
	.gicd_size = 0x00010000UL,
	.gicr_base = 0x00000000UL,	/* TBD */
	.gicr_size = 0x00100000UL,
	.vtimer_intid = 27,		/* TBD: Exynos timer PPI */
	.ptimer_intid = 26,		/* TBD */
	.sgi_intid = 1,
	.timebase = 24000000,		/* TBD: CNTFRQ_EL0 */

	.psci_version = 0x84000000UL,
	.psci_cpu_on = 0xc4000003UL,
	.psci_cpu_off = 0x84000002UL,
	.psci_cpu_suspend = 0xc4000001UL,
	.psci_system_reset = 0x84000009UL,
	.psci_features = 0x8400000aUL,

	.has_ufs = 0,			/* the M30 has eMMC, not UFS */
	.ufs_base = 0, .ufs_size = 0,
	.emmc_base = 0x00000000UL,	/* TBD: Exynos DWMC host controller */
	.emmc_size = 0x00001000UL,	/* TBD */

	.restart_reason = 0x00000000UL,	/* TBD: Samsung restart reason register */
	.restart_magic = 0x00000000UL,	/* TBD */
	.pshold = 0x00000000UL,		/* TBD */

	.nr_cpus = 8,			/* 2x Cortex-A73 + 6x Cortex-A53 */
	.nr_clusters = 2,
	.cluster0_cpus = 6,		/* A53 little cluster */
	.cluster1_cpus = 2,		/* A73 big cluster */
};

const struct device_config *dev = &m30lte_config;
