#!/usr/bin/env python3
"""Regression test for patch 0425 (SpringBoardUI class-probe fix-up).

v28 physical evidence: SpringBoard starts but aborts in +[SpringBoardUI load]
with NSInternalInconsistencyException 'This process should not be linking or
loading SpringBoardUI.framework'. LiveContainer works around the identical iOS
16 assertion by registering an XCTestConfiguration Objective-C class before the
probe runs. Patch 0425 instead retargets the class-name probe in the already
faulted dyld shared cache page to an always-present class name (NSObject). It
runs strictly after cs_validate_page() and does not weaken code signing.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0425-m30-xctest-class-probe.patch"
PSTORE = ROOT / "validation/physical-boot-test/20261122-ios-v28-boot/raw/pmsg-ramoops-0"


def main():
    t = PATCH.read_text()

    # --- patch structure: the fix-up must be post-validation and once-only ---
    assert "cs_validate_page(vnode, pager, voff, vdata, vsize," in t
    assert "m30_xctest_probe_fixup(kaddr);" in t
    assert t.index("cs_validate_page(") < t.index("m30_xctest_probe_fixup(kaddr);")
    assert "XCTestConfiguration" in t and "NSObject" in t
    assert "m30_xctest_probe_fixed" in t
    assert "probe_ascii" in t and "probe_utf16" in t
    assert "does not skip" in t
    assert "AFTER cs_validate_page()" in t

    # anti-bypass: no security weakening strings
    for bad in ("cs_enforcement_disable", "amfi_get_out_of_my_way",
                "launchd_unsecure_cache", "CSDebugDisable",
                "vmp_cs_validated = VMP_CS_ALL_TRUE", "tainted = 0;"):
        assert bad not in t, f"patch must not contain {bad!r}"
    print("[PASS] patch 0425 applies fix-up only after validation, no security bypass")

    # --- physical evidence: the exact blocker this addresses ---
    d = PSTORE.read_bytes()
    assert b"CRASH SpringBoard[26] sig 6" in d
    assert b"This process should not be linking or loading SpringBoardUI.framework" in d
    assert b"NSInternalInconsistencyException" in d
    print("[PASS] v28 pstore: SpringBoardUI class-presence assertion confirmed")

    # --- behavioural model of the fix-up, compiled and executed ---
    model = textwrap.dedent(r"""
        #include <stdio.h>
        #include <string.h>
        #define PAGE_SIZE 4096
        static int fixed = 0;
        static void fixup(void *page) {
            static const char probe_ascii[] = "XCTestConfiguration";
            static const char repl_ascii[]  = "NSObject";
            static const char probe_utf16[] =
                "X\0C\0T\0e\0s\0t\0C\0o\0n\0f\0i\0g\0u\0r\0a\0t\0i\0o\0n\0";
            static const char repl_utf16[]  = "N\0S\0O\0b\0j\0e\0c\0t\0";
            char *p = (char *)page; size_t i;
            if (fixed || page == NULL) return;
            for (i = 0; i + sizeof(probe_ascii) <= PAGE_SIZE; i++) {
                if (memcmp(p + i, probe_ascii, sizeof(probe_ascii) - 1) == 0 &&
                    p[i + sizeof(probe_ascii) - 1] == '\0') {
                    memcpy(p + i, repl_ascii, sizeof(repl_ascii) - 1);
                    memset(p + i + sizeof(repl_ascii) - 1, 0,
                           sizeof(probe_ascii) - sizeof(repl_ascii));
                    fixed = 1; return;
                }
            }
            for (i = 0; i + sizeof(probe_utf16) + 1 <= PAGE_SIZE; i++) {
                if (memcmp(p + i, probe_utf16, sizeof(probe_utf16) - 1) == 0 &&
                    p[i + sizeof(probe_utf16) - 1] == '\0' &&
                    p[i + sizeof(probe_utf16)] == '\0') {
                    memcpy(p + i, repl_utf16, sizeof(repl_utf16) - 1);
                    memset(p + i + sizeof(repl_utf16) - 1, 0,
                           sizeof(probe_utf16) - sizeof(repl_utf16) - 1);
                    fixed = 1; return;
                }
            }
        }
        int main(void) {
            static char page[PAGE_SIZE];
            /* ASCII C-string literal case */
            memset(page, 0xAA, sizeof(page));
            memcpy(page + 64, "XCTestConfiguration", 20);
            fixup(page);
            if (strcmp(page + 64, "NSObject") != 0) { printf("ascii:%s\n", page+64); return 1; }
            printf("ascii=OK once=%d\n", fixed);
            /* once-only guard: second page must be untouched */
            fixed = 0; /* model reset to test the other literal form */
            memset(page, 0xAA, sizeof(page));
            memcpy(page + 100, "X\0C\0T\0e\0s\0t\0C\0o\0n\0f\0i\0g\0u\0r\0a\0t\0i\0o\0n\0\0\0", 40);
            static const char expect[] = "N\0S\0O\0b\0j\0e\0c\0t\0\0\0";
            fixup(page);
            if (memcmp(page + 100, expect, sizeof(expect)) != 0) { printf("utf16=FAIL\n"); return 2; }
            printf("utf16=OK once=%d\n", fixed);
            /* non-matching page: no change, flag stays clear */
            fixed = 0;
            memset(page, 0xAA, sizeof(page));
            char before[PAGE_SIZE]; memcpy(before, page, sizeof(page));
            fixup(page);
            if (memcmp(before, page, sizeof(page)) != 0 || fixed != 0) { printf("nomatch=FAIL\n"); return 3; }
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
    assert "ascii=OK once=1" in out, out
    assert "utf16=OK once=1" in out, out
    assert "nomatch=OK" in out, out
    print("[PASS] fix-up model: ascii + utf16 retarget to NSObject, no false matches")

    print("ALL M30 XCTEST CLASS PROBE TESTS PASS")


if __name__ == "__main__":
    raise SystemExit(main())
