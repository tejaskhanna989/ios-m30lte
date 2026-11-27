#!/usr/bin/env python3
"""Focused tests for the native SpringBoard MCM container registration."""
from __future__ import annotations

import importlib.util
import os
import plistlib
import stat
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
spec = importlib.util.spec_from_file_location(
    "m30lte_root_tweaks", ROOT / "tools" / "m30lte-root-tweaks.py")
tweaks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tweaks)

UUID = "97F8E922-00A4-48E1-B62F-CC799A4D0795"
IDENT = "com.apple.springboard"


class SpringBoardContainerTests(unittest.TestCase):
    def test_creates_container_and_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.assertEqual(tweaks.ensure_ui_daemon_containers(root), 1)
            d = root / "private/var/containers/Data/System" / UUID
            self.assertTrue(d.is_dir())
            self.assertTrue((d / "Library/Caches").is_dir())
            meta = d / tweaks.MCM_META
            data = plistlib.loads(meta.read_bytes())
            self.assertEqual(data["MCMMetadataIdentifier"], IDENT)
            self.assertEqual(data["MCMMetadataUUID"], UUID)
            self.assertEqual(data["MCMMetadataContentClass"], 12)
            self.assertEqual(data["MCMMetadataSchemaVersion"], 1)
            self.assertEqual(data["MCMMetadataActiveDPClass"], -1)
            self.assertEqual(data["MCMMetadataInfo"],
                             {"com.apple.MobileInstallation.ContentProtectionClass": -1})
            self.assertEqual(stat.S_IMODE(meta.stat().st_mode), 0o644)

    def test_idempotent_and_preserves_existing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            tweaks.ensure_ui_daemon_containers(root)
            meta = root / "private/var/containers/Data/System" / UUID / tweaks.MCM_META
            before = meta.read_bytes()
            self.assertEqual(tweaks.ensure_ui_daemon_containers(root), 0)
            self.assertEqual(meta.read_bytes(), before)

    def test_upgrades_sparse_v75_record(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            d = root / "private/var/containers/Data/System" / UUID
            d.mkdir(parents=True)
            with (d / tweaks.MCM_META).open("wb") as fh:
                plistlib.dump({"MCMMetadataIdentifier": IDENT,
                               "MCMMetadataUUID": UUID}, fh)
            self.assertEqual(tweaks.ensure_ui_daemon_containers(root), 1)
            data = plistlib.loads((d / tweaks.MCM_META).read_bytes())
            self.assertEqual(data["MCMMetadataContentClass"], 12)
            self.assertEqual(tweaks.ensure_ui_daemon_containers(root), 0)

    def test_conflicting_metadata_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            d = root / "private/var/containers/Data/System" / UUID
            d.mkdir(parents=True)
            with (d / tweaks.MCM_META).open("wb") as fh:
                plistlib.dump({"MCMMetadataIdentifier": "com.apple.other",
                               "MCMMetadataUUID": UUID}, fh)
            with self.assertRaises(RuntimeError):
                tweaks.ensure_ui_daemon_containers(root)

    def test_malformed_metadata_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            d = root / "private/var/containers/Data/System" / UUID
            d.mkdir(parents=True)
            (d / tweaks.MCM_META).write_bytes(b"not a plist")
            with self.assertRaises(RuntimeError):
                tweaks.ensure_ui_daemon_containers(root)

    def test_setup_switch_is_independent(self):
        src = (ROOT / "tools/m30lte-root-tweaks.py").read_text()
        assert "M30_SETUP_DONE" in src
        assert "'SetupDone': setup_done" in src
        # Touch state is not tied to the setup switch.
        assert "m30touch" not in src

    def test_only_springboard_in_allow_list(self):
        self.assertEqual(tweaks.UI_DAEMON_CONTAINERS,
                         {"com.apple.springboard": UUID})
        src = (ROOT / "tools/m30lte-root-tweaks.py").read_text()
        # Touch-sensitive code is untouched by this change.
        self.assertNotIn("sweet_hid_touch", src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
