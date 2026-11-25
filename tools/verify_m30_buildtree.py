#!/usr/bin/env python3
"""Verify that an XNU buildtree contains the complete, effective M30LTE stack.

This verifier is intentionally independent of the XNU build result.  It checks
both source-level board wiring and patch provenance:

* every board-critical patch must reverse-apply cleanly to the completed tree;
* the effective M30LTE/A5XELTE headers must expose only the verified M30
  constants under the M30 preprocessor configuration;
* each M30 constant must reach its hardware consumer; and
* the inherited interrupt/timer path must remain the GICv2 path.

A successful kernel link is therefore not accepted as proof that a malformed
or skipped board patch was effective.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

CRITICAL_PATCHES = (
    "0096-m30lte-a5xelte-h-overrides.patch",
    "0400-m30lte-board-target.patch",
    "0402-m30lte-board-config-header.patch",
    "0403-m30lte-hardware-overrides.patch",
)

# v69 diagnostics overlay files that a critical patch also touches.  These are
# reverse-applied first when their marker is present, so the critical-patch
# round trip still proves the hardware/board changes survived unchanged.
OPTIONAL_OVERLAYS = (
    ("0446-m30-framebuffer-status-quiet.patch",
     "iokit/Kernel/arm/SweetFramebuffer.cpp", "fb->fDiagTick <= 4800"),
    ("0447-m30-key-input-diag.patch",
     "bsd/dev/a5xelte_keys.c", "m30_key_diag_count[key] < 4"),
    ("0448-m30-hid-event-diag.patch",
     "iokit/Kernel/arm/hid/SweetHID.cpp", "M30 HID: key usage=0x%x down=%d clients=%u"),
)


def fail(message: str) -> None:
    raise ValueError(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_text(tree: Path, relative: str) -> str:
    path = tree / relative
    require(path.is_file(), f"missing required buildtree file: {relative}")
    return path.read_text(encoding="utf-8", errors="strict")


def require_text(tree: Path, relative: str, pattern: str, description: str) -> re.Match[str]:
    text = read_text(tree, relative)
    match = re.search(pattern, text, re.MULTILINE)
    require(match is not None, f"{relative}: missing {description}")
    return match


def require_macro(text: str, name: str, expected: str) -> None:
    pattern = rf"^\s*#\s*define\s+{re.escape(name)}\s+{re.escape(expected)}\s*(?:/\*.*)?$"
    require(
        re.search(pattern, text, re.MULTILINE) is not None,
        f"missing or incorrect macro {name}={expected}",
    )


def reverse_patch_provenance(tree: Path, patch_dir: Path) -> list[dict[str, object]]:
    git = shutil.which("git")
    require(git is not None, "git is required for critical-patch provenance checks")
    patches: list[tuple[str, Path]] = []
    for name in CRITICAL_PATCHES:
        patch = patch_dir / name
        require(patch.is_file(), f"missing critical patch: {patch}")
        patches.append((name, patch))

    # Some critical patches intentionally touch the same file (0402 creates
    # M30LTE.h and 0403 extends it).  Reverse them in stack order on a
    # disposable copy, rather than checking each patch against the final
    # bytes independently.  A malformed, skipped, or partially applied patch
    # cannot complete this round trip.
    with tempfile.TemporaryDirectory(prefix="m30-buildtree-verify-", dir=tree.parent) as temp_name:
        temp_tree = Path(temp_name)
        shutil.copytree(tree, temp_tree, dirs_exist_ok=True, symlinks=True)

        top = subprocess.run(
            [git, "-C", str(temp_tree), "rev-parse", "--show-toplevel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
        if top.returncode == 0:
            repository = Path(top.stdout.strip()).resolve()
            prefix = os.path.relpath(temp_tree, repository)
            apply_root = repository
            directory = [] if prefix == "." else [f"--directory={prefix}"]
        else:
            apply_root = temp_tree
            directory = []

        # Peel diagnostic overlays off first.  Earlier candidates do not ship
        # these patches, so an absent patch or marker is not a failure; a
        # present marker with a failed reverse apply is a failure.
        for name, relative, marker in reversed(OPTIONAL_OVERLAYS):
            overlay = patch_dir / name
            if not overlay.is_file():
                continue
            marked = temp_tree / relative
            if not marked.is_file() or marker not in marked.read_text(
                encoding="utf-8", errors="ignore"
            ):
                continue
            completed = subprocess.run(
                [
                    git,
                    "-C",
                    str(apply_root),
                    "apply",
                    "--reverse",
                    *directory,
                    str(overlay),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
            require(
                completed.returncode == 0 and "Skipped patch" not in completed.stdout,
                f"diagnostic overlay was not applied cleanly: {name}\n"
                f"{completed.stdout.strip()}",
            )

        results: list[dict[str, object]] = []
        for name, patch in reversed(patches):
            completed = subprocess.run(
                [
                    git,
                    "-C",
                    str(apply_root),
                    "apply",
                    "--reverse",
                    *directory,
                    str(patch),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
            require(
                completed.returncode == 0 and "Skipped patch" not in completed.stdout,
                f"critical patch was not applied to the effective buildtree: {name}\n"
                f"{completed.stdout.strip()}",
            )
            results.append({"name": name, "reverse_apply": "PASS"})
        return list(reversed(results))


def effective_macro_check(tree: Path, clang: str) -> dict[str, str]:
    command = [
        clang,
        "-E",
        "-dM",
        "-x",
        "c",
        f"-I{tree}",
        "-DARM64_BOARD_CONFIG_M30LTE",
        "-DARM64_BOARD_CONFIG_A5XELTE",
        "-include",
        "pexpert/pexpert/arm64/M30LTE.h",
        "-include",
        "pexpert/pexpert/arm64/A5XELTE.h",
        os.devnull,
    ]
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    require(
        completed.returncode == 0,
        "failed to preprocess the effective M30LTE/A5XELTE headers:\n" + completed.stderr,
    )
    require(
        "macro redefined" not in completed.stderr,
        "effective M30 headers contain conflicting macro definitions:\n" + completed.stderr,
    )

    macros: dict[str, str] = {}
    for line in completed.stdout.splitlines():
        match = re.match(r"^#define\s+(\S+)(?:\s+(.*))?$", line)
        if match:
            macros[match.group(1)] = (match.group(2) or "").strip()

    expected = {
        "M30LTE": "1",
        "A5XELTE": "1",
        "SWEET": "1",
        "HAS_GIC_V3": "0",
        "A5XELTE_VTIMER_INTID": "M30LTE_VTIMER_INTID",
        "M30LTE_VTIMER_INTID": "27",
        "M30LTE_FB_PA": "0xec000000",
        "M30LTE_FB_WIDTH": "1080",
        "M30LTE_FB_HEIGHT": "2340",
        "M30LTE_FB_STRIDE": "4320",
        "M30LTE_FB_STRIDE_PIXELS": "1080",
        "M30LTE_FB_BLOCKS": "5",
        "M30LTE_FB_DOT_PITCH": "409",
        "M30LTE_MARKER_PA": "0x93fff100",
        "M30LTE_BOOT_MPIDR": "0x100",
        "M30LTE_EMMC_PA": "0x13500000",
        "M30LTE_EMMC_NODE_NAME": '"m30lte-emmc"',
        "M30LTE_FBCON_NODE_NAME": '"m30lte-fbcon"',
        "M30LTE_ALIVE_PA": "0x11cb0000",
        "M30LTE_GPA1_CON": "0x60",
        "M30LTE_GPA1_DAT": "0x64",
        "M30LTE_GPA1_PUD": "0x68",
        "M30LTE_KEY_POWER_PIN": "7",
        "M30LTE_KEY_VOLUP_PIN": "5",
        "M30LTE_KEY_VOLDOWN_PIN": "6",
        "A5XELTE_FB_PA": "0xec000000",
        "A5XELTE_FB_WIDTH": "1080",
        "A5XELTE_FB_HEIGHT": "2340",
        "A5XELTE_FB_STRIDE": "4320",
        "A5XELTE_FB_BLOCKS": "5",
        "A5XELTE_MARKER_PA": "0x93fff100",
        "A5XELTE_EMMC_PA": "0x13500000",
    }
    for name, value in expected.items():
        require(
            macros.get(name) == value,
            f"effective M30 macro {name} is {macros.get(name)!r}, expected {value!r}",
        )
    return {name: macros[name] for name in expected}


def verify_source(tree: Path) -> list[str]:
    checks: list[str] = []

    # 0400: M30LTE must be a first-class ARM64 machine target.
    makeinc = read_text(tree, "makedefs/MakeInc.def")
    require(
        re.search(
            r"^SUPPORTED_ARM64_MACHINE_CONFIGS\s*=.*\bM30LTE\b",
            makeinc,
            re.MULTILINE,
        )
        is not None,
        "MakeInc.def does not register M30LTE as a supported ARM64 target",
    )
    flags = require_text(
        tree,
        "makedefs/MakeInc.def",
        r"^MACHINE_FLAGS_ARM64_M30LTE\s*=\s*(?P<flags>[^\n]+)$",
        "M30LTE machine flags",
    ).group("flags")
    for flag in (
        "-DARM64_BOARD_CONFIG_A5XELTE",
        "-DARM64_BOARD_CONFIG_M30LTE",
        "-mcpu=cortex-a53",
        "-march=armv8-a+crypto",
    ):
        require(flag in flags, f"M30LTE machine flags omit {flag}")
    require(
        re.search(
            r"filter\s+\$\(CURRENT_MACHINE_CONFIG\),\s*A5XELTE\s+M30LTE",
            makeinc,
        )
        is not None,
        "M30LTE is not included in the compact ARM64 kernel-VA configuration",
    )
    master = read_text(tree, "config/MASTER.arm64.m30lte")
    require(re.search(r'^machine\s+"arm64"', master, re.MULTILINE) is not None,
            "M30LTE MASTER file does not select arm64")
    checks.append("0400 M30LTE machine target and MASTER overlay")

    # 0402 and 0403: the board header must contain every verified constant.
    header = read_text(tree, "pexpert/pexpert/arm64/M30LTE.h")
    for name, value in {
        "M30LTE_FB_PA": "0xec000000",
        "M30LTE_FB_WIDTH": "1080",
        "M30LTE_FB_HEIGHT": "2340",
        "M30LTE_FB_STRIDE": "4320",
        "M30LTE_FB_STRIDE_PIXELS": "1080",
        "M30LTE_FB_BLOCKS": "5",
        "M30LTE_FB_DOT_PITCH": "409",
        "M30LTE_MARKER_PA": "0x93fff100",
        "M30LTE_BOOT_MPIDR": "0x100",
        "M30LTE_EMMC_PA": "0x13500000",
        "M30LTE_EMMC_NODE_NAME": '"m30lte-emmc"',
        "M30LTE_FBCON_NODE_NAME": '"m30lte-fbcon"',
        "M30LTE_ALIVE_PA": "0x11cb0000",
        "M30LTE_GPA1_CON": "0x60",
        "M30LTE_GPA1_DAT": "0x64",
        "M30LTE_GPA1_PUD": "0x68",
        "M30LTE_KEY_POWER_PIN": "7",
        "M30LTE_KEY_VOLUP_PIN": "5",
        "M30LTE_KEY_VOLDOWN_PIN": "6",
        "HAS_GIC_V3": "0",
        "M30LTE_VTIMER_INTID": "27",
    }.items():
        require_macro(header, name, value)
    board = read_text(tree, "pexpert/pexpert/arm64/board_config.h")
    m30_include = board.find("#include <pexpert/arm64/M30LTE.h>")
    a5_include = board.find("#include <pexpert/arm64/A5XELTE.h>")
    require(m30_include >= 0, "board_config.h does not include M30LTE.h")
    require(a5_include > m30_include, "board_config.h must include M30LTE.h before A5XELTE.h")
    arm_makefile = read_text(tree, "pexpert/pexpert/arm64/Makefile")
    require(re.search(r"^\s*M30LTE\.h\s*\\?$", arm_makefile, re.MULTILINE) is not None,
            "pexpert arm64 Makefile does not install M30LTE.h")
    checks.append("0402/0403 effective M30LTE board header and board_config wiring")

    # 0096: the legacy A5XELTE compatibility header must explicitly select M30.
    a5_header = read_text(tree, "pexpert/pexpert/arm64/A5XELTE.h")
    m30_branch = re.search(
        r"#if\s+defined\(ARM64_BOARD_CONFIG_M30LTE\)(?P<body>.*?)#else",
        a5_header,
        re.DOTALL,
    )
    require(m30_branch is not None, "A5XELTE.h has no explicit M30LTE branch")
    for name, value in {
        "A5XELTE_FB_PA": "0xec000000",
        "A5XELTE_FB_WIDTH": "1080",
        "A5XELTE_FB_HEIGHT": "2340",
        "A5XELTE_FB_STRIDE": "4320",
        "A5XELTE_FB_BLOCKS": "5",
        "A5XELTE_MARKER_PA": "0x93fff100",
        "A5XELTE_BOOT_MPIDR": "0x100",
        "A5XELTE_EMMC_PA": "0x13500000",
    }.items():
        require_macro(m30_branch.group("body"), name, value)
    checks.append("0096 effective M30 branch in A5XELTE.h")

    # 0403: every verified constant must reach its board consumer.
    start = read_text(tree, "osfmk/arm64/start.s")
    for name, value in {
        "A5_BOOT_FB_BASE": "M30LTE_FB_PA",
        "A5_BOOT_MARKER_PA": "M30LTE_MARKER_PA",
        "A5_BOOT_SCANOUT_ENTRY_PA": "M30LTE_FB_SCANOUT_ENTRY_PA",
        "A5_BOOT_SCANOUT_MMU_PA": "M30LTE_FB_SCANOUT_MMU_PA",
        "A5_BOOT_SCANOUT_FP_PA": "M30LTE_FB_SCANOUT_FP_PA",
        "A5_BOOT_SCANOUT_TUN_PA": "M30LTE_FB_SCANOUT_TUN_PA",
        "A5_BOOT_SCANOUT_ARM_PA": "M30LTE_FB_SCANOUT_ARM_PA",
    }.items():
        require_macro(start, name, value)
    for consumer in (
        "MOV64\tx10, A5_BOOT_MARKER_PA",
        "MOV64\tx10, A5_BOOT_SCANOUT_ENTRY_PA",
        "MOV64\tx0, A5_BOOT_FB_BASE",
        "MOV64\tx10, A5_BOOT_SCANOUT_MMU_PA",
        "MOV64\tx10, A5_BOOT_SCANOUT_FP_PA",
        "MOV64\tx10, A5_BOOT_SCANOUT_TUN_PA",
        "MOV64\tx10, A5_BOOT_SCANOUT_ARM_PA",
    ):
        require(consumer in start, f"start.s does not consume {consumer}")
    require(
        "MOV64\tx10, 0x6705d0c0" not in start
        and "MOV64\tx10, 0x469ff100" not in start,
        "start.s still contains donor checkpoint physical addresses",
    )
    checks.append("0403 M30 marker and relocated framebuffer checkpoint consumers")

    early = read_text(tree, "osfmk/arm64/sweet_early.c")
    require(
        "#if defined(M30LTE)" in early
        and "#define A5_FB ((volatile uint32_t *)(uintptr_t)M30LTE_FB_PA)" in early
        and "#define A5_STRIDE M30LTE_FB_STRIDE_PIXELS" in early
        and "#define A5_HEIGHT M30LTE_FB_HEIGHT" in early,
        "sweet_early.c does not select the M30 framebuffer geometry",
    )
    fb = read_text(tree, "iokit/Kernel/arm/SweetFramebuffer.cpp")
    require(
        "#if defined(ARM64_BOARD_CONFIG_M30LTE)" in fb
        and "fPhys = M30LTE_FB_PA;" in fb
        and "fWidth = M30LTE_FB_WIDTH;" in fb
        and "fHeight = M30LTE_FB_HEIGHT;" in fb
        and "fRowBytes = M30LTE_FB_STRIDE;" in fb
        and "#define SWEET_FB_DOT_PITCH              M30LTE_FB_DOT_PITCH" in fb,
        "SweetFramebuffer.cpp does not use the M30 display constants",
    )

    keys = read_text(tree, "bsd/dev/a5xelte_keys.c")
    require(
        "#define A5_ALIVE_PA M30LTE_ALIVE_PA" in keys
        and "#define A5_GPIO_CON M30LTE_GPA1_CON" in keys
        and "#define A5_GPIO_DAT M30LTE_GPA1_DAT" in keys
        and "#define A5_GPIO_PUD M30LTE_GPA1_PUD" in keys
        and "#define A5_KEY_COUNT 3" in keys
        and "M30LTE_KEY_POWER_PIN, M30LTE_KEY_VOLUP_PIN, M30LTE_KEY_VOLDOWN_PIN" in keys
        and "A5_GPA2" not in keys,
        "a5xelte_keys.c does not use the M30 ALIVE/GPA1 mapping",
    )

    # The donor touch controller is an Exynos7580-only probe.  M30LTE must
    # exclude its implementation as well as its call site; otherwise donor
    # MMIO addresses are still compiled into the exact M30 kernel.
    touch = read_text(tree, "bsd/dev/a5xelte_touch.c")
    require(
        "#if defined(ARM64_BOARD_CONFIG_A5XELTE) && "
        "!defined(ARM64_BOARD_CONFIG_M30LTE)" in touch,
        "a5xelte_touch.c does not exclude the donor touch implementation for M30LTE",
    )
    init = read_text(tree, "iokit/bsddev/IOKitBSDInit.cpp")
    require(
        "#if !defined(ARM64_BOARD_CONFIG_M30LTE)" in init
        and "a5xelte_touch_probe();" in init,
        "IOKitBSDInit.cpp does not exclude the donor touch call for M30LTE",
    )

    emmc = read_text(tree, "bsd/dev/a5xelte_emmc.c")
    require(
        "#define A5_EMMC_DT_PATH M30LTE_EMMC_NODE_NAME" in emmc
        and "#define A5_EMMC_PA M30LTE_EMMC_PA" in emmc
        and "SecureDTLookupEntry(NULL, A5_EMMC_DT_PATH, &node)" in emmc
        and "reg[0] != A5_EMMC_PA" in emmc,
        "a5xelte_emmc.c does not consume the M30 eMMC node and base",
    )

    serial = read_text(tree, "pexpert/arm/pe_serial.c")
    require(
        "#if defined(ARM64_BOARD_CONFIG_M30LTE)" in serial
        and 'SecureDTFindEntry("name", M30LTE_FBCON_NODE_NAME, &entry)' in serial,
        "pe_serial.c does not consume the M30 framebuffer-console node",
    )
    checks.append("0403 framebuffer, key, eMMC, and fbcon hardware consumers")

    # The inherited interrupt path must be physical GICv2, not GICv3 system registers.
    fiq = read_text(tree, "pexpert/arm/pe_fiq.c")
    a5_fiq = re.search(
        r"#if\s+defined\(A5XELTE\)(?P<body>.*?)#else\s*\nvoid\s*\npe_init_fiq",
        fiq,
        re.DOTALL,
    )
    require(a5_fiq is not None, "pe_fiq.c has no A5XELTE GICv2 implementation")
    a5_fiq_body = a5_fiq.group("body")
    for token in (
        '"/arm-io/gic"',
        "0x080",  # GICD_IGROUPR0
        "0x100",  # GICD_ISENABLER0
        "0x004",  # GICC_PMR
        "0x008",  # GICC_BPR
        "0x000",  # GICC_CTLR
    ):
        require(token in a5_fiq_body, f"A5XELTE GICv2 source path lacks {token}")
    for forbidden in ("ICC_IGRPEN1_EL1", "ICC_PMR_EL1", "ICC_BPR1_EL1"):
        require(forbidden not in a5_fiq_body, f"GICv3-only register remains in the A5XELTE GIC path: {forbidden}")
    sleh = read_text(tree, "osfmk/arm64/sleh.c")
    require(
        "a5xelte_irq_ack()" in sleh
        and "a5xelte_irq_eoi" in sleh
        and "A5XELTE_VTIMER_INTID" in sleh,
        "A5XELTE interrupt path is not wired to the GICv2 ack/EOI implementation",
    )
    machine = read_text(tree, "osfmk/arm64/machine_routines.c")
    require(
        "CNTV_CTL_EL0_ENABLE" in machine
        and "CNTP_CTL_EL0_IMASKED" in machine
        and "CNTV_TVAL_EL0" in machine,
        "XNU timer ownership path is missing virtual-timer enable/deadline writes",
    )
    checks.append("inherited GICv2 interrupt path and XNU virtual-timer ownership")

    # machineType is only a local tag; XNU 8796.141.3 must not consume it.
    consumers: list[str] = []
    suffixes = {".c", ".h", ".cpp", ".s", ".S"}
    for path in tree.rglob("*"):
        if not path.is_file() or path.suffix not in suffixes:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"(?:->|\.)machineType\b", text):
            consumers.append(str(path.relative_to(tree)))
    require(not consumers, "XNU source unexpectedly consumes boot_args.machineType: " + ", ".join(consumers))
    checks.append("no XNU boot_args.machineType consumer")

    return checks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tree", required=True, type=Path, help="effective xnu source tree")
    parser.add_argument("--patch-dir", required=True, type=Path, help="directory containing the applied patches")
    parser.add_argument("--clang", default=shutil.which("clang") or "clang")
    args = parser.parse_args()

    tree = args.tree.resolve(strict=True)
    patch_dir = args.patch_dir.resolve(strict=True)
    try:
        provenance = reverse_patch_provenance(tree, patch_dir)
        checks = verify_source(tree)
        macros = effective_macro_check(tree, args.clang)
    except (OSError, UnicodeError, subprocess.SubprocessError, ValueError) as exc:
        print(json.dumps({"result": "FAIL", "error": str(exc)}, indent=2), file=sys.stderr)
        raise SystemExit(1) from exc

    print(
        json.dumps(
            {
                "result": "PASS",
                "tree": str(tree),
                "critical_patch_provenance": provenance,
                "source_checks": checks,
                "effective_m30_macros": macros,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
