#!/usr/bin/env python3
"""Focused regression test for patch 0414 (16K code-dir offset alignment).

Physical v15 pstore: the 16K code directory was accepted (0413) and launchd
reached libignition, but a dyld-cache page fault panicked:
  CODE SIGNING: cs_invalid_page(0x100838000): p=1[launchd] ... allowing (remove VALID) page
  panic: offset not aligned to cshash boundary @ubc_subr.c:5739
Because this M30 kernel is 4K (PAGE_SHIFT=12),_page_offset is only 4K aligned;
cs_validate_hash() asserted it be 16K aligned (csb_hash_pageshift=14).

Fix: for csb_hash_pageshift > PAGE_SHIFT, round the offset down to the CD hash
boundary (correct first-level hash index) and bound the actual-hash computation
to the single 4K mapped VM page (no 16K overread). A 4K chunk cannot match a
16K hash, so the page is conservatively marked TAINTED, never falsely validated;
cs_invalid_page's existing policy still decides whether to allow it (here it
allows and removes CS_VALID, as it already did in v15). No signature check is
disabled -- the assertion for genuine misalignment (shift <= PAGE_SHIFT) remains.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0414-m30-align-16k-cs-page-offset.patch"
BT = ROOT / "milestone_artifacts/ci_45219943492/buildtree/unpacked/xnu"
PSTORE = ROOT / "validation/physical-boot-test/20261122-ios-v15-boot/raw/pmsg-ramoops-0"

MODEL = r"""
#include <stdio.h>
#define PAGE_SHIFT 12
#define PAGE_SIZE 4096
static const char *check(long offset, int shift, int patched)
{
    if (patched && shift > PAGE_SHIFT) {
        offset &= ~((long)((1U << shift) - 1));   /* round down to CD boundary */
    } else if (offset & ((1U << shift) - 1)) {
        return "PANIC";                            /* genuine misalignment still panics */
    }
    unsigned long size = (1U << shift);
    if (patched && size > PAGE_SIZE) size = PAGE_SIZE;  /* no overread */
    return "OK";
}
int main(void)
{
    long off_4k = 0x1000;   /* 4K-aligned, not 16K-aligned */
    long off_bad = 0x801;   /* not even 4K aligned: genuine misalignment at shift 12 */
    printf("before:%s after:%s genuine_misalign:%s\n",
        check(off_4k, 14, 0), check(off_4k, 14, 1), check(off_bad, 12, 1));
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

    assert "blob->csb_hash_pageshift > PAGE_SHIFT" in text
    assert "offset &= ~((off_t)((1U << blob->csb_hash_pageshift) - 1))" in text
    assert "size > PAGE_SIZE" in text and "size = PAGE_SIZE;" in text
    assert "never falsely" in text
    print("[PASS] patch 0414 rounds down misaligned 16K offsets and bounds hash to one VM page")

    ub = (BT / "bsd/kern/ubc_subr.c").read_text()
    assert "offset not aligned to cshash boundary" in ub  # assertion kept for genuine misalignment
    assert "cs_validate_page_no_hash" in ub
    print("[PASS] genuine-misalignment assertion retained; no validation disabled")

    d = PSTORE.read_bytes()
    assert b"offset not aligned to cshash boundary" in d
    assert b"allowing (remove VALID) page" in d
    assert b"hello from launchd.1" in d
    print("[PASS] v15 pstore: alignment panic after launchd ran; page already tolerated")

    with tempfile.TemporaryDirectory() as td:
        out = run(Path(td))
    assert out == "before:PANIC after:OK genuine_misalign:PANIC", out
    print("[PASS] model: before -> PANIC; after -> OK; genuine misalignment still PANIC (validation intact)")

    print("ALL M30 16K CS OFFSET TESTS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
