#pragma once
#include <stdint.h>

/* Boot the M30LTXNU payload found in the ABL ramdisk; returns only on error. */
const char *loader_boot(uintptr_t dtb);
