#!/usr/bin/env python3
"""Regression test for patch 0422 (loader initial-page 16K validation).

Physical v23 diagnostic: exec_mach_imgact showed result.csflags 0x26000002
(CS_SIGNED 0x20000000 | CS_PLATFORM_BINARY 0x04000000 | CS_DEBUGGED 0x02000000
| CS_ADHOC 0x2) but CS_VALID (0x1) CLEAR. mach_loader.c validates initial pages
with cs_validate_range(vp,...,MIN(PAGE_SIZE,cmds_size)) = 4K; a 16K code
directory needs 16K, so validation fails and clears CS_VALID (line 1334). Then
kern_exec.c only propagates CS_SIGNED when CS_VALID is set, so process csflags
stay 0 -> csproc_get_blob returns NULL -> launchd boot-task platform check fails.

Patch 0422: when the blob's hash page shift > PAGE_SHIFT, read the full hash
block from the vnode via vn_rdwr (already used in this file) and validate it,
so CS_VALID stays set and CS_SIGNED/CS_PLATFORM_BINARY propagate to the process.
Fail securely if the block cannot be read.
"""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0422-m30-loader-16k-initial-page.patch"
BT = ROOT / "milestone_artifacts/ci_45219943492/buildtree/unpacked/xnu"
PSTORE = ROOT / "validation/physical-boot-test/20261122-ios-v23-boot/raw/pmsg-ramoops-0"

def main():
    t = PATCH.read_text()
    assert "diff --git a/bsd/kern/mach_loader.c" in t
    assert "csb->csb_hash_pageshift > PAGE_SHIFT" in t
    assert "vn_rdwr(UIO_READ, vp, bigbuf" in t
    assert "cs_validate_range(vp, NULL, voff, vdata, vsize" in t
    assert "Fail securely if the block cannot be read" in t
    print("[PASS] patch 0422 reads full 16K block from vnode for loader validation")
    ml = (BT / "bsd/kern/mach_loader.c").read_text()
    assert "result->csflags &= ~CS_VALID;" in ml
    print("[PASS] CS_VALID clear path confirmed in loader")
    d = PSTORE.read_bytes()
    assert b"result.csflags 0x26000002" in d
    assert b"p.csflags 0x0 after update" in d
    assert b"boot task is not a platform binary" in d
    print("[PASS] v23 pstore: CS_VALID clear -> csflags 0 -> platform binary panic")
    print("ALL M30 LOADER 16K PAGE TESTS PASS")
if __name__ == "__main__":
    raise SystemExit(main())
