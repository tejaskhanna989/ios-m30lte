#!/usr/bin/env python3
"""v80 regression tests: reconstructed lock-screen regression attribution.

These tests encode the two facts that the physical records fix
(validation/input-analysis/v80-lockscreen-regression-analysis.md):

1. The staging script must produce the proven baseline by default.  The image
   that physically displayed the lock screen (SHA256 5f2e2aa6..., release
   ios-root-20H392-44905109656, commit 7e029cdd) carried no MCM metadata
   rewrite.  A build must therefore never rewrite container metadata unless an
   explicit switch (MCM_BUILD_INPUT or M30_MCM_REWRITE=1) is provided.

2. The BOOT image used for the accepted observation must stay reproducible and
   must be distinguishable from the later diagnostic builds.
"""
from __future__ import annotations

import base64
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import plistlib
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

spec = importlib.util.spec_from_file_location(
    "m30lte_root_tweaks", ROOT / "tools" / "m30lte-root-tweaks.py")
tweaks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tweaks)

# Accepted physical configuration (2026-11-25 lock-screen PASS).
V68_BOOT_SHA256 = "629843b597fd665b7de6b6578a1605455ef5786ae9e06101b591d13a80bf8c50"
V68_KERNEL_SHA256 = "b5e3b704a771fa7dc3e0afb23b7e2c99c7d251f7c8a4665ba0a0b5b16c163f83"
V68_CMDLINE = ("debug=0xc serial=3 cpus=6 keepsyms=1 maxmem=292 rd=emmcroot0 "
               "emmcroot=USERDATA emmcprobe=1 emmcwrite=1 a5fb_noconsole=1 "
               "a5fb_keep_on=1")
GOOD_USERDATA_SHA256 = ("5f2e2aa6a80aea489946287d8cc32ef0ff6a1905a0d2923e8"
                        "d4324163bb699b5")

MCM_META = tweaks.MCM_META
SB_UUID = "97F8E922-00A4-48E1-B62F-CC799A4D0795"


def make_root(td: Path) -> Path:
    """Minimal staged root: launchd source, preferences dir, stale container."""
    (td / "System/Library/xpc").mkdir(parents=True)
    with (td / "System/Library/xpc/launchd.plist").open("wb") as fh:
        plistlib.dump({"LaunchDaemons": {}}, fh)
    (td / "private/var/mobile/Library/Preferences").mkdir(parents=True)
    c = td / "private/var/containers/Data/System" / "6532C5C7-7AF8-4D04-94D3-6E13239457D2"
    (c / "Library/Caches").mkdir(parents=True)
    with (c / MCM_META).open("wb") as fh:
        plistlib.dump({"MCMMetadataIdentifier": "com.apple.backboardd",
                       "MCMMetadataUUID": "7993DF92-69FB-42C8-963A-B1E3B7AAF64F",
                       "MCMMetadataVersion": 6,
                       "MCMMetadataContentClass": 12}, fh)
    return td


def run_main(root: Path, env: dict) -> str:
    argv = ["m30lte-root-tweaks.py", str(root)]
    buf = io.StringIO()
    clean = {k: v for k, v in os.environ.items()
             if k not in ("MCM_BUILD_INPUT", "M30_MCM_REWRITE", "M30_SETUP_DONE")}
    clean.update(env)
    # Staging runs as root in CI.  These tests run unprivileged, so ownership
    # changes are recorded instead of attempted.
    chowns = []
    real_chown = os.chown

    def record_chown(path, uid, gid, **kw):
        chowns.append((str(path), uid, gid))

    with mock.patch.object(sys, "argv", argv), \
            mock.patch.dict(os.environ, clean, clear=True), \
            mock.patch.object(os, "chown", record_chown), \
            mock.patch.object(tweaks.os, "chown", record_chown), \
            contextlib.redirect_stdout(buf):
        try:
            tweaks.main()
        finally:
            os.chown = real_chown
    run_main.chowns = chowns
    return buf.getvalue()


def counter(f) -> int:
    """sys.getrefcount()-free race counter; caps the run_main invocation."""
    def wrapped(*a, **k):
        counter.n += 1
        return f(*a, **k)
    return wrapped


class StagingBaselineTests(unittest.TestCase):
    def test_default_run_does_not_rewrite_container_metadata(self):
        """Proven-baseline default: stale MCMMetadataUUID is preserved."""
        with tempfile.TemporaryDirectory() as td:
            root = make_root(Path(td))
            meta = (root / "private/var/containers/Data/System/"
                    "6532C5C7-7AF8-4D04-94D3-6E13239457D2" / MCM_META)
            before = meta.read_bytes()
            out = run_main(root, {})
            self.assertIn("M30_MCM_REWRITE: disabled", out)
            self.assertIn("MCM_BUILD_INPUT: absent", out)
            self.assertEqual(meta.read_bytes(), before,
                             "staging must not touch container metadata by default")
            with meta.open("rb") as fh:
                self.assertEqual(plistlib.load(fh)["MCMMetadataUUID"],
                                 "7993DF92-69FB-42C8-963A-B1E3B7AAF64F")

    def test_explicit_rewrite_switch_applies_alignment(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_root(Path(td))
            meta = (root / "private/var/containers/Data/System/"
                    "6532C5C7-7AF8-4D04-94D3-6E13239457D2" / MCM_META)
            out = run_main(root, {"M30_MCM_REWRITE": "1"})
            self.assertIn("M30_MCM_REWRITE: enabled", out)
            self.assertIn("container metadata: 1/2", out)  # stale backboardd + SpringBoard record
            with meta.open("rb") as fh:
                data = plistlib.load(fh)
            self.assertEqual(data["MCMMetadataUUID"],
                             "6532C5C7-7AF8-4D04-94D3-6E13239457D2")
            # Everything else about the record is preserved.
            self.assertEqual(data["MCMMetadataIdentifier"], "com.apple.backboardd")
            self.assertEqual(data["MCMMetadataContentClass"], 12)

    def test_rewrite_switch_conflicts_with_explicit_build_input(self):
        """Two metadata sources must never be mixed silently."""
        uuid = "AAD4FDC5-016A-4A46-8DCD-0C7E85EB53E2"
        ident = "com.apple.lsd"
        container = ("private/var/containers/Data/System/"
                     "6561B268-BDB7-42A2-986F-8A6E4861FBE0")
        blob = plistlib.dumps({"MCMMetadataIdentifier": ident,
                               "MCMMetadataUUID": uuid,
                               "MCMMetadataVersion": 6,
                               "MCMMetadataContentClass": 12})
        with tempfile.TemporaryDirectory() as td:
            root = make_root(Path(td))
            inp = Path(td) / "mcm-input.json"
            inp.write_text(json.dumps({"schema": 1, "containers": [
                {"identifier": ident, "uuid": uuid, "container": container,
                 "metadata_b64": base64.b64encode(blob).decode(),
                 "sha256": hashlib.sha256(blob).hexdigest()}]}))
            with self.assertRaises(SystemExit):
                run_main(root, {"M30_MCM_REWRITE": "1",
                                "MCM_BUILD_INPUT": str(inp)})
            # Neither source may have been applied.
            self.assertIn("M30_MCM_REWRITE: disabled", run_main(root, {}))

    def test_springboard_container_registration_is_still_unconditional(self):
        """The v75/v79 SpringBoard container is not tied to the rewrite switch."""
        with tempfile.TemporaryDirectory() as td:
            root = make_root(Path(td))
            run_main(root, {})
            d = root / "private/var/containers/Data/System" / SB_UUID
            self.assertTrue((d / "Library/Caches").is_dir())
            with (d / MCM_META).open("rb") as fh:
                data = plistlib.load(fh)
            self.assertEqual(data["MCMMetadataIdentifier"], "com.apple.springboard")
            self.assertEqual(data["MCMMetadataUUID"], SB_UUID)
            self.assertEqual(stat.S_IMODE((d / MCM_META).stat().st_mode), 0o644)


class AcceptedBootIdentityTests(unittest.TestCase):
    """The accepted v68 BOOT must remain identifiable in the repository."""

    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (ROOT / "validation/ios-candidate-v68-out/manifest.json").read_text())

    def test_v68_boot_image_hash(self):
        self.assertEqual(
            self.manifest["images"]["ios-boot.img"]["sha256"], V68_BOOT_SHA256)

    def test_v68_kernel_hash(self):
        self.assertEqual(
            self.manifest["kernel_source"]["sha256"], V68_KERNEL_SHA256)

    def test_v68_cmdline_has_no_post_v68_switches(self):
        cl = self.manifest["payload"]["cmdline"]
        self.assertEqual(cl, V68_CMDLINE)
        for arg in ("m30touch", "m30touchhid", "m30uihb", "m30sblockdiag",
                    "sweetsample"):
            self.assertNotIn(arg, cl, f"{arg} is not part of the accepted boot")

    def test_v68_expected_kernel_matches_linked_verifier(self):
        log = (ROOT / "validation/ios-candidate-v68-out/kernel-verify.log").read_text()
        self.assertIn(V68_KERNEL_SHA256, log)


class KnownGoodUserdataIdentityTests(unittest.TestCase):
    def test_known_good_userdata_hash_is_recorded(self):
        """The USERDATA present during the accepted boot must stay citable."""
        doc = (ROOT / "validation/input-analysis/"
               "v80-lockscreen-regression-analysis.md").read_text()
        self.assertIn(GOOD_USERDATA_SHA256, doc)

    def test_release_that_produced_it_is_recorded(self):
        doc = (ROOT / "validation/ios-root-ci-build-20261121.md").read_text()
        self.assertIn("ios-root-20H392-44905109656", doc)
        self.assertIn(GOOD_USERDATA_SHA256, doc)

    def test_first_failing_boot_preceded_the_userdata_rewrite(self):
        """v69 flashed before the 17:00 USERDATA write of the same day."""
        v69 = (ROOT / "validation/physical-boot-test/20261125-ios-v69-boot/"
               "raw/flash-start.txt").read_text()
        fixed = (ROOT / "validation/physical-boot-test/"
                 "20261125-ios-root-install-fixed/raw/write-start.txt").read_text()
        self.assertIn("2026-11-25T09:17", v69)
        self.assertIn("2026-11-25T17:00", fixed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
