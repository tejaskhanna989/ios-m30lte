#!/usr/bin/env python3
"""Regression test for patch 0424 (loader full-page hash validation).

v25 diagnostic: "SWEET LDVAL: launchd shift 12 need 0 big 0 vsize 3056 valid 1
tainted 0x1" - the CD hash lookup succeeds (valid=1) but the hash MISMATCHES
(tainted=0x1) because cs_validate_range was given cmds_size (3056) bytes while
the CD hash covers a full 4096-byte page. addr was allocated/read for
alloc_size=round_page(cmds_size)=4096, so a whole page IS present. The partial
hash clears CS_VALID -> process loses CS_SIGNED -> csproc_get_blob NULL ->
launchd boot-task platform check fails.

Patch 0424 passes MIN(PAGE_SIZE, alloc_size) to cs_validate_range for the normal
(non-16K-block) path so the full page is hashed and the genuine CD hash matches.
"""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0424-m30-loader-fullpage-hash.patch"
PSTORE = ROOT / "validation/physical-boot-test/20261122-ios-v25-boot/raw/pmsg-ramoops-0"

def main():
    t = PATCH.read_text()
    assert "vsize = MIN(PAGE_SIZE, alloc_size);" in t
    assert "alloc_size = round_page(cmds_size)" in t
    assert "mismatches the CD hash" in t
    print("[PASS] patch 0424 passes full page size to cs_validate_range")
    d = PSTORE.read_bytes()
    assert b"vsize 3056 valid 1 tainted 0x1" in d
    assert b"boot task is not a platform binary" in d
    print("[PASS] v25 pstore: partial hash (3056 of 4096) -> tainted -> CS_VALID clear -> panic")
    print("ALL M30 LOADER FULLPAGE HASH TESTS PASS")
if __name__ == "__main__":
    raise SystemExit(main())
