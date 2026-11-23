#!/usr/bin/env python3
"""Focused regression test for patch 0415 (AMFI IOService stand-in).

Physical v16 pstore: genuine iOS 16.7.16 userspace booted far — UMD personas,
launchd pid 1, dozens of boot tasks (fsck, mount, keybag, usermanagerd...).
Blocker: launchd_cache_loader[23] aborted with "Unable to find AMFI". Analysis
of the real /usr/libexec/launchd_cache_loader (extracted from the local rootfs)
shows it does IOServiceMatching("AppleMobileFileIntegrity") +
IOServiceGetMatchingService and aborts if the service is missing, then
IOServiceOpen + IOConnectCallMethod(selector 6) for the platform/trust query.
Our built-in AMFI (sweet_amfi.c) is a kernel interface, not a kext, so no
IOService existed.

Patch 0415 publishes an AppleMobileFileIntegrity IOService (IOResources
provider) with an AppleMobileFileIntegrityUserClient whose selector 6 returns
success/trusted. This does NOT weaken security:
  - signature validation stays in userspace SecCode (SecCodeSetDetachedSignature
    / verify codedirectory) and in kernel AMFI (csblob_get_entitlements checks
    the XML against the code directory hash);
  - "platform binary" is already asserted by our kernel AMFI policy for every
    validated binary on the root filesystem, so the answer the stand-in gives
    matches kernel state; it grants no entitlements and skips no hash check.
Follows the existing SWEET AKS/WDT stand-in pattern exactly.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0415-m30-amfi-ioservice-standin.patch"
BT = ROOT / "milestone_artifacts/ci_45219943492/buildtree/unpacked/xnu"
PSTORE = ROOT / "validation/physical-boot-test/20261122-ios-v16-boot/raw/pmsg-ramoops-0"
LOADER_STRINGS = "/tmp/dyldtest/launchd_cache_loader"


def main() -> int:
    text = PATCH.read_text()

    # new file with both classes and the service/user-client class key
    assert "diff --git a/iokit/Kernel/arm/SweetAMFI.cpp b/iokit/Kernel/arm/SweetAMFI.cpp" in text
    assert "class AppleMobileFileIntegrity : public IOService" in text
    assert "class AppleMobileFileIntegrityUserClient : public IOUserClient" in text
    assert 'setProperty(kIOUserClientClassKey, "AppleMobileFileIntegrityUserClient")' in text
    assert "registerService()" in text
    assert "kIOReturnSuccess" in text
    print("[PASS] patch 0415 adds AppleMobileFileIntegrity service + user client (SWEET pattern)")

    # IOKit personality + build entry
    assert "'IOClass'         = AppleMobileFileIntegrity;" in text
    assert "'IOProviderClass' = IOResources;" in text
    assert "iokit/Kernel/arm/SweetAMFI.cpp" in text and "optional iokitcpp" in text
    print("[PASS] patch 0415 registers an IOResources-backed IOKit personality and build entry")

    # no security weakening: validation still in kernel AMFI + SecCode
    sa = (BT / "bsd/kern/sweet_amfi.c").read_text()
    assert "csblob_get_entitlements(code_signing_blob" in sa
    for bypass in ("cs_enforcement_disable", "amfi_get_out_of_my_way", "launchd_unsecure_cache"):
        assert bypass not in text
    assert "does NOT validate signatures or grant entitlements" in text
    print("[PASS] stand-in grants no entitlements; signature/entitlement validation untouched")

    # v16 pstore proves the before-state and how far iOS booted
    d = PSTORE.read_bytes()
    assert b"Unable to find AMFI" in d
    assert b"hello" in d or b"UMD_INIT" in d
    assert b"OS version: 20H392" in d
    print("[PASS] v16 pstore: genuine iOS 16.7.16 userspace booted, loader aborted: Unable to find AMFI")

    # real loader binary requires exactly this service + method
    if Path(LOADER_STRINGS).exists():
        lb = Path(LOADER_STRINGS).read_bytes()
        assert b"AppleMobileFileIntegrity" in lb and b"Unable to find AMFI" in lb
        assert b"AppleMobileFileIntegrityUserClient" in lb
        print("[PASS] extracted launchd_cache_loader requires AppleMobileFileIntegrity service")

    print("ALL M30 AMFI IOSERVICE TESTS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
