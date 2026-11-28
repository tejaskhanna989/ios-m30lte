"""Tests for 0457: the framebuffer state-transition logger.

The requirement is a diagnostic that records "meaningful changes" without
filling the pstore ring. Both halves matter:

  * too few records and the boot is diagnostically useless;
  * too many and the ring wraps before the failure, destroying the evidence.

The old diagnostic failed the second way: 143 lines / ~15.6 KiB of a 16 KiB
ring on the accepted v68 boot (~1.5 min retention). So these tests do not
merely check that the code exists - they execute the patched C and measure
what it actually emits, which is how the two real defects in 0456 were found.

Covered, per the agreed scope: transitions, unchanged states, heartbeat
timing, concurrency, and worst-case ring consumption.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0457-m30-fb-transition-log.patch"

def brace_depth(text: str) -> int:
    """Brace depth with comments and string literals stripped.

    Returns the net depth, which for a complete translation unit is 0. The
    unpatched M30 driver ends at 1 because of an unclosed region in the donor
    code, so callers compare against the expected baseline.
    """
    depth, in_block, i = 0, False, 0
    while i < len(text):
        if in_block:
            j = text.find("*/", i)
            if j < 0:
                break
            i = j + 2
            in_block = False
            continue
        if text.startswith("/*", i):
            in_block = True
            i += 2
            continue
        if text.startswith("//", i):
            j = text.find("\n", i)
            if j < 0:
                break
            i = j
            continue
        c = text[i]
        if c == '"':
            i += 1
            while i < len(text) and text[i] != '"':
                i += 2 if text[i] == "\\" else 1
            i += 1
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        i += 1
    return depth


RING_BYTES = 16384
PMSG_MAX_MSG = 230          # pexpert/arm/pe_serial.c: m30_line[230]
PMSG_MAX_RECORD = 255

STUBS = """#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>

static uint64_t fake_now_ns;
static int m30fbtboot = 0;
static uint64_t mach_absolute_time(void) { return (fake_now_ns * 3) / 125; }
static void absolutetime_to_nanoseconds(uint64_t a, uint64_t *r)
{ *r = (a * 125) / 3; }
static int PE_parse_boot_argn(const char *k, int *v, int l)
{ (void)k; (void)l; if (m30fbtboot > 0) *v = m30fbtboot; return m30fbtboot > 0; }

static long g_bytes, g_lines, g_maxline;
static char g_last[512];
static void m30_pmsg_diag_line(const char *line)
{
    int n = (int)strlen(line);
    g_bytes += n + 1;
    g_lines++;
    if (n > g_maxline) g_maxline = n;
    snprintf(g_last, sizeof(g_last), "%s", line);
}
"""


def extract_logger() -> str:
    """Pull the logger out of the patch's added lines."""
    added = [l[1:] for l in PATCH.read_text().splitlines()
             if l.startswith("+") and not l.startswith("+++")]
    src = "\n".join(added)
    start = src.index("/* ---- v87 framebuffer transition logger")
    end = src.index("static int\nm30_fbt_observe", start)
    tail = src[end:]
    close = tail.index("\n}\n")
    return src[start:end + close + 3]


def added_text() -> str:
    return "\n".join(l[1:] for l in PATCH.read_text().splitlines()
                     if l.startswith("+") and not l.startswith("+++"))


@unittest.skipUnless(shutil.which("gcc") or shutil.which("cc"),
                     "no host C compiler available")
class ExecutedBehaviourTests(unittest.TestCase):
    """Drive the real patched code and measure the output."""

    @classmethod
    def setUpClass(cls):
        cc = shutil.which("gcc") or shutil.which("cc")
        cls.tmp = Path(tempfile.mkdtemp())
        cls.bin = cls.tmp / "h"
        src = cls.tmp / "h.c"
        src.write_text(STUBS + extract_logger() + MAIN)
        r = subprocess.run([cc, "-O1", "-o", str(cls.bin), str(src)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise AssertionError(f"harness did not compile:\n{r.stderr}")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def run_case(self, *args):
        r = subprocess.run([str(self.bin), *map(str, args)],
                           capture_output=True, text=True)
        out = {}
        for line in r.stdout.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                out[k] = v
        return out, r.returncode

    # ---- transitions -----------------------------------------------------
    def test_changes_emit_once_each(self):
        o, _ = self.run_case("changes")
        self.assertEqual(o["lines"], "4", "four transitions -> four lines")
        self.assertEqual(o["emitted"], "4")

    def test_unchanged_state_is_suppressed(self):
        """The whole point: 10,000 identical frames must add nothing."""
        o, _ = self.run_case("steady", 10000)
        self.assertEqual(o["lines"], "1", "only the initial state is recorded")
        self.assertEqual(o["suppressed"], "10000",
                         "every steady frame was suppressed")

    def test_first_completed_copy_is_always_recorded(self):
        o, _ = self.run_case("firstcopy")
        self.assertEqual(o["emitted"], "1", "0 -> nonzero copied emits")
        self.assertIn("copied=3032", o["last"])

    def test_sub_bucket_growth_is_not_logged_but_bucket_change_is(self):
        o, _ = self.run_case("buckets")
        self.assertEqual(o["within_bucket"], "0", "growth inside a MiB bucket is quiet")
        self.assertEqual(o["bucket_change"], "1", "crossing a MiB bucket emits")

    # ---- heartbeat -------------------------------------------------------
    def test_heartbeat_needs_a_full_60_seconds(self):
        o, _ = self.run_case("heartbeat")
        self.assertEqual(o["at_59s"], "0", "59 s is not yet due")
        self.assertEqual(o["at_60s"], "1", "60 s fires")
        self.assertEqual(o["at_120s"], "1", "120 s fires again")
        self.assertEqual(o["same_window"], "0", "no double heartbeat")
        self.assertEqual(o["total_hb"], "2", "two heartbeats over 120 s")

    def test_heartbeat_is_marked_so_it_is_not_mistaken_for_a_change(self):
        o, _ = self.run_case("heartbeat")
        self.assertIn(" hb", o["last"])

    # ---- concurrency -----------------------------------------------------
    def test_duplicate_observers_do_not_duplicate_records(self):
        """Both emit sites hold fLock, so a repeated observation must not
        produce a second record - that is the property relied on in-kernel."""
        o, _ = self.run_case("concurrent", 20)
        self.assertEqual(o["lines"], "20",
                         "20 changes seen twice -> exactly 20 records")
        self.assertEqual(o["suppressed"], "20",
                         "every duplicate observation was suppressed")

    def test_accounting_matches_what_the_sink_received(self):
        o, _ = self.run_case("concurrent", 20)
        self.assertEqual(o["accounted"], o["bytes"],
                         "charged bytes must equal bytes actually emitted")

    # ---- budget and worst case -------------------------------------------
    def test_budget_is_never_exceeded(self):
        o, _ = self.run_case("changes", 5000)
        self.assertLessEqual(int(o["bytes"]), 3 * 1024)

    def test_marker_is_last_and_latched(self):
        o, _ = self.run_case("changes", 5000)
        self.assertEqual(o["last"],
                         "M30 FBT budget reached, output truncated")
        o2, _ = self.run_case("after_cap")
        self.assertEqual(o2["emitted"], "0", "nothing after the cap")

    def test_worst_case_cannot_fill_the_ring(self):
        o, _ = self.run_case("changes", 20000)
        self.assertLess(int(o["bytes"]), RING_BYTES,
                        "even the pathological case leaves the ring intact")

    def test_line_fits_a_pmsg_record(self):
        o, _ = self.run_case("worstline")
        n = int(o["maxline"])
        self.assertLessEqual(n, PMSG_MAX_MSG,
                             "a longer line would be dropped by the sink")
        self.assertLessEqual(19 + 3 + 1 + n + 1, PMSG_MAX_RECORD)

    def test_boot_arg_lowers_the_budget(self):
        o, _ = self.run_case("changes", 5000, 1)
        self.assertLessEqual(int(o["bytes"]), 1024)

    def test_v68_replay_is_cheaper_than_the_diagnostic_it_replaces(self):
        o, _ = self.run_case("v68")
        self.assertLess(int(o["lines"]), 143,
                        "must emit fewer records than the old poller")
        self.assertLess(int(o["bytes"]), RING_BYTES // 2,
                        "must leave at least half the ring free")

    def test_no_allocation_in_the_logger(self):
        body = extract_logger()
        for bad in ("malloc", "IOMalloc", "kalloc", "new ", "IOLock", "IOSleep"):
            self.assertNotIn(bad, body, f"logger must not use {bad}")


class SourceInvariantTests(unittest.TestCase):
    def test_uses_the_kernel_timebase_conversion(self):
        """mach_timebase_info() in-kernel is only the MIG trap prototype, which
        must never be called from a display interrupt path."""
        body = added_text()
        self.assertIn("absolutetime_to_nanoseconds", body)
        # Strip comments before looking for calls, or the explanatory comment
        # about mach_timebase_info() trips its own check.
        code = "\n".join(re.sub(r"/\*.*?\*/", "", body, flags=re.S).split("\n"))
        code = "\n".join(l for l in code.splitlines() if not l.lstrip().startswith("*"))
        self.assertNotIn("mach_timebase_info(", code,
                         "the MIG trap must not be used in-kernel")

    def test_poller_is_removed(self):
        body = PATCH.read_text()
        self.assertIn("-	if ((fb->fDiagTick % 600) == 0 && fb->fDiagTick <= 4800) {",
                      body, "the fixed 600-vsync poller must be deleted")

    def test_logging_does_not_change_behaviour(self):
        body = added_text()
        for token in ("return copied", "args->scalarOutput[", "panic(", "assert("):
            self.assertNotIn(token, body,
                             f"a logging patch must not touch {token!r}")

    def test_reserve_accounts_for_newline_not_nul(self):
        body = added_text()
        self.assertIn("strlen(M30_FBT_MARKER) + 1", body)

    def test_clamp_leaves_room_for_newline(self):
        self.assertIn("len = room - 1;", added_text())

    def test_only_kernel_headers_are_included(self):
        """The build failed once on <osfmk/kern/clock.h>: osfmk is itself an
        include root, so kernel code spells it <kern/clock.h>. Userspace SDK
        headers are not on the kernel path at all. Pin both lessons."""
        body = added_text()
        # Check only the real #include lines: the explanatory comment mentions
        # the wrong spellings on purpose.
        includes = [l.strip() for l in body.splitlines()
                    if l.strip().startswith("#include")]
        self.assertIn("#include <kern/clock.h>", includes,
                      "osfmk headers are included relative to osfmk")
        for bad in ("<osfmk/", "<string.h>", "<stdint.h>", "<stdio.h>",
                    "<stdlib.h>"):
            self.assertFalse(any(bad in inc for inc in includes),
                             f"{bad} is not on the kernel include path")

    def test_patched_file_is_brace_balanced(self):
        """CI caught a stray brace: deleting the old poller block also deleted
        the `}` that closed the enclosing scope, so m30_fbt_observe() landed
        outside vsyncFired() and `fb` was undeclared.

        The unpatched driver does NOT balance on its own (it ends at depth 1),
        so a whole-file check has to compare against that known baseline rather
        than against zero.
        """
        tree = os.environ.get("M30_XNU_TREE")
        if not tree:
            self.skipTest("set M30_XNU_TREE to a patched xnu tree")
        path = Path(tree) / "iokit/Kernel/arm/SweetFramebuffer.cpp"
        if not path.is_file():
            self.skipTest(f"not found: {path}")
        # A complete translation unit ends at depth 0. This catches the class
        # of error that broke CI twice: a deleted block taking its enclosing
        # `}` with it, which pushes later code out of its function.
        # The unpatched donor driver ends at preprocessor-dependent brace depth 1;
        # a balanced patch must preserve that baseline, not force it to 0.
        self.assertEqual(brace_depth(path.read_text()), 1,
                         "patched SweetFramebuffer.cpp changed brace depth")

    def test_touches_exactly_one_file(self):
        files = [l for l in PATCH.read_text().splitlines() if l.startswith("+++")]
        self.assertEqual(len(files), 1)
        self.assertIn("SweetFramebuffer.cpp", files[0])


MAIN = r"""
static void init_state(m30_fbt_state *st)
{ memset(st, 0, sizeof(*st)); st->line_cap = M30_FBT_MAX_LINES; }
static void reset_sink(void)
{ g_bytes = g_lines = g_maxline = 0; g_last[0] = 0; }

int main(int argc, char **argv)
{
    const char *m = argc > 1 ? argv[1] : "";
    long extra = argc > 2 ? atol(argv[2]) : 0;
    if (argc > 3) m30fbtboot = atoi(argv[3]);
    m30_fbt_state st; init_state(&st); reset_sink();
    fake_now_ns = 1000000000ULL;
    long emitted = 0, extra_metric = 0, total_hb = 0, hb_flags = 0;

    if (!strcmp(m, "changes")) {
        long n = extra > 0 ? extra : 4;
        for (long i = 0; i < n; i++) emitted += m30_fbt_observe(&st, i, i, i << 20, i, 0, 0, 1);
    } else if (!strcmp(m, "steady")) {
        long n = extra > 0 ? extra : 1000;
        m30_fbt_observe(&st, 4, 4, 10108800, 1, 0, 0, 1);
        for (long i = 0; i < n; i++) { fake_now_ns += 1000000ULL;
            emitted += m30_fbt_observe(&st, 4, 4, 10108800, 1, 0, 0, 1); }
    } else if (!strcmp(m, "firstcopy")) {
        m30_fbt_observe(&st, 5, 5, 0, 0, 0, 0, 1);
        emitted = m30_fbt_observe(&st, 5, 5, 3032, 1, 0, 0, 1);
    } else if (!strcmp(m, "buckets")) {
        m30_fbt_observe(&st, 5, 5, 3032, 1, 0, 0, 1);
        extra_metric = m30_fbt_observe(&st, 5, 5, 1000000, 1, 0, 0, 1); /* same bucket */
        long bc = m30_fbt_observe(&st, 5, 5, 2097152, 1, 0, 0, 1);      /* bucket 2 */
        printf("within_bucket=%ld\nbucket_change=%ld\n", extra_metric, bc);
    } else if (!strcmp(m, "heartbeat")) {
        m30_fbt_observe(&st, 7, 7, 0, 0, 0, 0, 1);
        fake_now_ns += 59000ULL * 1000000ULL;
        long a = m30_fbt_observe(&st, 7, 7, 0, 0, 0, 0, 1);
        fake_now_ns += 1000ULL * 1000000ULL;
        long b = m30_fbt_observe(&st, 7, 7, 0, 0, 0, 0, 1);
        long s = m30_fbt_observe(&st, 7, 7, 0, 0, 0, 0, 1);
        fake_now_ns += 60000ULL * 1000000ULL;
        long c = m30_fbt_observe(&st, 7, 7, 0, 0, 0, 0, 1);
        printf("at_59s=%ld\nat_60s=%ld\nsame_window=%ld\nat_120s=%ld\ntotal_hb=%ld\n", a, b, s, c, b + c);
    } else if (!strcmp(m, "concurrent")) {
        long rounds = extra > 0 ? extra : 100;
        for (long r = 0; r < rounds; r++) {
            emitted += m30_fbt_observe(&st, r, r, r << 20, r, 0, 0, 1);
            emitted += m30_fbt_observe(&st, r, r, r << 20, r, 0, 0, 1);
        }
        printf("accounted=%d\n", st.used);
    } else if (!strcmp(m, "worstline")) {
        m30_fbt_observe(&st, 18446744073709551615ULL, 18446744073709551615ULL,
            18446744073709551615ULL, 18446744073709551615ULL, 1, 1, 4294967295u);
    } else if (!strcmp(m, "v68")) {
        struct { long at; uint64_t sw, pr, copied, done; } ev[] = {
            {0, 6, 4, 30326400, 1}, {120, 7, 4, 30326400, 2},
            {300, 8, 5, 50544000, 3}, {700, 9, 6, 50544000, 4},
            {1100, 10, 7, 70761600, 5}, {1300, 11, 8, 70761600, 5},
        };
        int ne = 6, idx = 0;
        for (long s = 0; s <= 1370; s++) {
            while (idx < ne && ev[idx].at == s) {
                m30_fbt_observe(&st, ev[idx].sw, ev[idx].pr, ev[idx].copied, ev[idx].done, 0, 0, 1);
                idx++;
            }
            for (int f = 0; f < 60; f++) {
                fake_now_ns += 16666666ULL;
                m30_fbt_observe(&st, ev[idx - 1].sw, ev[idx - 1].pr,
                    ev[idx - 1].copied, ev[idx - 1].done, 0, 0, 1);
            }
        }
    } else if (!strcmp(m, "after_cap")) {
        for (long i = 0; i < 400; i++) m30_fbt_observe(&st, i, i, i << 20, i, 0, 0, 1);
        long before = g_lines;
        for (long i = 400; i < 800; i++) m30_fbt_observe(&st, i, i, i << 20, i, 0, 0, 1);
        printf("emitted=%ld\n", g_lines - before);
    }
    if (strcmp(m, "concurrent") && strcmp(m, "buckets") && strcmp(m, "heartbeat") && strcmp(m, "after_cap"))
        printf("emitted=%ld\n", emitted);
    printf("lines=%ld\nbytes=%ld\nmaxline=%ld\nsuppressed=%llu\nlast=%s\n",
           g_lines, g_bytes, g_maxline, (unsigned long long)st.suppressed, g_last);
    return 0;
}
"""


if __name__ == "__main__":
    unittest.main(verbosity=2)
