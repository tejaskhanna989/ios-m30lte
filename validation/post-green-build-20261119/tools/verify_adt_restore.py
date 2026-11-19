#!/usr/bin/env python3
"""Verify the ADT restore path of a linked M30LTE kernel (21 checks).

Checks split into two groups:

  ADT content (from the linked Mach-O's _m30_adt_expected, which must be
  byte-identical to the buildtree header's embedded array):
    1-2. size and SHA256 of the embedded ADT
    3.   embedded ADT parses (tools/adt.py semantics)
    4-7. device-tree node name, compatible (samsung,m30lte primary),
         model, target-type
    8-11. chosen: dram-base, dram-size, firmware-version, panic log size
    12-13. unique-chip-id, chip-id
    14-17. structure: memory-map, cpus with exynos7885 cores, GIC node,
         vtimer INTID 27

  Linked restore path:
    18. _m30_adt_expected symbol present and located in __TEXT __const
    19. _m30_adt_dcache_op_range symbol present (IVAC/CIVAC path)
    20. _m30_adt_hex symbol present (diagnostic path)
    21. _PE_init_platform disassembly calls _SecureDTInit, then a
        dt_size < 0x40 guard, then _pe_identify_machine - i.e. the restore
        runs between SecureDTInit and pe_identify_machine

Exit status is 0 only if all checks pass.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import struct
import subprocess
import sys
from pathlib import Path

ADT_SIZE = 0x27c4
ADT_SHA256 = "2dc36c056e62a563bc5b2262c296d8731e1d8ad9e804d388054c156cec7bd577"
DRAM_BASE = 0x80000000
DRAM_SIZE = 0x3D900000
CHIP_ID = 0x8015
UNIQUE_CHIP_ID = 0x5357454554000001
FIRMWARE_VERSION = b"m30lte-shim"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(cmd: list[str]) -> str:
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True,
                              errors="replace")
    return completed.stdout


def read_adt(path: Path) -> bytes:
    return path.read_bytes()


def section_file_offset(kernel: Path) -> tuple[int, int]:
    """Return (file_offset_of___TEXT___const, ...) for the section containing _m30_adt_expected."""
    buf = open(kernel, "rb").read()
    magic, cputype, cpusubtype, filetype, ncmds, sizeofcmds, flags, reserved = struct.unpack_from(
        "<IiiIIIII", buf, 0)
    assert magic == 0xFEEDFACF, "expected 64-bit Mach-O"
    off = 32
    secs = []
    for _ in range(ncmds):
        cmd, cmdsize = struct.unpack_from("<II", buf, off)
        if cmd == 0x19:
            (segname, vmaddr, vmsize, fileoff, filesize, maxprot, initprot, nsects, sflags) = struct.unpack_from(
                "<16sQQQQiiII", buf, off + 8)
            sec_off = off + 72
            for _ in range(nsects):
                sectname, seg2, addr, size, sfileoff, align, reloff, nreloc, sflags2, r1, r2, r3 = struct.unpack_from(
                    "<16s16sQQIIIIIIII", buf, sec_off)
                secs.append((seg2.split(b"\0")[0].decode(), sectname.split(b"\0")[0].decode(),
                             addr, size, sfileoff))
                sec_off += 80
        off += cmdsize
    return buf, secs


def adt_parse(data: bytes):
    """Minimal ADT walk using tools/adt.py semantics."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
    import adt as adtlib  # noqa: E402
    root, _ = adtlib.parse(data)
    return root


def node_props(node):
    return {k: v for k, _, v in node.props}


def find_child(node, name):
    for c in node.children:
        if node_props(c).get("name", b"").split(b"\0")[0].decode() == name:
            return c
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", required=True, type=Path)
    ap.add_argument("--buildtree", required=True, type=Path)
    ap.add_argument("--nm", default="llvm-nm")
    ap.add_argument("--objdump", default="llvm-objdump")
    args = ap.parse_args()

    kernel = args.kernel
    buf, secs = section_file_offset(kernel)

    results = []

    def check(name, ok, detail=""):
        results.append((name, bool(ok), detail))

    # --- extract embedded ADT from the linked kernel ---
    nm = run([args.nm, "-n", str(kernel)])
    exp_addr = None
    for line in nm.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[2] == "_m30_adt_expected":
            exp_addr = int(parts[0], 16)
            break
    exp_data = None
    exp_section = None
    for seg, name, addr, size, foff in secs:
        if addr <= (exp_addr or 0) < addr + size:
            local = exp_addr - addr
            exp_data = buf[foff + local: foff + local + ADT_SIZE]
            exp_section = f"{seg} {name}"
            break

    check("18. _m30_adt_expected symbol present in __TEXT __const",
          exp_addr is not None and exp_data is not None and exp_section == "__TEXT __const",
          f"addr={hex(exp_addr) if exp_addr else 'missing'} section={exp_section}")

    check("1. embedded ADT size is 0x27c4 (10180 bytes)",
          exp_data is not None and len(exp_data) == ADT_SIZE,
          f"size={len(exp_data) if exp_data else 'missing'}")

    check("2. embedded ADT SHA256 is the corrected M30LTE tree",
          exp_data is not None and sha256(exp_data) == ADT_SHA256,
          sha256(exp_data) if exp_data else "missing")

    # --- buildtree header array must be byte-identical to the linked array ---
    hdr = (args.buildtree / "osfmk" / "arm64" / "sweet_early_adt_readback.h").read_text()
    m = re.search(r"m30_adt_expected\[M30_ADT_EXPECTED_SIZE\]\s*=\s*\{(.*?)\};", hdr, re.S)
    hdr_bytes = bytes(int(b, 16) for b in re.findall(r"0x[0-9a-fA-F]{2}", m.group(1))) if m else b""
    check("2b. buildtree header embedded ADT matches the linked kernel ADT",
          hdr_bytes == exp_data, f"header_sha={sha256(hdr_bytes) if hdr_bytes else 'missing'}")

    # --- parse the ADT ---
    try:
        root = adt_parse(exp_data)
        parsed = True
    except Exception as exc:  # noqa: BLE001
        root = None
        parsed = False
        print(f"adt parse error: {exc}")
    check("3. embedded ADT parses (device_tree format)", parsed)

    props = node_props(root) if root else {}
    name = props.get("name", b"").split(b"\0")[0].decode("utf-8", "replace")
    check("4. root node name is device-tree", name == "device-tree", name)

    compat_items = [p.decode("utf-8", "replace") for p in props.get("compatible", b"").split(b"\0") if p]
    check("5. compatible leads with samsung,m30lte",
          compat_items and compat_items[0] == "samsung,m30lte", "|".join(compat_items))

    model = props.get("model", b"").split(b"\0")[0].decode("utf-8", "replace")
    check("6. model is iPhone10,3 (donor identity, intentional)",
          model == "iPhone10,3", model)

    ttype = props.get("target-type", b"").split(b"\0")[0].decode("utf-8", "replace")
    check("7. target-type is D22 (XNU match constraint)",
          ttype == "D22", ttype)

    chosen = find_child(root, "chosen") if root else None
    chosen_props = node_props(chosen) if chosen else {}
    dram_base = struct.unpack("<Q", chosen_props.get("dram-base", b"\0" * 8)[:8])[0]
    check("8. dram-base is 0x80000000", dram_base == DRAM_BASE, hex(dram_base))

    dram_size = struct.unpack("<Q", chosen_props.get("dram-size", b"\0" * 8)[:8])[0]
    check("9. dram-size is 0x3d900000 (985 MiB)", dram_size == DRAM_SIZE, hex(dram_size))

    fw = chosen_props.get("firmware-version", b"").split(b"\0")[0]
    check("10. firmware-version is m30lte-shim", fw == FIRMWARE_VERSION, fw.decode("utf-8", "replace"))

    pls = struct.unpack("<I", chosen_props.get("embedded-panic-log-size", b"\0\0\0\0")[:4])[0]
    check("11. embedded-panic-log-size is 0x100000 (1 MiB)", pls == 0x100000, hex(pls))

    uchip = struct.unpack("<Q", chosen_props.get("unique-chip-id", b"\0" * 8)[:8])[0]
    check("12. unique-chip-id is 0x5357454554000001 (SWEET marker)",
          uchip == UNIQUE_CHIP_ID, hex(uchip))

    chip = struct.unpack("<I", chosen_props.get("chip-id", b"\0\0\0\0")[:4])[0]
    check("13. chip-id is 0x8015", chip == CHIP_ID, hex(chip))

    memmap = find_child(chosen, "memory-map") if chosen else None
    check("14. memory-map node present (under chosen)", memmap is not None)

    cpus = find_child(root, "cpus") if root else None
    cpu_children = [c for c in cpus.children] if cpus else []
    exynos = [c for c in cpu_children if "exynos7885" in node_props(c).get("compatible", b"").decode("utf-8", "replace")]
    check("15. cpus node has 8 samsung,exynos7885 cores", len(exynos) == 8, f"cores={len(exynos)}")

    armio = find_child(root, "arm-io") if root else None
    gic = find_child(armio, "gic") if armio else None
    gic_compat = node_props(gic).get("compatible", b"").split(b"\0")[0].decode("utf-8", "replace") if gic else ""
    check("16. arm-io/gic node present with arm,cortex-a15-gic",
          gic_compat == "arm,cortex-a15-gic", gic_compat)

    vintid = struct.unpack("<I", node_props(gic).get("virtual-timer-intid", b"\0\0\0\0")[:4])[0] if gic else 0
    check("17. GIC virtual-timer-intid is 27", vintid == 27, str(vintid))

    syms = nm
    check("19. _m30_adt_dcache_op_range symbol linked (DC IVAC/CIVAC path)",
          re.search(r"\b_m30_adt_dcache_op_range\b", syms) is not None)
    check("20. _m30_adt_hex symbol linked (hex diagnostic path)",
          re.search(r"\b_m30_adt_hex\b", syms) is not None)

    # --- control flow of PE_init_platform ---
    dis = run([args.objdump, "-d", "--no-show-raw-insn", str(kernel)])
    pe_start = dis.find("<_PE_init_platform>:")
    m_end = re.search(r"\n[0-9a-f]+ <_", dis[pe_start + 30:])
    block = dis[pe_start: pe_start + 30 + m_end.start()] if m_end else dis[pe_start:]
    sec_dt = block.find("<_SecureDTInit>")
    guard = re.search(r"cmp\s+w\d+,\s+#0x40\s*\n", block)
    bail = re.search(r"b\.lo\s+0x", block)
    identify = block.find("<_pe_identify_machine>")
    ok = (sec_dt >= 0 and guard is not None and bail is not None
          and identify > sec_dt)
    check("21. PE_init_platform: SecureDTInit -> dt_size<0x40 guard -> pe_identify_machine",
          ok, f"SecureDTInit@{sec_dt} guard@{guard.start() if guard else 'n/a'} identify@{identify}")

    failed = 0
    for name, ok, detail in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")
        failed += 0 if ok else 1
    print(f"RESULT: {len(results) - failed}/{len(results)} PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
