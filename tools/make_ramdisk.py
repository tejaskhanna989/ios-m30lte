#!/usr/bin/env python3
"""Construct the minimal stage-A iOS ramdisk from a VERIFIED mounted Apple rootfs.

Host/CI only. Never writes to a device. Every included file is copied from the
mounted, SHA-pinned Apple rootfs and recorded with its source path and SHA-256.

  make_ramdisk.py --rootfs MNT --rootfs-sha256 SHA --manifest JSON \
      --out IMG --size-mb N --staging DIR --report JSON

Steps:
  1. verify rootfs identity and required markers
  2. resolve the 12 stage-A jobs (plist + executable)
  3. recursively resolve Mach-O dylib dependencies; include dyld shared cache
  4. bake activation/setup preferences instead of running migration daemons
  5. validate the dependency closure
  6. build an HFSX image from the staging tree (mkfs.hfsplus + loop mount)
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import shutil
import struct
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

LC_LOAD_DYLIB = 0xC
LC_LOAD_WEAK_DYLIB = 0x80000018
LC_REEXPORT_DYLIB = 0x8000001F
LC_LAZY_LOAD_DYLIB = 0x20
LC_LOAD_UPWARD_DYLIB = 0x80000023
LC_RPATH = 0x8000001C
DYLIB_CMDS = {LC_LOAD_DYLIB, LC_LOAD_WEAK_DYLIB, LC_REEXPORT_DYLIB,
              LC_LAZY_LOAD_DYLIB, LC_LOAD_UPWARD_DYLIB}

PLIST_NAMES = {
    "SpringBoard": "com.apple.springboard.plist",
    "backboardd": "com.apple.backboardd.plist",
    "runningboardd": "com.apple.runningboardd.plist",
    "lsd": "com.apple.lsd.plist",
    "notifyd": "com.apple.notifyd.plist",
    "cfprefsd": "com.apple.cfprefsd.plist",
    "distnoted": "com.apple.distnoted.plist",
    "configd": "com.apple.configd.plist",
    "securityd": "com.apple.securityd.plist",
    "amfid": "com.apple.amfid.plist",
    "mobileactivationd": "com.apple.mobileactivationd.plist",
}

DYLD_CACHE_DIR = "System/Library/Caches/com.apple.dyld"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd, **kw):
    print("[make_ramdisk] +", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def macho_deps(path):
    """Return (dylib install names, rpaths) from a thin or fat Mach-O."""
    data = path.read_bytes()
    if data[:4] in (b"\xca\xfe\xba\xbe", b"\xbe\xba\xfe\xca"):
        # fat binary: take the first ARM64 slice
        nfat = struct.unpack_from(">I", data, 4)[0]
        off = None
        for i in range(nfat):
            cputype, _ = struct.unpack_from(">II", data, 12 + i * 20)
            if cputype == 0x0100000C:
                off, _ = struct.unpack_from(">II", data, 12 + i * 20 + 8)
                break
        if off is None:
            return [], []
        data = data[off:]
    if data[:4] != b"\xcf\xfa\xed\xfe":
        return [], []
    ncmds, = struct.unpack_from("<I", data, 16)
    off = 32
    deps, rpaths = [], []
    for _ in range(ncmds):
        if off + 8 > len(data):
            break
        cmd, size = struct.unpack_from("<II", data, off)
        if size < 8 or off + size > len(data):
            break
        if cmd in DYLIB_CMDS and size >= 24:
            name_off, = struct.unpack_from("<I", data, off + 8)
            if 0 < name_off < size:
                end = data.find(b"\0", off + name_off, off + size)
                if end > 0:
                    deps.append(data[off + name_off:end].decode("utf-8", "replace"))
        elif cmd == LC_RPATH and size >= 12:
            path_off, = struct.unpack_from("<I", data, off + 8)
            if 0 < path_off < size:
                end = data.find(b"\0", off + path_off, off + size)
                if end > 0:
                    rpaths.append(data[off + path_off:end].decode("utf-8", "replace"))
        off += size
    return deps, rpaths


class Builder:
    def __init__(self, rootfs, staging, manifest):
        self.rootfs = rootfs.resolve()
        self.staging = staging.resolve()
        self.manifest = manifest
        self.files = {}          # relpath -> {sha256, size, source}
        self.unresolved = []
        self.cache_blobs = b""

    def src(self, rel):
        p = (self.rootfs / rel).resolve()
        if not str(p).startswith(str(self.rootfs) + os.sep):
            raise RuntimeError(f"path escapes pinned rootfs: {rel}")
        return p

    def add(self, rel, required=True):
        p = self.src(rel)
        if not p.is_file():
            if required:
                self.unresolved.append(rel)
            return False
        if rel in self.files:
            return True
        dst = self.staging / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst, follow_symlinks=True)
        self.files[rel] = {
            "source": rel,
            "source_sha256": sha256(p),
            "staged_sha256": sha256(dst),
            "size": p.stat().st_size,
        }
        return True

    def resolve_dep(self, name, exe_rel, rpaths):
        candidates = []
        if name.startswith("@executable_path/"):
            candidates.append(os.path.normpath(
                os.path.join(os.path.dirname(exe_rel), name[len("@executable_path/"):])))
        elif name.startswith("@rpath/"):
            tail = name[len("@rpath/"):]
            for rp in rpaths:
                rp2 = rp.replace("@executable_path/", os.path.dirname(exe_rel) + "/")
                if rp2.startswith("/"):
                    candidates.append(os.path.normpath(rp2.lstrip("/") + "/" + tail))
            candidates.append(os.path.normpath("usr/lib/" + tail))
            candidates.append(os.path.normpath("System/Library/Frameworks/" + tail))
        elif name.startswith("/"):
            candidates.append(os.path.normpath(name.lstrip("/")))
        else:
            candidates.append(os.path.normpath("usr/lib/" + name))
        for c in candidates:
            if self.add(c, required=False):
                return c
        return None

    def walk(self, exe_rel, seen=None):
        seen = seen if seen is not None else set()
        if exe_rel in seen:
            return
        seen.add(exe_rel)
        if not self.add(exe_rel, required=True):
            return
        deps, rpaths = macho_deps(self.staging / exe_rel)
        for dep in deps:
            provider = self.resolve_dep(dep, exe_rel, rpaths)
            if provider is None:
                self.unresolved.append(f"{exe_rel} -> {dep}")
                continue
            self.walk(provider, seen)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rootfs", required=True)
    ap.add_argument("--rootfs-sha256", required=True)
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--size-mb", type=int, default=1536)
    ap.add_argument("--staging", required=True, type=Path)
    ap.add_argument("--report", required=True, type=Path)
    ap.add_argument("--skip-image", action="store_true",
                    help="build staging + report only (no HFSX image)")
    a = ap.parse_args()

    manifest = json.loads(a.manifest.read_text())
    if a.rootfs_sha256.lower() != manifest["rootfs_source"]["image_sha256"].lower():
        raise SystemExit("rootfs image SHA does not match pinned manifest")
    rootfs = Path(a.rootfs)
    for marker in ("usr/lib/dyld", "System/Library/CoreServices/SpringBoard.app/SpringBoard"):
        if not (rootfs / marker).exists():
            raise SystemExit(f"rootfs marker missing: {marker}")

    if a.staging.exists():
        shutil.rmtree(a.staging)
    a.staging.mkdir(parents=True)
    b = Builder(rootfs, a.staging, manifest)

    jobs = {}
    for job in manifest["stage_a_allowlist"]:
        if job == "launchd":
            exe = "usr/sbin/launchd"
            b.add(exe)
            jobs[job] = {"plist": None, "executable": exe}
            continue
        plist_rel = "System/Library/LaunchDaemons/" + PLIST_NAMES[job]
        if not b.add(plist_rel, required=False):
            plist_rel = "System/Library/LaunchAgents/" + PLIST_NAMES[job]
            b.add(plist_rel)
        with open(b.src(plist_rel), "rb") as f:
            pl = plistlib.load(f)
        argv = pl.get("ProgramArguments") or ([pl["Program"]] if "Program" in pl else [])
        if not argv:
            raise SystemExit(f"no ProgramArguments for {job}")
        exe_rel = str(argv[0]).lstrip("/")
        b.walk(exe_rel)
        jobs[job] = {"plist": plist_rel, "executable": exe_rel,
                     "mach_services": sorted(pl.get("MachServices", {}).keys())}

    # dyld shared cache is the provider for unresolved system dylibs
    cache_dir = rootfs / DYLD_CACHE_DIR
    if not cache_dir.is_dir():
        raise SystemExit(f"dyld shared cache dir missing: {cache_dir}")
    for p in sorted(cache_dir.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(rootfs))
            b.add(rel)
            b.cache_blobs += p.read_bytes()
    unresolved_after_cache = []
    for item in b.unresolved:
        leaf = item.split("->")[-1].strip().split("/")[-1].encode()
        if leaf and leaf in b.cache_blobs:
            continue
        unresolved_after_cache.append(item)

    # Bake preferences instead of running first-boot migration/setup daemons.
    prefs = {
        "SetupDone": True, "SetupFinishedAllSteps": True, "SetupVersion": 11,
        "BKNoWatchdogs": True,
    }
    prefs_root = a.staging / "var/mobile/Library/Preferences"
    prefs_root.mkdir(parents=True, exist_ok=True)
    with open(prefs_root / "com.apple.springboard.plist", "wb") as f:
        plistlib.dump(prefs, f)
    act_root = a.staging / "var/mobile/Library/Activation"
    act_root.mkdir(parents=True, exist_ok=True)
    (act_root / "activated").write_text("activated\n")
    baked = {
        "var/mobile/Library/Preferences/com.apple.springboard.plist": prefs,
        "var/mobile/Library/Activation/activated": "generated, not from rootfs",
    }

    total = sum(v["size"] for v in b.files.values())
    report = {
        "schema": "m30lte-minimal-ramdisk-v1",
        "rootfs_image_sha256": a.rootfs_sha256,
        "stage_a_jobs": len(manifest["stage_a_allowlist"]),
        "jobs": jobs,
        "included_file_count": len(b.files),
        "included_bytes": total,
        "baked_preferences": baked,
        "unresolved_dependencies": unresolved_after_cache,
        "all_files_from_pinned_rootfs": all(
            v["source_sha256"] == v["staged_sha256"] for v in b.files.values()),
        "files": b.files,
    }
    if unresolved_after_cache:
        report["closure"] = "FAIL"
    elif not report["all_files_from_pinned_rootfs"]:
        report["closure"] = "FAIL"
    else:
        report["closure"] = "PASS"
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2, sort_keys=True))
    print(f"[make_ramdisk] jobs={len(jobs)} files={len(b.files)} bytes={total} "
          f"closure={report['closure']} unresolved={len(unresolved_after_cache)}")

    if not a.skip_image:
        if a.size_mb * 1024 * 1024 < total:
            raise SystemExit(f"ramdisk size {a.size_mb} MB < content {total} bytes")
        run("truncate", "-s", f"{a.size_mb}M", a.out)
        run("mkfs.hfsplus", "-v", "M30MIN", a.out)
        mnt = a.staging.parent / "ramdisk-mnt"
        mnt.mkdir(parents=True, exist_ok=True)
        run("sudo", "mount", "-t", "hfsplus", "-o", "loop,force,rw", a.out, mnt)
        try:
            run("sudo", "cp", "-a", str(a.staging) + "/.", str(mnt) + "/")
        finally:
            run("sudo", "umount", str(mnt))
        run("fsck.hfsplus", "-n", a.out)
        report["ramdisk_image_sha256"] = sha256(a.out)
        report["ramdisk_image_size"] = a.out.stat().st_size
        a.report.write_text(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["closure"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
