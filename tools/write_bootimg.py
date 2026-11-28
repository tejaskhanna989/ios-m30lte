#!/usr/bin/env python3
"""Write a generic Android boot image v0 with the exact M30 layout used by v87.

No external mkbootimg dependency; deterministic and byte-checkable.

  write_bootimg.py KERNEL_BLOB OUT --cmdline "..." [--ramdisk FILE]
"""
import argparse
import hashlib
import struct

PAGE = 2048
BASE = 0x80000000
KERNEL_OFFSET = 0x80000
RAMDISK_OFFSET = 0x200000
TAGS_OFFSET = 0x100
OS_VERSION_RAW = 0x14000145   # 10.0.0 / 2020-05, same as v87
BOARD = b"m30lte"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kernel")
    ap.add_argument("out")
    ap.add_argument("--cmdline", default="console=null")
    ap.add_argument("--ramdisk")
    a = ap.parse_args()

    kernel = open(a.kernel, "rb").read()
    ramdisk = open(a.ramdisk, "rb").read() if a.ramdisk else b""
    hdr = bytearray(PAGE)
    struct.pack_into("<8s", hdr, 0, b"ANDROID!\0")
    struct.pack_into("<10I", hdr, 8,
                     len(kernel), BASE + KERNEL_OFFSET,
                     len(ramdisk), BASE + RAMDISK_OFFSET if ramdisk else 0,
                     0, 0, BASE + TAGS_OFFSET, PAGE, 0, OS_VERSION_RAW)
    hdr[48:48 + len(BOARD)] = BOARD
    cl = a.cmdline.encode()
    hdr[64:64 + min(len(cl), 511)] = cl[:511]
    image_id = hashlib.sha1(kernel + ramdisk).digest()
    hdr[1600:1620] = image_id
    out = bytes(hdr) + kernel
    if ramdisk:
        out += b"\0" * (-len(out) % PAGE)
        out += ramdisk
        out += b"\0" * (-len(out) % PAGE)
    open(a.out, "wb").write(out)
    print(f"wrote {a.out}: {len(out)} bytes, kernel={len(kernel)}, ramdisk={len(ramdisk)}")


if __name__ == "__main__":
    main()
