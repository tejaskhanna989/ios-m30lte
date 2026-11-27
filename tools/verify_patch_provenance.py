#!/usr/bin/env python3
"""Verify the build's applied-patch manifest against xnu/patches-minimal/.

The build script (patched by tools/patch_build_sh.py) writes a TSV manifest:

    order <TAB> patch_name <TAB> sha256 <TAB> status

Status is ``applied``, ``allowed-skip`` or ``FAILED``.

This tool is the CI gate. It fails when:

* the manifest is missing, empty, or contains a ``FAILED`` row;
* a patch in ``xnu/patches-minimal/`` has no manifest row (undocumented);
* a manifest row names a patch that does not exist (phantom);
* a manifest SHA-256 does not match the file on disk (tampered/drifted);
* a name appears twice (duplicate);
* a recorded apply order differs from the sorted-name order (order drift);
* an ``allowed-skip`` row is not justified in SKIP-ALLOWLIST.txt;
* an allow-list entry documents a patch that actually applied (stale reason).

Every failure is reported with the offending patch, not just a count, because
the whole point is that a silent divergence must be impossible to miss.

Nothing here needs a real buildtree: the manifest is the source of truth about
what the build claims to have done, and the patch directory is the source of
truth about what exists. Comparing them is a pure offline operation.

Usage:
    python3 tools/verify_patch_provenance.py \
        --manifest m30-patch-manifest.tsv \
        --patch-dir xnu/patches-minimal \
        [--allowlist xnu/patches-minimal/SKIP-ALLOWLIST.txt] \
        [--kernel-sha256 <hash>] [--json out.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

VALID_STATUSES = {"applied", "allowed-skip", "FAILED"}
ALLOWLIST_HEADER = "# patch-name\treason"


class Problem(list):
    """Collected failures; empty means the provenance is sound."""

    def add(self, code: str, detail: str) -> None:
        self.append({"code": code, "detail": detail})


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_manifest(path: Path, problems: Problem) -> list[dict]:
    if not path.is_file():
        problems.add("manifest-missing", f"{path} does not exist")
        return []
    rows: list[dict] = []
    for lineno, raw in enumerate(path.read_text().splitlines(), 1):
        line = raw.rstrip("\n")
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) != 4:
            problems.add("manifest-malformed",
                         f"{path.name}:{lineno}: expected 4 tab-separated fields, got {len(parts)}")
            continue
        order_s, name, sha, status = (p.strip() for p in parts)
        if not order_s.isdigit():
            problems.add("manifest-malformed",
                         f"{path.name}:{lineno}: non-numeric order {order_s!r}")
            continue
        if status not in VALID_STATUSES:
            problems.add("manifest-malformed",
                         f"{path.name}:{lineno}: unknown status {status!r}")
            continue
        rows.append({"order": int(order_s), "name": name, "sha256": sha,
                     "status": status, "line": lineno})
    if not rows:
        problems.add("manifest-empty",
                     f"{path}: no patch rows recorded (was SKIP_PATCHES set?)")
    return rows


def parse_allowlist(path: Path | None, problems: Problem) -> dict[str, str]:
    allowed: dict[str, str] = {}
    if path is None or not path.is_file():
        return allowed
    for lineno, raw in enumerate(path.read_text().splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "\t" not in line:
            problems.add("allowlist-malformed",
                         f"{path.name}:{lineno}: expected 'name<TAB>reason'")
            continue
        name, reason = line.split("\t", 1)
        name, reason = name.strip(), reason.strip()
        if not reason:
            problems.add("allowlist-malformed",
                         f"{path.name}:{lineno}: empty reason for {name}")
        allowed[name] = reason
    return allowed


def check(manifest_path: Path, patch_dir: Path, allowlist_path: Path | None,
          kernel_sha256: str | None,
          upstream_dir: Path | None = None) -> dict:
    problems = Problem()
    rows = parse_manifest(manifest_path, problems)
    allowed = parse_allowlist(allowlist_path, problems)

    disk = {p.name: sha256_of(p) for p in sorted(patch_dir.glob("*.patch"))}
    # The build iterates the *staged* patch directory, which contains our
    # patches plus whatever darwin-xnu-build ships. Upstream patches are in
    # scope for accounting but not for the "undocumented" check, because they
    # are not ours to track; they are recorded so skips are explained.
    upstream = {}
    if upstream_dir is not None and upstream_dir.is_dir():
        upstream = {p.name: sha256_of(p) for p in sorted(upstream_dir.glob("*.patch"))}
    recorded = {r["name"]: r for r in rows}

    # duplicates
    seen: set[str] = set()
    for r in rows:
        if r["name"] in seen:
            problems.add("duplicate", f"{r['name']} appears more than once")
        seen.add(r["name"])

    # explicit build failure recorded in the manifest
    for r in rows:
        if r["status"] == "FAILED":
            problems.add("patch-failed", f"{r['name']} is recorded as FAILED")

    # undocumented / phantom / hash drift
    for name, sha in disk.items():
        rec = recorded.get(name)
        if rec is None:
            problems.add("undocumented", f"{name} exists on disk but is absent from the manifest")
            continue
        if rec["sha256"] != sha:
            problems.add("hash-mismatch",
                         f"{name}: manifest {rec['sha256'][:16]} != disk {sha[:16]}")

    for name in recorded:
        if name not in disk and name not in upstream:
            problems.add("phantom", f"{name} is in the manifest but not in either patch source")

    # allowed-skip must be justified, and justification must not be stale
    for r in rows:
        if r["status"] == "allowed-skip" and r["name"] not in allowed:
            problems.add("unjustified-skip",
                         f"{r['name']} was skipped without a SKIP-ALLOWLIST.txt entry")
    warnings: list[dict] = []
    for name, reason in allowed.items():
        rec = recorded.get(name)
        if rec is not None and rec["status"] == "applied":
            msg = f"{name} is allow-listed ({reason!r}) but applied successfully"
            # Our own patches are ours to keep accurate: a stale entry means the
            # documented reason is wrong, so fail. An upstream patch that starts
            # applying is upstream's change, not a defect in this repo: warn.
            if name in disk:
                problems.add("stale-allowlist", msg)
            else:
                warnings.append({"code": "stale-allowlist-upstream", "detail": msg})

    # order must match the sorted patch-name order the build uses
    expected_order = {n: i + 1 for i, n in enumerate(disk)}
    for r in rows:
        if r["name"] in expected_order and r["order"] != expected_order[r["name"]]:
            problems.add("order-drift",
                         f"{r['name']}: recorded order {r['order']}, expected {expected_order[r['name']]}")

    return {
        "result": "PASS" if not problems else "FAIL",
        "manifest": str(manifest_path),
        "patch_dir": str(patch_dir),
        "counts": {
            "on_disk": len(disk),
            "upstream_on_disk": len(upstream),
            "manifest_rows": len(rows),
            "applied": sum(1 for r in rows if r["status"] == "applied"),
            "allowed_skip": sum(1 for r in rows if r["status"] == "allowed-skip"),
            "failed": sum(1 for r in rows if r["status"] == "FAILED"),
        },
        "kernel_sha256": kernel_sha256,
        "allowlist_entries": len(allowed),
        "applied_patches": [
            {"order": r["order"], "name": r["name"], "sha256": r["sha256"]}
            for r in sorted(rows, key=lambda r: r["order"]) if r["status"] == "applied"
        ],
        "problems": list(problems),
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--patch-dir", required=True, type=Path)
    ap.add_argument("--allowlist", type=Path, default=None)
    ap.add_argument("--upstream-dir", type=Path, default=None,
                    help="darwin-xnu-build's own patch directory (dxb/patches)")
    ap.add_argument("--kernel-sha256", default=None)
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args(argv)

    report = check(args.manifest, args.patch_dir, args.allowlist,
                   args.kernel_sha256, args.upstream_dir)

    if args.json:
        args.json.write_text(json.dumps(report, indent=2) + "\n")

    c = report["counts"]
    print(f"patch provenance: {report['result']}")
    print(f"  on disk (ours) : {c['on_disk']}")
    print(f"  on disk (upstr): {c['upstream_on_disk']}")
    print(f"  manifest rows  : {c['manifest_rows']}")
    print(f"  applied        : {c['applied']}")
    print(f"  allowed-skip   : {c['allowed_skip']}")
    if report["kernel_sha256"]:
        print(f"  kernel sha256  : {report['kernel_sha256']}")
    for w in report.get("warnings", []):
        print(f"  WARNING [{w['code']}] {w['detail']}", file=sys.stderr)
    for p in report["problems"]:
        print(f"  PROBLEM [{p['code']}] {p['detail']}", file=sys.stderr)
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
