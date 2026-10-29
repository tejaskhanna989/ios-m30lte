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

python3 << 'PY'
import os
shim = open('out/Image','rb').read()
# pad to 32KB
pad = (0x8000 - len(shim)) % 0x8000
shim_p = shim + b'\x00'*pad
payload = open('/home/tejas/Projects/m30lte-ios/out/payload.bin','rb').read()
combined = shim_p + payload
open('out/combined.bin','wb').write(combined)
print(f'shim_padded={len(shim_p)} payload={len(payload)} combined={len(combined)}')
PY

dd if=/dev/zero of=out/empty bs=1 count=4096
mkbootimg --header_version 2 --kernel out/combined.bin --ramdisk out/empty \
	 --base 0x10000000 --kernel_offset 0x8000 --ramdisk_offset 0x200000 \
	--tags_offset 0x100  --pagesize 2048 \
	--os_version 17.0.0 --os_patch_level 2035-06 \
	--cmdline "console=null" -o out/shim-boot.img
ls -lh out/shim-boot.img
