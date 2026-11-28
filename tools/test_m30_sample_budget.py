"""Regression tests for 0456-m30-uihb-ring-budget.patch.

The defect: our process sampler wrote 101-253 byte backtrace lines into a
16384-byte pmsg ring. Measured from our own captures, one sample of
SpringBoard plus backboardd is 29-58 lines, i.e. a quarter to a half of the
ring, so three or four samples evict the framebuffer and SWEET SURF records
that are the actual lock-screen evidence.

These tests pin the properties that make the fix a *diagnostic* change: it
bounds volume, stays read-only, and always leaves a visible marker.
"""
from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0456-m30-uihb-ring-budget.patch"


def added_lines() -> list[str]:
    return [l[1:] for l in PATCH.read_text().splitlines()
            if l.startswith("+") and not l.startswith("+++")]


class SampleBudgetPatchTests(unittest.TestCase):
    def test_patch_exists_and_is_non_empty(self):
        self.assertTrue(PATCH.is_file())
        self.assertGreater(len(added_lines()), 10)

    def test_targets_only_the_sampler(self):
        """A diagnostic-volume fix must not reach into functional code."""
        files = re.findall(r"^\+\+\+ b/(\S+)", PATCH.read_text(), re.M)
        self.assertEqual(files, ["osfmk/kern/exception.c"])

    def test_header_lines_parse(self):
        out = subprocess.run(["git", "apply", "--numstat", str(PATCH)],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("osfmk/kern/exception.c", out.stdout)

    def test_budget_is_configurable_with_a_safe_default(self):
        body = "\n".join(added_lines())
        self.assertIn("m30samplebudget", body, "must be boot-arg controllable")
        m = re.search(r"int m30_sample_budget_kib = (\d+);", body)
        self.assertIsNotNone(m, "default budget must be a literal")
        kib = int(m.group(1))
        # ring is 16 KiB; leave the majority of it for other evidence
        self.assertLessEqual(kib, 4, f"default {kib} KiB crowds out evidence")
        self.assertGreaterEqual(kib, 1, "a zero budget would silence the sampler")
        self.assertIn("m30_sample_budget_kib < 1", body, "must clamp bad input")

    def test_budget_is_enforced_and_accounted(self):
        body = "\n".join(added_lines())
        self.assertIn("m30_sample_bytes > m30_sample_budget_kib * 1024", body)
        # header line and each thread line must both be counted, or the cap
        # under-reports exactly the traffic it exists to bound
        self.assertGreaterEqual(body.count("m30_sample_bytes +="), 2)

    def test_exhaustion_leaves_exactly_one_marker(self):
        """A wrapped ring must never look like a silent sampler."""
        body = "\n".join(added_lines())
        self.assertEqual(body.count("further samples suppressed"), 2,
                         "one marker for the durable sink, one for printf")
        self.assertIn("m30_sample_capped = true", body,
                      "the cap must latch, or the marker repeats every thread")

    def test_stays_read_only(self):
        body = "\n".join(added_lines())
        forbidden = [
            "task_lock(", "task_unlock(", "vm_map_read_user(",
            "mach_header_vm_address =", "slide =", "amtf", "AMFI",
            "exception_deliver", "thread_continue", "kernel_thread_start",
            "PE_parse_boot_args", "panic(", "assert(",
        ]
        for token in forbidden:
            self.assertNotIn(token, body, f"diagnostic patch must not use {token!r}")
        self.assertNotIn("m30_ls_diag_enabled =", body,
                         "must not change the sampler's enable state")

    def test_uses_existing_sink_rather_than_inventing_one(self):
        body = "\n".join(added_lines())
        for line in body.splitlines():
            if "printf(" in line or "m30_ls_diag_line(" in line:
                continue
            self.assertNotIn("diag_line(", line.replace("m30_ls_diag_line(", ""))
        self.assertIn("m30_ls_diag_line", body, "must route through the pmsg sink")


if __name__ == "__main__":
    unittest.main(verbosity=2)
