/*
 * M30LTE: Exynos eMMC driver stub.
 * Will be implemented fully for real hardware bring-up.
 * For QEMU testing, this is a no-op.
 */
#include <stdint.h>
#include "console.h"
#include "device.h"

void test_emmc(void) {
	con_str("EMMC", "stub - not implemented");
	con_skip();
}
