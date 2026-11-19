#!/usr/bin/env python3
"""Offline structural verification of candidate v3 (no device access).

Checks: ARM64 Image header, boot header v2 fields, kernel/payload/combined
bounds and offsets, entry/ADT/boot_args arithmetic, and watchdog absence in
the final linked shim ELF.
"""
from __future__ import annotations

import hashlib
import re
import struct
import subprocess
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
KERNEL = D.parent.parent.parent / "milestone_artifacts/ci_44528894772/kernel.development.m30lte"
SHIM_ELF = D / "build/shim.elf"
IMG = D / "m30lte-ios-candidate-20261119-v4.img"

PAGE = 2048
BASE = 0x10000000
KERN_OFF = 0x8000
INITRD_OFF = 0x1000000
DTB_OFF = 0x1F00000
ADT_SIZE = 0x27C4
EXPECTED_KERNEL_SHA = "a14a266833ddad0c7099240ad62eee118ec533522e6cdbbe6cb739554cb6ec36"
EXPECTED_ADT_SHA = "2dc36c056e62a563bc5b2262c296d8731e1d8ad9e804d388054c156cec7bd577"

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, bool(ok), detail))


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    kernel = KERNEL.read_bytes()
    shim = (D / "Image").read_bytes()
    payload = (D / "payload.bin").read_bytes()
    combined = (D / "combined.bin").read_bytes()
    img = IMG.read_bytes()

    check("kernel SHA256 matches CI", sha(kernel) == EXPECTED_KERNEL_SHA, sha(kernel))
    check("payload embeds corrected ADT",
          sha((D / "m30lte-corrected.adt").read_bytes()) == EXPECTED_ADT_SHA)

    # ARM64 Image header (shim)
    to, isz, flags = struct.unpack_from("<QQQ", shim, 8)
    code0, = struct.unpack_from("<I", shim, 0)
    check("ARM64 Image header code0 = branch to _start",
          (code0 & 0xFC000000) == 0x14000000, hex(code0))
    check("ARM64 Image header text_offset=0, magic ARM64, flags=0xa",
          to == 0 and shim[0x38:0x3c] == b"ARMd" and flags == 0xA,
          f"text_offset={hex(to)} magic={shim[0x38:0x3c]!r} flags={hex(flags)}")
    check("ARM64 Image image_size sane (< 1MiB)", 0 < isz < 0x100000, hex(isz))

    # Boot header v2
    magic = img[:8]
    ksize, kaddr, rsize, raddr, ssize, saddr, tags, page, hdrv, osv = struct.unpack_from("<10I", img, 8)
    cmdline = img[0x40:0x240].split(b"\0")[0]
    hdr_size, = struct.unpack_from("<I", img, 0x66C)
    dtb_size, dtb_addr = struct.unpack_from("<IQ", img, 0x670)
    check("boot.img magic ANDROID!/header v2/page 2048",
          magic == b"ANDROID!" and hdrv == 2 and page == PAGE,
          f"{magic!r} hdrv={hdrv} page={page}")
    check("kernel load addr = base+0x8000", kaddr == BASE + KERN_OFF, hex(kaddr))
    check("ramdisk load addr = base+0x1000000", raddr == BASE + INITRD_OFF, hex(raddr))
    check("DTB load addr = base+0x1f00000", dtb_addr == BASE + DTB_OFF, hex(dtb_addr))
    check("tags addr = base+0x100", tags == BASE + 0x100, hex(tags))
    check("cmdline matches payload cmdline",
          cmdline == b"debug=0xc serial=3 keepsyms=1", cmdline.decode())
    check("boot header size 0x67c, dtb size 16", hdr_size == 0x67C and dtb_size == 16,
          f"hdr={hex(hdr_size)} dtb={hex(dtb_size)}")

    # Bounds
    kern_start = PAGE
    kern_end = kern_start + ksize
    rd_start = (kern_end + PAGE - 1) & ~(PAGE - 1)
    rd_end = rd_start + ((rsize + PAGE - 1) & ~(PAGE - 1))
    dtb_start = rd_end
    check("kernel bytes in image == combined.bin",
          img[kern_start:kern_end] == combined[:ksize], f"ksize={hex(ksize)}")
    check("combined.bin starts with shim Image", combined[:len(shim)] == shim)
    check("shim padded to 0x8000 with zeros", set(combined[len(shim):0x8000]) == {0})
    check("all image regions within file bounds",
          kern_end <= len(img) and rd_end <= len(img) and dtb_start + dtb_size <= len(img),
          f"img={len(img)} kern_end={hex(kern_end)} rd_end={hex(rd_end)} dtb_end={hex(dtb_start+dtb_size)}")

    # Payload / arithmetic
    magic_p, ver, nsegs = struct.unpack_from("<8sII", payload, 0)
    vbase, entry_va, adt_off, adt_sz, kend_va, pbase, memsz = struct.unpack_from("<7Q", payload, 0x10)
    pa_delta = (pbase - vbase) & 0xFFFFFFFFFFFFFFFF
    entry_pa = (entry_va + pa_delta) & 0xFFFFFFFFFFFFFFFF
    adt_pa = (kend_va + pa_delta) & 0xFFFFFFFFFFFFFFFF
    ba_pa = (adt_pa + adt_sz + 0x4000 - 1) & ~0x3FFF
    M30_DELTA = 0xFFFFFFEF86000000
    check("payload magic M30LTXNU v1, nsegs=10",
          magic_p == b"M30LTXNU" and ver == 1 and nsegs == 10, f"nsegs={nsegs}")
    # The shim uses pa_of_va_base = phys_base - virt_base (mod 2^64), which is
    # the additive inverse of M30_ADT_KVA_DELTA = virt_base - phys_base.
    check("phys_base - virt_base == -M30_ADT_KVA_DELTA (mod 2^64)",
          pa_delta == ((-M30_DELTA) & 0xFFFFFFFFFFFFFFFF),
          f"pa_delta={hex(pa_delta)} inverse={hex((-M30_DELTA) & 0xFFFFFFFFFFFFFFFF)}")
    check("entry VA -> PA arithmetic", entry_pa == 0x81427488, hex(entry_pa))
    check("ADT PA in RAM window [0x80000000,0xbd900000)",
          0x80000000 <= adt_pa and adt_pa + ADT_SIZE <= 0xBD900000,
          f"adt_pa={hex(adt_pa)} end={hex(adt_pa+ADT_SIZE)}")
    check("boot_args 16K-aligned after ADT", ba_pa == 0x824A4000, hex(ba_pa))
    check("payload ADT sha256 correct",
          sha(payload[adt_off:adt_off + adt_sz]) == EXPECTED_ADT_SHA)

    # Watchdog absence in linked ELF
    dis = subprocess.run(["llvm-objdump", "-d", "--no-show-raw-insn", str(SHLF := SHIM_ELF)],
                         capture_output=True, text=True, check=True).stdout
    check("watchdog 0x10160000 absent from linked shim ELF",
          "10160000" not in dis.lower())
    check("interrupts masked at entry, never unmasked",
          re.search(r"msr\s+DAIFSet,\s*#0xf", dis, re.I) is not None
          and re.search(r"msr\s+DAIFClr", dis, re.I) is None)

    failed = 0
    for name, ok, detail in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")
        failed += 0 if ok else 1
    print(f"RESULT: {len(results) - failed}/{len(results)} PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
