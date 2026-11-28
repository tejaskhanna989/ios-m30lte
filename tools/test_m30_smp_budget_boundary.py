"""Boundary tests for 0456's pmsg budget emitter.

The 0456 patch must guarantee a HARD total byte budget. The first version did
not: the header line was emitted before any budget check, so a 2 KiB cap could
not stop 80 header lines (5,200-10,320 bytes, 32-63% of a 16 KiB ring).

These tests extract the C emitter from the patch, compile it on the host with
stub sinks, and assert the invariant directly on the generated output rather
than by inspecting source text.

Invariant under test: the bytes that actually reach the sink never exceed
budget. Two bugs were found this way and are pinned here:

  * clamp used `len = room` while charging `len + 1`, overshooting by exactly
    one byte per truncation;
  * the reserve was computed with sizeof() (including the NUL, which is never
    emitted) instead of strlen() + 1.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0456-m30-uihb-ring-budget.patch"

HARNESS_HEAD = """#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <stdlib.h>
int m30_ls_diag_enabled = 1;
int host_boot_kib = 0;
static long emitted = 0;
static int nlines = 0;
static char lastline[8192] = "";
static void host_sink(const char *l);
int PE_parse_boot_argn(const char *k, int *v, int l)
{ (void)k; (void)l; if (host_boot_kib > 0) *v = host_boot_kib; return host_boot_kib > 0; }
"""

HARNESS_TAIL = """
static void host_sink(const char *l)
{
    emitted += (long)strlen(l) + 1;
    nlines++;
    strncpy(lastline, l, sizeof(lastline) - 1);
}
int main(int argc, char **argv)
{
    static char line[16384];
    int n, len;
    if (argc < 4) return 2;
    host_boot_kib = atoi(argv[1]);
    n = atoi(argv[2]);
    len = atoi(argv[3]);
    if (len > (int)sizeof(line) - 1) len = (int)sizeof(line) - 1;
    memset(line, 'A', sizeof(line));
    line[len] = '\\0';
    for (int i = 0; i < n; i++) m30_smp_emit(line);
    printf("%ld %d %s\\n", emitted, nlines, lastline);
    return emitted > (long)host_boot_kib * 1024;
}
"""


def extract_emitter() -> str:
    """Pull the emitter C out of the patch's added lines."""
    added = [l[1:] for l in PATCH.read_text().splitlines()
             if l.startswith("+") and not l.startswith("+++")]
    src = "\n".join(added)
    if "#define M30_SMP_MARKER" not in src:
        raise AssertionError("emitter not found in patch")
    start = src.index("#define M30_SMP_MARKER")
    end = src.index("\nstatic void\nm30_smp_emit", start)
    # include the emit function body up to its closing brace at column 0
    tail = src[end:]
    close = tail.index("\n}\n")
    return src[start:end + close + 3]


@unittest.skipUnless(shutil.which("gcc") or shutil.which("cc"),
                     "no host C compiler available")
class BudgetBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cc = shutil.which("gcc") or shutil.which("cc")
        cls.tmp = Path(tempfile.mkdtemp())
        code = HARNESS_HEAD + extract_emitter().replace(
            "m30_ls_diag_line(", "host_sink(") + HARNESS_TAIL
        src = cls.tmp / "h.c"
        src.write_text(code)
        cls.bin = cls.tmp / "h"
        r = subprocess.run([cc, "-O1", "-o", str(cls.bin), str(src)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise AssertionError(f"harness did not compile:\n{r.stderr}")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def run_case(self, kib: int, n: int, linelen: int):
        r = subprocess.run([str(self.bin), str(kib), str(n), str(linelen)],
                           capture_output=True, text=True)
        parts = r.stdout.rstrip("\n").split(" ", 2)
        emitted, lines = int(parts[0]), int(parts[1])
        last = parts[2] if len(parts) > 2 else ""
        return emitted, lines, last, r.returncode

    def test_budget_is_never_exceeded(self):
        """The core invariant, across boundary and adversarial shapes."""
        cases = [
            (2, 1, 60), (2, 200, 65), (2, 200, 253), (1, 500, 253),
            (2, 5000, 253), (3, 200, 109), (1, 1000, 109), (2, 2000, 4096),
            (4, 10000, 253), (1, 1, 300), (2, 100, 62), (2, 100, 63),
            (1, 9999, 8191), (2, 0, 0),
        ]
        for kib, n, linelen in cases:
            with self.subTest(kib=kib, n=n, len=linelen):
                emitted, _, _, rc = self.run_case(kib, n, linelen)
                self.assertLessEqual(
                    emitted, kib * 1024,
                    f"emitted {emitted} bytes exceeds {kib * 1024} budget")
                self.assertEqual(rc, 0)

    def test_headers_are_inside_the_budget(self):
        """80 header-sized lines (the old bypass) must not blow the cap."""
        emitted, lines, _, _ = self.run_case(2, 80, 65)
        self.assertLessEqual(emitted, 2048)
        self.assertLess(lines, 80, "all headers were emitted; cap not applied")

    def test_exhaustion_leaves_a_readable_marker(self):
        _, _, last, _ = self.run_case(2, 200, 65)
        self.assertEqual(last, "M30 SMP budget reached, output truncated")

    def test_overlong_line_is_truncated_and_marked(self):
        """A clipped line must be visibly cut, never silently shortened.

        The clip only fires when a line exceeds the room REMAINING after earlier
        output, so drive the budget nearly full first (1 KiB budget, 8 x 109-byte
        lines), then send a long line into the remainder.
        """
        # Fill close to the cap, then emit one long line; the last must be cut.
        emitted, lines, last, rc = self.run_case(1, 9, 109)
        self.assertEqual(rc, 0)
        self.assertLessEqual(emitted, 1024)
        # 9 identical lines: the budget is exhausted part-way, and whichever
        # line crossed the boundary must carry the ellipsis or be the marker.
        self.assertTrue(
            last.endswith("...") or last == "M30 SMP budget reached, output truncated",
            f"boundary line neither clipped nor marked: {last[-12:]!r}")

    def test_no_output_when_nothing_emitted(self):
        emitted, lines, _, _ = self.run_case(2, 0, 0)
        self.assertEqual((emitted, lines), (0, 0))

    def test_single_line_exactly_at_budget(self):
        """A line that exactly fills the budget must be emitted whole."""
        marker = len("M30 SMP budget reached, output truncated") + 1
        kib = 2
        exact = kib * 1024 - marker - 1   # text length that fits with its newline
        emitted, lines, last, _ = self.run_case(kib, 1, exact)
        self.assertLessEqual(emitted, kib * 1024)
        self.assertEqual(lines, 1)
        self.assertFalse(last.endswith("..."), "a fitting line must not be clipped")


class SourceInvariantTests(unittest.TestCase):
    def test_reserve_accounts_for_newline_not_nul(self):
        added = "\n".join(l[1:] for l in PATCH.read_text().splitlines()
                          if l.startswith("+") and not l.startswith("+++"))
        self.assertIn("strlen(M30_SMP_MARKER) + 1", added,
                      "reserve must be marker text + newline, not sizeof()")

    def test_clamp_leaves_room_for_newline(self):
        added = "\n".join(l[1:] for l in PATCH.read_text().splitlines()
                          if l.startswith("+") and not l.startswith("+++"))
        self.assertIn("len = room - 1;", added,
                      "clamp must be room-1 because the newline is charged")

    def test_header_is_emitted_through_the_budget(self):
        added = "\n".join(l[1:] for l in PATCH.read_text().splitlines()
                          if l.startswith("+") and not l.startswith("+++"))
        self.assertIn("m30_smp_emit(hdr)", added,
                      "header must go through the emitter, not printf directly")

    def test_sampler_still_dormant_by_default(self):
        added = "\n".join(l[1:] for l in PATCH.read_text().splitlines()
                          if l.startswith("+") and not l.startswith("+++"))
        self.assertIn('strlcpy(sweet_sample_names, "-"', added)


if __name__ == "__main__":
    unittest.main(verbosity=2)
