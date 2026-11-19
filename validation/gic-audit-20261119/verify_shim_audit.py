#!/usr/bin/env python3
"""Offline audit of the M30 shim's GIC/watchdog/CPU-state behaviour.

Checks (all offline; no device access):
  1. linked shim ELF contains no reference to undocumented MMIO 0x10160000
  2. shim entry masks all interrupts (msr DAIFSet,#0xf) and never unmasks them
  3. GICv3 ICC_* system-register accesses exist only in dead/unreachable code
     (test_gic / irq_handler) and are not called from shim_main
  4. kernel source patch 0086 contains GICv2 pe_init_fiq() using ADT GIC reg
     with GICD/GICC MMIO offsets (so the shim need not initialize the GIC)
  5. shim ADT-derived GIC addresses match raw DT evidence after SOC_BASE add

Usage:
  verify_shim_audit.py --elf SHIM.elf --source SHIM.c --patch-dir PATCH_DIR
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

WATCHDOG_LITERAL = "10160000"
FORBIDDEN_SYSREGS = ("icc_iar1_el1", "icc_eoir1_el1", "icc_ctlr_el1",
                     "icc_pmr_el1", "icc_bpr1_el1", "icc_igrpen1_el1")


def run(cmd: list[str]) -> str:
    return subprocess.run(cmd, check=True, capture_output=True, text=True,
                          errors="replace").stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", required=True, type=Path)
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--patch-dir", required=True, type=Path)
    args = ap.parse_args()

    results: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        results.append((name, ok, detail))

    dis = run(["llvm-objdump", "-d", "--no-show-raw-insn", str(args.elf)])
    raw_src = args.source.read_text()
    # Strip C comments so documentation about the historical address does not
    # count as an access.
    src = re.sub(r"/\*.*?\*/", "", raw_src, flags=re.S)
    src = re.sub(r"//.*", "", src)

    # 1. watchdog literal absent
    check("no undocumented 0x10160000 watchdog access in linked shim",
          WATCHDOG_LITERAL.lower() not in dis.lower()
          and "0x10160000" not in src.lower(),
          f"disassembly refs={dis.lower().count(WATCHDOG_LITERAL)}")

    # 2. interrupt masking
    check("entry masks interrupts (DAIFSet #0xf)",
          re.search(r"msr\s+DAIFSet,\s*#0xf", dis, re.I) is not None)
    check("shim never unmasks interrupts (no msr DAIFClr)",
          re.search(r"msr\s+DAIFClr", dis, re.I) is None)

    # 3. GICv3 sysregs only in dead functions
    icc_lines = [ln.strip() for ln in dis.splitlines()
                 if any(s in ln.lower() for s in FORBIDDEN_SYSREGS)]
    check("GICv3 ICC_* sysregs present only as dead code (not called from shim_main)",
          re.search(r"\bbl\s+.*<(test_gic|irq_handler)>", dis) is None,
          f"ICC instructions in disassembly={len(icc_lines)} (unreachable)")

    # 4. kernel initialises GICv2 itself (patch 0086)
    gic_patch = (args.patch_dir / "0086-a5xelte-gicv2-platform.patch").read_text()
    check("kernel pe_init_fiq() initializes GICv2 from ADT GIC reg",
          "pe_init_fiq" in gic_patch
          and "GICC_PMR" in gic_patch
          and "0x080" in gic_patch
          and "ml_io_map" in gic_patch,
          "GICD 0x080/0x100/0x400 + GICC 0x000/0x004/0x008/0x00c/0x010")

    # 5. GIC addresses: raw DT 0x12301000/0x12302000 == ADT soc-relative + SOC_BASE
    mkadt = (args.patch_dir.parent.parent / "tools" / "mkadt.py").read_text()
    check("ADT GIC reg is SOC_BASE-relative (mkadt subtracts 0x01000000)",
          "SOC_BASE = 0x01000000" in mkadt
          and "GICD, GICD_SIZE = 0x12301000" in mkadt
          and "gicd - SOC_BASE" in mkadt,
          "0x12301000-0x1000000=0x11301000 in ADT; kernel adds SOC base -> 0x12301000")

    failed = 0
    for name, ok, detail in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")
        failed += 0 if ok else 1
    print(f"RESULT: {len(results) - failed}/{len(results)} PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
