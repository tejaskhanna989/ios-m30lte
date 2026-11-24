#!/usr/bin/env python3
"""Structural verification of candidate v62 (USERDATA root target)."""
from __future__ import annotations
import hashlib, struct, subprocess
from pathlib import Path

D = Path(__file__).resolve().parent
results = []
def check(n, ok, d=""): results.append((n, bool(ok), d))
def sha(b): return hashlib.sha256(b).hexdigest()

def main():
    img = (D/"shim-boot.img").read_bytes()
    shim = (D/"build/shim_fixed.Image").read_bytes()
    elf = (D/"build/shim_fixed.elf").read_bytes()
    payload = (D/"payload/xnu-payload.bin").read_bytes()
    kernel = (D/"inputs/kernel.development.m30lte").read_bytes()

    # image header v0: kernel region = combined (shim + pad 0x20000 + payload)
    magic, ksz, kaddr, rsz, raddr = struct.unpack_from('<8sIIII', img, 0)
    check("boot.img ANDROID! magic", magic == b'ANDROID!')
    check("kernel_addr == 0x80080000 (proven shim link)", kaddr == 0x80080000, hex(kaddr))
    check("no ramdisk", rsz == 0)
    combined = img[2048:2048+ksz]
    check("combined == shim Image + 0x20000 pad + payload",
          combined[:len(shim)] == shim and combined[0x20000:] == payload
          and set(combined[len(shim):0x20000]) == {0},
          f"shim={len(shim)} pad_to=0x20000 payload={len(payload)}")

    # kernel embedded exactly
    vm, vs, fo, fs = struct.unpack_from('<4Q', payload, 0x2a8)
    seg = payload[fo:fo+fs]
    check("payload seg0 in D22AP-fixed kernel", kernel.find(seg) >= 0)
    check("kernel SHA256 == 45aff1b0...",
          sha(kernel) == "45aff1b01f85b1dbe5a77903050005333eb858980cd1118465c3f11f02bda13d")
    check("payload SHA256 == e1c41dd8...",
          sha(payload) == "e1c41dd83ee70cafc7af9ab91c8c20ed5320ee54a87392434790870d99d39bd0")

    # ELF: entry, CurrentEL, GICv2, watchdog absent
    eh = subprocess.run(["llvm-readelf","-h",str(D/"build/shim_fixed.elf")],capture_output=True,text=True).stdout
    check("ELF entry 0x80080000", "0x80080000" in eh)
    dis = subprocess.run(["llvm-objdump","-d","--no-show-raw-insn",str(D/"build/shim_fixed.elf")],capture_output=True,text=True).stdout
    check("CurrentEL dispatch present", "CurrentEL" in dis)
    check("EL2 state install (HCR/SCTLR/CNTHCTL/eret) present",
          all(x in dis for x in ["HCR_EL2","SCTLR_EL1","CNTHCTL_EL2","eret"]))
    check("GICv2 init present (gicv2_init + 0x1230 base)",
          "gicv2_init" in eh or "gicv2_init" in dis)
    check("watchdog 0x10160000 absent", "10160000" not in dis.lower())

    # ADT / arithmetic
    madt, ver, nsegs = struct.unpack_from('<8sII', payload, 0)
    vb, ev, ao, asz, ke, pb, ms = struct.unpack_from('<7Q', payload, 0x10)
    check("payload M30LTXNU v1, 10 segs", madt == b'M30LTXNU' and ver == 1 and nsegs == 10)
    check("ADT SHA256 == 2dc36c05...", sha(payload[ao:ao+asz]) == "2dc36c056e62a563bc5b2262c296d8731e1d8ad9e804d388054c156cec7bd577")
    adt_pa = (ke + pb - vb) & 0xffffffffffffffff
    ba_pa = (adt_pa + asz + 0x4000 - 1) & ~0x3fff
    check("ADT PA 0x82454000 in RAM", adt_pa == 0x82454000)
    check("boot_args PA 0x82458000", ba_pa == 0x82458000)
    check("entry VA 0xfffffff007411488", ev == 0xfffffff007411488)

    # Runtime layout from the generated manifest; the shim reads these values
    # from the payload header, and its complete footprint ends before payload.
    import json
    manifest = json.loads((D/"manifest.json").read_text())
    cmdline = manifest["payload"]["cmdline"]
    check("v62 payload cmdline uses cpus=6", "cpus=6" in cmdline, cmdline)
    check("v62 payload cmdline mutes M30/A5 framebuffer console", "a5fb_noconsole=1" in cmdline)
    check("v62 payload cmdline keeps display on", "a5fb_keep_on=1" in cmdline)
    runtime = manifest["runtime_layout"]
    check("manifest payload runtime address 0x800a0000",
          int(runtime["payload_runtime_address"], 16) == 0x800a0000)
    check("payload starts after complete shim footprint",
          int(manifest["shim"]["elf_footprint"]["footprint_end"], 16) <= 0x800a0000
          and runtime["payload_after_complete_shim_footprint"] is True)
    check("payload offset in kernel 0x20000",
          runtime["payload_offset_in_kernel"] == 0x20000)

    failed = 0
    for n, ok, d in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {n}: {d}")
        failed += 0 if ok else 1
    print(f"RESULT: {len(results)-failed}/{len(results)} PASS")
    return 1 if failed else 0

if __name__ == "__main__": raise SystemExit(main())
