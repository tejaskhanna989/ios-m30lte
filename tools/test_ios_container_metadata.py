#!/usr/bin/env python3
"""Focused tests for container metadata repair and verification."""
from __future__ import annotations

import importlib.util
import plistlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import verify_ios_container_metadata as verify  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "m30lte_root_tweaks", ROOT / "tools" / "m30lte-root-tweaks.py")
tweaks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tweaks)  # noqa: E402


class ContainerMetadataTests(unittest.TestCase):
    def make_container(self, root: Path, uuid: str, identifier: str) -> Path:
        d = root / "private/var/containers/Data/System" / uuid / "Library/Caches"
        d.mkdir(parents=True)
        meta = d.parent.parent / verify.MCM_META
        with meta.open("wb") as fh:
            plistlib.dump({
                "MCMMetadataIdentifier": identifier,
                "MCMMetadataUUID": "00000000-0000-0000-0000-000000000000",
                "MCMMetadataVersion": 6,
                "MCMMetadataContentClass": 12,
            }, fh)
        return meta

    def test_fix_mismatched_uuid(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            uuid = "7993DF92-69FB-42C8-963A-B1E3B7AAF64F"
            meta = self.make_container(root, uuid, "com.apple.backboardd")
            self.assertTrue(verify.check(root))
            fixed, total = tweaks.fix_container_metadata(root)
            self.assertEqual((fixed, total), (1, 1))
            with meta.open("rb") as fh:
                data = plistlib.load(fh)
            self.assertEqual(data["MCMMetadataUUID"], uuid)
            self.assertEqual(data["MCMMetadataIdentifier"], "com.apple.backboardd")
            self.assertEqual(data["MCMMetadataVersion"], 6)
            self.assertEqual(verify.check(root), [])

    def test_already_correct_is_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            uuid = "42E32136-6D81-42FC-AE4F-CAE7C4FCED0D"
            meta = self.make_container(root, uuid, "com.apple.springboard")
            with meta.open("rb") as fh:
                data = plistlib.load(fh)
            data["MCMMetadataUUID"] = uuid
            with meta.open("wb") as fh:
                plistlib.dump(data, fh)
            before = meta.read_bytes()
            fixed, total = tweaks.fix_container_metadata(root)
            self.assertEqual((fixed, total), (0, 1))
            self.assertEqual(meta.read_bytes(), before)

    def test_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            uuid = "6532C5C7-7AF8-4D04-94D3-6E13239457D2"
            self.make_container(root, uuid, "com.apple.backboardd")
            tweaks.fix_container_metadata(root)
            self.assertEqual(tweaks.fix_container_metadata(root), (0, 1))

    def test_verifier_detects_missing_caches_directory(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            uuid = "11111111-2222-3333-4444-555555555555"
            d = root / "private/var/containers/Data/System" / uuid
            d.mkdir(parents=True)
            meta = d / verify.MCM_META
            with meta.open("wb") as fh:
                plistlib.dump({"MCMMetadataUUID": uuid,
                               "MCMMetadataIdentifier": "com.apple.backboardd"}, fh)
            tweaks.fix_container_metadata(root)
            issues = verify.check(root)
            self.assertTrue(any("missing Library/Caches" in i for i in issues))
            self.assertFalse((d / "Library/Caches").is_dir())


    def test_missing_metadata_uuid_directory_is_created(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            d = root / "private/var/containers/Data/System" / "6561B268-BDB7-42A2-986F-8A6E4861FBE0"
            d.mkdir(parents=True)
            meta = d / verify.MCM_META
            with meta.open("wb") as fh:
                plistlib.dump({"MCMMetadataIdentifier": "com.apple.lsd",
                               "MCMMetadataUUID": "AAD4FDC5-016A-4A46-8DCD-0C7E85EB53E2"}, fh)
            n = tweaks.ensure_metadata_uuid_dirs(root)
            self.assertEqual(n, 1)
            target = d.parent / "AAD4FDC5-016A-4A46-8DCD-0C7E85EB53E2"
            self.assertTrue(target.is_dir())
            self.assertTrue((target / verify.MCM_META).is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
