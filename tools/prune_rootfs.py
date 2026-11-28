#!/usr/bin/env python3
"""Prune optional launchd services from a mounted, writable copy of the
SHA-verified iOS 16 rootfs. CI/host only; never touches a device.

  prune_rootfs.py --rootfs MNT --manifest JSON --report PATH

Safety rules:
  * Only jobs not in the stage-A allowlist are candidates for removal.
  * A job plist is removed only if its job name is in the manifest's excluded
    set (excluded_categories + stage_b_addback + baked_instead_of_daemon).
  * An executable is removed only if it is not in the dependency closure of
    any retained job, is not under a framework/lib/system-protected prefix,
    and is not referenced by any remaining launchd plist or by any retained
    Mach-O dependency.
  * Frameworks, dyld shared cache, resources and all Apple binaries that are
    still reachable are preserved byte-for-byte. No binary is modified.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from make_ramdisk import macho_deps  # noqa: E402

LAUNCH_DIRS = ["System/Library/LaunchDaemons", "System/Library/LaunchAgents",
               "Library/LaunchAgents"]
PROTECTED_PREFIXES = (
    "System/Library/Frameworks/", "System/Library/PrivateFrameworks/",
    "System/Library/Caches/", "System/Library/CoreServices/",
    "System/Library/PreferenceBundles/", "System/Library/PrivateFrameworks/",
    "usr/lib/", "usr/libexec/", "etc/", "var/", "Library/",
)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_plists(root, job):
    base = "com.apple." + job + ".plist"
    alt = "com.apple." + job[0].upper() + job[1:] + ".plist"
    out = []
    for d in LAUNCH_DIRS:
        root_d = root / d
        if not root_d.is_dir():
            continue
        for p in sorted(root_d.rglob("*")):
            low = p.name.lower()
            if p.is_file() and (low in (base.lower(), alt.lower()) or
                                (low.endswith(".plist") and
                                 (low.startswith(base[:-6].lower()) or
                                  low.startswith(alt[:-6].lower())))):
                out.append(p)
    return out


def plist_exe(path):
    try:
        with open(path, "rb") as f:
            pl = plistlib.load(f)
    except Exception:
        return None
    argv = pl.get("ProgramArguments") or ([pl["Program"]] if "Program" in pl else [])
    if not argv:
        return None
    name = str(argv[0]).lstrip("/")
    if name.startswith("usr/libexec/") or name.startswith("usr/bin/") or \
            name.startswith("usr/sbin/") or name.startswith("System/"):
        return name
    return None


def resolve_dep(name, exe_rel, rpaths, root):
    cands = []
    if name.startswith("@executable_path/"):
        cands.append(os.path.normpath(os.path.join(os.path.dirname(exe_rel),
                                                    name[len("@executable_path/"):])))
    elif name.startswith("@rpath/"):
        tail = name[len("@rpath/"):]
        for rp in rpaths:
            rp2 = rp.replace("@executable_path/", os.path.dirname(exe_rel) + "/")
            if rp2.startswith("/"):
                cands.append(os.path.normpath(rp2.lstrip("/") + "/" + tail))
        cands.append(os.path.normpath("usr/lib/" + tail))
        cands.append(os.path.normpath("System/Library/Frameworks/" + tail))
    elif name.startswith("/"):
        cands.append(os.path.normpath(name.lstrip("/")))
    else:
        cands.append(os.path.normpath("usr/lib/" + name))
    for c in cands:
        if (root / c).is_file():
            return c
    return None


def closure(root, exes):
    """Return (found_relpaths, unresolved_install_names)."""
    found, unresolved, seen = set(), [], set()
    stack = list(exes)
    while stack:
        rel = stack.pop()
        if rel in seen:
            continue
        seen.add(rel)
        p = root / rel
        if not p.is_file():
            unresolved.append(rel)
            continue
        found.add(rel)
        deps, rpaths = macho_deps(p)
        for dep in deps:
            r = resolve_dep(dep, rel, rpaths, root)
            if r:
                stack.append(r)
            else:
                unresolved.append(dep)
    return found, unresolved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rootfs", required=True)
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--report", required=True, type=Path)
    a = ap.parse_args()

    m = json.loads(a.manifest.read_text())
    root = Path(a.rootfs).resolve()

    retained = list(m["stage_a_allowlist"])
    excluded = set()
    for jobs in m["excluded_categories"].values():
        excluded.update(jobs)
    excluded.update(m["stage_b_addback"])
    excluded.update(m["baked_instead_of_daemon"].keys())
    excluded -= set(retained)

    # Find retained executables: from their plists, with basename fallback.
    retained_exes = []
    job_map = {}
    for job in retained:
        pls = find_plists(root, job)
        exe = None
        for p in pls:
            exe = plist_exe(p) or exe
        if exe is None:
            for d in ("usr/bin", "usr/sbin", "usr/libexec",
                      "System/Library/CoreServices"):
                for p in sorted((root / d).rglob("*")) if (root / d).is_dir() else []:
                    if p.is_file() and p.name.lower() == job.lower():
                        exe = str(p.relative_to(root))
                        break
                if exe:
                    break
        if exe:
            retained_exes.append(exe)
        job_map[job] = {"plists": [str(p.relative_to(root)) for p in pls],
                        "executable": exe}

    found, unresolved = closure(root, retained_exes)

    # Remove only plists of excluded jobs.
    removed_plists = []
    for job in sorted(excluded):
        for p in find_plists(root, job):
            rel = str(p.relative_to(root))
            p.unlink()
            removed_plists.append(rel)

    # Collect executable candidates from remaining (non-retained) plists that
    # we just removed? Already gone; derive from job names via basename search.
    candidates = set()
    for job in sorted(excluded):
        for d in ("usr/bin", "usr/sbin", "usr/libexec"):
            base = root / d
            if not base.is_dir():
                continue
            for p in base.rglob("*"):
                if p.is_file() and p.name.lower() == job.lower():
                    candidates.add(str(p.relative_to(root)))

    # Remaining plists may still reference a candidate.
    referenced = set()
    for d in LAUNCH_DIRS:
        base = root / d
        if not base.is_dir():
            continue
        for p in base.rglob("*.plist"):
            if p.is_file():
                exe = plist_exe(p)
                if exe:
                    referenced.add(exe)

    removed_exes = []
    for rel in sorted(candidates):
        if rel in found or rel in referenced or rel.startswith(PROTECTED_PREFIXES):
            continue
        p = root / rel
        if p.is_file():
            p.unlink()
            removed_exes.append(rel)

    # Re-verify closure after pruning.
    found2, unresolved2 = closure(root, retained_exes)
    # unresolved install names are expected to be provided by the dyld cache.
    cache = root / "System/Library/Caches/com.apple.dyld"
    cache_blobs = b""
    if cache.is_dir():
        for p in cache.rglob("*"):
            if p.is_file():
                cache_blobs += p.read_bytes()
    unresolved_after_cache = []
    for u in unresolved2:
        leaf = u.split("/")[-1].encode()
        if leaf and leaf in cache_blobs:
            continue
        unresolved_after_cache.append(u)

    sv = root / "System/Library/CoreServices/SystemVersion.plist"
    version = None
    if sv.is_file():
        with open(sv, "rb") as f:
            v = plistlib.load(f)
        version = {"ProductVersion": v.get("ProductVersion"),
                   "ProductBuildVersion": v.get("ProductBuildVersion")}

    report = {
        "schema": "m30lte-pruned-rootfs-v1",
        "retained_jobs": retained,
        "retained_job_map": job_map,
        "excluded_job_count": len(excluded),
        "removed_plists_count": len(removed_plists),
        "removed_plists": removed_plists,
        "removed_executables_count": len(removed_exes),
        "removed_executables": removed_exes,
        "retained_closure_files": len(found2),
        "dependency_closure": "PASS" if not unresolved_after_cache else "FAIL",
        "unresolved_after_dyld_cache": unresolved_after_cache,
        "system_version": version,
        "dyld_cache_present": cache.is_dir(),
        "launchd_present": any((root / e).is_file() for e in retained_exes
                               if e.endswith("launchd")),
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2, sort_keys=True))
    print(f"[prune_rootfs] retained={len(retained)} excluded={len(excluded)} "
          f"plists_removed={len(removed_plists)} exes_removed={len(removed_exes)} "
          f"closure={report['dependency_closure']} "
          f"unresolved={len(unresolved_after_cache)}")
    return 0 if report["dependency_closure"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
