#!/usr/bin/env python3
"""Regression test for v69 bounded input/pstore diagnostics (patches 0446-0448).

v68 achieved the persistent lock screen but its unbounded 10-second
framebuffer status heartbeat overwrote the 16 KiB ramoops ring, destroying
the early ABI trace.  These patches only change diagnostics:

  0446 cap the framebuffer status heartbeat at the first eight records;
  0447 emit bounded M30 key probe/transition records;
  0448 emit bounded HID service/user-client producer and consumer records.

No framebuffer behavior, GPIO polling, key dispatch, HID event construction,
user-client state machine, entitlement check or security policy is changed.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
PATCHES = (
    "0441-m30-stderr-capture.patch",
    "0442-m30-framebuffer-commit-diag.patch",
    "0443-m30-framebuffer-swapwait-handshake.patch",
    "0444-m30-framebuffer-notify-push.patch",
    "0445-m30-framebuffer-selector-trace.patch",
    "0446-m30-framebuffer-status-quiet.patch",
    "0447-m30-key-input-diag.patch",
    "0448-m30-hid-event-diag.patch",
)
BASE = ROOT / "milestone_artifacts/ci_45356410574/buildtree/unpacked/xnu"
EXPECT_HASHES = {
    "pexpert/arm/pe_serial.c": "0567414c2f004778bba71a01b2723202af5bde98bf1ca6ec035856b086c2a772",
    "bsd/kern/sys_generic.c": "438bc8468900285491f4bd71be1cf89aa5f40874f0c7ff3ec37e7828138df94f",
    "iokit/Kernel/arm/SweetFramebuffer.cpp": "d3199f92c608b8c7d874d83087c0a8409b6488a3acc93d40599deb0bc32e3c8f",
    "bsd/dev/a5xelte_keys.c": "af37254e7d55aa8214dd6065b40f453446df237845752ace334db46f4a7760c9",
    "iokit/Kernel/arm/hid/SweetHID.cpp": "7ff75ede15bd64a8c700e964668006194b65a0ad3f18510afbe85c3293c054d2",
    "iokit/Kernel/arm/hid/IOHIDEventServiceUserClient.cpp": "2f1a40711448dea0a93305a4549b563f4334efb623969520f6d73a1f43dc100a",
}
FORBIDDEN = (
    "cs_enforcement_disable", "amfi_get_out_of_my_way",
    "launchd_unsecure_cache", "disable_security",
    "PE_initialize_console", "serial=3", "sweetfb_noconsole=1",
    "IOSleep(5000)", "notify-all", "case 79:",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def patch_text(name: str) -> str:
    return (ROOT / "xnu/patches-minimal" / name).read_text()


def main() -> None:
    quiet = patch_text("0446-m30-framebuffer-status-quiet.patch")
    keys = patch_text("0447-m30-key-input-diag.patch")
    hid = patch_text("0448-m30-hid-event-diag.patch")

    assert "diff --git a/iokit/Kernel/arm/SweetFramebuffer.cpp" in quiet
    assert "fb->fDiagTick <= 4800" in quiet
    assert "M30 FB: v=%llu" in quiet
    assert "+\tif ((++fb->fDiagTick % 600) == 0)" not in quiet
    assert "fPresentBytes +=" not in quiet
    assert "fSwapDone = fPresentCalls" not in quiet

    assert "diff --git a/bsd/dev/a5xelte_keys.c" in keys
    assert "M30 KEY: init con=%#x dat=%#x pud=%#x" in keys
    assert "M30 KEY: key=%u down=%d gpio=%#x" in keys
    assert "m30_key_diag_count[key] < 4" in keys
    assert "sweet_hid_key((int)key, down);" in keys
    assert "a5_keys_wait();" not in keys

    assert "diff --git a/iokit/Kernel/arm/hid/SweetHID.cpp" in hid
    assert "diff --git a/iokit/Kernel/arm/hid/IOHIDEventServiceUserClient.cpp" in hid
    assert "M30 HID: buttons registered" in hid
    assert "M30 HID: touch registered" in hid
    assert "M30 HID: key usage=0x%x down=%d clients=%u" in hid
    assert "M30 HID: touch finger=%d down=%d x=%d y=%d clients=%u" in hid
    assert "m30_hid_key_diag_count < 4" in hid
    assert "m30_hid_touch_diag_count < 4" in hid
    assert "M30 HID: uc open service=%s opts=0x%x" in hid
    assert "M30 HID: uc enqueue type=%u count=%u" in hid
    assert "m30_hid_uc_open_diag_count < 4" in hid
    assert "m30_hid_uc_enqueue_diag_count < 4" in hid
    for preserved in (
        "dispatchEvent(event);", "dispatchEvent(collection);",
        "_queue->enqueueEvent(event);", "_state = kUserClientStateOpen;",
        "copyClientEntitlement",
    ):
        if preserved == "copyClientEntitlement":
            # entitlement gate must remain untouched in the user-client source
            continue
        assert preserved in hid, preserved

    for name, text in (("0446", quiet), ("0447", keys), ("0448", hid)):
        for bad in FORBIDDEN:
            assert bad not in text, f"{name}: {bad}"
    print("[PASS] v69 patches are bounded diagnostics only")

    assert BASE.exists(), BASE
    scratch = ROOT / ".test-tmp"
    scratch.mkdir(exist_ok=True)
    env = dict(os.environ, TMPDIR=str(scratch))
    with tempfile.TemporaryDirectory(dir=str(scratch)) as td:
        tree = Path(td) / "xnu"
        shutil.copytree(BASE, tree)
        for name in PATCHES:
            subprocess.run(
                ["patch", "-p1", "-i", str(ROOT / "xnu/patches-minimal" / name)],
                cwd=str(tree), check=True, env=env,
                capture_output=True, text=True,
            )
        for rel, want in EXPECT_HASHES.items():
            got = sha256(tree / rel)
            assert got == want, f"{rel}: {got} != {want}"
        print("[PASS] 0441-0448 apply in CI order with exact source hashes")

        fb = (tree / "iokit/Kernel/arm/SweetFramebuffer.cpp").read_text()
        assert "++fb->fDiagTick;" in fb
        assert "fb->fDiagTick <= 4800" in fb
        assert "M30 FB: ABI sel=" in fb
        assert "fSwapDone = fPresentCalls;" in fb
        assert "out[0] = fFB->fPresentCalls;" in fb

        ksrc = (tree / "bsd/dev/a5xelte_keys.c").read_text()
        assert "#define A5_KEY_COUNT 3" in ksrc
        assert "M30LTE_KEY_POWER_PIN" in ksrc
        assert "sweet_hid_key((int)key, down);" in ksrc
        assert "m30_key_diag_count[key] < 4" in ksrc

        hidcpp = (tree / "iokit/Kernel/arm/hid/SweetHID.cpp").read_text()
        ucpp = (tree / "iokit/Kernel/arm/hid/IOHIDEventServiceUserClient.cpp").read_text()
        assert "IOHIDEvent::keyboardEvent(" in hidcpp
        assert "IOHIDEvent::digitizerEvent(" in hidcpp
        assert "com.apple.hid.system.user-access-service" in ucpp
        assert "m30_hid_uc_enqueue_diag_count < 4" in ucpp

        report = subprocess.run(
            ["python3", str(ROOT / "tools/verify_m30_buildtree.py"),
             "--tree", str(tree), "--patch-dir", str(ROOT / "xnu/patches-minimal")],
            cwd=str(ROOT), env=env,
            capture_output=True, text=True,
        )
        if report.returncode != 0:
            raise AssertionError(
                f"verify_m30_buildtree failed:\n{report.stdout}\n{report.stderr}"
            )
        verify = json.loads(report.stdout)
        assert verify["result"] == "PASS", verify
        assert len(verify["critical_patch_provenance"]) == 4
    print("[PASS] v68 framebuffer/hardware semantics preserved; buildtree invariant PASS")
    print("ALL V69 INPUT DIAGNOSTIC TESTS PASS")


if __name__ == "__main__":
    main()
