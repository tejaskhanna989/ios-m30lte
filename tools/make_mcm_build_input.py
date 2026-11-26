#!/usr/bin/env python3
"""Build a minimal, device-derived MCM metadata build input (host only).

Reads the read-only HFS+ catalog and cached metadata plists from the
2026-11-24 USERDATA inspection, selects ONLY the allow-listed LaunchServices /
backboardd containers, and writes a base64 JSON bundle to an explicit output
path.  The output is device-derived data: keep it OUTSIDE the git worktree and
never print its raw contents.

    python3 tools/make_mcm_build_input.py \
        --catalog /path/to/catalog.bin \
        --meta-dir /path/to/meta2 \
        --out /path/outside/repo/mcm-input.json
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import plistlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hfsplus_ro  # noqa: E402
from mcm_reconcile import ALLOWED, MCM_META, SCHEMA  # noqa: E402


def folder_paths(catalog: Path) -> dict[int, str]:
    size = catalog.stat().st_size
    reader = hfsplus_ro.ImageReader(catalog, 4096, None)
    fork = hfsplus_ro.Fork(size, 0, [hfsplus_ro.Extent(0, (size + 4095) // 4096)])
    records = hfsplus_ro.load_catalog(reader, fork)
    folders: dict[int, tuple[int, str]] = {}
    for r in records:
        if r.kind == hfsplus_ro.FOLDER_RECORD and r.folder_id:
            folders[r.folder_id] = (r.parent, r.name)

    def path_of(fid: int) -> str | None:
        parts: list[str] = []
        seen: set[int] = set()
        root = hfsplus_ro.ROOT_FOLDER_ID
        while fid and fid != root and fid not in seen:
            seen.add(fid)
            entry = folders.get(fid)
            if not entry:
                return None
            parent, name = entry
            parts.append(name)
            fid = parent
        return '/' + '/'.join(reversed(parts)) if fid == root else None

    result: dict[int, str] = {}
    for fid in folders:
        p = path_of(fid)
        if p:
            result[fid] = p
    return result


def build(catalog: Path, meta_dir: Path, out: Path) -> list[str]:
    paths = folder_paths(catalog)
    manifest = json.loads((meta_dir / 'manifest.json').read_text('utf-8'))
    found: dict[str, dict] = {}
    for row in manifest:
        if Path(row.get('source_name', '')).name != MCM_META:
            continue
        blob = Path(row['output']).read_bytes()
        try:
            data = plistlib.loads(blob)
        except Exception:
            continue
        uuid = data.get('MCMMetadataUUID')
        if uuid not in ALLOWED:
            continue
        identifier, container = ALLOWED[uuid]
        if data.get('MCMMetadataIdentifier') != identifier:
            raise SystemExit(f'identifier mismatch for allow-listed UUID {uuid}')
        actual = paths.get(row['parent'])
        if actual is None:
            raise SystemExit(f'cannot resolve catalog path for UUID {uuid}')
        if actual.lstrip('/') != container:
            raise SystemExit(f'container path mismatch for {uuid}: {actual} != {container}')
        found[uuid] = {
            'identifier': identifier,
            'uuid': uuid,
            'container': container,
            'metadata_b64': base64.b64encode(blob).decode('ascii'),
            'sha256': hashlib.sha256(blob).hexdigest(),
        }

    missing = sorted(set(ALLOWED) - set(found))
    if missing:
        raise SystemExit(f'fail closed: allow-listed metadata missing from cache: {missing}')
    doc = {
        'schema': SCHEMA,
        'source': ('read-only HFS+ USERDATA inspection documented in '
                   'validation/input-analysis/v68-container-metadata-finding.md'),
        'scope': 'LaunchServices containers + backboardd only (not all 595)',
        'containers': [found[u] for u in sorted(found)],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2, sort_keys=True) + '\n', 'utf-8')
    os.chmod(out, 0o600)
    return [f'{e["identifier"]} {e["uuid"]}' for e in doc['containers']]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--catalog', type=Path, required=True)
    ap.add_argument('--meta-dir', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    lines = build(args.catalog, args.meta_dir, args.out)
    print(f'wrote {len(lines)} allow-listed MCM records to {args.out} (mode 0600)')
    for line in lines:
        print('  ' + line)


if __name__ == '__main__':
    main()
