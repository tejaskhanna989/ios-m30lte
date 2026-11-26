#!/usr/bin/env python3
"""Inspect MCM container metadata vs directories in a staged rootfs.

Read-only. With no --expect arguments it prints a diagnostic inventory; with
--expect UUID values it fails if any expected UUID directory is absent.
"""
from __future__ import annotations

import argparse
import os
import plistlib
import sys
from pathlib import Path

MCM_META = '.com.apple.mobile_container_manager.metadata.plist'
BASES = ('private/var/containers', 'private/var/mobile/Containers')


def inventory(root: Path) -> tuple[list[dict], list[str]]:
    rows = []
    failures = []
    for base in BASES:
        top = root / base
        if not top.is_dir():
            continue
        for path, _dirs, files in os.walk(top):
            if MCM_META not in files:
                continue
            meta = Path(path) / MCM_META
            try:
                with meta.open('rb') as fh:
                    data = plistlib.load(fh)
            except Exception as exc:
                failures.append(f'unreadable {meta}: {exc}')
                continue
            uuid = data.get('MCMMetadataUUID', '')
            ident = data.get('MCMMetadataIdentifier', '')
            sibling = Path(path).parent / str(uuid)
            row = {'identifier': ident, 'uuid': uuid,
                   'container': str(Path(path).relative_to(root)),
                   'uuid_dir': str(sibling.relative_to(root)),
                   'uuid_dir_exists': sibling.is_dir()}
            rows.append(row)
            if not sibling.is_dir():
                failures.append(f'{ident}: UUID dir missing {row["uuid_dir"]}')
    return rows, failures


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('root', type=Path)
    ap.add_argument('--expect', action='append', default=[],
                    help='UUID that must have a directory')
    args = ap.parse_args()
    rows, failures = inventory(args.root)
    for r in rows:
        if 'lsd' in str(r['identifier']):
            print('LSD ' + ' '.join(f'{k}={v}' for k, v in r.items()))
    print(f'metadata records: {len(rows)}; UUID dir failures: '
          f'{sum(1 for r in rows if not r["uuid_dir_exists"])}')
    if not rows:
        print('FAIL no MCM metadata records found (wrong user, path, or image)')
        return 1
    for f in failures[:20]:
        print('FAIL', f)
    if args.expect:
        names = {str(r['container']).split('/')[-1] for r in rows}
        dirs = set()
        for base in BASES:
            top = args.root / base
            if top.is_dir():
                dirs.update(p.name for p in top.rglob('*') if p.is_dir())
        for uuid in args.expect:
            if uuid not in dirs:
                print(f'FAIL expected UUID directory absent: {uuid}')
                return 1
            print(f'PASS expected UUID directory: {uuid}')
    return 0 if not failures else 1


if __name__ == '__main__':
    raise SystemExit(main())
