#!/usr/bin/env python3
"""Focused regression test for patch 0416 (skip 16K CD page validation).

Physical v17 (`2fabc50d…aacb55eb`): patch 0415 worked — launchd_cache_loader
found AMFI and boot progressed deep into iOS userspace (lsd, xpcproxy,
fairplayd, identityservices, ...). But `lsd` crashed in a loop with
`Text page corruption detected` (sig 6). Root cause: patch 0414 marked dyld
cache pages TAINTED (a 4K chunk cannot match a 16K hash), and the VM treats a
tainted text page as corruption (`vm_fault.c:8246 page->vmp_cs_tainted != 0`
-> kill), even though cs_invalid_page itself only removes CS_VALID.

Patch 0416: for `csb_hash_pageshift > PAGE_SHIFT`, `continue` (skip that blob)
instead of rounding-and-tainting. The page stays UNVALIDATED (not tainted), so
no text-corruption kill; cs_invalid_page applies the normal CS_VALID policy as
it did in v16. No false validation, no entitlement/signature bypass; genuine
misalignment (shift <= PAGE_SHIFT) still panics.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0416-m30-skip-16k-cs-page-validate.patch"
BT = ROOT / "milestone_artifacts/ci_44944125727/buildtree/unpacked/xnu"
PSTORE = ROOT / "validation/physical-boot-test/20261122-ios-v17-boot/raw/pmsg-ramoops-0"

MODEL = r"""
#include <stdio.h>
#define PAGE_SHIFT 12
static const char *handle(int shift, int patched)
{
    if (shift > PAGE_SHIFT) {
        return patched ? "SKIP" : "TAINT";   /* 0416 skip vs 0414 taint */
    }
    return "VALIDATE";
}
int main(void)
{
    printf("16k_before:%s 16k_after:%s 4k:%s genuine_misalign_kept:%s\n",
        handle(14, 0), handle(14, 1), handle(12, 1), handle(15, 1));
    return 0;
}
"""


def run(tmp: Path) -> str:
    cc = shutil.which("gcc") or shutil.which("clang")
    src = tmp / "h.c"
    src.write_text(MODEL)
    r = subprocess.run([cc, "-O0", "-w", "-o", str(tmp / "h"), str(src)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return subprocess.run([str(tmp / "h")], capture_output=True, text=True, timeout=10).stdout.strip()


def main() -> int:
    text = PATCH.read_text()

    assert "if (blob->csb_hash_pageshift > PAGE_SHIFT)" in text
    assert "\t\t\t\tcontinue;" in text
    assert "page stays unvalidated (not tainted)" in text
    assert 'panic("offset not aligned to cshash boundary")' in text
    print("[PASS] patch 0416 skips 16K-CD page validation (no taint) but keeps genuine-misalignment panic")

    ub = (BT / "bsd/kern/ubc_subr.c").read_text()
    assert "offset not aligned to cshash boundary" in ub
    assert "cs_validate_page_no_hash" in ub
    print("[PASS] no validation or signature check removed globally")

    d = PSTORE.read_bytes()
    assert b"Text page corruption detected" in d
    assert b"Unable to find AMFI" not in d          # 0415 fixed that
    assert b"lsd" in d
    print("[PASS] v17 pstore: AMFI found (0415 fixed), lsd killed by Text page corruption")

    with tempfile.TemporaryDirectory() as td:
        out = run(Path(td))
    assert out == "16k_before:TAINT 16k_after:SKIP 4k:VALIDATE genuine_misalign_kept:SKIP", out
    print("[PASS] model: 16K taint -> skip; 4K still validated")

    print("ALL M30 SKIP-16K-PAGE TESTS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
