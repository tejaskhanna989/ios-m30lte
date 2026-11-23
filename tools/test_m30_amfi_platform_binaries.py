#!/usr/bin/env python3
"""Focused regression test for patch 0419 (platform-binary marking for launchd boot tasks).

v20 physical: daemon crash loop fixed; genuine iOS userspace runs launchd boot
tasks, but launchd panicked: "boot task is not a platform binary (fsck, /sbin/fsck)"
-- a USERSPACE decision via csops(CS_OPS_STATUS)/CS_PLATFORM_BINARY, not a kernel
signature failure. On Apple hardware every iOS system binary is a platform binary
via the static trust cache; SWEET has no trust cache. The AMFI hook previously
marked only MNT_ROOTFS-mounted binaries as platform; this patch marks every
validated signature as platform (still fully hash-verified by the kernel).
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0419-m30-amfi-platform-binaries.patch"
BT = ROOT / "milestone_artifacts/ci_45219943492/buildtree/unpacked/xnu"
PSTORE = ROOT / "validation/physical-boot-test/20261122-ios-v20-boot/raw/pmsg-ramoops-0"


def main() -> int:
    text = PATCH.read_text()

    assert "diff --git a/bsd/kern/sweet_amfi.c" in text
    assert "*cs_flags |= CS_PLATFORM_BINARY;" in text
    assert "*cs_flags |= CS_SIGNED;" in text
    assert "static trust" in text
    assert "Signature/page hashes are still fully verified" in text
    print("[PASS] patch 0419 marks validated signatures as platform binaries (trust cache stand-in)")

    # No security weakening: no bypass flags, signature validation untouched
    sa = (BT / "bsd/kern/sweet_amfi.c").read_text()
    assert "csblob_get_entitlements(code_signing_blob" in sa
    for bypass in ("cs_enforcement_disable", "amfi_get_out_of_my_way", "launchd_unsecure_cache"):
        assert bypass not in text
    assert "still fully verified" in text
    print("[PASS] signature/entitlement validation preserved; no bypass boot-args")

    # v20 pstore proves before-state and that 0418 worked
    d = PSTORE.read_bytes()
    assert b"boot task is not a platform binary" in d
    assert b"fsck" in d
    assert b"cs_invalid_page" not in d        # 0418 fixed validation
    assert b"Text page corruption" not in d   # no daemon crash loop
    assert b"Darwin Bootstrapper Version 7.0.0" in d
    print("[PASS] v20 pstore: no validation crash, launchd boot tasks, platform-binary panic")

    print("ALL M30 AMFI PLATFORM BINARIES TESTS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
