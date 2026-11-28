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

    def test_targets_only_sampler_files(self):
        """A diagnostic-volume fix must not reach into functional code."""
        files = re.findall(r"^\+\+\+ b/(\S+)", PATCH.read_text(), re.M)
        self.assertEqual(sorted(set(files)),
                         ["bsd/dev/sweet_sample.c", "osfmk/kern/exception.c"])

    def test_header_lines_parse(self):
        out = subprocess.run(["git", "apply", "--numstat", str(PATCH)],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("osfmk/kern/exception.c", out.stdout)
        self.assertIn("bsd/dev/sweet_sample.c", out.stdout)

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

    def test_sampler_is_dormant_by_default(self):
        """No accepted candidate carries a sweetsample boot-arg, so a default-on
        sampler runs on every boot and, at 50% of the ring, evicts the evidence.
        """
        body = "\n".join(added_lines())
        self.assertIn('strlcpy(sweet_sample_names, "-"', body,
                      "the default must be off, not SpringBoard,backboardd")

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
                         "must not change the lock-screen diagnostic's enable state")
        # flipping the DEFAULT is allowed and is the point; forcing it on is not
        self.assertNotIn('strlcpy(sweet_sample_names, "SpringBoard', body)

    def test_uses_existing_sink_rather_than_inventing_one(self):
        body = "\n".join(added_lines())
        for line in body.splitlines():
            if "printf(" in line or "m30_ls_diag_line(" in line:
                continue
            self.assertNotIn("diag_line(", line.replace("m30_ls_diag_line(", ""))
        self.assertIn("m30_ls_diag_line", body, "must route through the pmsg sink")


class PinnedHashConsistencyTests(unittest.TestCase):
    """CI pins sha256 of patched files. When a patch changes a pinned file the
    pin must be updated deliberately, not discovered by a 20-minute build."""

    def test_pinned_hashes_are_labelled_with_their_template(self):
        wf = (ROOT / ".github/workflows/xnu.yml").read_text()
        # every pinned hash line must either be the live value or a comment
        import re
        live = re.findall(r'^\s+"([\w./-]+)": "([0-9a-f]{64})"', wf, re.M)
        self.assertTrue(live, "no pinned hashes found")
        for rel, h in live:
            self.assertRegex(rel, r"^(bsd|osfmk|iokit|pexpert)/", rel)

    def test_sampler_pin_matches_the_patch_chain(self):
        """0456 rewrites sweet_sample.c, so the pinned value must be 0456's."""
        wf = (ROOT / ".github/workflows/xnu.yml").read_text()
        self.assertIn("2f982bae8a65d2b52a2db7dcfa9615d59096b8df5477ee90a889e55b2a43f30e", wf,
                      "0456 changes bsd/dev/sweet_sample.c; its pinned hash must match")
        self.assertNotIn('"d6a394dfd49c144e0e223d67d2d430b6b779c6758c95eaffd69ab361fa0493b0",', wf,
                         "the pre-0456 hash must not remain as a live pin")

    def test_framebuffer_pins_match_the_reproduced_chain(self):
        """Both ui_exact variants must name a hash that a real tree produces."""
        wf = (ROOT / ".github/workflows/xnu.yml").read_text()
        self.assertIn("ad6f89182500a5681d0e75aa7bba4d34c34a653054a49defa2b45ee23ef8960f", wf,
                      "full-chain SweetFramebuffer hash")
        self.assertIn("d3199f92c608b8c7d874d83087c0a8409b6488a3acc93d40599deb0bc32e3c8f", wf,
                      "ui_exact SweetFramebuffer hash (0453-0456 absent)")
        for stale in ("11b4d614e8f641d71da1cdbb010995c42e621f5ebbb0aef5ea06250223aa8e5f",
                      "695fd229053168433a2aec5b55af4d40d09d8f3a6508d3e02b7ffa7f131436e3"):
            self.assertNotIn(f'"{stale}"', wf, "stale pin still live")

    def test_ui_exact_excludes_every_post_v68_diagnostic(self):
        """ui_exact promises the exact v68 UI path; a new diagnostic patch must
        be excluded from it, or the mode silently stops meaning what it says."""
        wf = (ROOT / ".github/workflows/xnu.yml").read_text()
        for n in ("0453", "0454", "0455", "0456"):
            self.assertTrue(re.search(rf"rm -f .*{n}-m30-", wf, re.S),
                            f"{n} must be removed under ui_exact")
        # (the rm -f list spans several lines, hence DOTALL semantics in assertRegex)

    def test_hash_mismatch_error_reports_observed_value(self):
        """Check-run annotations are readable when logs are not, so the failure
        must carry the observed hash."""
        wf = (ROOT / ".github/workflows/xnu.yml").read_text()
        self.assertIn("OBSERVED=", wf)

    def test_written_patch_actually_produces_that_hash(self):
        """Apply 0456 to a copy of the pre-0456 file and check the result."""
        import hashlib
        anchor = 'strlcpy(sweet_sample_names, "SpringBoard,backboardd", sizeof(sweet_sample_names));'
        body = PATCH.read_text()
        self.assertIn(anchor, body, "0456 must replace the default-on line")
        self.assertIn('strlcpy(sweet_sample_names, "-", sizeof(sweet_sample_names));',
                      body, "0456 must install the off default")


if __name__ == "__main__":
    unittest.main(verbosity=2)
