#!/usr/bin/env python3
"""Regression test for v70: restore v68 lock-screen behavior after v69.

v69 added three logging-only patches after v68.  The physical run reached
backboardd and presented frames but SpringBoard terminated with an uncaught
NSException, while the device stayed at the Apple logo.  The v70 correction is
narrow: keep 0446 (the bounded framebuffer heartbeat) but revert 0447/0448,
the only v69 patches that touched the button producer or HID consumer paths.
The functional GPIO -> HID path is unchanged from v68 and remains proven by the
v69 runtime capture.
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
    "0449-m30-revert-key-input-diag.patch",
    "0450-m30-revert-hid-event-diag.patch",
)
BASE = ROOT / "milestone_artifacts/ci_45356410574/buildtree/unpacked/xnu"
EXPECT_HASHES = {
    "pexpert/arm/pe_serial.c": "0567414c2f004778bba71a01b2723202af5bde98bf1ca6ec035856b086c2a772",
    "bsd/kern/sys_generic.c": "438bc8468900285491f4bd71be1cf89aa5f40874f0c7ff3ec37e7828138df94f",
    "iokit/Kernel/arm/SweetFramebuffer.cpp": "d3199f92c608b8c7d874d83087c0a8409b6488a3acc93d40599deb0bc32e3c8f",
    "bsd/dev/a5xelte_keys.c": "d53238ba0ca163a36ef17d1847d56f442bca3964001e0b998aa50d073a6f12db",
    "iokit/Kernel/arm/hid/SweetHID.cpp": "d30c9adf85a89b5c94151e57bad24007655d1a9beb06742fc3d821a0f89805f3",
    "iokit/Kernel/arm/hid/IOHIDEventServiceUserClient.cpp": "0e8df68c047322c220cdbd1b4c9db194c5dc1fb80117bfc8c726e9fab967637e",
}
FORBIDDEN = (
    "cs_enforcement_disable", "amfi_get_out_of_my_way",
    "launchd_unsecure_cache", "disable_security", "case 79:",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def patch_text(name: str) -> str:
    return (ROOT / "xnu/patches-minimal" / name).read_text()


def assert_pure_revert(name: str, files: tuple[str, ...]) -> str:
    text = patch_text(name)
    for relative in files:
        assert f"--- a/{relative}" in text, (name, relative)
        assert f"+++ b/{relative}" in text, (name, relative)
    added = [line for line in text.splitlines()
             if line.startswith("+") and not line.startswith("+++")]
    assert not added, f"{name} unexpectedly adds code: {added[:5]}"
    for bad in FORBIDDEN:
        assert bad not in text, f"{name}: {bad}"
    return text


def main() -> None:
    key_revert = assert_pure_revert(
        "0449-m30-revert-key-input-diag.patch", ("bsd/dev/a5xelte_keys.c",))
    hid_revert = assert_pure_revert(
        "0450-m30-revert-hid-event-diag.patch", (
            "iokit/Kernel/arm/hid/SweetHID.cpp",
            "iokit/Kernel/arm/hid/IOHIDEventServiceUserClient.cpp",
        ))
    assert "m30_key_diag_count" in key_revert
    assert "M30 HID: uc enqueue" in hid_revert
    assert "-				sweet_hid_key((int)key, down);" not in key_revert
    assert "-        Boolean result = _queue->enqueueEvent(event);" not in hid_revert

    quiet = patch_text("0446-m30-framebuffer-status-quiet.patch")
    assert "fb->fDiagTick <= 4800" in quiet
    assert "M30 FB: v=%llu" in quiet
    assert "fPresentBytes +=" not in quiet
    assert "fSwapDone = fPresentCalls" not in quiet
    print("[PASS] v70 reverts only v69 input diagnostics; 0446 heartbeat cap kept")

    assert BASE.exists(), BASE
    scratch = ROOT / ".test-tmp"
    scratch.mkdir(exist_ok=True)
    env = dict(os.environ, TMPDIR=str(scratch))
    with tempfile.TemporaryDirectory(dir=str(scratch)) as td:
        tree = Path(td) / "xnu"
        shutil.copytree(BASE, tree)
        for name in PATCHES:
            subprocess.run(
                ["patch", "-s", "-p1", "-i", str(ROOT / "xnu/patches-minimal" / name)],
                cwd=str(tree), check=True, env=env,
                capture_output=True, text=True,
            )

        for rel, want in EXPECT_HASHES.items():
            got = sha256(tree / rel)
            assert got == want, f"{rel}: {got} != {want}"
        print("[PASS] 0441-0450 apply with exact v70 source hashes")

        fb = (tree / "iokit/Kernel/arm/SweetFramebuffer.cpp").read_text()
        assert "++fb->fDiagTick;" in fb
        assert "fb->fDiagTick <= 4800" in fb
        assert "M30 FB: ABI sel=" in fb
        assert "fSwapDone = fPresentCalls;" in fb
        assert "out[0] = fFB->fPresentCalls;" in fb

        ksrc = (tree / "bsd/dev/a5xelte_keys.c").read_text()
        assert "M30 KEY:" not in ksrc
        assert "m30_key_diag_count" not in ksrc
        assert "sweet_hid_key((int)key, down);" in ksrc
        assert "M30LTE_KEY_POWER_PIN" in ksrc

        hidcpp = (tree / "iokit/Kernel/arm/hid/SweetHID.cpp").read_text()
        ucpp = (tree / "iokit/Kernel/arm/hid/IOHIDEventServiceUserClient.cpp").read_text()
        assert "M30 HID:" not in hidcpp
        assert "M30 HID:" not in ucpp
        assert "IOHIDEvent::keyboardEvent(" in hidcpp
        assert "IOHIDEvent::digitizerEvent(" in hidcpp
        assert "com.apple.hid.system.user-access-service" in ucpp
        assert "_queue->enqueueEvent(event);" in ucpp

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
    print("[PASS] v68 framebuffer/GPIO/HID semantics restored; buildtree invariant PASS")
    print("ALL V70 LOCK-SCREEN RESTORE TESTS PASS")


if __name__ == "__main__":
    main()
