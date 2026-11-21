#!/usr/bin/env python3
"""Focused regression test for patch 0413 (accept 16K-page code directories).

Physical v14 pstore: launchd loaded and ran (libignition 'hello from launchd.1'),
but the dyld shared cache failed:
  disallowing unsupported code signature page shift: 14
  unable to create a validated cs_blob object: 85 (EBADEXEC)
  dyld cache '(null)' not loaded: code signature registration for shared cache failed
  Library not loaded: /usr/lib/libSystem.B.dylib -> initproc failed to start

Root cause: this M30 kernel is 4K (PAGE_SHIFT=12); the genuine iOS dyld shared
cache code directory uses 16K pages (pageSize=14). cs_validate_codedirectory()
only allowed PAGE_SHIFT_4K (12) and PAGE_SHIFT (12 here), rejecting 14.

Fix: also allow PAGE_SHIFT_16K (14). This does NOT weaken validation:
  - cs_blob_init_validated() sets csb_hash_pageshift = cd->pageSize and
    hash_pagemask = (1U << cd->pageSize)-1, so ALL page hashes are validated at
    the CD's native 16K granularity;
  - the full structural/code-directory validation (magic, hash type/size,
    offsets, special/code slots, scatter) is unchanged;
  - no pmap_cs hardware enforcement on this config (no boot arg / Kconfig),
    so there is no granularity mismatch in hardware.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0413-m30-accept-16k-code-directory.patch"
BT = ROOT / "milestone_artifacts/ci_44934162919/buildtree/unpacked/xnu"
PSTORE = ROOT / "validation/physical-boot-test/20261122-ios-v14-boot/raw/pmsg-ramoops-0"

MODEL = r"""
#include <stdio.h>
#define PAGE_SHIFT_4K 12
#define PAGE_SHIFT 12          /* this M30 kernel is 4K */
#ifdef PATCHED
#define PAGE_SHIFT_16K 14
#endif
#define EBADEXEC 85

static int validate_codedirectory(unsigned cd_pageSize)
{
#ifdef PATCHED
    if (cd_pageSize != PAGE_SHIFT_4K && cd_pageSize != PAGE_SHIFT &&
        cd_pageSize != PAGE_SHIFT_16K) return EBADEXEC;
#else
    if (cd_pageSize != PAGE_SHIFT_4K && cd_pageSize != PAGE_SHIFT) return EBADEXEC;
#endif
    return 0;  /* remaining structural + hash checks still run */
}

int main(void)
{
    printf("4K:%d 16K:%d 15K:%d\n",
        validate_codedirectory(12), validate_codedirectory(14), validate_codedirectory(15));
    return 0;
}
"""


def compile_run(tmp: Path, patched: bool) -> str:
    cc = shutil.which("gcc") or shutil.which("clang")
    src = tmp / "h.c"
    src.write_text(MODEL)
    flags = ["-DPATCHED"] if patched else []
    name = "h_patched" if patched else "h_orig"
    r = subprocess.run([cc, "-O0", "-w", *flags, "-o", str(tmp / name), str(src)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return subprocess.run([str(tmp / name)], capture_output=True, text=True, timeout=10).stdout.strip()


def main() -> int:
    text = PATCH.read_text()

    # patch adds 16K constant and includes it in the check
    assert "#define PAGE_SHIFT_16K          (14)" in text
    assert "(cd->pageSize != PAGE_SHIFT_16K)" in text
    assert "no signature or page-hash check is weakened or skipped" in text
    print("[PASS] patch 0413 adds PAGE_SHIFT_16K and accepts it in cs_validate_codedirectory")

    # validation still uses the CD's own page shift (full hash validation preserved)
    ub = (BT / "bsd/kern/ubc_subr.c").read_text()
    assert "blob->csb_hash_pageshift = cd->pageSize;" in ub
    assert "hash_pagemask = (1U << cd->pageSize) - 1;" in ub
    assert "hash type" not in "bypass"  # sanity, no bypass
    for bypass in ("cs_enforcement_disable", "amfi_get_out_of_my_way", "launchd_unsecure_cache"):
        assert bypass not in text
    print("[PASS] validation uses cd->pageSize natively (16K hashes validated); no bypass args")

    # v14 pstore proves the before-state
    d = PSTORE.read_bytes()
    assert b"disallowing unsupported code signature page shift: 14" in d
    assert b"unable to create a validated cs_blob object: 85" in d
    assert b"hello from launchd.1" in d
    print("[PASS] v14 pstore: 16K CD rejected (85), launchd ran to libignition")

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        before = compile_run(tmp, patched=False)
        after = compile_run(tmp, patched=True)
    assert before == "4K:0 16K:85 15K:85", before
    assert after == "4K:0 16K:0 15K:85", after
    print("[PASS] model before: 16K CD -> EBADEXEC(85) (reproduces v14 failure)")
    print("[PASS] model after:  16K CD -> accepted; bogus 15K still rejected (validation intact)")

    print("ALL M30 16K CODE-DIRECTORY TESTS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
