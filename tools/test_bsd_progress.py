#!/usr/bin/env python3
"""Focused regression test for patches 0409/0410 (post-bsd_init progress).

Evidence (v9 recovered pmsg, 93 records): bsd_init entered (copyright, MAC
Framework, buffer headers) but stalled before sweet_hfs_register / bsd_autoconf.
Root cause path: IOKitInitializeTime() waited 30s on a nonexistent IORTC.

Verifies:
  * 0410 adds board_config include and guards the IORTC wait with M30LTE.
  * A faithful model of that #if, compiled three ways:
      - M30LTE defined        -> wait skipped  (new behavior)
      - no board macro        -> wait retained (original arm64 behavior)
      - BCM2837 defined       -> wait skipped  (original BCM2837 behavior)
  * 0409 adds newline-terminated M30LTE markers around IOKitInitializeTime,
    vfsinit, sweet_hfs_register and bsd_autoconf, guarded by M30LTE.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P409 = ROOT / "xnu/patches-minimal/0409-m30-bsd-init-markers.patch"
P410 = ROOT / "xnu/patches-minimal/0410-m30-skip-iortc-wait.patch"

# Faithful reproduction of the patched #if in IOKitInitializeTime.
MODEL = r"""
#include <stdio.h>
static int wait_calls = 0;
static void waitForService_IORTC(void) { wait_calls++; }
void IOKitInitializeTime(void) {
#if !defined(BCM2837) && !defined(ARM64_BOARD_CONFIG_M30LTE)
    waitForService_IORTC();
#endif
}
int main(void) { IOKitInitializeTime(); printf("wait_calls=%d\n", wait_calls); return 0; }
"""


def run_model(tmp: Path, cc: str, flags: list[str], expect: str, label: str) -> None:
    name = label.replace(" ", "_")
    r = subprocess.run([cc, "-O2", "-w", *flags, "-o", str(tmp / name), str(tmp / "m.c")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    out = subprocess.run([str(tmp / name)], capture_output=True, text=True)
    assert out.stdout.strip() == expect, f"{label}: {out.stdout.strip()} != {expect}"
    print(f"[PASS] {label}: {out.stdout.strip()}")


def main() -> int:
    t410 = P410.read_text()
    assert "#include <pexpert/arm64/board_config.h>" in t410
    assert "#if !defined(BCM2837) && !defined(ARM64_BOARD_CONFIG_M30LTE)" in t410
    print("[PASS] 0410 guards IORTC wait with M30LTE and includes board_config")
    t409 = P409.read_text()
    for marker in ["IOKitInitializeTime returned", "vfsinit returned",
                   "sweet_hfs registered", "calling bsd_autoconf",
                   "bsd_autoconf returned"]:
        assert f'printf("M30 BSD: {marker}\\n")' in t409, marker
    assert t409.count("#if defined(ARM64_BOARD_CONFIG_M30LTE)") >= 5
    print("[PASS] 0409 adds all 5 newline-terminated M30LTE markers")

    with tempfile.TemporaryDirectory(prefix="bsd_progress_") as d:
        tmp = Path(d)
        (tmp / "m.c").write_text(MODEL)
        cc = shutil.which("gcc") or shutil.which("clang")
        run_model(tmp, cc, ["-DARM64_BOARD_CONFIG_M30LTE"], "wait_calls=0", "M30LTE skips IORTC wait")
        run_model(tmp, cc, [], "wait_calls=1", "generic arm64 retains IORTC wait")
        run_model(tmp, cc, ["-DBCM2837"], "wait_calls=0", "BCM2837 retains original skip")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
