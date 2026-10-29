#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
CC=aarch64-linux-gnu-gcc
OBJCOPY=aarch64-linux-gnu-objcopy
CFLAGS="-O2 -ffreestanding -nostdlib -fno-pic -mgeneral-regs-only -mstrict-align -fno-stack-protector -Wall -Wextra"
mkdir -p out
$CC $CFLAGS -c start.S -o out/start.o
$CC $CFLAGS -static -T shim.ld -Wl,--build-id=none -Wl,--no-warn-rwx-segments -Wl,-N \
	out/start.o -o out/shim.elf
$OBJCOPY -O binary out/shim.elf out/Image

# Pad shim to exact stock kernel size (24323976 bytes)
STOCK_KERNEL_SIZE=24323976
python3 -c "
data = open('out/Image','rb').read()
data += b'\x00' * ($STOCK_KERNEL_SIZE - len(data))
open('out/Image_24mb','wb').write(data)
print('Padded to 24MB')
"

dd if=/dev/zero of=out/empty.img bs=4096 count=1 2>/dev/null
mkbootimg --header_version 0 \
	--kernel out/Image_24mb \
	--ramdisk out/empty.img \
	--base 0x10000000 \
	--kernel_offset 0x8000 \
	--ramdisk_offset 0x1000000 \
	--second_offset 0x00f00000 \
	--tags_offset 0x100 \
	--pagesize 2048 \
	--os_version 10.0.0 \
	--os_patch_level 2020-05 \
	--cmdline "androidboot.selinux=permissive androidboot.selinux=permissive" \
	-o out/shim-24mb.img 2>&1 | tail -3
ls -lh out/shim-24mb.img
