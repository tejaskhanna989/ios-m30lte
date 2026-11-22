#!/usr/bin/env python3
"""Regression test for patch 0425 (SpringBoardUI class-probe fix-up, v30).

v28 physical: SpringBoard aborts in +[SpringBoardUI load] with
NSInternalInconsistencyException. v29 physical: one-shot fix-up fired but the
crash persisted because only the FIRST page containing the literal was patched
(possibly from a different process), leaving SpringBoard's copy untouched.

v30 regenerates patch 0425 to patch EVERY occurrence on EVERY code-signed page,
with per-patch diagnostics (object offset + running total). It runs strictly
after cs_validate_page() and does not weaken code signing.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0425-m30-xctest-class-probe.patch"
PSTORE_V28 = ROOT / "validation/physical-boot-test/20261122-ios-v28-boot/raw/pmsg-ramoops-0"
PSTORE_V29 = ROOT / "validation/physical-boot-test/20261122-ios-v29-boot/raw/pmsg-ramoops-0"


def main():
    t = PATCH.read_text()

    # --- patch structure: post-validation, every page, every occurrence ---
    assert "cs_validate_page(vnode, pager, voff, vdata, vsize," in t
    assert "m30_xctest_probe_fixup(kaddr, mo_offset);" in t
    assert t.index("cs_validate_page(") < t.index("m30_xctest_probe_fixup(kaddr, mo_offset);")
    assert "XCTestConfiguration" in t and "NSObject" in t
    assert "m30_xctest_patch_count" in t
    assert "probe_ascii" in t and "probe_utf16" in t
    assert "does not skip" in t
    assert "AFTER cs_validate_page()" in t
    # v30 specifically: no one-shot guard, all-copy patching, diagnostics
    assert "m30_xctest_probe_fixed" not in t, "one-shot guard must be removed"
    assert "patch EVERY occurrence" in t
    assert "EVERY" in t and "every copy" in t
    assert "m30_xctest_patch_count" in t and "total %lu" in t
    assert "0x%llx+%zu" in t, "per-patch object offset diagnostics required"
    assert "page_offset" in t

    # anti-bypass: no security weakening strings
    for bad in ("cs_enforcement_disable", "amfi_get_out_of_my_way",
                "launchd_unsecure_cache", "CSDebugDisable",
                "vmp_cs_validated = VMP_CS_ALL_TRUE", "tainted = 0;"):
        assert bad not in t, f"patch must not contain {bad!r}"
    print("[PASS] patch 0425 (v30): all-copy post-validation fix-up, no security bypass")

    # --- physical evidence: the exact blockers this addresses ---
    d28 = PSTORE_V28.read_bytes()
    assert b"CRASH SpringBoard[26] sig 6" in d28
    assert b"This process should not be linking or loading SpringBoardUI.framework" in d28
    assert b"NSInternalInconsistencyException" in d28
    print("[PASS] v28 pstore: SpringBoardUI class-presence assertion confirmed")

    d29 = PSTORE_V29.read_bytes()
    assert b"M30 XCTEST: retargeted SpringBoardUI class probe (ascii)" in d29
    assert b"CRASH SpringBoard[27] sig 6" in d29
    assert b"This process should not be linking or loading SpringBoardUI.framework" in d29
    print("[PASS] v29 pstore: one-shot fix fired but crash persists (root cause confirmed)")

    # --- behavioural model: patch ALL occurrences in one page ---
    model = textwrap.dedent(r"""
        #include <stdio.h>
        #include <string.h>
        #define PAGE_SIZE 4096
        static unsigned long count = 0;
        static void fixup(void *kaddr, unsigned long long off) {
            static const char probe_ascii[] = "XCTestConfiguration";
            static const char repl_ascii[]  = "NSObject";
            static const char probe_utf16[] =
                "X\0C\0T\0e\0s\0t\0C\0o\0n\0f\0i\0g\0u\0r\0a\0t\0i\0o\0n\0";
            static const char repl_utf16[]  = "N\0S\0O\0b\0j\0e\0c\0t\0";
            char *p = (char *)kaddr; size_t i;
            if (!p) return;
            for (i = 0; i + sizeof(probe_ascii) <= PAGE_SIZE; i++) {
                if (p[i] != 'X') continue;
                if (memcmp(p+i, probe_ascii, sizeof(probe_ascii)-1) == 0 &&
                    p[i + sizeof(probe_ascii)-1] == '\0') {
                    memcpy(p+i, repl_ascii, sizeof(repl_ascii)-1);
                    memset(p+i+sizeof(repl_ascii)-1, 0,
                           sizeof(probe_ascii)-sizeof(repl_ascii));
                    count++;
                }
            }
            for (i = 0; i + sizeof(probe_utf16) + 1 <= PAGE_SIZE; i++) {
                if (p[i] != 'X') continue;
                if (memcmp(p+i, probe_utf16, sizeof(probe_utf16)-1) == 0 &&
                    p[i+sizeof(probe_utf16)-1] == '\0' &&
                    p[i+sizeof(probe_utf16)] == '\0') {
                    memcpy(p+i, repl_utf16, sizeof(repl_utf16)-1);
                    memset(p+i+sizeof(repl_utf16)-1, 0,
                           sizeof(probe_utf16)-sizeof(repl_utf16)-1);
                    count++;
                }
            }
        }
        int main(void) {
            static char page[PAGE_SIZE];
            /* TWO ASCII copies + one UTF16 copy on ONE page */
            memset(page, 0xAA, sizeof(page));
            memcpy(page + 64,  "XCTestConfiguration", 20);
            memcpy(page + 200, "XCTestConfiguration", 20);
            memcpy(page + 500, "X\0C\0T\0e\0s\0t\0C\0o\0n\0f\0i\0g\0u\0r\0a\0t\0i\0o\0n\0\0\0", 40);
            fixup(page, 0x1234000);
            if (strcmp(page+64, "NSObject") != 0 ||
                strcmp(page+200, "NSObject") != 0) { printf("allcopy=FAIL ascii\n"); return 1; }
            static const char expect[] = "N\0S\0O\0b\0j\0e\0c\0t\0\0\0";
            if (memcmp(page+500, expect, sizeof(expect)) != 0) { printf("allcopy=FAIL utf16\n"); return 2; }
            if (count != 3) { printf("allcopy=FAIL count %lu\n", count); return 3; }
            printf("allcopy=OK count=%lu\n", count);
            /* second page: still patches (no one-shot guard) */
            memset(page, 0xAA, sizeof(page));
            memcpy(page + 300, "XCTestConfiguration", 20);
            fixup(page, 0x5678000);
            if (strcmp(page+300, "NSObject") != 0 || count != 4) { printf("nos guard=FAIL\n"); return 4; }
            printf("nosguard=OK count=%lu\n", count);
            /* non-matching page: no change */
            memset(page, 0xAA, sizeof(page));
            char before[PAGE_SIZE]; memcpy(before, page, sizeof(page));
            fixup(page, 0x9abc000);
            if (memcmp(before, page, sizeof(page)) != 0 || count != 4) { printf("nomatch=FAIL\n"); return 5; }
            printf("nomatch=OK\n");
            return 0;
        }
    """)
    with tempfile.TemporaryDirectory() as td:
        c = Path(td) / "model.c"
        b = Path(td) / "model"
        c.write_text(model)
        subprocess.run(["cc", "-O0", "-Wall", "-Wextra", "-o", str(b), str(c)], check=True)
        out = subprocess.run([str(b)], check=True, capture_output=True, text=True).stdout
    assert "allcopy=OK count=3" in out, out
    assert "nosguard=OK count=4" in out, out
    assert "nomatch=OK" in out, out
    print("[PASS] fix-up model: all copies patched, no one-shot guard, no false matches")

    print("ALL M30 XCTEST CLASS PROBE TESTS PASS")


if __name__ == "__main__":
    raise SystemExit(main())
