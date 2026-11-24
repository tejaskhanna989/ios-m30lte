#!/usr/bin/env python3
"""Read-only HFSX catalogue/data-fork helper for the M30 USERDATA partition.

This tool never writes to the device.  All device access is through
`adb exec-out dd ... 2>/dev/null`, and every operation is a READ from
/dev/block/by-name/USERDATA.

It understands the hardlink layout used by the iOS root image on USERDATA:
a catalog entry such as dyld_shared_cache_arm64.symbols is often an old-style
'hlnk'/'hfs+' stub whose real data fork lives in an iNode* file below the
private hardlink directory.
"""

import argparse
import json
import struct
import subprocess
import sys

BLOCK_SIZE_FALLBACK = 4096
VOLUME_HEADER_OFFSET = 1024
ROOT_FOLDER_ID = 2
PRIVATE_FILE_LINK_NAME = "\x00\x00\x00\x00HFS+ Private Data"
HARD_LINK_FILE_TYPE = 0x686C6E6B  # 'hlnk'
HFS_PLUS_CREATOR = 0x6866732B     # 'hfs+'
REC_FOLDER = 1
REC_FILE = 2
REC_FOLDER_THREAD = 3
REC_FILE_THREAD = 4


class HFSXError(Exception):
    pass


class BlockReader:
    def __init__(self, partition="USERDATA", serial=None):
        self.partition = partition
        self.serial = serial

    def _device_path(self):
        if self.partition != "USERDATA":
            raise HFSXError("only USERDATA is permitted")
        return "/dev/block/by-name/USERDATA"

    def check_identity(self):
        if self.serial is None:
            return
        props = {}
        for name in (
            "ro.boot.em.model",
            "ro.product.device",
            "ro.serialno",
            "ro.boot.serialno",
            "ro.twrp.boot",
        ):
            out = subprocess.run(
                ["adb", "shell", "getprop", name],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                check=True,
                text=True,
            ).stdout.strip()
            props[name] = out
        expected = {
            "ro.boot.em.model": "SM-M305F",
            "ro.product.device": "m30lte",
            "ro.serialno": self.serial,
            "ro.boot.serialno": self.serial,
            "ro.twrp.boot": "1",
        }
        for name, want in expected.items():
            if props.get(name) != want:
                raise HFSXError(
                    f"identity mismatch {name}: got {props.get(name)!r}, want {want!r}"
                )

    def read_blocks(self, start, count, block_size=BLOCK_SIZE_FALLBACK):
        if count <= 0:
            return b""
        cmd = (
            f"dd if={self._device_path()} bs={block_size} "
            f"skip={start} count={count} 2>/dev/null"
        )
        proc = subprocess.run(
            ["adb", "exec-out", cmd], stdout=subprocess.PIPE, check=True
        )
        want = count * block_size
        if len(proc.stdout) != want:
            raise HFSXError(
                f"short block read at {start}:{count}: got {len(proc.stdout)}, want {want}"
            )
        return proc.stdout

    def read_bytes(self, offset, length, block_size=BLOCK_SIZE_FALLBACK):
        if length <= 0:
            return b""
        first = offset // block_size
        last = (offset + length - 1) // block_size
        data = self.read_blocks(first, last - first + 1, block_size)
        begin = offset - first * block_size
        return data[begin:begin + length]


def parse_fork(data, off):
    if len(data) < off + 80:
        raise HFSXError("short fork data")
    logical, clump, total = struct.unpack_from(">QII", data, off)
    extents = []
    for i in range(8):
        start, blocks = struct.unpack_from(">II", data, off + 16 + i * 8)
        if blocks:
            extents.append((start, blocks))
    return {
        "logical": logical,
        "clump": clump,
        "total_blocks": total,
        "extents": extents,
    }


class BTree:
    def __init__(self, name, data, node_size):
        self.name = name
        self.data = data
        self.node_size = node_size
        if len(data) < node_size:
            raise HFSXError(f"{name}: data shorter than one node")
        (f_link, b_link, kind, height, nrec) = struct.unpack_from(">IIBBH", data, 0)
        (
            self.depth,
            self.root,
            self.leaf_nodes,
            self.first_leaf,
            self.last_leaf,
            self.node_size,
            self.key_length,
            self.total_nodes,
            self.free_nodes,
        ) = struct.unpack_from(">IIIIIHHII", data, 12)
        if len(data) < self.total_nodes * self.node_size:
            raise HFSXError(
                f"{name}: fork has {len(data)} bytes but tree declares "
                f"{self.total_nodes} nodes of {self.node_size}"
            )

    def node(self, number):
        if number < 0 or number >= self.total_nodes:
            raise HFSXError(f"{self.name}: bad node {number}")
        start = number * self.node_size
        return self.data[start:start + self.node_size]

    @staticmethod
    def descriptor(node):
        return struct.unpack_from(">IIBBH", node, 0)

    def record_offsets(self, node):
        _f, _b, _kind, _height, nrec = self.descriptor(node)
        # HFS stores the offset table at the end of the node in reverse
        # physical order; reading it from the end yields key order.
        base = self.node_size - 2 * nrec
        return [struct.unpack_from(">H", node, base + 2 * i)[0] for i in range(nrec)]

    def iter_catalog_records(self):
        for number in range(self.total_nodes):
            node = self.node(number)
            _f, _b, kind, _height, _nrec = self.descriptor(node)
            if kind != 255:  # kBTLeafNode is -1 == 255
                continue
            for off in self.record_offsets(node):
                keylen = struct.unpack_from(">H", node, off)[0]
                parent = struct.unpack_from(">I", node, off + 2)[0]
                namelen = struct.unpack_from(">H", node, off + 6)[0]
                if off + 8 + 2 * namelen > self.node_size:
                    continue
                name = node[off + 8:off + 8 + 2 * namelen].decode(
                    "utf-16-be", "replace"
                )
                yield number, off, parent, name, off + 2 + keylen

    def iter_extent_records(self):
        for number in range(self.total_nodes):
            node = self.node(number)
            _f, _b, kind, _height, _nrec = self.descriptor(node)
            if kind != 255:
                continue
            for off in self.record_offsets(node):
                keylen = struct.unpack_from(">H", node, off)[0]
                file_id = struct.unpack_from(">I", node, off + 2)[0]
                fork_type = node[off + 6]
                start_block = struct.unpack_from(">I", node, off + 7)[0]
                rec = off + 2 + keylen
                exts = []
                for i in range(8):
                    p, n = struct.unpack_from(">II", node, rec + i * 8)
                    if n:
                        exts.append((p, n))
                yield number, off, file_id, fork_type, start_block, exts


class HFSXVolume:
    def __init__(self, reader):
        self.reader = reader
        raw = reader.read_bytes(VOLUME_HEADER_OFFSET, 512)
        sig = raw[0:2].decode("latin1")
        if sig not in ("H+", "HX"):
            raise HFSXError(f"bad volume signature {sig!r}")
        self.signature = sig
        self.version = struct.unpack_from(">H", raw, 2)[0]
        self.block_size = struct.unpack_from(">I", raw, 40)[0]
        self.total_blocks = struct.unpack_from(">I", raw, 44)[0]
        self.allocation_file = parse_fork(raw, 112)
        self.extents_file = parse_fork(raw, 192)
        self.catalog_file = parse_fork(raw, 272)
        self.attributes_file = parse_fork(raw, 352)
        self.startup_file = parse_fork(raw, 432)
        self.reader.block_size = self.block_size
        self._catalog_data = None
        self._extents_data = None
        self._catalog = None
        self._extents = None

    def read_fork(self, fork):
        out = []
        logical = 0
        for phys, count in fork["extents"]:
            out.append(self.reader.read_blocks(phys, count, self.block_size))
            logical += count
        data = b"".join(out)
        need = fork["total_blocks"] * self.block_size
        if fork["logical"] and len(data) < min(fork["logical"], need):
            raise HFSXError(
                f"short fork read: got {len(data)}, logical {fork['logical']}"
            )
        return data

    @property
    def catalog(self):
        if self._catalog is None:
            self._catalog_data = self.read_fork(self.catalog_file)
            node_size = struct.unpack_from(">H", self._catalog_data, 12 + 20)[0]
            self._catalog = BTree("catalog", self._catalog_data, node_size)
        return self._catalog

    @property
    def extents(self):
        if self._extents is None:
            self._extents_data = self.read_fork(self.extents_file)
            node_size = struct.unpack_from(">H", self._extents_data, 12 + 20)[0]
            self._extents = BTree("extents", self._extents_data, node_size)
        return self._extents

    def find_records(self, parent, name):
        hits = []
        for node, off, p, n, rec in self.catalog.iter_catalog_records():
            if p == parent and n == name:
                hits.append((node, off, rec))
        return hits

    def find_one(self, parent, name, want_types=None):
        hits = self.find_records(parent, name)
        if want_types is not None:
            hits = [h for h in hits if struct.unpack_from(">H", self.catalog.node(h[0]), h[2])[0] in want_types]
        if not hits:
            raise HFSXError(f"catalog lookup failed for parent={parent} name={name!r}")
        return hits[0]

    def resolve_path(self, path, want_type=REC_FILE):
        parts = [p for p in path.split("/") if p]
        if not parts:
            raise HFSXError("empty path")
        parent = ROOT_FOLDER_ID
        for part in parts[:-1]:
            node, _off, rec = self.find_one(parent, part, (REC_FOLDER,))
            parent = struct.unpack_from(">I", self.catalog.node(node), rec + 8)[0]
        node, _off, rec = self.find_one(parent, parts[-1], (want_type,))
        return node, rec

    def private_file_dir_id(self):
        node, _off, rec = self.find_one(ROOT_FOLDER_ID, PRIVATE_FILE_LINK_NAME, (REC_FOLDER,))
        return struct.unpack_from(">I", self.catalog.node(node), rec + 8)[0]

    def record(self, node, off):
        b = self.catalog.node(node)
        rec_type = struct.unpack_from(">H", b, off)[0]
        flags = struct.unpack_from(">H", b, off + 2)[0]
        file_id = struct.unpack_from(">I", b, off + 8)[0]
        fd_type = struct.unpack_from(">I", b, off + 48)[0]
        fd_creator = struct.unpack_from(">I", b, off + 52)[0]
        return {
            "node": node,
            "offset": off,
            "type": rec_type,
            "flags": flags,
            "file_id": file_id,
            "fd_type": fd_type,
            "fd_creator": fd_creator,
        }

    def resolve_hardlink(self, node, off):
        b = self.catalog.node(node)
        fd_type = struct.unpack_from(">I", b, off + 48)[0]
        fd_creator = struct.unpack_from(">I", b, off + 52)[0]
        if fd_type != HARD_LINK_FILE_TYPE or fd_creator != HFS_PLUS_CREATOR:
            return node, off, None
        link_ref = struct.unpack_from(">I", b, off + 44)[0]
        private_id = self.private_file_dir_id()
        inode_name = f"iNode{link_ref}"
        inode_node, _inode_off, inode_rec = self.find_one(
            private_id, inode_name, (REC_FILE,)
        )
        return inode_node, inode_rec, link_ref

    def fork_for_record(self, node, off):
        b = self.catalog.node(node)
        fork = parse_fork(b, off + 88)
        file_id = struct.unpack_from(">I", b, off + 8)[0]
        covered = sum(n for _p, n in fork["extents"])
        if fork["total_blocks"] > covered:
            logical = covered
            for _n, _o, fid, fork_type, start, exts in self.extents.iter_extent_records():
                if fid != file_id or fork_type != 0:
                    continue
                if start != logical:
                    continue
                for phys, count in exts:
                    fork["extents"].append((phys, count))
                    logical += count
        fork["file_id"] = file_id
        return fork

    def open_file(self, path):
        node, off = self.resolve_path(path, REC_FILE)
        node, off, link_ref = self.resolve_hardlink(node, off)
        fork = self.fork_for_record(node, off)
        return HFSXFile(self, fork, link_ref)

    def info(self):
        return {
            "signature": self.signature,
            "version": self.version,
            "block_size": self.block_size,
            "total_blocks": self.total_blocks,
            "catalog": self.catalog_file,
            "extents": self.extents_file,
            "catalog_tree": {
                "depth": self.catalog.depth,
                "root": self.catalog.root,
                "total_nodes": self.catalog.total_nodes,
                "node_size": self.catalog.node_size,
                "key_length": self.catalog.key_length,
            },
            "extents_tree": {
                "depth": self.extents.depth,
                "root": self.extents.root,
                "total_nodes": self.extents.total_nodes,
                "node_size": self.extents.node_size,
                "key_length": self.extents.key_length,
            },
        }


class HFSXFile:
    def __init__(self, volume, fork, link_ref=None):
        self.volume = volume
        self.fork = fork
        self.link_ref = link_ref
        self.block_size = volume.block_size
        mapping = []
        logical = 0
        for phys, count in fork["extents"]:
            mapping.append((logical, phys, count))
            logical += count
        self.mapping = mapping

    def read(self, offset, length):
        if offset < 0 or length < 0:
            raise HFSXError("negative file range")
        if length == 0:
            return b""
        limit = self.fork["logical"] or sum(n for _p, n in self.fork["extents"]) * self.block_size
        if offset + length > limit:
            raise HFSXError(
                f"read past EOF: offset={offset} length={length} limit={limit}"
            )
        out = []
        done = 0
        while done < length:
            pos = offset + done
            lb = pos // self.block_size
            inblock = pos % self.block_size
            found = None
            for logical, phys, count in self.mapping:
                if logical <= lb < logical + count:
                    found = (phys + (lb - logical), inblock)
                    break
            if found is None:
                raise HFSXError(f"no extent maps logical block {lb}")
            phys, inblock = found
            take = min(self.block_size - inblock, length - done)
            data = self.volume.reader.read_blocks(phys, 1, self.block_size)
            out.append(data[inblock:inblock + take])
            done += take
        return b"".join(out)

    def describe(self, path):
        return {
            "path": path,
            "file_id": self.fork["file_id"],
            "link_ref": self.link_ref,
            "logical_size": self.fork["logical"],
            "total_blocks": self.fork["total_blocks"],
            "extents": self.fork["extents"],
        }


DEFAULT_SYMBOLS_PATH = (
    "/private/preboot/Cryptexes/OS/System/Library/Caches/com.apple.dyld/"
    "dyld_shared_cache_arm64.symbols"
)


class DyldSymbols:
    """Minimal reader for dyld shared-cache local symbols in a .symbols file."""

    def __init__(self, hfs_file):
        self.file = hfs_file
        hdr = hfs_file.read(0, 96)
        self.magic = hdr[:16]
        if self.magic[:6] != b"dyld_v":
            raise HFSXError(f"not a dyld cache: magic={self.magic!r}")
        self.mapping_off = struct.unpack_from("<I", hdr, 16)[0]
        self.mapping_count = struct.unpack_from("<I", hdr, 20)[0]
        self.local_symbols_off = struct.unpack_from("<Q", hdr, 72)[0]
        if self.local_symbols_off == 0:
            raise HFSXError("no local symbols table")
        lsi = hfs_file.read(self.local_symbols_off, 24)
        (
            self.nlist_off,
            self.nlist_count,
            self.str_off,
            self.str_size,
            self.entries_off,
            self.entries_count,
        ) = struct.unpack_from("<IIIIII", lsi)
        self.entry_size = 16 if self.mapping_off >= 400 else 12

    def symbol_name(self, n_strx, size=256):
        if n_strx >= self.str_size:
            return f"<bad strx {n_strx}>"
        want = min(size, self.str_size - n_strx)
        raw = self.file.read(self.local_symbols_off + self.str_off + n_strx, want)
        end = raw.find(b"\0")
        if end >= 0:
            raw = raw[:end]
        return raw.decode("utf-8", "replace")

    def nearest(self, address, count=8):
        best = []
        step = 65536
        for start in range(0, self.nlist_count, step):
            n = min(step, self.nlist_count - start)
            buf = self.file.read(
                self.local_symbols_off + self.nlist_off + start * 16, n * 16
            )
            for i in range(n):
                strx, ntype, nsect, ndesc, value = struct.unpack_from(
                    "<IBBHQ", buf, i * 16
                )
                if value == 0 or value > address:
                    continue
                item = (value, strx, ntype, nsect, ndesc, start + i)
                best.append(item)
                if len(best) > 8192:
                    best.sort(reverse=True)
                    del best[8192:]
        best.sort(reverse=True)
        out = []
        for value, strx, ntype, nsect, ndesc, index in best[:count]:
            out.append(
                {
                    "value": hex(value),
                    "offset": hex(address - value),
                    "index": index,
                    "n_type": ntype,
                    "n_sect": nsect,
                    "n_desc": ndesc,
                    "name": self.symbol_name(strx),
                }
            )
        return out

    def find_name(self, wanted, limit=20):
        found = []
        step = 65536
        want = wanted.encode()
        for start in range(0, self.nlist_count, step):
            n = min(step, self.nlist_count - start)
            buf = self.file.read(
                self.local_symbols_off + self.nlist_off + start * 16, n * 16
            )
            for i in range(n):
                strx, ntype, nsect, ndesc, value = struct.unpack_from(
                    "<IBBHQ", buf, i * 16
                )
                name = self.symbol_name(strx, 128)
                if name == wanted or (limit > 1 and want in name.encode("utf-8", "replace")):
                    found.append(
                        {
                            "value": hex(value),
                            "index": start + i,
                            "name": name,
                            "n_type": ntype,
                        }
                    )
                    if len(found) >= limit:
                        return found
        return found


def build_parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--partition", default="USERDATA")
    p.add_argument("--serial", default="320081735bb166a3")
    p.add_argument("--no-identity-check", action="store_true")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("info")

    lookup = sub.add_parser("lookup")
    lookup.add_argument("path")

    dump = sub.add_parser("dump")
    dump.add_argument("path")
    dump.add_argument("output")
    dump.add_argument("--offset", type=int, default=0)
    dump.add_argument("--length", type=int, default=0)

    syms = sub.add_parser("symbols")
    syms.add_argument("addresses", nargs="+")
    syms.add_argument("--path", default=DEFAULT_SYMBOLS_PATH)
    syms.add_argument("--count", type=int, default=8)

    find = sub.add_parser("find")
    find.add_argument("name")
    find.add_argument("--path", default=DEFAULT_SYMBOLS_PATH)
    find.add_argument("--limit", type=int, default=20)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    reader = BlockReader(args.partition, None if args.no_identity_check else args.serial)
    reader.check_identity()
    vol = HFSXVolume(reader)

    if args.command == "info":
        print(json.dumps(vol.info(), indent=2, sort_keys=True))
        return 0

    if args.command == "lookup":
        f = vol.open_file(args.path)
        print(json.dumps(f.describe(args.path), indent=2, sort_keys=True))
        return 0

    if args.command == "dump":
        f = vol.open_file(args.path)
        length = args.length or (
            f.fork["logical"] - args.offset
        )
        data = f.read(args.offset, length)
        with open(args.output, "wb") as out:
            out.write(data)
        print(
            json.dumps(
                {
                    "output": args.output,
                    "offset": args.offset,
                    "length": len(data),
                    "sha256": __import__("hashlib").sha256(data).hexdigest(),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "symbols":
        f = vol.open_file(args.path)
        dyld = DyldSymbols(f)
        result = {
            "path": args.path,
            "magic": dyld.magic.decode("latin1"),
            "mapping_off": hex(dyld.mapping_off),
            "mapping_count": dyld.mapping_count,
            "local_symbols_off": hex(dyld.local_symbols_off),
            "nlist_off": hex(dyld.nlist_off),
            "nlist_count": dyld.nlist_count,
            "str_off": hex(dyld.str_off),
            "str_size": dyld.str_size,
            "entries_off": hex(dyld.entries_off),
            "entries_count": dyld.entries_count,
            "entry_size": dyld.entry_size,
            "addresses": {},
        }
        for raw in args.addresses:
            addr = int(raw, 0)
            result["addresses"][hex(addr)] = dyld.nearest(addr, args.count)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    if args.command == "find":
        f = vol.open_file(args.path)
        dyld = DyldSymbols(f)
        print(json.dumps(dyld.find_name(args.name, args.limit), indent=2))
        return 0

    raise HFSXError(f"unknown command {args.command}")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except HFSXError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
