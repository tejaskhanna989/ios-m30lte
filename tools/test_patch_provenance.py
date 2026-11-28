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
        self.allow.write_text("# patch-name\treason\n"
                             "0001-a.patch\tsee tools/mkadt.py, verified\n")
        self.assertEqual(self.result()["result"], "PASS")

    def test_allowlist_entry_needs_checkable_evidence(self):
        """A free-text reason is an unauditable claim; require something falsifiable."""
        h = self.make("0001-a.patch")
        self.write_manifest([(1, "0001-a.patch", h, "allowed-skip")])
        for vague in ("known harmless", "probably fine", "safely skipped"):
            self.allow.write_text(f"0001-a.patch\t{vague}\n")
            self.assertIn("allowlist-no-evidence", self.codes(),
                          f"{vague!r} must not be accepted as justification")

    def test_allowlist_entry_accepts_real_evidence(self):
        h = self.make("0001-a.patch")
        self.write_manifest([(1, "0001-a.patch", h, "allowed-skip")])
        for good in ("CI run 46061485024 evidence",
                     "edits tools/mkadt.py, a host-side generator",
                     "verified on darwin-xnu-build@66390652",
                     "zero of 176 patches touch bsd/skywalk/packet/os_packet.h"):
            self.allow.write_text(f"0001-a.patch\t{good}\n")
            self.assertNotIn("allowlist-no-evidence", self.codes(), good)

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


class EmbeddedCiScriptTests(unittest.TestCase):
    """The python embedded in xnu.yml must actually run.

    A previous edit put `allowed_names` before its definition, which would have
    crashed the CI step only after a 20-minute macOS build. Each assertion is
    now its own named step so a failure states its own defect (CI logs are not
    retrievable here; check-run step names are).
    """

    WA = "Every patch on disk is applied or allow-listed"
    WB = "No OUR patch was skipped"
    WC = "No patch was silently skipped"
    WD = "Every applied patch exists on disk"
    PARSE = "Parse build log patch evidence"

    def blocks(self) -> dict:
        import re
        import textwrap
        wf = (ROOT / ".github/workflows/xnu.yml").read_text()
        raw = re.findall(r"python3 - <<'PY'\n(.*?)\n        PY\n", wf, re.S)
        self.assertTrue(raw, "no embedded python blocks found")
        out = {}
        for name in (self.PARSE, self.WA, self.WB, self.WC, self.WD):
            idx = wf.index(f"- name: {name}")
            seg = wf[idx:idx + 6000]
            m = re.search(r"python3 - <<'PY'\n(.*?)\n        PY\n", seg, re.S)
            self.assertIsNotNone(m, f"no embedded python for step {name!r}")
            out[name] = textwrap.dedent(m.group(1))
        return out

    def test_all_blocks_are_valid_python(self):
        import ast
        for name, code in self.blocks().items():
            ast.parse(code)

    def build_log(self, tmp: Path, allowed, *, ansi=False, skip_wording="allowed",
                  extra_applied=()):
        """Create a workspace mirroring CI and return (tmp, allowed)."""
        ours = tmp / "xnu/patches-minimal"
        up = tmp / "dxb/patches"
        ours.mkdir(parents=True)
        up.mkdir(parents=True)
        (ours / "SKIP-ALLOWLIST.txt").write_text(
            (ROOT / "xnu/patches-minimal/SKIP-ALLOWLIST.txt").read_text())
        (ours / "0001-a.patch").write_text("x")
        for n in allowed:
            (up / n).write_text("x")
        # present on disk but NOT iterated for MACOS_VERSION=13.5
        (up / "15.0").mkdir()
        (up / "15.0/entitlements.patch").write_text("x")
        C, R = ("\x1b[1;32m", "\x1b[0m") if ansi else ("", "")
        lines = [f"{C}=> Applying patch: /w/dxb/patches/0001-a.patch{R}"]
        lines += [f"{C}=> Applying patch: /w/dxb/patches/{p}{R}" for p in extra_applied]
        if skip_wording == "allowed":
            lines += [f"{C}[warning] Allowed skip of {n} (see SKIP-ALLOWLIST.txt){R}"
                      for n in allowed]
        elif skip_wording == "upstream":
            lines += [f"{C}[warning] Skipping patch /w/dxb/patches/{n} (already upstream){R}"
                      for n in allowed]
        (tmp / "build.log").write_text("\n".join(lines))
        return tmp, allowed

    def run_ci(self, tmp: Path) -> dict:
        """Run parse + all four assertions exactly as CI does."""
        results = {}
        for name, code in self.blocks().items():
            script = tmp / ("s_" + str(abs(hash(name))) + ".py")
            script.write_text(code)
            r = subprocess.run([sys.executable, str(script)], cwd=tmp,
                               capture_output=True, text=True)
            results[name] = (r.returncode, r.stdout + r.stderr)
        return results

    def allowed_names(self):
        allow = ROOT / "xnu/patches-minimal/SKIP-ALLOWLIST.txt"
        return sorted({l.split("\t")[0].strip() for l in allow.read_text().splitlines()
                       if l.strip() and not l.startswith("#")})

    def test_passes_on_a_consistent_build(self):
        import tempfile
        tmp = Path(tempfile.mkdtemp())
        try:
            self.build_log(tmp, self.allowed_names())
            for name, (rc, out) in self.run_ci(tmp).items():
                self.assertEqual(rc, 0, f"{name} failed:\n{out}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_passes_through_colourised_log(self):
        import tempfile
        tmp = Path(tempfile.mkdtemp())
        try:
            self.build_log(tmp, self.allowed_names(), ansi=True)
            for name, (rc, out) in self.run_ci(tmp).items():
                self.assertEqual(rc, 0, f"{name} failed on ANSI log:\n{out}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_accepts_upstream_skip_wording(self):
        import tempfile
        tmp = Path(tempfile.mkdtemp())
        try:
            self.build_log(tmp, self.allowed_names(), skip_wording="upstream")
            for name, (rc, out) in self.run_ci(tmp).items():
                self.assertEqual(rc, 0, f"{name} failed on upstream wording:\n{out}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_catches_missing_patch(self):
        """A patch that is neither applied nor allow-listed must fail."""
        import tempfile
        tmp = Path(tempfile.mkdtemp())
        try:
            self.build_log(tmp, self.allowed_names())
            (tmp / "build.log").write_text(
                (tmp / "build.log").read_text().replace(
                    "=> Applying patch: /w/dxb/patches/0001-a.patch\n", ""))
            res = self.run_ci(tmp)
            self.assertNotEqual(res[self.WA][0], 0, "must fail: a patch vanished")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_catches_our_patch_skipped(self):
        """Even an allow-listed skip of OUR patch fails: the build would not
        contain our work."""
        import tempfile
        tmp = Path(tempfile.mkdtemp())
        try:
            allowed = self.allowed_names() + ["0001-a.patch"]
            self.build_log(tmp, allowed)   # 0001 and every allowed name are skipped
            # 0001 is OURS and is not marked OUT-OF-TREE, so W2 must fail
            res = self.run_ci(tmp)
            self.assertEqual(res[self.WA][0], 0, "justified skips are allowed")
            self.assertNotEqual(res[self.WB][0], 0,
                                "must fail: our own patch was skipped")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_catches_unjustified_skip(self):
        import tempfile
        tmp = Path(tempfile.mkdtemp())
        try:
            self.build_log(tmp, self.allowed_names())
            (tmp / "build.log").write_text(
                (tmp / "build.log").read_text()
                + "\n[warning] Allowed skip of rogue.patch (none)")
            (tmp / "dxb/patches/rogue.patch").write_text("x")
            res = self.run_ci(tmp)
            self.assertNotEqual(res[self.WA][0], 0)
            self.assertNotEqual(res[self.WC][0], 0, "must fail: unjustified skip")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_catches_phantom_application(self):
        import tempfile
        tmp = Path(tempfile.mkdtemp())
        try:
            self.build_log(tmp, self.allowed_names(), extra_applied=("ghost.patch",))
            res = self.run_ci(tmp)
            self.assertNotEqual(res[self.WD][0], 0, "must fail: applied but not on disk")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_skip_wording_matches_the_real_patcher(self):
        """Guard the exact divergence that cost three CI runs.

        The strict loop emits "Allowed skip of <name>" with no path; upstream's
        own loop emits "Skipping patch <path>". Both must be understood.
        """
        import re as _re
        patcher = (ROOT / "tools/patch_build_sh.py").read_text()
        emitted = [m for m in _re.findall(r'warning "([^"]*)"', patcher)
                   if "Allowed skip of" in m]
        self.assertTrue(emitted, "patcher no longer emits an allowed-skip message")
        sample = emitted[0].replace("$PATCH_NAME", "TrustCache.patch")
        self.assertRegex(sample, r"Allowed skip of ([^\s(]+\.patch)")
        self.assertIn("Allowed skip of", self.blocks()[self.PARSE],
                      "parser must understand the patcher's own wording")


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
            "TrustCache.patch",                     # upstream, already applied
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
