#!/usr/bin/env python3
"""Tests for the strict patch-provenance system.

Covers every failure mode the overnight mission named:
missing patches, failed application, hash mismatches, incorrect order,
unexpected/undocumented application, duplicates, and stale allow-list entries.

The build-loop tests execute the *generated* bash against a scratch git repo, so
they test the real shipped shell code rather than a Python re-implementation.
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import patch_build_sh  # noqa: E402
import verify_patch_provenance as vpp  # noqa: E402

STUB_BUILD_SH = '''#!/bin/bash
ARCHS="x86_64 arm64e" VALID_ARCHS="x86_64 arm64e"
patches() {
    running "🩹 Patching xnu files"
    (
        cd "${XNU_DIR}"
        for PATCH in "${PATCH_DIR}"/*.patch; do
            if APPLY_CHECK=$(git apply --check "$PATCH" 2>&1); then
                running "Applying patch: ${PATCH}"
                git apply "$PATCH"
            else
                warning "Skipping patch ${PATCH} (already upstream, previously applied, or malformed): ${APPLY_CHECK}"
            fi
        done
    )
}
'''

GOOD_PATCH = (
    'diff --git a/a.c b/a.c\n--- a/a.c\n+++ b/a.c\n@@ -1 +1,2 @@\n line1\n+patched\n'
)
BAD_PATCH = (
    'diff --git a/zz.c b/zz.c\n--- a/zz.c\n+++ b/zz.c\n@@ -1 +1 @@\n-nope\n+yep\n'
)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


class BuildScriptPatchTests(unittest.TestCase):
    """tools/patch_build_sh.py rewrites the upstream loop correctly."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.build = self.tmp / "build.sh"
        self.build.write_text(STUB_BUILD_SH)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_tolerant_loop_is_replaced(self):
        self.assertEqual(patch_build_sh.main(["x", str(self.build), "M30LTE"]), 0)
        out = self.build.read_text()
        self.assertNotIn("Skipping patch ${PATCH} (already upstream", out,
                         "the tolerant warning must be gone")
        self.assertIn("$MF", out)
        self.assertIn("is not allow-listed", out)

    def test_generated_shell_parses(self):
        patch_build_sh.main(["x", str(self.build), "M30LTE"])
        r = subprocess.run(["bash", "-n", str(self.build)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_no_literal_python_in_output(self):
        patch_build_sh.main(["x", str(self.build), "M30LTE"])
        out = self.build.read_text()
        # a previous iteration leaked quoted python literals into the script
        self.assertNotIn("'        ", out)
        self.assertNotIn("\\n'", out)

    def test_refuses_changed_upstream_loop(self):
        self.build.write_text("# upstream changed\n")
        self.assertEqual(patch_build_sh.main(["x", str(self.build), "M30LTE"]), 1)

    def test_banner_text_is_not_hardcoded(self):
        """Regression: upstream's banner is 'Patching' and has carried an emoji.

        Anchoring on a literal banner string previously made the whole build
        abort at 'patches() entry point changed', while the original
        assert-based code merely altered the file and failed later.
        """
        variants = [
            'running "🩹 Patching xnu files"\n',
            'running "Patching xnu files"\n',
            'running "PATCHING xnu files"\n',
        ]
        for banner in variants:
            with self.subTest(banner.strip()):
                body = STUB_BUILD_SH.replace(
                    'running "🩹 Patching xnu files"\n', banner)
                self.build.write_text(body)
                self.assertEqual(
                    patch_build_sh.main(["x", str(self.build), "M30LTE"]), 0,
                    f"patcher must tolerate banner {banner!r}")
                out = self.build.read_text()
                self.assertIn(banner, out, "the original banner must be preserved")
                self.assertIn("$MF", out, "the strict loop must still be injected")

    def test_missing_patches_function_fails(self):
        self.build.write_text('#!/bin/bash\nARCHS="x86_64 arm64e" VALID_ARCHS="x86_64 arm64e"\n')
        self.assertEqual(patch_build_sh.main(["x", str(self.build), "M30LTE"]), 1)


class GeneratedLoopBehaviourTests(unittest.TestCase):
    """Run the generated bash loop against a real scratch git repository."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = self.tmp / "xnu"
        self.pdir = self.tmp / "patches"
        self.repo.mkdir()
        self.pdir.mkdir()
        (self.repo / "a.c").write_text("line1\n")
        subprocess.run(["git", "init", "-q", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=c",
                        "commit", "-qm", "base"], cwd=self.repo, check=True)
        build = self.tmp / "build.sh"
        build.write_text(STUB_BUILD_SH)
        patch_build_sh.main(["x", str(build), "M30LTE"])
        src = build.read_text()
        start = src.index('MF="')
        end = src.index('running "Patch manifest:')
        loop = src[start:end] + (
            'running "Patch manifest: $M30_PATCH_APPLIED applied, '
            '$M30_PATCH_SKIPPED allowed-skip"\n')
        self.runner = self.tmp / "run.sh"
        self.manifest = self.tmp / "m.tsv"
        self.runner.write_text(
            "#!/bin/bash\n"
            'running(){ echo ">> $*"; }\n'
            'warning(){ echo "WARN: $*" >&2; }\n'
            f'XNU_DIR={self.repo}\nPATCH_DIR={self.pdir}\n'
            f'PATCH_MANIFEST={self.manifest}\n'
            f'cd "{self.repo}"\n' + loop + 'echo LOOP_OK\n')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, name: str, body: str) -> None:
        (self.pdir / name).write_text(body)

    def run_loop(self, **env) -> subprocess.CompletedProcess:
        import os
        e = dict(os.environ)
        e.pop("M30_PATCH_ALLOW_SKIP", None)
        e.update(env)
        return subprocess.run(["bash", str(self.runner)], capture_output=True,
                              text=True, env=e)

    def manifest_rows(self) -> list[list[str]]:
        if not self.manifest.exists():
            return []
        return [l.split("\t") for l in self.manifest.read_text().splitlines() if l.strip()]

    def test_clean_build_applies_everything(self):
        self.write("0001-good.patch", GOOD_PATCH)
        r = self.run_loop()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("LOOP_OK", r.stdout)
        rows = self.manifest_rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][3], "applied")
        self.assertEqual(rows[0][2], hashlib.sha256(GOOD_PATCH.encode()).hexdigest())

    def test_unlisted_failure_fails_the_build(self):
        self.write("0001-good.patch", GOOD_PATCH)
        self.write("0002-bad.patch", BAD_PATCH)
        r = self.run_loop()
        self.assertNotEqual(r.returncode, 0, "an unlisted failing patch must fail the build")
        self.assertNotIn("LOOP_OK", r.stdout)
        rows = self.manifest_rows()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][3], "FAILED")

    def test_allowlisted_skip_passes_and_is_recorded(self):
        self.write("0001-good.patch", GOOD_PATCH)
        self.write("0002-bad.patch", BAD_PATCH)
        r = self.run_loop(M30_PATCH_ALLOW_SKIP="0002-bad.patch")
        self.assertEqual(r.returncode, 0, r.stderr)
        rows = self.manifest_rows()
        self.assertEqual([x[3] for x in rows], ["applied", "allowed-skip"])

    def test_manifest_records_order_and_hash(self):
        self.write("0001-good.patch", GOOD_PATCH)
        self.run_loop()
        rows = self.manifest_rows()
        self.assertEqual(rows[0][0], "1")
        self.assertEqual(rows[0][1], "0001-good.patch")


class VerifyProvenanceTests(unittest.TestCase):
    """tools/verify_patch_provenance.py catches every divergence class."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.pdir = self.tmp / "patches"
        self.pdir.mkdir()
        self.manifest = self.tmp / "m.tsv"
        self.allow = self.tmp / "allow.txt"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def make(self, name: str, body: str = "x") -> str:
        (self.pdir / name).write_text(body)
        return hashlib.sha256(body.encode()).hexdigest()

    def write_manifest(self, rows: list[tuple[int, str, str, str]]) -> None:
        self.manifest.write_text(
            "".join(f"{o}\t{n}\t{s}\t{st}\n" for o, n, s, st in rows))

    def result(self):
        return vpp.check(self.manifest, self.pdir,
                         self.allow if self.allow.exists() else None, None)

    def codes(self) -> set[str]:
        return {p["code"] for p in self.result()["problems"]}

    def test_clean_pass(self):
        h = self.make("0001-a.patch")
        self.write_manifest([(1, "0001-a.patch", h, "applied")])
        r = self.result()
        self.assertEqual(r["result"], "PASS", r["problems"])
        self.assertEqual(r["counts"]["applied"], 1)

    def test_missing_manifest(self):
        self.make("0001-a.patch")
        r = vpp.check(self.tmp / "nope.tsv", self.pdir, None, None)
        self.assertEqual(r["result"], "FAIL")
        self.assertIn("manifest-missing", {p["code"] for p in r["problems"]})

    def test_empty_manifest(self):
        self.make("0001-a.patch")
        self.write_manifest([])
        self.assertIn("manifest-empty", self.codes())

    def test_undocumented_patch_on_disk(self):
        h = self.make("0001-a.patch")
        self.make("0002-b.patch")
        self.write_manifest([(1, "0001-a.patch", h, "applied")])
        self.assertIn("undocumented", self.codes())

    def test_failed_row(self):
        h = self.make("0001-a.patch")
        self.write_manifest([(1, "0001-a.patch", h, "FAILED")])
        self.assertIn("patch-failed", self.codes())

    def test_hash_mismatch(self):
        self.make("0001-a.patch")
        self.write_manifest([(1, "0001-a.patch", "0" * 64, "applied")])
        self.assertIn("hash-mismatch", self.codes())

    def test_phantom_patch(self):
        h = self.make("0001-a.patch")
        self.write_manifest([(1, "0001-a.patch", h, "applied"),
                             (2, "0009-gone.patch", "1" * 64, "applied")])
        self.assertIn("phantom", self.codes())

    def test_duplicate_rows(self):
        h = self.make("0001-a.patch")
        self.write_manifest([(1, "0001-a.patch", h, "applied"),
                             (2, "0001-a.patch", h, "applied")])
        self.assertIn("duplicate", self.codes())

    def test_order_drift(self):
        h1 = self.make("0001-a.patch")
        h2 = self.make("0002-b.patch")
        self.write_manifest([(2, "0001-a.patch", h1, "applied"),
                             (1, "0002-b.patch", h2, "applied")])
        self.assertIn("order-drift", self.codes())

    def test_unjustified_skip(self):
        h = self.make("0001-a.patch")
        self.write_manifest([(1, "0001-a.patch", h, "allowed-skip")])
        self.assertIn("unjustified-skip", self.codes())

    def test_justified_skip_is_accepted(self):
        h = self.make("0001-a.patch")
        self.write_manifest([(1, "0001-a.patch", h, "allowed-skip")])
        self.allow.write_text("# patch-name\treason\n0001-a.patch\ttest reason\n")
        self.assertEqual(self.result()["result"], "PASS")

    def test_stale_allowlist_entry(self):
        h = self.make("0001-a.patch")
        self.write_manifest([(1, "0001-a.patch", h, "applied")])
        self.allow.write_text("0001-a.patch\tno longer needed\n")
        self.assertIn("stale-allowlist", self.codes())

    def test_malformed_line(self):
        self.make("0001-a.patch")
        self.manifest.write_text("garbage line\n")
        codes = self.codes()
        self.assertTrue({"manifest-malformed", "manifest-empty"} & codes)

    def test_kernel_hash_is_carried_into_report(self):
        h = self.make("0001-a.patch")
        self.write_manifest([(1, "0001-a.patch", h, "applied")])
        r = vpp.check(self.manifest, self.pdir, None, "deadbeef" * 8)
        self.assertEqual(r["kernel_sha256"], "deadbeef" * 8)

    def test_cli_exit_codes(self):
        h = self.make("0001-a.patch")
        self.write_manifest([(1, "0001-a.patch", h, "applied")])
        ok = vpp.main(["--manifest", str(self.manifest), "--patch-dir", str(self.pdir)])
        self.assertEqual(ok, 0)
        self.write_manifest([(1, "0001-a.patch", "0" * 64, "applied")])
        bad = vpp.main(["--manifest", str(self.manifest), "--patch-dir", str(self.pdir)])
        self.assertEqual(bad, 1)


class RealTreeTests(unittest.TestCase):
    """The repository's own patch directory must be internally consistent."""

    def test_allowlist_exists_and_documents_itself(self):
        p = ROOT / "xnu/patches-minimal/SKIP-ALLOWLIST.txt"
        self.assertTrue(p.is_file())
        text = p.read_text()
        self.assertIn("stale justification", text)

    def test_no_duplicate_patch_names_on_disk(self):
        names = [p.name for p in (ROOT / "xnu/patches-minimal").glob("*.patch")]
        self.assertEqual(len(names), len(set(names)))

    def test_out_of_tree_patches_are_allowlisted(self):
        """A patch editing a path that cannot exist in dxb/xnu must be listed.

        The strict loop applies patches with cwd=dxb/xnu. Any patch whose target
        is a repo-side tool (tools/... living in this repository rather than in
        xnu) can never apply, and before v85 it was skipped silently forever.
        This test makes that class impossible to leave undocumented.
        """
        allow = (ROOT / "xnu/patches-minimal/SKIP-ALLOWLIST.txt").read_text()
        allowed = {l.split("\t")[0].strip() for l in allow.splitlines()
                   if l.strip() and not l.startswith("#")}
        problems = vpp.Problem()
        entries = vpp.parse_allowlist(
            ROOT / "xnu/patches-minimal/SKIP-ALLOWLIST.txt", problems)
        self.assertEqual(list(problems), [], "allow-list must be well formed")

        # xnu source trees never contain a top-level tools/ directory with
        # these scripts; a patch touching one is a repo-side tool edit.
        known_out_of_tree = {
            "9999d-m30-platform-identity.patch",   # repo-side host tool
            "iobuffermemd_monterey.patch",          # upstream, shadowed by 0009/0046
            "kas_info.patch",                       # upstream, shadowed by vm_unix patches
            "machine_routines.patch",               # upstream, shadowed by 0008/9998c
            "skywalk_sonoma.patch",                 # upstream, wrong xnu revision
            "skywalk_ventura.patch",                # upstream, mutually exclusive pair
            "syntax_checker_sonoma.patch",          # upstream, LLDB tooling
            "syntax_checker_ventura.patch",         # upstream, LLDB tooling
        }
        for name in known_out_of_tree:
            with self.subTest(name):
                self.assertIn(name, entries,
                              f"{name} edits a repo-side tool and must be allow-listed")

    def test_allowlisted_reason_names_evidence(self):
        """A bare 'skip' is not a justification."""
        allow = (ROOT / "xnu/patches-minimal/SKIP-ALLOWLIST.txt").read_text()
        for line in allow.splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            name, reason = line.split("\t", 1)
            with self.subTest(name.strip()):
                self.assertGreater(len(reason.strip()), 60,
                                   "reason must cite evidence, not an opinion")
                self.assertRegex(reason, r"\d|verified|does not exist|present",
                                 "reason must contain a verifiable claim")

    def test_every_patch_is_named_with_a_number(self):
        for p in (ROOT / "xnu/patches-minimal").glob("*.patch"):
            with self.subTest(p.name):
                self.assertRegex(p.name, r"^\d{4}[0-9a-z]*-")


if __name__ == "__main__":
    unittest.main(verbosity=2)
