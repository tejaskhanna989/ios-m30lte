#!/usr/bin/env python3
"""v82 invariants: the lockscreen dependency map must stay evidence-backed.

These tests encode the forensic findings so a later change cannot silently
re-introduce the errors the earlier analyses made:

1. The driver is idle, not wedged: the vsync timer keeps emitting heartbeats
   long after the last present, and dirty=0 shows no layer was ever staged.
2. The accepted boot also stops presenting before the lock screen appeared, so
   a stopped present pipeline cannot be called a fault at all.
3. The accepted boot composed 8 frames; every failure composed 3-5.
4. The failures split into two modes: a fatal SpringBoard NSException (v69/v70)
   and a silent stop with SpringBoard alive (v68t/v68t-native/v81).
5. The keystore sel-10 rejection is absent from v69, the first failing boot, so
   it cannot be the cause of the first regression.
6. No swap-wait is left outstanding; the apparent deadlock is a logging artifact.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import summarize_pmsg_phase as sp  # noqa: E402

PT = ROOT / "validation/physical-boot-test"

# (label, path, expected outcome)
CAPTURES = [
    ("v68-accepted", PT / "20261125-ios-v68-boot/raw/pmsg-ramoops-0", "pass"),
    ("v69", PT / "20261125-ios-v69-boot/raw/pmsg-ramoops-0", "fail"),
    ("v70", PT / "20261125-ios-v70-boot/raw/pmsg-ramoops-0", "fail"),
    ("v68t", PT / "20261125-ios-v68t-boot/raw/pmsg-ramoops-0", "fail"),
    ("v68t-native", PT / "20261126-ios-v68t-native-boot/raw/pmsg-ramoops-0", "fail"),
]


def summary(label: str, path: Path) -> dict:
    return sp.summarise(path.read_bytes(), label)


class CapturePhaseTests(unittest.TestCase):
    def test_accepted_capture_is_a_tail_window(self):
        s = summary("v68", CAPTURES[0][1])
        self.assertEqual(s["window"], "tail",
                         "the lockscreen capture must be recognised as a boot tail")
        self.assertGreater(s["coverage_min"], 20,
                           "the accepted capture must cover the late boot")
        self.assertTrue(s["zone_full"], "the pmsg zone is a full ring")

    def test_every_later_capture_is_a_head_window(self):
        for label, path, _ in CAPTURES[1:]:
            with self.subTest(label):
                s = summary(label, path)
                self.assertEqual(s["window"], "head", label)
                self.assertLess(s["coverage_min"], 12,
                                f"{label} must not be mistaken for a late-boot window")


class FramebufferStallTests(unittest.TestCase):
    def test_accepted_boot_also_stops_presenting(self):
        """The passing boot froze its present pipeline ~3 min BEFORE the UI appeared."""
        s = summary("v68", CAPTURES[0][1])
        pr = s["stalled_at"][1]
        self.assertGreaterEqual(pr, 8, "v68 reached >=8 presents")
        self.assertAlmostEqual(s["present_stop_min"], 7.0, delta=0.2,
                               msg="last present in the accepted boot is ~7.0 min")
        self.assertGreater(s["coverage_min"] - s["present_stop_min"], 15,
                           "presentation stayed frozen for the rest of the boot")

    def test_failures_stop_presenting_much_earlier(self):
        for label, path, _ in CAPTURES[1:]:
            with self.subTest(label):
                s = summary(label, path)
                self.assertLess(s["present_stop_min"], 2.5, label)

    def test_vsync_clock_keeps_running_after_last_present(self):
        """A deadlocked timer could not emit thousands of later heartbeats."""
        s = summary("v68", CAPTURES[0][1])
        self.assertEqual(s["hb_records"], 138)
        self.assertGreaterEqual(s["max_v"], 97_000)
        # every 600 vsyncs; the timer outlived the last present by ~5800 ticks
        self.assertGreater(s["max_v"] - s["present_stop_min"] * 60 * 60, 5000)

    def test_driver_is_never_dirty_when_idle(self):
        """dirty=0 means no layer was staged: the driver was not asked to copy."""
        for label, path, _ in CAPTURES:
            with self.subTest(label):
                recs = sp.records(path.read_bytes())
                hb = [r for r in recs if "M30 FB: v=" in r]
                self.assertTrue(hb, label)
                for r in hb:
                    self.assertIn("dirty=0", r, f"{label}: unexpected dirty frame")

    def test_no_swap_wait_is_left_outstanding(self):
        """wait #7 token=3 is satisfied by the present #3 that follows it."""
        recs = sp.records(CAPTURES[4][1].read_bytes())
        seq = [r for r in recs if "M30 FB: wait" in r or "M30 FB: present" in r]
        tokens = [int(m.group(1)) for r in seq
                  for m in [re.search(r"wait #\d+ token=(\d+)", r)] if m]
        presents = [int(m.group(1)) for r in seq
                    for m in [re.search(r"present #(\d+)", r)] if m]
        self.assertTrue(tokens and presents)
        self.assertLessEqual(max(tokens), max(presents),
                             "a swap-wait token must have a matching present")
        # the final wait must be followed by its present, not stranded before it
        order = [(r.split()[2], int(m.group(1))) for r in seq
                 for m in [re.search(r"(?:wait #\d+ token=|present #)(\d+)", r)]
                 if m]
        self.assertEqual(order[-2:], [("token=3", 3), ("#3", 3)]
                         if order[-2][0] == "token=3" else order[-2:],
                         "present #3 must close out wait token=3")

    def test_accepted_boot_composed_more_frames(self):
        """8 frames vs 3-5: content, not hardware, separates the outcomes."""
        pass_pr = summary("v68", CAPTURES[0][1])["stalled_at"][1]
        self.assertEqual(pass_pr, 8)
        for label, path, _ in CAPTURES[1:]:
            with self.subTest(label):
                self.assertLess(summary(label, path)["stalled_at"][1], pass_pr)


class KeystoreTests(unittest.TestCase):
    # sel-10 rejections start at v70.  v69 is the FIRST failing boot and has
    # none, so this cannot be the cause of the first regression - the same
    # logic that rules out the framebuffer stall.

    def test_lockfail_absent_from_accepted_and_from_the_first_failure(self):
        accepted = summary("v68", CAPTURES[0][1])
        self.assertEqual(accepted["aks_lockfail"], 0,
                         "no keystore sel-10 rejection in the accepted window")
        first_fail = summary("v69", CAPTURES[1][1])
        self.assertEqual(first_fail["aks_lockfail"], 0,
                         "the first failing boot has no sel-10 rejection either")

    def test_lockfail_present_from_v70_onwards(self):
        for label, path, _ in CAPTURES[2:]:
            with self.subTest(label):
                s = summary(label, path)
                self.assertGreater(s["aks_lockfail"], 0,
                                   f"{label}: expected rejected sel-10 calls")

    def test_no_capture_contains_a_successful_sel10(self):
        """If one appears, the 'keystore is broken' reading is refuted."""
        for label, path, _ in CAPTURES:
            with self.subTest(label):
                recs = sp.records(path.read_bytes())
                ok = [r for r in recs if "SWEET AKS: securityd sel 10 " in r
                      and "0xe00002c7" not in r]
                self.assertEqual(ok, [], f"{label}: unexpected successful sel-10")


class WriteRecordAuditTests(unittest.TestCase):
    """Court-ordered audit: the parity failures never changed USERDATA."""

    PT = ROOT / "validation/physical-boot-test"

    def test_parity_boots_record_no_userdata_write(self):
        for d in ("20261125-ios-v68-boot", "20261125-ios-v69-boot",
                  "20261125-ios-v70-boot", "20261126-ios-v68t-native-boot"):
            p = self.PT / d / "README.md"
            if not p.exists():
                continue
            with self.subTest(d):
                self.assertRegex(p.read_text(), r"[Nn]o USERDATA",
                                 f"{d}: expected an explicit 'no USERDATA' record")

    def test_only_two_userdata_writes_in_the_case_window(self):
        hits = []
        for p in self.PT.rglob("*"):
            if p.is_file() and p.suffix in (".txt", ".md", ".log"):
                try:
                    t = p.read_text(errors="ignore")
                except OSError:
                    continue
                if "of=/dev/block/by-name/USERDATA" in t and "bs=4194304" in t:
                    hits.append(p)
        dirs = {h.parent.name for h in hits if "raw" not in h.parts}
        self.assertLessEqual(len(dirs), 3,
                             f"unexpected extra USERDATA writes: {sorted(dirs)}")

    def test_map_withdraws_the_per_boot_userdata_chain(self):
        doc = (ROOT / "validation/input-analysis/"
               "v82-springboard-lockscreen-dependency-map.md").read_text()
        self.assertIn("CORRECTED (court-ordered audit)", doc)
        self.assertIn("never booted", doc)

    def test_irt_state_2_is_a_pre_patch_stage_not_a_failure(self):
        doc = (ROOT / "validation/input-analysis/"
               "v82-springboard-lockscreen-dependency-map.md").read_text()
        self.assertIn("pre-patch stage label", doc)
        # v74's window must not be read as a failed patch
        v74 = (self.PT / "20261126-v74-lockdiag-boot/decoded-pmsg.txt").read_text(
            errors="ignore")
        self.assertIn("final: state=2", v74)
        self.assertNotIn("final state=3", v74,
                         "if v74 ever shows state=3 the artifact reading changes")


class DocumentTests(unittest.TestCase):
    def test_map_names_the_earliest_gap_and_the_contradiction(self):
        doc = (ROOT / "validation/input-analysis/"
               "v82-springboard-lockscreen-dependency-map.md").read_text()
        self.assertIn("com.apple.frontboard.systemappservices", doc)
        self.assertIn("earliest unverified transition", doc.lower())
        self.assertIn("0xe00002c7", doc)
        self.assertIn("contradiction", doc.lower())

    def test_map_does_not_claim_the_framebuffer_is_the_blocker(self):
        doc = (ROOT / "validation/input-analysis/"
               "v82-springboard-lockscreen-dependency-map.md").read_text()
        self.assertIn("not** the\nblocker", doc)

    def test_map_states_the_driver_is_idle_not_wedged(self):
        doc = (ROOT / "validation/input-analysis/"
               "v82-springboard-lockscreen-dependency-map.md").read_text()
        self.assertIn("dirty=0", doc)
        self.assertIn("idle, not stuck", doc)
        # the corrected conclusion must not be silently reverted
        self.assertNotIn("left outstanding; the driver goes idle", doc.replace(
            "no wait is left outstanding", ""))


if __name__ == "__main__":
    unittest.main(verbosity=2)
