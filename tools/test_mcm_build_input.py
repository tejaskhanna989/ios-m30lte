#!/usr/bin/env python3
"""Focused tests for the explicit device-derived MCM build input."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import plistlib
import stat
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import mcm_reconcile as mr  # noqa: E402

UUID = "AAD4FDC5-016A-4A46-8DCD-0C7E85EB53E2"
IDENT = "com.apple.lsd"
CONT = mr.ALLOWED[UUID][1]


def make_doc(uuid=UUID, ident=IDENT, container=CONT, blob=None, sha=None):
    blob = blob or plistlib.dumps({"MCMMetadataIdentifier": ident,
                                   "MCMMetadataUUID": uuid,
                                   "MCMMetadataVersion": 6})
    return {
        "schema": 1,
        "containers": [{
            "identifier": ident,
            "uuid": uuid,
            "container": container,
            "metadata_b64": base64.b64encode(blob).decode("ascii"),
            "sha256": sha or hashlib.sha256(blob).hexdigest(),
        }],
    }


class MCMBuildInputTests(unittest.TestCase):
    def write_input(self, td, doc):
        p = Path(td) / "input.json"
        p.write_text(json.dumps(doc))
        return p

    def test_valid_mapping_is_applied(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "root"
            inp = self.write_input(td, make_doc())
            entries = mr.load_input(inp)
            lines = mr.reconcile(root, entries)
            self.assertEqual(len(lines), 1)
            target = root / CONT
            self.assertTrue(target.is_dir())
            self.assertTrue((target / mr.MCM_META).is_file())
            self.assertEqual(mr.verify(root, entries)[0].split()[0], "PASS")
            # Idempotent: second run preserves metadata bytes.
            before = (target / mr.MCM_META).read_bytes()
            mr.reconcile(root, entries)
            self.assertEqual((target / mr.MCM_META).read_bytes(), before)

    def test_missing_directories_are_created_with_contents(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "root"
            entries = mr.load_input(self.write_input(td, make_doc()))
            mr.reconcile(root, entries)
            target = root / CONT
            caches = target / "Library/Caches"
            caches.mkdir(parents=True, exist_ok=True)
            (caches / "marker").write_text("preserve me")
            uuid_dir = target.parent / UUID
            # Remove UUID dir and confirm content is copied from container.
            import shutil
            shutil.rmtree(uuid_dir)
            mr.reconcile(root, entries)
            self.assertTrue((uuid_dir / "Library/Caches/marker").is_file())
            self.assertEqual((uuid_dir / "Library/Caches/marker").read_text(), "preserve me")

    def test_owner_and_mode_for_mobile_container(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "root"
            uuid = "58B7EA8C-8845-480F-8612-750117473D24"
            cont = mr.ALLOWED[uuid][1]
            entries = mr.load_input(self.write_input(td, make_doc(uuid=uuid, container=cont)))
            mr.reconcile(root, entries)
            if hasattr(os, "geteuid") and os.geteuid() == 0:
                st = os_stat(root / cont)
                self.assertEqual((st.st_uid, st.st_gid), (501, 501))

    def test_conflicting_existing_metadata_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "root"
            target = root / CONT
            target.mkdir(parents=True)
            with (target / mr.MCM_META).open("wb") as fh:
                plistlib.dump({"MCMMetadataIdentifier": "com.apple.other",
                               "MCMMetadataUUID": UUID}, fh)
            entries = mr.load_input(self.write_input(td, make_doc()))
            with self.assertRaises(mr.InputError):
                mr.reconcile(root, entries)

    def test_malformed_existing_metadata_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "root"
            target = root / CONT
            target.mkdir(parents=True)
            (target / mr.MCM_META).write_bytes(b"not a plist")
            entries = mr.load_input(self.write_input(td, make_doc()))
            with self.assertRaises(mr.InputError):
                mr.reconcile(root, entries)

    def test_malformed_input_plist_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            blob = b"broken"
            doc = make_doc(blob=blob)
            with self.assertRaises(mr.InputError):
                mr.load_input(self.write_input(td, doc))

    def test_bad_hash_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            doc = make_doc(sha="0" * 64)
            with self.assertRaises(mr.InputError):
                mr.load_input(self.write_input(td, doc))

    def test_unknown_uuid_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            doc = make_doc(uuid="DEADBEEF-0000-4000-8000-000000000000")
            with self.assertRaises(mr.InputError):
                mr.load_input(self.write_input(td, doc))

    def test_traversal_path_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            doc = make_doc(container="private/var/containers/../../escape")
            with self.assertRaises(mr.InputError):
                mr.load_input(self.write_input(td, doc))

    def test_absent_input_reported(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(mr.InputError):
                mr.load_input(Path(td) / "missing.json")

    def test_verify_detects_missing_uuid_dir(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "root"
            entries = mr.load_input(self.write_input(td, make_doc()))
            mr.reconcile(root, entries)
            import shutil
            shutil.rmtree(root / Path(CONT).parent / UUID)
            with self.assertRaises(mr.InputError):
                mr.verify(root, entries)


def os_stat(path):
    import os
    return os.stat(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
