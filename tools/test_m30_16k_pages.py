#!/usr/bin/env python3
"""Focused regression test for patch 0417 (16K pages for M30LTE).

Physical v16-v18: genuine iOS 16.7.16 (iPhone10,3 / D22) userspace booted deep
(launchd + many daemons), but a daemon crash loop (lsd, securityd, backboardd,
identityservices; sig 5/6 with 'Text page corruption') persisted through the
4K-kernel workarounds (0413 accept 16K CD, 0414/0416 page handling). Root cause:
the M30 kernel is 4K (PAGE_SHIFT=12) while the iOS rootfs/dyld cache is 16K.
XNU selects 4K when memSize <= 1GB (arm_init.c) and, critically, the TCR
translation granule and ARM_PGSHIFT are COMPILE-TIME (__ARM_16K_PG__), so the
kernel must be built for 16K to map/validate the dyld cache natively (SWEET.h
already does this).

Patch 0417 defines __ARM_16K_PG__ 1 in M30LTE.h. With 16K pages:
  - ARM_PGSHIFT = 14, TCR_TG0 granule = 16KB, PAGE_MAX_SHIFT = 14;
  - the dyld cache 16K code directory (pageSize=14) validates natively with
    NO special-case patches needed (0413/0414/0416 become harmless no-ops);
  - genuine code signing is STRONGER, not weaker (native page hash granularity).
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0417-m30-16k-pages.patch"
BT = ROOT / "milestone_artifacts/ci_44946634655/buildtree/unpacked/xnu"

MODEL = r"""
#include <stdio.h>
#ifdef PATCHED
#define __ARM_16K_PG__ 1
#else
#define __ARM_16K_PG__ 0
#endif
#if __ARM_16K_PG__
#define ARM_PGSHIFT 14
#define TCR_TG0 "16KB"
#else
#define ARM_PGSHIFT 12
#define TCR_TG0 "4KB"
#endif
#define PAGE_MAX_SHIFT 14
int main(void)
{
    printf("pgshift=%d granule=%s matches_ios=%d\n",
        ARM_PGSHIFT, TCR_TG0, ARM_PGSHIFT == PAGE_MAX_SHIFT);
    return 0;
}
"""


def run(tmp: Path, patched: bool) -> str:
    cc = shutil.which("gcc") or shutil.which("clang")
    src = tmp / "h.c"
    src.write_text(MODEL)
    flags = ["-DPATCHED"] if patched else []
    name = "h_p" if patched else "h_o"
    r = subprocess.run([cc, "-O0", "-w", *flags, "-o", str(tmp / name), str(src)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return subprocess.run([str(tmp / name)], capture_output=True, text=True, timeout=10).stdout.strip()


def main() -> int:
    text = PATCH.read_text()

    assert "diff --git a/pexpert/pexpert/arm64/M30LTE.h" in text
    assert "#define __ARM_16K_PG__               1" in text
    print("[PASS] patch 0417 defines __ARM_16K_PG__ 1 for M30LTE")

    # M30LTE.h is included for this build, and SWEET already uses the same define
    bc = (BT / "pexpert/pexpert/arm64/board_config.h").read_text()
    assert "#ifdef ARM64_BOARD_CONFIG_M30LTE" in bc and "M30LTE.h" in bc
    sweet = (BT / "pexpert/pexpert/arm64/SWEET.h").read_text()
    assert "__ARM_16K_PG__" in sweet
    print("[PASS] M30LTE board header is included; SWEET reference uses same 16K define")

    # compile-time dependencies confirm 16K changes granule + shift
    pr = (BT / "osfmk/arm64/proc_reg.h").read_text()
    vp = (BT / "osfmk/mach/arm/vm_param.h").read_text()
    assert "#define TCR_TG0_GRANULE_16KB" in pr and "#define ARM_PGSHIFT 14" in pr
    assert "#define PAGE_MAX_SHIFT          14" in vp
    print("[PASS] __ARM_16K_PG__ selects TCR 16KB granule and ARM_PGSHIFT=14 (== PAGE_MAX_SHIFT)")

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        before = run(tmp, patched=False)
        after = run(tmp, patched=True)
    assert before == "pgshift=12 granule=4KB matches_ios=0", before
    assert after == "pgshift=14 granule=16KB matches_ios=1", after
    print("[PASS] model: before -> 4K mismatch; after -> native 16K matches iOS rootfs")

    print("ALL M30 16K PAGES TESTS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
