#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
CC=aarch64-linux-gnu-gcc
OBJCOPY=aarch64-linux-gnu-objcopy
CFLAGS="-O2 -ffreestanding -nostdlib -fno-pic -mgeneral-regs-only -mstrict-align -fno-stack-protector -Wall -Wextra"
mkdir -p out
for f in start.S shim.c devices/m30lte.c; do
	$CC $CFLAGS -c $f -o out/${f%.*}.o
done
$CC $CFLAGS -static -T shim.ld -Wl,--build-id=none -Wl,--no-warn-rwx-segments -Wl,-N \
	out/start.o out/shim.o out/devices/m30lte.o -o out/shim.elf
$OBJCOPY -O binary out/shim.elf out/Image
echo "Shim: $(wc -c < out/Image) bytes"

dd if=/dev/zero of=out/empty bs=1 count=4096
mkbootimg --header_version 2 --kernel out/Image --ramdisk out/empty \
	--dtb /tmp/opencode/m30.dtb \
	--base 0x10000000 --kernel_offset 0x8000 --ramdisk_offset 0x2000000 --dtb_offset 0x1f00000 \
	--tags_offset 0x100 --pagesize 2048 \
	--os_version 17.0.0 --os_patch_level 2035-06 \
	--cmdline "console=null" -o out/shim-only.img 2>&1 | tail -10
ls -lh out/shim-only.img 2>&1 | tail -2
