#!/usr/bin/env python3
"""Verify the exact linked M30 XNU kernel's board-critical machine code.

This is intentionally a binary check rather than another source check.  It
proves that the linked artifact contains the M30 hardware constants and
GICv2/timer control flow, and that donor-only hardware constants and the
Exynos7580 touch implementation are absent from the compiled kernel.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys


class VerificationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def command(value: str) -> list[str]:
    parts = shlex.split(value)
    require(bool(parts), "empty tool command")
    return parts


def run_tool(argv: list[str]) -> str:
    completed = subprocess.run(
        argv,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    require(
        completed.returncode == 0,
        f"command failed ({completed.returncode}): {' '.join(argv)}\n{completed.stdout}",
    )
    return completed.stdout


def function_block(disassembly: str, symbol: str) -> str:
    marker = f"<{symbol}>:"
    lines = disassembly.splitlines()
    for index, line in enumerate(lines):
        if marker in line:
            block = [line]
            for following in lines[index + 1 :]:
                if not following.strip():
                    break
                block.append(following)
            return "\n".join(block)
    raise VerificationError(f"required kernel symbol is absent: {symbol}")


def require_pattern(text: str, pattern: str, description: str) -> None:
    require(
        re.search(pattern, text, re.MULTILINE) is not None,
        f"missing {description}",
    )


def forbid_text(text: str, needle: str, description: str) -> None:
    require(needle not in text, f"forbidden {description} is present: {needle}")


def verify(
    kernel: Path,
    objdump_arg: str,
    nm_arg: str,
    expected_sha256: str | None,
) -> dict[str, object]:
    kernel_hash = sha256(kernel)
    if expected_sha256:
        require(
            kernel_hash == expected_sha256,
            f"kernel SHA256 mismatch: {kernel_hash} != {expected_sha256}",
        )

    disassembly = run_tool(command(objdump_arg) + ["-d", "--no-show-raw-insn", str(kernel)])
    symbols = run_tool(command(nm_arg) + ["-n", str(kernel)])
    checks: list[str] = []

    start = function_block(disassembly, "_start_first_cpu")
    common = function_block(disassembly, "common_start")
    trampoline = function_block(disassembly, "arm_init_tramp")
    early = function_block(disassembly, "_sweet_early_putc")
    emmc = function_block(disassembly, "_emmc_map_host")
    keys = function_block(disassembly, "_a5xelte_keys_init")
    pe_fiq = function_block(disassembly, "_pe_init_fiq")
    irq_ack = function_block(disassembly, "_a5xelte_irq_ack")
    irq_eoi = function_block(disassembly, "_a5xelte_irq_eoi")
    self_ipi = function_block(disassembly, "_a5xelte_send_self_ipi")
    decrementer = function_block(disassembly, "_ml_set_decrementer")
    fiq_context = function_block(disassembly, "_fiq_context_init")

    # Framebuffer: the linked early console and bootstrap mapping must use
    # 0xec000000, not the donor's 0x67000000.
    require_pattern(early, r"mov\s+w9,\s+#-0x14000000", "M30 framebuffer base in sweet_early_putc")
    require_pattern(start, r"movk\s+x0,\s+#0xec00,\s+lsl\s+#16", "M30 framebuffer base in start_first_cpu")
    require_pattern(trampoline, r"movk\s+x4,\s+#0xec00,\s+lsl\s+#16", "M30 framebuffer base in arm_init_tramp")
    forbid_text(disassembly, "0x67000000", "donor framebuffer base")
    checks.append("linked M30 framebuffer base 0xec000000")

    # Marker and the five relocated donor checkpoint offsets.
    require_pattern(start, r"movk\s+x10,\s+#0x93ff,\s+lsl\s+#16", "M30 marker high half")
    require_pattern(start, r"movk\s+x10,\s+#0xf100", "M30 marker low half")
    for location, high, low, description in (
        (start, r"movk\s+x10,\s+#0xec05,\s+lsl\s+#16", r"movk\s+x10,\s+#0xd0c0", "entry checkpoint"),
        (common, r"movk\s+x10,\s+#0xec07,\s+lsl\s+#16", r"movk\s+x10,\s+#0xecc0", "MMU checkpoint"),
        (common, r"movk\s+x10,\s+#0xec0a,\s+lsl\s+#16", r"movk\s+x10,\s+#0x8c0", "FP checkpoint"),
        (common, r"movk\s+x10,\s+#0xec0c,\s+lsl\s+#16", r"movk\s+x10,\s+#0x24c0", "tunables checkpoint"),
        (common, r"movk\s+x10,\s+#0xec0e,\s+lsl\s+#16", r"movk\s+x10,\s+#0x40c0", "arm-init checkpoint"),
    ):
        require_pattern(location, high, f"M30 {description} high half")
        require_pattern(location, low, f"M30 {description} low half")
    forbid_text(disassembly, "0x469ff100", "donor early marker")
    forbid_text(disassembly, "0x8ffff100", "historical donor early marker")
    for fragment in ("#0x469f, lsl #16", "#0x8fff, lsl #16"):
        forbid_text(start, fragment, "donor marker immediate sequence")
    for fragment in ("#0x6705,", "#0x6707,", "#0x670a,", "#0x670c,", "#0x670e,"):
        forbid_text(start + "\n" + common, fragment, "donor checkpoint immediate sequence")
    checks.append("linked M30 marker and relocated framebuffer checkpoints")

    # eMMC and ALIVE/GPA1 hardware consumers.
    require_pattern(emmc, r"mov\s+w10,\s+#0x13500000", "M30 eMMC base")
    require_pattern(emmc, r"mov\s+w0,\s+#0x13500000", "M30 eMMC mapping base")
    forbid_text(disassembly, "0x13540000", "donor eMMC base")
    require_pattern(keys, r"mov\s+w0,\s+#0x11cb0000", "M30 ALIVE base")
    # v69's bounded key diagnostics legitimately change compiler register
    # allocation.  Check the verified offsets regardless of which general
    # registers clang chooses, while still requiring them inside the linked
    # a5xelte_keys_init block.
    require_pattern(keys, r"ldr\s+w[0-9]+,\s+\[x[0-9]+,\s+#0x60\]", "M30 GPA1 CON offset")
    require_pattern(keys, r"ldr\s+w[0-9]+,\s+\[x[0-9]+,\s+#0x64\]", "M30 GPA1 DAT offset")
    require_pattern(keys, r"ldr\s+w[0-9]+,\s+\[x[0-9]+,\s+#0x68\]", "M30 GPA1 PUD offset")
    forbid_text(disassembly, "0x139b0000", "donor ALIVE base")
    checks.append("linked M30 eMMC and ALIVE/GPA1 constants")

    # The donor Exynos7580 touch implementation must not merely be uncalled;
    # it must not be compiled into the M30 kernel.
    require("_a5xelte_touch_probe" not in symbols, "donor touch probe symbol is compiled")
    for address in (
        "0x138c0000",
        "0x104e0000",
        "0x139f0000",
        "0x10430000",
        "0x13850000",
        "0x104c0000",
    ):
        forbid_text(disassembly, address, "donor touch MMIO base")
    checks.append("donor Exynos7580 touch implementation absent")

    # GICv2 MMIO control: IGROUPR0, ISENABLER0, priority registers, GICC
    # PMR/BPR/CTLR, and the memory-mapped acknowledge/EOI interface.
    require_pattern(pe_fiq, r"ldr\s+w10,\s+\[x9,\s+#0x80\]", "GICD_IGROUPR0 read")
    require_pattern(pe_fiq, r"str\s+w10,\s+\[x9,\s+#0x80\]", "GICD_IGROUPR0 write")
    require_pattern(pe_fiq, r"str\s+w11,\s+\[x9,\s+#0x100\]", "GICD_ISENABLER0 write")
    require_pattern(pe_fiq, r"str\s+w10,\s+\[x9,\s+#0x400\]", "GICD_IPRIORITYR0 write")
    require_pattern(pe_fiq, r"str\s+w10,\s+\[x9,\s+#0x4\]", "GICC_PMR write")
    require_pattern(pe_fiq, r"str\s+wzr,\s+\[x9,\s+#0x8\]", "GICC_BPR write")
    require_pattern(irq_ack, r"ldr\s+w0,\s+\[x8,\s+#0xc\]", "GICC_IAR read")
    require_pattern(irq_eoi, r"str\s+w0,\s+\[x8,\s+#0x10\]", "GICC_EOIR write")
    require_pattern(self_ipi, r"str\s+w9,\s+\[x8,\s+#0xf00\]", "GICD_SOFTINT write")
    for register in ("ICC_IGRPEN1_EL1", "ICC_PMR_EL1", "ICC_BPR1_EL1"):
        forbid_text(disassembly, register, "GICv3-only system register")
    checks.append("linked GICv2 MMIO initialization and acknowledge/EOI path")

    # XNU owns the virtual timer: it enables CNTV_CTL_EL0, masks CNTP_CTL_EL0,
    # and programs CNTV_TVAL_EL0 deadlines.
    require_pattern(fiq_context, r"mov\s+w8,\s+#0x1", "CNTV_CTL_EL0 enable value")
    require_pattern(fiq_context, r"msr\s+CNTV_CTL_EL0", "CNTV_CTL_EL0 write")
    require_pattern(fiq_context, r"mov\s+w9,\s+#0x2", "CNTP_CTL_EL0 masked value")
    require_pattern(fiq_context, r"msr\s+CNTP_CTL_EL0", "CNTP_CTL_EL0 write")
    require_pattern(decrementer, r"msr\s+CNTV_TVAL_EL0", "CNTV_TVAL_EL0 deadline write")
    forbid_text(disassembly, "msr\tCNTP_TVAL_EL0", "physical-timer deadline write")
    checks.append("linked XNU virtual-timer ownership")

    return {
        "result": "PASS",
        "kernel": str(kernel),
        "kernel_size_bytes": kernel.stat().st_size,
        "kernel_sha256": kernel_hash,
        "checks": checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel", required=True, type=Path)
    parser.add_argument("--objdump", default=shutil.which("llvm-objdump") or "llvm-objdump")
    parser.add_argument("--nm", default=shutil.which("llvm-nm") or "llvm-nm")
    parser.add_argument("--expected-sha256")
    args = parser.parse_args()

    try:
        kernel = args.kernel.resolve(strict=True)
        result = verify(kernel, args.objdump, args.nm, args.expected_sha256)
    except (OSError, subprocess.SubprocessError, VerificationError) as exc:
        print(json.dumps({"result": "FAIL", "error": str(exc)}, indent=2), file=sys.stderr)
        raise SystemExit(1) from exc

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
