#!/usr/bin/env python3
"""Controlled, explicit MCM metadata reconciliation for a staged iOS rootfs.

This module applies a SMALL, device-derived build input to a host-staged rootfs.
It never reads or writes the physical device.  The input is an allow-listed set
of MCM metadata plists captured by the read-only HFS+ inspection recorded in
validation/input-analysis/v68-container-metadata-finding.md.  It is deliberately
NOT all 595 containers: only the LaunchServices containers and backboardd, the
ones with direct evidence in the SIGABRT loop and recovered .ips reports.

The input is supplied via an explicit path (MCM_BUILD_INPUT) and is expected to
live OUTSIDE the git worktree.  Absent input means NO reconciliation and is
reported as such.  Conflicts, malformed plists and unknown UUIDs fail closed:
no UUID mapping is ever invented.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import plistlib
import re
import shutil
import stat
from pathlib import Path

MCM_META = '.com.apple.mobile_container_manager.metadata.plist'
SCHEMA = 1
UUID_RE = re.compile(r'^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}$', re.I)

# The ONLY mappings this tool is permitted to apply.  Keyed by UUID; each value
# is (identifier, container path relative to the rootfs).  Derived from the
# read-only catalog join in make_mcm_build_input.py and the crash evidence.
ALLOWED = {
    'AAD4FDC5-016A-4A46-8DCD-0C7E85EB53E2': (
        'com.apple.lsd', 'private/var/containers/Data/System/6561B268-BDB7-42A2-986F-8A6E4861FBE0'),
    '58B7EA8C-8845-480F-8612-750117473D24': (
        'com.apple.lsd', 'private/var/mobile/Containers/Data/InternalDaemon/3EA10E23-74E5-4E0D-BFDF-347B135F2C81'),
    'DBD5D5E0-E129-471E-A351-0DB73584D03F': (
        'systemgroup.com.apple.lsd', 'private/var/containers/Shared/SystemGroup/FDC8A26C-6381-447B-9F88-4000F578D727'),
    '4A495630-106A-431F-90E4-393D845BC448': (
        'systemgroup.com.apple.lsd.iconscache', 'private/var/containers/Shared/SystemGroup/systemgroup.com.apple.lsd.iconscache'),
    '44D68AC1-157C-4411-8726-54E6CD9B4A83': (
        'com.apple.backboardd', 'private/var/containers/Data/System/F5099506-C581-4C69-BF94-F39FD86DAE89'),
}

BASES = {
    'private/var/containers': (0, 0),
    'private/var/mobile/Containers': (501, 501),
}


class InputError(Exception):
    """Fail-closed input validation error."""


def _validate_relpath(value: str) -> str:
    if not isinstance(value, str) or not value or value.startswith('/'):
        raise InputError(f'container path must be relative: {value!r}')
    parts = value.split('/')
    if '..' in parts or '.' in parts or '\\' in value:
        raise InputError(f'container path has traversal: {value!r}')
    if not any(value.startswith(b + '/') for b in BASES):
        raise InputError(f'container path outside approved bases: {value!r}')
    return value


def load_input(path: str | os.PathLike) -> list[dict]:
    """Parse and fully validate a build input.  No raw bytes are logged."""
    path = Path(path)
    if not path.is_file():
        raise InputError(f'build input not found: {path}')
    try:
        doc = json.loads(path.read_text('utf-8'))
    except Exception as exc:
        raise InputError(f'build input is not valid JSON: {exc}')
    if not isinstance(doc, dict) or doc.get('schema') != SCHEMA:
        raise InputError('build input schema mismatch')
    entries = doc.get('containers')
    if not isinstance(entries, list) or not entries:
        raise InputError('build input has no containers')

    seen_uuids: set[str] = set()
    result: list[dict] = []
    for i, e in enumerate(entries):
        if not isinstance(e, dict):
            raise InputError(f'container[{i}] is not an object')
        identifier, uuid = e.get('identifier'), e.get('uuid')
        container = e.get('container')
        blob_b64, want_sha = e.get('metadata_b64'), e.get('sha256')
        if not isinstance(uuid, str) or not UUID_RE.fullmatch(uuid):
            raise InputError(f'container[{i}] has malformed UUID')
        if uuid in seen_uuids:
            raise InputError(f'container[{i}] duplicates UUID {uuid}')
        seen_uuids.add(uuid)
        if uuid not in ALLOWED:
            raise InputError(f'container[{i}] UUID is not allow-listed: {uuid}')
        allowed_id, allowed_path = ALLOWED[uuid]
        if identifier != allowed_id or container != allowed_path:
            raise InputError(f'container[{i}] identifier/path mismatch for {uuid}')
        _validate_relpath(container)
        if not isinstance(blob_b64, str) or not isinstance(want_sha, str):
            raise InputError(f'container[{i}] missing metadata payload')
        try:
            blob = base64.b64decode(blob_b64, validate=True)
        except Exception as exc:
            raise InputError(f'container[{i}] invalid base64: {exc}')
        if hashlib.sha256(blob).hexdigest() != want_sha.lower():
            raise InputError(f'container[{i}] payload hash mismatch')
        try:
            data = plistlib.loads(blob)
        except Exception as exc:
            raise InputError(f'container[{i}] malformed plist: {exc}')
        if not isinstance(data, dict):
            raise InputError(f'container[{i}] plist is not a dict')
        if data.get('MCMMetadataIdentifier') != identifier or data.get('MCMMetadataUUID') != uuid:
            raise InputError(f'container[{i}] plist values do not match its mapping')
        result.append({'identifier': identifier, 'uuid': uuid,
                       'container': container, 'blob': blob, 'sha256': want_sha.lower()})
    return result


def _owner_for(container: str) -> tuple[int, int]:
    for base, owner in BASES.items():
        if container.startswith(base + '/'):
            return owner
    raise InputError(f'cannot determine owner for {container}')


def _is_root() -> bool:
    return hasattr(os, 'geteuid') and os.geteuid() == 0


def _set_owner(path: Path, uid: int, gid: int) -> None:
    # Production staging runs as root.  Unit tests run unprivileged, where
    # chown is impossible; ownership is then verified only when privileged.
    if _is_root():
        os.chown(path, uid, gid)


def _copy_dir_contents(src: Path, dst: Path) -> None:
    """Copy a container as the UUID-named sibling, preserving contents/ownership."""
    shutil.copytree(src, dst, symlinks=True)
    for src_dir, dirs, files in os.walk(src, followlinks=False):
        rel = os.path.relpath(src_dir, src)
        dst_dir = dst if rel == '.' else dst / rel
        for name in ['.'] + dirs + files:
            sp = src_dir if name == '.' else Path(src_dir) / name
            dp = dst_dir if name == '.' else dst_dir / name
            st = os.lstat(sp)
            if stat.S_ISLNK(st.st_mode):
                if _is_root():
                    os.chown(dp, st.st_uid, st.st_gid, follow_symlinks=False)
                continue
            _set_owner(dp, st.st_uid, st.st_gid)
            os.chmod(dp, stat.S_IMODE(st.st_mode))


def reconcile(root: str | os.PathLike, entries: list[dict]) -> list[str]:
    """Apply validated entries to a staged rootfs.  Fail closed on conflicts.

    Returns a list of safe (identifier, uuid, status) report lines.  Never
    prints or logs raw metadata bytes.
    """
    root = Path(root)
    report: list[str] = []
    for e in entries:
        container = e['container']
        uuid = e['uuid']
        identifier = e['identifier']
        uid, gid = _owner_for(container)
        target = root / container
        created_container = not target.is_dir()
        if created_container:
            target.mkdir(parents=True, exist_ok=True)
            _set_owner(target, uid, gid)
            os.chmod(target, 0o755)
            caches = target / 'Library/Caches'
            caches.mkdir(parents=True, exist_ok=True)
            _set_owner(caches, uid, gid)
            os.chmod(caches, 0o755)

        meta = target / MCM_META
        if meta.exists():
            if not meta.is_file():
                raise InputError(f'{container}: metadata path is not a regular file')
            try:
                existing = plistlib.loads(meta.read_bytes())
            except Exception as exc:
                raise InputError(f'{container}: existing metadata is malformed: {exc}')
            if (existing.get('MCMMetadataIdentifier') != identifier
                    or existing.get('MCMMetadataUUID') != uuid):
                raise InputError(f'{container}: conflicting metadata already present')
            status = 'metadata already correct (preserved)'
        else:
            with meta.open('wb') as fh:
                fh.write(e['blob'])
            _set_owner(meta, uid, gid)
            os.chmod(meta, 0o644)
            status = 'metadata installed'

        uuid_dir = target.parent / uuid
        if uuid_dir.exists():
            if not uuid_dir.is_dir():
                raise InputError(f'{container}: UUID path exists but is not a directory')
            other = uuid_dir / MCM_META
            if other.is_file():
                try:
                    data = plistlib.loads(other.read_bytes())
                except Exception as exc:
                    raise InputError(f'{container}: UUID dir metadata malformed: {exc}')
                if (data.get('MCMMetadataIdentifier') != identifier
                        or data.get('MCMMetadataUUID') != uuid):
                    raise InputError(f'{container}: UUID dir holds conflicting metadata')
            status += '; UUID dir present'
        else:
            _copy_dir_contents(target, uuid_dir)
            status += '; UUID dir created from container content'

        report.append(f'{identifier} {uuid} {status}')
    return report


def verify(root: str | os.PathLike, entries: list[dict]) -> list[str]:
    """Strict post-build verification of every reconciled container."""
    root = Path(root)
    lines: list[str] = []
    for e in entries:
        container, uuid, identifier = e['container'], e['uuid'], e['identifier']
        uid, gid = _owner_for(container)
        target = root / container
        if not target.is_dir():
            raise InputError(f'{container}: container directory missing')
        if _is_root():
            st = os.stat(target)
            if (st.st_uid, st.st_gid) != (uid, gid):
                raise InputError(f'{container}: container ownership {(st.st_uid, st.st_gid)} != {(uid, gid)}')
        meta = target / MCM_META
        if not meta.is_file():
            raise InputError(f'{container}: metadata missing')
        blob = meta.read_bytes()
        if hashlib.sha256(blob).hexdigest() != e['sha256']:
            raise InputError(f'{container}: metadata bytes changed')
        data = plistlib.loads(blob)
        if (data.get('MCMMetadataIdentifier') != identifier
                or data.get('MCMMetadataUUID') != uuid):
            raise InputError(f'{container}: metadata values changed')
        uuid_dir = target.parent / uuid
        if not uuid_dir.is_dir():
            raise InputError(f'{container}: UUID directory missing')
        lines.append(f'PASS {identifier} {uuid} metadata+UUID dir+ownership verified')
    return lines
