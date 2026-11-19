#!/usr/bin/env python3
"""Verify the single-CPU CPU-identity fallback in a built M30LTE kernel.

Source-level checks run against the exact build tree packaged by CI.  The
linked Mach-O is checked by SHA256, by the presence of ml_get_cpu_number_local
and by an MPIDR_EL1 read inside that function.  The original Device Tree
bounds assertion and the exact-ADT restore implementation are rechecked for
non-regression.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
from pathlib import Path

PATCH_SHA256 = "8eb85ef7332773cc7cbe0070e5a488c3b9db8dec2114c336b89cb18f276e7dd8"
DT_C_SHA256 = "d0bd1085f269fd5e6661836c59e7eb87fd2463deb5bb0ab400590c03ac7a0ca1"
# Baseline for the post-green-build (2026-11-19) candidate: the exact-ADT
# restore header was intentionally rebuilt to embed the corrected ADT whose
# device-tree `compatible` list leads with `samsung,m30lte` (SHA256
# 2dc36c056e62a563bc5b2262c296d8731e1d8ad9e804d388054c156cec7bd577).
# Verified byte-identical to the CI-packaged source at
# dxb/xnu/osfmk/arm64/sweet_early_adt_readback.h.
RESTORE_HEADER_SHA256 = "6a607854a8cec038dfe0f1273130fbc147939f9d5d012116d14a94102cc4dac5"
FALLBACK_LINES = (
    "lookup_id = ml_get_cpu_number((uint32_t)mpidr_el1_value);",
    "if (lookup_id == -1 && topology_info.num_cpus == 1 &&",
    "topology_info.boot_cpu != NULL)",
    "unsigned int boot_cpu_id = topology_info.boot_cpu->cpu_id;",
    "boot_cpu_id < topology_info.num_cpus",
    "boot_cpu_id == (unsigned int)ml_get_max_cpu_number()",
    "topology_info.boot_cpu == &topology_info.cpus[boot_cpu_id]",
    "return boot_cpu_id;",
)
ASSERT_LINE = "assert(cpu_id <= (unsigned int)ml_get_max_cpu_number());"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def function_block(disassembly: str, symbol: str) -> str:
    marker = f"<{symbol}>:"
    start = disassembly.find(marker)
    if start < 0:
        raise AssertionError(f"missing disassembly for {symbol}")
    end = disassembly.find("\n\n", start)
    return disassembly[start:] if end < 0 else disassembly[start:end]


def run(cmd: list[str]) -> str:
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", required=True, type=Path)
    ap.add_argument("--expected-sha256", required=True)
    ap.add_argument("--buildtree", required=True, type=Path)
    ap.add_argument("--patch", required=True, type=Path)
    ap.add_argument("--nm", default="llvm-nm")
    ap.add_argument("--objdump", default="llvm-objdump")
    args = ap.parse_args()

    checks: list[tuple[str, bool, str]] = []

    kernel = args.kernel.read_bytes()
    actual = sha(kernel)
    checks.append(("linked kernel SHA256", actual == args.expected_sha256.lower(), actual))

    patch = args.patch.read_bytes()
    checks.append(("focused patch SHA256", sha(patch) == PATCH_SHA256, sha(patch)))

    mr = (args.buildtree / "osfmk" / "arm64" / "machine_routines.c").read_text()
    for line in FALLBACK_LINES:
        checks.append((f"built source: {line}", line in mr,
                       "present" if line in mr else "MISSING"))
    checks.append(("original assertion preserved", mr.count(ASSERT_LINE) == 1,
                   f"count={mr.count(ASSERT_LINE)}"))
    checks.append(("no hardcoded MPIDR in built source",
                   "M30LTE_BOOT_MPIDR" not in mr,
                   "absent" if "M30LTE_BOOT_MPIDR" not in mr else "PRESENT"))

    dt = args.buildtree / "pexpert" / "gen" / "device_tree.c"
    dt_sha = sha(dt.read_bytes())
    checks.append(("Apple device_tree.c unchanged", dt_sha == DT_C_SHA256, dt_sha))

    header = args.buildtree / "osfmk" / "arm64" / "sweet_early_adt_readback.h"
    hdr_sha = sha(header.read_bytes())
    checks.append(("exact-ADT restore header unchanged",
                   hdr_sha == RESTORE_HEADER_SHA256, hdr_sha))

    symbols = run([args.nm, str(args.kernel)])
    has_symbol = re.search(r"\b_?ml_get_cpu_number_local\b", symbols) is not None
    checks.append(("ml_get_cpu_number_local symbol linked", has_symbol,
                   "present" if has_symbol else "MISSING"))

    if has_symbol:
        dis = run([args.objdump, "-d", "--no-show-raw-insn", str(args.kernel)])
        block = function_block(dis, "_ml_get_cpu_number_local")
        reads_mpidr = re.search(r"\bmrs\s+\w+,\s*mpidr_el1\b", block, re.I) is not None
        checks.append(("linked function reads MPIDR_EL1", reads_mpidr,
                       "present" if reads_mpidr else "MISSING"))
        has_branch = re.search(r"\b(b\.eq|b\.ne|cbz|cbnz|tbz|tbnz)\b", block) is not None
        checks.append(("linked function retains conditional fallback path", has_branch,
                       "present" if has_branch else "MISSING"))

    failed = 0
    for name, ok, detail in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")
        failed += 0 if ok else 1
    print(f"RESULT: {len(checks) - failed}/{len(checks)} PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
