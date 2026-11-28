"""mkpayload.py must refuse a kernel that was not built for iOS.

Why this test exists: the v68-vs-CI investigation showed the accepted kernel is
an iOS build (LC_BUILD_VERSION platform=2, linking at 0xfffffff007004000, the
address xnu gives only to non-MacOSX platforms). A MacOSX build links 32 MB
away at 0xfffffe0007004000, which would make the payload's derived virt_base
wrong and map the kernel to the wrong physical address - a brick, not a bug
report. This guard makes that impossible to do by accident.

The test also pins the important negative result: with the guard in place, the
accepted v68 kernel and ADT still produce a payload byte-identical to the
shipped one. A guard that changes the output for the known-good input would be
worse than no guard.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAND = ROOT / "validation/ios-candidate-v68-out"
MK = CAND / "mkpayload.py"
KERNEL = CAND / "inputs/kernel.development.m30lte"
ADT = CAND / "inputs/m30lte-corrected.adt"
MANIFEST = CAND / "manifest.json"

LC_SEGMENT_64, LC_BUILD_VERSION = 0x19, 0x32
PLATFORM_MACOS, PLATFORM_IOS = 1, 2
M30_LINK_ADDR = 0xfffffff007004000
MACOSX_LINK_ADDR = 0xfffffe0007004000


def load_mkpayload():
    spec = importlib.util.spec_from_file_location("mkpayload", MK)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(CAND))
    spec.loader.exec_module(mod)
    return mod


def retag(kernel_bytes: bytes, platform: int, link_addr: int) -> bytes:
    """Rewrite platform and __TEXT vmaddr in a copy of a real kernel."""
    buf = bytearray(kernel_bytes)
    _, _, _, _, ncmds, _, _, _ = struct.unpack_from("<8I", buf, 0)
    off = 32
    for _ in range(ncmds):
        cmd, size = struct.unpack_from("<II", buf, off)
        if cmd == LC_BUILD_VERSION:
            struct.pack_into("<I", buf, off + 8, platform)
        elif cmd == LC_SEGMENT_64:
            name = bytes(buf[off + 8:off + 24]).split(b"\0")[0]
            if name == b"__TEXT":
                struct.pack_into("<Q", buf, off + 24, link_addr)
        off += size
    return bytes(buf)


class TargetGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_mkpayload()
        cls.kernel = KERNEL.read_bytes()
        cls.tmp = Path(tempfile.mkdtemp())
        cls.manifest = json.loads(MANIFEST.read_text())
        # The payload embeds the cmdline, so reproducing the shipped hash
        # requires the shipped cmdline - not an arbitrary one.
        cls.cmdline = cls.manifest["payload"]["cmdline"]

    def build(self, kernel_bytes, **kw):
        """build() returns (payload_bytes, info_dict)."""
        k = self.tmp / "k.bin"
        k.write_bytes(kernel_bytes)
        return self.mod.build(str(k), str(ADT), self.cmdline, None, **kw)

    def test_accepts_the_accepted_v68_kernel(self):
        """The guard must not break the known-good input."""
        payload, info = self.build(self.kernel)
        self.assertEqual(len(payload), self.manifest["payload"]["size_bytes"])
        self.assertEqual(hashlib.sha256(payload).hexdigest(),
                         self.manifest["payload"]["sha256"],
                         "packaging v68 must still be byte-identical")

    def test_refuses_a_macos_platform_kernel(self):
        bad = retag(self.kernel, PLATFORM_MACOS, MACOSX_LINK_ADDR)
        with self.assertRaises(SystemExit) as cm:
            self.build(bad)
        self.assertIn("platform=1", str(cm.exception))

    def test_refuses_a_macos_link_address_even_if_tagged_ios(self):
        """Platform tag alone is not enough; the link address must match too."""
        bad = retag(self.kernel, PLATFORM_IOS, MACOSX_LINK_ADDR)
        with self.assertRaises(SystemExit) as cm:
            self.build(bad)
        self.assertIn("__TEXT vmaddr", str(cm.exception))

    def test_refuses_a_kernel_with_no_build_version_command(self):
        # Zero the LC_BUILD_VERSION command id.
        buf = bytearray(self.kernel)
        _, _, _, _, ncmds, _, _, _ = struct.unpack_from("<8I", buf, 0)
        off = 32
        for _ in range(ncmds):
            cmd, size = struct.unpack_from("<II", buf, off)
            if cmd == LC_BUILD_VERSION:
                struct.pack_into("<I", buf, off, 0x7FFFFFFF)
            off += size
        with self.assertRaises(SystemExit) as cm:
            self.build(bytes(buf))
        self.assertIn("target cannot be established", str(cm.exception))

    def test_escape_hatch_exists_for_testing_only(self):
        bad = retag(self.kernel, PLATFORM_MACOS, M30_LINK_ADDR)
        payload, info = self.build(bad, allow_non_ios=True,
                                   text_vmaddr_expected=False)
        self.assertGreater(len(payload), 0)

    def test_validated_kernel_declares_the_expected_headers(self):
        """Guard the premise: v68 really is iOS at the embedded link address."""
        m = self.mod.parse_macho(bytearray(self.kernel))
        self.assertEqual(m["build"]["platform"], PLATFORM_IOS)
        self.assertEqual(m["segs"][0]["name"], "__TEXT")
        self.assertEqual(m["segs"][0]["vmaddr"], M30_LINK_ADDR)


class CliTests(unittest.TestCase):
    def test_cli_refuses_and_exits_nonzero(self):
        """A refusal must be a non-zero exit, or CI would treat it as success."""
        with tempfile.TemporaryDirectory() as d:
            k = Path(d) / "k.bin"
            k.write_bytes(retag(KERNEL.read_bytes(), PLATFORM_MACOS,
                                MACOSX_LINK_ADDR))
            r = subprocess.run([sys.executable, str(MK), str(k), str(ADT),
                                str(Path(d) / "p.bin"), "--cmdline", "x"],
                               capture_output=True, text=True, cwd=CAND)
            self.assertNotEqual(r.returncode, 0, "refusal must exit non-zero")
            self.assertIn("refusing to package", r.stderr + r.stdout)
            self.assertFalse((Path(d) / "p.bin").exists(),
                             "no payload may be written on refusal")


if __name__ == "__main__":
    unittest.main(verbosity=2)
