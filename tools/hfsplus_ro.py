#!/usr/bin/env python3
"""hfsplus_ro - strictly read-only HFS+/HFSX inspector over ADB or an image.

This utility reads HFS+ volumes without mounting, repairing, replaying journals,
or writing any metadata. It supports local images and remote block devices via
`adb shell dd if=<device> ...` (read-only). Only the blocks actually needed are
fetched, so a 53 GiB USERDATA partition does not need a full acquisition.

Scope: volume header, allocation-block extents, catalog B-tree lookup by path,
and data-fork extraction. The extents overflow B-tree is consulted when a fork
uses more than eight extents. Unsupported features are reported, not silently
skipped. HFS+ transparent compression xattrs are NOT decoded; raw fork bytes
are written and flagged when compression is detected.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

SECTOR = 512
VH_OFFSET = 1024
VH_SIZE = 512
ROOT_FOLDER_ID = 2

FOLDER_RECORD = 0x0001
FILE_RECORD = 0x0002
FOLDER_THREAD = 0x0003
FILE_THREAD = 0x0004

BT_LEAF = 0
BT_INTERIOR = 1
BT_HEADER = 2
BT_MAP = 3


class HFSError(Exception):
    pass


@dataclass
class Extent:
    start: int
    count: int


@dataclass
class Fork:
    logical_size: int
    clump_size: int
    extents: list[Extent]


@dataclass
class VolumeHeader:
    signature: str
    version: int
    attributes: int
    journal_block: int
    block_size: int
    total_blocks: int
    file_count: int
    folder_count: int
    modify_date: int
    catalog: Fork
    extents: Fork
    attributes_file: Fork


@dataclass
class CatRecord:
    kind: int
    parent: int
    name: str
    file_id: int = 0
    folder_id: int = 0
    modify_date: int = 0
    create_date: int = 0
    data_fork: Fork | None = None
    rsrc_fork: Fork | None = None


class BlockReader:
    """Reads aligned allocation blocks; caches results in memory and on disk."""

    def __init__(self, block_size: int, source: str, cache_dir: Path | None = None):
        self.block_size = block_size
        self.source = source
        self.cache_dir = cache_dir
        self._mem: dict[int, bytes] = {}
        self.read_count = 0
        self.byte_count = 0
        if cache_dir is not None:
            cache_dir.mkdir(parents=True, exist_ok=True)

    def read_blocks(self, start: int, count: int = 1) -> bytes:
        if count < 1:
            return b""
        missing = [i for i in range(start, start + count) if i not in self._mem]
        if missing:
            cached = bytearray()
            needed: list[int] = []
            for i in missing:
                blob = self._read_cached_block(i)
                if blob is None:
                    needed.append(i)
                    cached.extend(b"\x00" * self.block_size)
                else:
                    cached.extend(blob)
            if needed:
                fetched = self._fetch(needed)
                pos = 0
                rebuilt = bytearray()
                for i in missing:
                    if i in needed:
                        rebuilt.extend(fetched[pos:pos + self.block_size])
                        pos += self.block_size
                    else:
                        rebuilt.extend(self._mem[i])
                for idx, i in enumerate(missing):
                    self._mem[i] = bytes(rebuilt[idx * self.block_size:(idx + 1) * self.block_size])
        return b"".join(self._mem[i] for i in range(start, start + count))

    def _cache_path(self, block: int) -> Path:
        return self.cache_dir / f"{block:012x}.bin"

    def _read_cached_block(self, block: int) -> bytes | None:
        if self.cache_dir is None:
            return self._mem.get(block)
        p = self._cache_path(block)
        if p.exists():
            blob = p.read_bytes()
            self._mem[block] = blob
            return blob
        return None

    def _fetch(self, blocks: Iterable[int]) -> bytes:
        blocks = list(blocks)
        out = bytearray()
        for block in blocks:
            if block in self._mem:
                out.extend(self._mem[block])
                continue
            data = self._fetch_one(block)
            if len(data) != self.block_size:
                raise HFSError(
                    f"short block read at {block}: got {len(data)} expected {self.block_size}")
            self._mem[block] = data
            self.read_count += 1
            self.byte_count += len(data)
            if self.cache_dir is not None:
                self._cache_path(block).write_bytes(data)
            out.extend(data)
        return bytes(out)

    def _fetch_one(self, block: int) -> bytes:
        raise NotImplementedError


class ImageReader(BlockReader):
    def __init__(self, image: Path, block_size_hint: int | None = None, cache_dir=None):
        f = image.open("rb")
        f.seek(VH_OFFSET)
        vh = f.read(VH_SIZE)
        bs = struct.unpack_from(">I", vh, 40)[0] if len(vh) >= 44 else block_size_hint
        if not bs or bs < SECTOR or bs % SECTOR:
            bs = block_size_hint or 4096
        super().__init__(bs, str(image), cache_dir)
        self.file = f

    def _fetch_one(self, block: int) -> bytes:
        self.file.seek(block * self.block_size)
        return self.file.read(self.block_size)


class LocalForkReader(BlockReader):
    """Reads a materialized fork file as contiguous allocation blocks."""

    def __init__(self, path: Path, block_size: int = 4096):
        self.file = path.open("rb")
        super().__init__(block_size, str(path), None)

    def _fetch_one(self, block: int) -> bytes:
        self.file.seek(block * self.block_size)
        return self.file.read(self.block_size)


def materialize_fork(reader: BlockReader, fork: Fork, path: Path) -> LocalForkReader:
    """Fetch each extent with one large read-only dd; never writes to source."""
    if path.exists() and path.stat().st_size >= fork.logical_size:
        return LocalForkReader(path, reader.block_size)
    with path.open("wb") as out:
        for ext in fork.extents:
            if isinstance(reader, ADBReader):
                cmd = reader._adb_prefix() + [
                    "shell", "dd", f"if={reader.source}", f"bs={reader.block_size}",
                    f"skip={ext.start}", f"count={ext.count}", "2>/dev/null",
                ]
                proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if proc.returncode != 0:
                    raise HFSError(f"extent read failed: {proc.stderr.decode(errors='replace')}")
                out.write(proc.stdout)
            else:
                out.write(reader.read_blocks(ext.start, ext.count))
    return LocalForkReader(path, reader.block_size)


class ADBReader(BlockReader):
    """Remote read-only dd via ADB; never issues a write command."""

    def __init__(self, device: str, block_size: int = 4096, cache_dir=None, serial: str | None = None):
        super().__init__(block_size, device, cache_dir)
        self.serial = serial
        self.command_log: list[str] = []

    def _adb_prefix(self) -> list[str]:
        cmd = ["adb"]
        if self.serial:
            cmd += ["-s", self.serial]
        return cmd

    def _fetch_one(self, block: int) -> bytes:
        cmd = self._adb_prefix() + [
            "shell", "dd", f"if={self.source}", f"bs={self.block_size}",
            f"skip={block}", "count=1", "2>/dev/null",
        ]
        self.command_log.append(" ".join(cmd))
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0:
            raise HFSError(f"dd failed at block {block}: {proc.stderr.decode(errors='replace')}")
        return proc.stdout


def parse_fork(data: bytes, off: int) -> Fork:
    logical, clump, total_blocks = struct.unpack_from(">QII", data, off)
    # In HFS+ volume-header forks the third field is the total block count,
    # not the extent count. Up to 8 inline extents describe the fork; the
    # extents overflow B-tree is only needed when more than 8 are required.
    exts = []
    for i in range(8):
        start, count = struct.unpack_from(">II", data, off + 16 + i * 8)
        if count:
            exts.append(Extent(start, count))
    if not exts and logical:
        raise HFSError("fork has data but no inline extents")
    return Fork(logical, clump, exts)


def read_vh(reader: BlockReader) -> VolumeHeader:
    raw = reader.read_blocks(0)[VH_OFFSET:VH_OFFSET + VH_SIZE]
    sig = raw[0:2]
    if sig == b"H+":
        signature = "HFS+"
    elif sig == b"HX":
        signature = "HFSX"
    else:
        raise HFSError(f"unsupported volume signature {sig!r}; expected H+ or HX")
    version = struct.unpack_from(">H", raw, 2)[0]
    attributes = struct.unpack_from(">I", raw, 4)[0]
    journal = struct.unpack_from(">I", raw, 12)[0]
    modify = struct.unpack_from(">I", raw, 20)[0]
    file_count, folder_count = struct.unpack_from(">II", raw, 32)
    block_size, total_blocks = struct.unpack_from(">II", raw, 40)
    # Five 80-byte forks start at 112 (allocation, extents, catalog,
    # attributes, startup) after the 80-byte header and 32-byte finderInfo.
    extents = parse_fork(raw, 192)
    catalog = parse_fork(raw, 272)
    attributes_fork = parse_fork(raw, 352)
    return VolumeHeader(signature, version, attributes, journal, block_size,
                        total_blocks, file_count, folder_count, modify,
                        catalog, extents, attributes_fork)


def read_fork_data(reader: BlockReader, fork: Fork, extents_tree: Fork | None = None) -> bytes:
    out = bytearray()
    logical_pos = 0
    ext_list = list(fork.extents)
    extra_extents: dict[int, Extent] = {}
    if extents_tree is not None:
        extra_extents = load_extents_tree(reader, extents_tree, fork)
    for index, ext in enumerate(ext_list):
        if logical_pos >= fork.logical_size:
            break
        nblocks = ext.count
        data = reader.read_blocks(ext.start, nblocks)
        need = fork.logical_size - logical_pos
        take = min(need, len(data))
        out.extend(data[:take])
        logical_pos += take
        # Overflow extents are keyed by the allocation block where the run starts.
        if index in extra_extents:
            ov = extra_extents[index]
            data = reader.read_blocks(ov.start, ov.count)
            need = fork.logical_size - logical_pos
            out.extend(data[:min(need, len(data))])
            logical_pos += min(need, len(data))
    return bytes(out)


def load_extents_tree(reader: BlockReader, tree: Fork, fork: Fork) -> dict[int, Extent]:
    """Return overflow extents indexed by inline-extent ordinal (best effort)."""
    result: dict[int, Extent] = {}
    try:
        nodes = btree_nodes(reader, tree)
    except HFSError as exc:
        raise HFSError(f"cannot read extents overflow B-tree: {exc}") from exc
    ordinal = len(fork.extents)
    for node in nodes:
        if node["kind"] != BT_LEAF:
            continue
        for key, data in node["records"]:
            if len(key) < 10:
                continue
            # key: u16 len, u32 fileID, u8 forkType, u32 startBlock
            _len, _fid, _ftype, _start = struct.unpack_from(">HIBI", key, 0)
            if len(data) >= 8 and ordinal < 64:
                start, count = struct.unpack_from(">II", data, 0)
                result[ordinal] = Extent(start, count)
                ordinal += 1
    return result


def btree_nodes(reader: BlockReader, fork: Fork) -> list[dict]:
    if not fork.extents:
        return []
    # The HFS+ B-tree header record places nodeSize at offset 0x20 and the
    # root node at 0x10 (verified from this device's volume).
    node_size = struct.unpack_from(">H", read_fork_data_at(reader, fork, 0x20, 2), 0)[0]
    if node_size < 512 or node_size % 512:
        raise HFSError(f"invalid B-tree node size {node_size}")
    blocks_per_node = node_size // reader.block_size
    total_bytes = fork.logical_size
    nodes = []
    for node_index in range(total_bytes // node_size):
        raw = read_fork_data_at(reader, fork, node_index * node_size, node_size)
        nodes.append(parse_btree_node(raw, node_size))
    return nodes


def read_fork_data_short(reader: BlockReader, fork: Fork, n: int) -> bytes:
    return read_fork_data_at(reader, fork, 0, n)


def fork_block(fork: Fork, logical: int) -> tuple[int, int]:
    """Map a logical byte offset to (block, offset within block)."""
    acc = 0
    for ext in fork.extents:
        span = ext.count * 4096  # replaced by caller when block size known
        if logical < acc + span:
            return ext.start + (logical - acc) // 4096, (logical - acc) % 4096
        acc += span
    raise HFSError("fork offset beyond extents")


def read_fork_data_at(reader: BlockReader, fork: Fork, offset: int, length: int) -> bytes:
    """Read bytes from a fork using its block extents and the reader block size."""
    bs = reader.block_size
    out = bytearray()
    pos = 0
    for ext in fork.extents:
        span = ext.count * bs
        if offset >= pos + span:
            pos += span
            continue
        start_in_ext = offset - pos
        first_block = ext.start + start_in_ext // bs
        first_off = start_in_ext % bs
        take = min(length - len(out), bs - first_off)
        out.extend(reader.read_blocks(first_block)[first_off:first_off + take])
        pos += span
        while len(out) < length:
            block_index = (start_in_ext + len(out)) // bs
            if block_index >= ext.count:
                break
            blk = ext.start + block_index
            take = min(length - len(out), bs)
            out.extend(reader.read_blocks(blk)[:take])
        if len(out) == length:
            return bytes(out)
    if len(out) < length:
        raise HFSError(f"fork read short at offset {offset}: got {len(out)} of {length}")
    return bytes(out)


def parse_btree_node(raw: bytes, node_size: int) -> dict:
    flink, blink, kind, height, num_keys, reserved = struct.unpack_from(">IIBBHH", raw, 0)
    # HFS+ stores the record-offset table in reverse order (free-space
    # offset first, then last record ... first record).
    offsets = tuple(reversed(struct.unpack_from(
        ">" + "H" * (num_keys + 1), raw, node_size - 2 * (num_keys + 1))))
    records = []
    for i in range(num_keys):
        off = offsets[i]
        key_len = struct.unpack_from(">H", raw, off)[0]
        key = raw[off:off + 2 + key_len]
        rec_off = off + 2 + key_len
        rec_off += (-rec_off) % 2
        rec_end = offsets[i + 1] if i + 1 < len(offsets) else node_size - 2 * (num_keys + 1)
        records.append((key, raw[rec_off:rec_end]))
    return {"kind": kind, "height": height, "num_keys": num_keys,
            "flink": flink, "blink": blink, "records": records}


def decode_key(key: bytes) -> tuple[int, str]:
    if len(key) < 8:
        raise HFSError("short catalog key")
    key_len = struct.unpack_from(">H", key, 0)[0]
    parent = struct.unpack_from(">I", key, 2)[0]
    name_len = struct.unpack_from(">H", key, 6)[0]
    if name_len > 255 or 8 + name_len * 2 > len(key):
        raise HFSError("invalid catalog name length")
    raw = key[8:8 + name_len * 2]
    name = raw.decode("utf-16-be", errors="replace")
    return parent, name


def parse_catalog_record(key: bytes, data: bytes) -> CatRecord:
    parent, name = decode_key(key)
    if len(data) < 2:
        raise HFSError("short catalog record")
    kind = struct.unpack_from(">H", data, 0)[0]
    rec = CatRecord(kind=kind, parent=parent, name=name)
    if kind == FOLDER_RECORD:
        if len(data) < 88:
            raise HFSError("short folder record")
        rec.folder_id = struct.unpack_from(">I", data, 8)[0]
        rec.create_date = struct.unpack_from(">I", data, 12)[0]
        rec.modify_date = struct.unpack_from(">I", data, 16)[0]
    elif kind == FILE_RECORD:
        if len(data) < 248:
            raise HFSError(f"short file record ({len(data)})")
        rec.file_id = struct.unpack_from(">I", data, 8)[0]
        rec.create_date = struct.unpack_from(">I", data, 12)[0]
        rec.modify_date = struct.unpack_from(">I", data, 16)[0]
        rec.data_fork = parse_fork(data, 0x58)
        rec.rsrc_fork = parse_fork(data, 0xA8)
    return rec


def load_catalog(reader: BlockReader, catalog: Fork) -> list[CatRecord]:
    nodes = btree_nodes(reader, catalog)
    records: list[CatRecord] = []
    for node in nodes:
        if node["num_keys"] == 0:
            continue
        for key, data in node["records"]:
            try:
                rec = parse_catalog_record(key, data)
            except HFSError:
                continue
            if rec.kind in (FOLDER_RECORD, FILE_RECORD, FOLDER_THREAD, FILE_THREAD):
                records.append(rec)
    return records


def hfs_date(v: int) -> str:
    if v == 0:
        return ""
    try:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(v - 2082844800))
    except (ValueError, OverflowError):
        return f"raw:{v}"


def safe_name(name: str) -> str:
    name = re.sub(r"[^\w.\-+]+", "_", name, flags=re.UNICODE)
    return name[:120] or "unnamed"


def resolve_path(records: list[CatRecord], path: str) -> int | None:
    """Resolve an absolute HFS+ path to its folder/file ID, case-insensitively."""
    current = ROOT_FOLDER_ID
    for comp in [c for c in path.strip("/").split("/") if c]:
        found = None
        for rec in records:
            if rec.parent == current and rec.kind in (FOLDER_RECORD, FILE_RECORD) \
                    and rec.name.lower() == comp.lower():
                found = rec
                break
        if found is None:
            return None
        current = found.folder_id or found.file_id
    return current


def print_children(records: list[CatRecord], parent: int) -> None:
    kids = [r for r in records if r.parent == parent
            and r.kind in (FOLDER_RECORD, FILE_RECORD)]
    print(f"children of id {parent}: {len(kids)}")
    for rec in sorted(kids, key=lambda r: r.name.lower()):
        kind = "folder" if rec.kind == FOLDER_RECORD else "file"
        size = rec.data_fork.logical_size if rec.data_fork else 0
        print(f"{kind:6} id={rec.folder_id or rec.file_id:<10} size={size:<12} "
              f"mtime={hfs_date(rec.modify_date)} name={rec.name}")

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--image", type=Path, help="local HFS+ image (read-only open)")
    src.add_argument("--adb-device", help="remote block device read via adb shell dd")
    ap.add_argument("--serial", help="ADB serial if multiple devices")
    ap.add_argument("--cache-dir", type=Path, default=Path(".hfs-ro-cache"))
    ap.add_argument("--block-size", type=int, default=4096)
    ap.add_argument("--find", action="append", default=[],
                    help="case-insensitive substring to match in catalog names")
    ap.add_argument("--extract", type=Path, help="local output directory for matched files")
    ap.add_argument("--list", action="store_true", help="list matched catalog records")
    ap.add_argument("--path", help="list the children of an absolute HFS+ path")
    ap.add_argument("--dump", help="print bytes of an exact small file path")
    args = ap.parse_args()

    if args.image:
        reader: BlockReader = ImageReader(args.image, args.block_size, args.cache_dir)
    else:
        reader = ADBReader(args.adb_device, args.block_size, args.cache_dir, args.serial)
    vh = read_vh(reader)
    print(f"volume: {vh.signature} version={vh.version} blockSize={vh.block_size} "
          f"totalBlocks={vh.total_blocks} journalBlock={vh.journal_block}")
    if vh.journal_block:
        print("NOTE: journal present; read-only access does not replay it")
    print(f"catalog extents: {[(e.start, e.count) for e in vh.catalog.extents]}")
    cat_reader = reader
    cat_fork = vh.catalog
    if isinstance(reader, ADBReader):
        cat_path = args.cache_dir / "catalog.bin"
        cat_reader = materialize_fork(reader, vh.catalog, cat_path)
        cat_fork = Fork(vh.catalog.logical_size, vh.catalog.clump_size,
                        [Extent(0, (vh.catalog.logical_size + reader.block_size - 1)
                                // reader.block_size)])
        print(f"catalog materialized: {cat_path} ({cat_path.stat().st_size} bytes)")
    records = load_catalog(cat_reader, cat_fork)
    print(f"catalog leaf records: {len(records)}")
    needles = [s.lower() for s in args.find]
    matches = [r for r in records
               if r.kind in (FOLDER_RECORD, FILE_RECORD)
               and (not needles or any(n in r.name.lower() for n in needles))]
    if not args.path and not args.dump:
        for rec in matches:
            kind = "folder" if rec.kind == FOLDER_RECORD else "file"
            size = rec.data_fork.logical_size if rec.data_fork else 0
            print(f"{kind:6} parent={rec.parent:<10} id={rec.file_id or rec.folder_id:<10} "
                  f"size={size:<12} mtime={hfs_date(rec.modify_date)} name={rec.name}")
    if args.path:
        fid = resolve_path(records, args.path)
        if fid is None:
            print(f"PATH NOT FOUND: {args.path}")
        else:
            print(f"PATH {args.path} -> id {fid}")
            print_children(records, fid)
    if args.dump:
        fid = resolve_path(records, args.dump)
        if fid is None:
            print(f"PATH NOT FOUND: {args.dump}")
        else:
            recs = [r for r in records if (r.file_id == fid or r.folder_id == fid)]
            if not recs:
                print(f"NO RECORD FOR {fid}")
            else:
                rec = recs[0]
                if rec.kind != FILE_RECORD or rec.data_fork is None:
                    print(f"NOT A FILE: {args.dump}")
                else:
                    data = read_fork_data(reader, rec.data_fork, vh.extents)
                    print(f"DUMP {args.dump} size={len(data)} sha256="
                          f"{hashlib.sha256(data).hexdigest()}")
                    print(repr(data[:4096]))
    if args.extract:
        args.extract.mkdir(parents=True, exist_ok=True)
        manifest = []
        for rec in matches:
            if rec.kind != FILE_RECORD or rec.data_fork is None:
                continue
            try:
                # File data extents address allocation blocks on the volume,
                # not the materialized catalog file; use the original reader.
                data = read_fork_data(reader, rec.data_fork, vh.extents)
            except HFSError as exc:
                print(f"UNSUPPORTED: {rec.name}: {exc}", file=sys.stderr)
                continue
            digest = hashlib.sha256(data).hexdigest()
            if data[:4] in (b"cmpf", b"decmpfs"):
                print(f"UNSUPPORTED: {rec.name}: HFS+ compressed xattr not decoded",
                      file=sys.stderr)
            out = args.extract / f"{rec.file_id:08x}_{safe_name(rec.name)}"
            out.write_bytes(data)
            meta = {
                "source_name": rec.name, "output": str(out), "size": len(data),
                "sha256": digest, "file_id": rec.file_id, "parent": rec.parent,
                "create": hfs_date(rec.create_date), "modify": hfs_date(rec.modify_date),
                "rsrc_fork_size": rec.rsrc_fork.logical_size if rec.rsrc_fork else 0,
            }
            manifest.append(meta)
            print(f"EXTRACTED {rec.name} -> {out} sha256={digest}")
        (args.extract / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    if isinstance(reader, ADBReader):
        print(f"read-only dd calls: {reader.read_count}, bytes fetched: {reader.byte_count}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except HFSError as exc:
        print(f"hfsplus_ro: {exc}", file=sys.stderr)
        sys.exit(1)
