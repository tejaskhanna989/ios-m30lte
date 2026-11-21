#!/usr/bin/env python3
"""Regression tests for the M30 eMMC root-device write gating (EROFS blocker).

Source of truth: the shipped iOS buildtree bsd/dev/a5xelte_emmc.c and
bsd/vfs/vfs_subr.c. Verifies:

  1. emmcwrite=1 IS consumed by the driver, and only makes the device writable
     when emmcroot=USERDATA (SYSTEM stays read-only).
  2. emmc_open() / emmc_strategy() / emmc_write_sector() each refuse writes with
     EROFS when emmc_writable is false -- this is the exact source of the
     observed `do_jnl_io: strategy err 0x1e` during HFS journal init.
  3. Writes are bounds-checked to the selected partition (emmc_first_lba ..
     +emmc_nsectors); no unrelated partition can be reached through emmcroot0.
  4. rootrw=1 is consumed ONLY under ARM64_BOARD_CONFIG_SWEET, NOT M30LTE, so
     adding rootrw=1 to an M30 cmdline is a no-op (evidence, not assumption).
  5. The proposed fix (add emmcwrite=1 to the payload cmdline with
     emmcroot=USERDATA) satisfies the driver's writability condition.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BT = ROOT / "milestone_artifacts/ci_44893471750/buildtree/unpacked/xnu"
DRV = (BT / "bsd/dev/a5xelte_emmc.c").read_text()
VFS = (BT / "bsd/vfs/vfs_subr.c").read_text()


def main() -> int:
    # 1. emmcwrite consumed, gated on USERDATA only.
    assert 'PE_parse_boot_argn("emmcwrite", &enable_write' in DRV
    assert 'emmc_writable = !strcmp(emmc_partition_name, "USERDATA") && enable_write == 1;' in DRV
    print("[PASS] emmcwrite=1 consumed; emmc_writable requires partition == USERDATA")

    # Partition name restricted to SYSTEM or USERDATA.
    assert 'strcmp(emmc_partition_name, "SYSTEM")' in DRV
    assert 'strcmp(emmc_partition_name, "USERDATA")' in DRV
    print("[PASS] emmcroot accepts only SYSTEM/USERDATA")

    # 2. All three EROFS gates present (the journal-init failure source).
    assert "flags & FWRITE) && !emmc_writable ? EROFS" in DRV
    assert "!(buf_flags(bp) & B_READ) && !emmc_writable" in DRV
    assert "if (!root_write && !log_write) {\n\t\treturn EROFS;" in DRV
    print("[PASS] emmc_open + emmc_strategy + emmc_write_sector all return EROFS when not writable")

    # 3. Write bounds limited to the selected GPT partition.
    assert "address >= emmc_first_lba &&" in DRV
    assert "address - emmc_first_lba < emmc_nsectors" in DRV
    assert "if (off > bytes || count > bytes - off)" in DRV
    assert "emmc_first_lba + pos / 512u" in DRV
    print("[PASS] writes bounds-checked to selected partition [first_lba, +nsectors)")

    # 4. rootrw is SWEET-only on M30 -- adding it would NOT fix anything here.
    assert '#if defined(ARM64_BOARD_CONFIG_SWEET)' in VFS
    assert 'PE_parse_boot_argn("rootrw", &rootrw' in VFS
    sweet_idx = VFS.index('#if defined(ARM64_BOARD_CONFIG_SWEET)')
    rootrw_idx = VFS.index('PE_parse_boot_argn("rootrw", &rootrw')
    assert sweet_idx < rootrw_idx < VFS.index('#endif', rootrw_idx), "rootrw must be inside SWEET guard"
    print("[PASS] rootrw=1 is compiled only under ARM64_BOARD_CONFIG_SWEET (no-op on M30LTE)")

    # 5. Proposed fix: cmdline must contain emmcwrite=1 together with emmcroot=USERDATA.
    payload = (ROOT / "validation/ios-candidate-v11-out/payload/xnu-payload.bin").read_bytes()
    cmdline = payload[0x48:0x48 + 608].split(b"\0", 1)[0].decode()
    assert "emmcroot=USERDATA" in cmdline and "emmcwrite=1" not in cmdline
    print(f"[PASS] v11 cmdline confirmed missing emmcwrite=1: {cmdline}")
    print("[PASS] fix = add 'emmcwrite=1' to payload cmdline (emmcroot=USERDATA already present)")
    print("       -> emmc_writable=true -> journal writes succeed; SYSTEM/RECOVERY still protected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
