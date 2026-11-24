#!/usr/bin/env python3
"""Package the M30 shim + payload as generic Android boot image v0 files.

The raw ``combined.bin`` is retained as a separately named, non-flashable
intermediate. This tool makes no claim that Samsung S-Boot accepts its output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

import mkpayload

PAGE_SIZE = 2048
DEFAULT_PAYLOAD_OFFSET = 0x20000
BASE = 0x80000000
KERNEL_OFFSET = 0x80000
KERNEL_ADDR = BASE + KERNEL_OFFSET
RAMDISK_OFFSET = 0x200000
SECOND_OFFSET = 0x00F00000
TAGS_OFFSET = 0x100
MAX_BOOT_SIZE = 32 * 1024 * 1024
ELF_MAGIC = b"\x7fELF"
ELFCLASS64 = 2
ELFDATA2LSB = 1
EM_AARCH64 = 183
PT_LOAD = 1
SHT_SYMTAB = 2


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def relative_path(path: Path, out_dir: Path) -> str:
    """Return a stable path relative to the output directory."""
    return Path(os.path.relpath(path.resolve(), out_dir.resolve())).as_posix()


def _elf_string(blob: bytes, offset: int) -> str:
    require(offset < len(blob), "ELF string-table offset is out of bounds")
    end = blob.find(b"\0", offset)
    require(end >= 0, "unterminated ELF string")
    return blob[offset:end].decode("ascii", errors="strict")


def parse_elf_layout(data: bytes) -> dict:
    """Parse the linked load extent, stack bounds, and binary projection."""
    require(len(data) >= 64 and data[:4] == ELF_MAGIC, "shim is not an ELF file")
    require(data[4] == ELFCLASS64 and data[5] == ELFDATA2LSB, "shim is not little-endian ELF64")
    require(struct.unpack_from("<H", data, 18)[0] == EM_AARCH64, "shim ELF is not AArch64")

    entry = struct.unpack_from("<Q", data, 24)[0]
    phoff = struct.unpack_from("<Q", data, 32)[0]
    shoff = struct.unpack_from("<Q", data, 40)[0]
    phentsize = struct.unpack_from("<H", data, 54)[0]
    phnum = struct.unpack_from("<H", data, 56)[0]
    shentsize = struct.unpack_from("<H", data, 58)[0]
    shnum = struct.unpack_from("<H", data, 60)[0]

    require(phentsize >= 56 and phnum > 0, "shim ELF has no usable program headers")
    require(shentsize >= 64 and shnum > 0, "shim ELF has no usable section headers")
    require(phoff + phentsize * phnum <= len(data), "shim program-header table exceeds file")
    require(shoff + shentsize * shnum <= len(data), "shim section-header table exceeds file")

    loads = []
    for index in range(phnum):
        offset = phoff + index * phentsize
        p_type, _flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, _align = struct.unpack_from(
            "<IIQQQQQQ", data, offset
        )
        if p_type != PT_LOAD:
            continue
        require(p_filesz <= p_memsz, "shim ELF has a load segment with filesz > memsz")
        require(p_offset + p_filesz <= len(data), "shim ELF load segment exceeds file")
        loads.append(
            {
                "offset": p_offset,
                "vaddr": p_vaddr,
                "paddr": p_paddr,
                "filesz": p_filesz,
                "memsz": p_memsz,
            }
        )
    require(loads, "shim ELF has no PT_LOAD segment")

    sections = []
    for index in range(shnum):
        offset = shoff + index * shentsize
        sh_name, sh_type, _sh_flags, _sh_addr, sh_offset, sh_size, sh_link, _sh_info, _sh_align, sh_entsize = struct.unpack_from(
            "<IIQQQQIIQQ", data, offset
        )
        require(sh_offset + sh_size <= len(data), "shim ELF section exceeds file")
        sections.append(
            {
                "name": sh_name,
                "type": sh_type,
                "offset": sh_offset,
                "size": sh_size,
                "link": sh_link,
                "entsize": sh_entsize,
            }
        )

    symbols: dict[str, int] = {}
    for section in sections:
        if section["type"] != SHT_SYMTAB:
            continue
        require(section["link"] < len(sections), "shim symbol table has invalid string-table link")
        strings = sections[section["link"]]
        string_data = data[strings["offset"]:strings["offset"] + strings["size"]]
        require(section["entsize"] >= 24, "shim symbol-table entries are too small")
        count = section["size"] // section["entsize"]
        for index in range(count):
            offset = section["offset"] + index * section["entsize"]
            st_name, _st_info, _st_other, _st_shndx, st_value, _st_size = struct.unpack_from(
                "<IBBHQQ", data, offset
            )
            name = _elf_string(string_data, st_name)
            if name:
                symbols[name] = st_value
        break

    require("_end" in symbols, "shim ELF does not expose the linker-script _end symbol")
    require("_stack_top" in symbols, "shim ELF does not expose the linker-script _stack_top symbol")
    load_start = min(segment["vaddr"] for segment in loads)
    load_file_end = max(segment["vaddr"] + segment["filesz"] for segment in loads)
    load_mem_end = max(segment["vaddr"] + segment["memsz"] for segment in loads)
    footprint_end = max(load_mem_end, symbols["_end"])
    require(symbols["_stack_top"] <= footprint_end, "shim stack top lies beyond linked footprint")
    require(symbols["_stack_top"] >= load_start, "shim stack top lies below linked load extent")

    return {
        "entry": entry,
        "load_start": load_start,
        "load_file_end": load_file_end,
        "load_mem_end": load_mem_end,
        "footprint_end": footprint_end,
        "stack_top": symbols["_stack_top"],
        "symbols": symbols,
        "loads": loads,
    }


def elf_binary_projection(data: bytes, layout: dict) -> bytes:
    """Reconstruct the byte image emitted by ``objcopy -O binary``."""
    loads = layout["loads"]
    start = layout["load_start"]
    end = max(segment["vaddr"] + segment["filesz"] for segment in loads)
    output = bytearray(end - start)
    occupied: list[tuple[int, int]] = []
    for segment in loads:
        relative = segment["vaddr"] - start
        segment_end = relative + segment["filesz"]
        for old_start, old_end in occupied:
            require(segment_end <= old_start or relative >= old_end, "overlapping shim ELF load segments")
        occupied.append((relative, segment_end))
        output[relative:segment_end] = data[segment["offset"]:segment["offset"] + segment["filesz"]]
    return bytes(output)


def parse_payload(payload: bytes) -> dict[str, int | str]:
    if len(payload) < 0x48 or payload[:8] != b"M30LTXNU":
        raise ValueError("XNU payload has no M30LTXNU header")
    version, nsegs = struct.unpack_from("<II", payload, 8)
    if version != 1:
        raise ValueError(f"unsupported M30LTXNU version {version}")
    virt_base, entry, adt_off, adt_size, kernel_end, phys_base, mem_size = struct.unpack_from(
        "<7Q", payload, 0x10
    )
    cmdline = payload[0x48:0x48 + 608].split(b"\0", 1)[0].decode("ascii")
    seg_table_end = 0x2A8 + 32 * nsegs
    if seg_table_end > len(payload):
        raise ValueError("payload segment table exceeds payload")
    if adt_off < seg_table_end or adt_off + adt_size > len(payload):
        raise ValueError("payload ADT range is invalid")
    for i in range(nsegs):
        _vmaddr, _vmsize, file_off, file_size = struct.unpack_from("<4Q", payload, 0x2A8 + 32 * i)
        if file_off + file_size > len(payload):
            raise ValueError(f"payload segment {i} exceeds payload bounds")
    return {
        "version": version,
        "segment_count": nsegs,
        "virt_base": virt_base,
        "entry_va": entry,
        "adt_offset": adt_off,
        "adt_size": adt_size,
        "kernel_end_va": kernel_end,
        "phys_base": phys_base,
        "mem_size": mem_size,
        "cmdline": cmdline,
    }


def run_mkbootimg(
    executable: str,
    kernel: Path,
    ramdisk: Path,
    output: Path,
    cmdline: str,
) -> None:
    args = [
        executable,
        "--header_version", "0",
        "--kernel", str(kernel),
        "--ramdisk", str(ramdisk),
        "--base", hex(BASE),
        "--kernel_offset", hex(KERNEL_OFFSET),
        "--ramdisk_offset", hex(RAMDISK_OFFSET),
        "--second_offset", hex(SECOND_OFFSET),
        "--tags_offset", hex(TAGS_OFFSET),
        "--pagesize", str(PAGE_SIZE),
        "--os_version", "10.0.0",
        "--os_patch_level", "2020-05",
        "--board", "m30lte",
        "--cmdline", cmdline,
        "--output", str(output),
    ]
    subprocess.run(args, check=True)


def image_component_layout(path: Path) -> tuple[dict, dict]:
    image = path.read_bytes()
    if image[:8] != b"ANDROID!":
        raise ValueError(f"mkbootimg output has bad magic: {path}")
    kernel_size, kernel_addr, ramdisk_size, ramdisk_addr, second_size, second_addr, tags_addr, page_size, version, os_version = struct.unpack_from(
        "<10I", image, 8
    )
    if version != 0 or page_size != PAGE_SIZE:
        raise ValueError(f"unexpected mkbootimg output version/page size: {version}/{page_size}")
    cursor = page_size
    components = {"header": {"offset": 0, "size_bytes": page_size, "end": page_size}}
    for name, size in (("kernel", kernel_size), ("ramdisk", ramdisk_size), ("second", second_size)):
        start = cursor
        end = start + size
        components[name] = {"offset": start, "size_bytes": size, "end": end}
        cursor = ((end + page_size - 1) // page_size * page_size) if size else start
    if cursor != len(image):
        raise ValueError(f"mkbootimg output layout mismatch: expected {cursor}, got {len(image)}")
    board = image[48:64].split(b"\0", 1)[0].decode("ascii")
    cmdline = image[64:576].split(b"\0", 1)[0].decode("ascii")
    extra_cmdline = image[608:1632].split(b"\0", 1)[0].decode("ascii")
    return (
        {
            "version": version,
            "page_size": page_size,
            "kernel_size": kernel_size,
            "kernel_addr": hex(kernel_addr),
            "ramdisk_size": ramdisk_size,
            "ramdisk_addr": hex(ramdisk_addr),
            "second_size": second_size,
            "second_addr": hex(second_addr),
            "tags_addr": hex(tags_addr),
            "os_version_raw": hex(os_version),
            "board": board,
            "cmdline": cmdline + extra_cmdline,
            "image_id_sha1": image[576:596].hex(),
        },
        components,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shim-image", required=True, type=Path)
    parser.add_argument("--shim-elf", required=True, type=Path)
    parser.add_argument("--payload", required=True, type=Path, help="M30LTXNU payload generated from XNU + ADT")
    parser.add_argument("--kernel", required=True, type=Path, help="untouched source XNU kernel used to generate payload")
    parser.add_argument("--adt", required=True, type=Path, help="exact ADT used to generate payload")
    parser.add_argument("--expected-kernel-sha256", help="optional required SHA256 for the source kernel")
    parser.add_argument("--expected-payload-sha256", help="optional required SHA256 for the payload")
    parser.add_argument("--expected-shim-image-sha256", help="optional required SHA256 for the shim image")
    parser.add_argument("--expected-shim-elf-sha256", help="optional required SHA256 for the shim ELF")
    parser.add_argument("--payload-offset", type=lambda value: int(value, 0), default=DEFAULT_PAYLOAD_OFFSET)
    parser.add_argument("--project-root", required=True, type=Path, help="stable root used for reproducible manifest paths")
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--mkbootimg", default=shutil.which("mkbootimg"))
    args = parser.parse_args()

    if not args.mkbootimg:
        raise SystemExit("mkbootimg was not found; install/provide it before packaging")
    require(args.payload_offset > 0 and args.payload_offset % 0x1000 == 0, "payload offset must be a positive 4-KiB multiple")
    require(args.payload_offset < MAX_BOOT_SIZE, "payload offset exceeds the boot-partition limit")

    kernel_hash = sha256(args.kernel)
    if args.expected_kernel_sha256 and kernel_hash != args.expected_kernel_sha256.lower():
        raise SystemExit(f"kernel SHA256 mismatch; refusing package: {args.kernel}")

    shim = args.shim_image.read_bytes()
    shim_hash = hashlib.sha256(shim).hexdigest()
    if args.expected_shim_image_sha256 and shim_hash != args.expected_shim_image_sha256.lower():
        raise SystemExit(f"shim image SHA256 mismatch; refusing package: {args.shim_image}")
    shim_elf = args.shim_elf.read_bytes()
    shim_elf_hash = hashlib.sha256(shim_elf).hexdigest()
    if args.expected_shim_elf_sha256 and shim_elf_hash != args.expected_shim_elf_sha256.lower():
        raise SystemExit(f"shim ELF SHA256 mismatch; refusing package: {args.shim_elf}")

    payload = args.payload.read_bytes()
    payload_hash = hashlib.sha256(payload).hexdigest()
    if args.expected_payload_sha256 and payload_hash != args.expected_payload_sha256.lower():
        raise SystemExit(f"payload SHA256 mismatch; refusing package: {args.payload}")

    payload_info = parse_payload(payload)
    regenerated_payload, _ = mkpayload.build(args.kernel, args.adt, payload_info["cmdline"])
    if regenerated_payload != payload:
        raise SystemExit(
            "payload is not the byte-exact output of the supplied kernel + ADT; refusing package"
        )

    elf_layout = parse_elf_layout(shim_elf)
    require(elf_layout["entry"] == KERNEL_ADDR, f"shim ELF entry 0x{elf_layout['entry']:x} does not match configured kernel address 0x{KERNEL_ADDR:x}")
    require(elf_layout["load_start"] == KERNEL_ADDR, "shim ELF load extent does not start at the configured kernel address")
    require(
        elf_layout["footprint_end"] <= KERNEL_ADDR + args.payload_offset,
        "shim ELF linked footprint overlaps the embedded payload slot",
    )
    projected_image = elf_binary_projection(shim_elf, elf_layout)
    require(shim == projected_image, "shim Image is not the byte-exact binary projection of the supplied ELF")
    require(len(shim) <= args.payload_offset, f"shim is {len(shim)} bytes; it exceeds the 0x{args.payload_offset:x} payload slot")

    pad_size = args.payload_offset - len(shim)
    combined = shim + b"\0" * pad_size + payload
    args.out_dir.mkdir(parents=True, exist_ok=True)
    combined_path = args.out_dir / "combined.bin"
    atomic_write(combined_path, combined)

    image_specs = {
        "shim-boot.img": "console=null",
        "ios-boot.img": "debug=0xc keepsyms=1",
    }
    image_manifest: dict[str, dict] = {}
    with tempfile.TemporaryDirectory(prefix=".boot-package-", dir=args.out_dir) as temp_dir:
        temp = Path(temp_dir)
        empty_ramdisk = temp / "empty-ramdisk"
        empty_ramdisk.write_bytes(b"")
        for filename, cmdline in image_specs.items():
            temporary_image = temp / filename
            run_mkbootimg(args.mkbootimg, combined_path, empty_ramdisk, temporary_image, cmdline)
            os.replace(temporary_image, args.out_dir / filename)
            image_path = args.out_dir / filename
            header, components = image_component_layout(image_path)
            image_manifest[filename] = {
                "size_bytes": image_path.stat().st_size,
                "sha256": sha256(image_path),
                "cmdline": cmdline,
                "header_version": 0,
                "header_fields": header,
                "component_layout": components,
            }

    manifest = {
        "format": "generic Android boot image v0 generated by mkbootimg; Samsung S-Boot acceptance is unverified",
        "path_base": "project_root",
        "partition_limit_bytes": MAX_BOOT_SIZE,
        "kernel_source": {
            "path": relative_path(args.kernel, args.project_root),
            "size_bytes": args.kernel.stat().st_size,
            "sha256": kernel_hash,
            "expected_sha256": args.expected_kernel_sha256.lower() if args.expected_kernel_sha256 else None,
            "hash_matches_expected": args.expected_kernel_sha256 is None or kernel_hash == args.expected_kernel_sha256.lower(),
        },
        "shim": {
            "image_path": relative_path(args.shim_image, args.project_root),
            "size_bytes": len(shim),
            "sha256": shim_hash,
            "elf_path": relative_path(args.shim_elf, args.project_root),
            "elf_size_bytes": len(shim_elf),
            "elf_sha256": shim_elf_hash,
            "elf_entry": hex(elf_layout["entry"]),
            "linked_address": hex(KERNEL_ADDR),
            "image_is_elf_binary_projection": True,
            "elf_footprint": {
                "load_start": hex(elf_layout["load_start"]),
                "load_file_end": hex(elf_layout["load_file_end"]),
                "load_mem_end": hex(elf_layout["load_mem_end"]),
                "linked_end": hex(elf_layout["symbols"]["_end"]),
                "footprint_end": hex(elf_layout["footprint_end"]),
                "stack_top": hex(elf_layout["stack_top"]),
                "size_bytes": elf_layout["footprint_end"] - elf_layout["load_start"],
            },
        },
        "payload": {
            "path": relative_path(args.payload, args.project_root),
            "size_bytes": len(payload),
            "sha256": payload_hash,
            "expected_sha256": args.expected_payload_sha256.lower() if args.expected_payload_sha256 else None,
            "hash_matches_expected": args.expected_payload_sha256 is None or payload_hash == args.expected_payload_sha256.lower(),
            "source_kernel_sha256": kernel_hash,
            "source_adt": {
                "path": relative_path(args.adt, args.project_root),
                "size_bytes": args.adt.stat().st_size,
                "sha256": sha256(args.adt),
            },
            "regenerated_from_source_kernel_and_adt": True,
            **{
                key: hex(value)
                if key in {
                    "virt_base",
                    "entry_va",
                    "adt_offset",
                    "adt_size",
                    "kernel_end_va",
                    "phys_base",
                    "mem_size",
                }
                else value
                for key, value in payload_info.items()
            },
        },
        "raw_combined": {
            "path": combined_path.name,
            "size_bytes": len(combined),
            "sha256": sha256(combined_path),
            "shim_offset": 0,
            "shim_size_bytes": len(shim),
            "zero_padding_offset": len(shim),
            "zero_padding_size_bytes": pad_size,
            "payload_offset": args.payload_offset,
            "payload_size_bytes": len(payload),
            "is_android_boot_image": False,
        },
        "runtime_layout": {
            "kernel_component_load_address": hex(KERNEL_ADDR),
            "shim_elf_footprint_end": hex(elf_layout["footprint_end"]),
            "shim_stack_top": hex(elf_layout["stack_top"]),
            "payload_offset_in_kernel": args.payload_offset,
            "payload_runtime_address": hex(KERNEL_ADDR + args.payload_offset),
            "payload_after_complete_shim_footprint": True,
        },
        "android_boot_components": {
            "page_size": PAGE_SIZE,
            "header_version": 0,
            "kernel_address": hex(KERNEL_ADDR),
            "kernel": {"source": combined_path.name, "size_bytes": len(combined)},
            "payload_offset_in_kernel": args.payload_offset,
            "payload_offset_in_image": PAGE_SIZE + args.payload_offset,
            "payload_size_bytes": len(payload),
            "ramdisk": {"size_bytes": 0, "included": False},
            "second": {"size_bytes": 0, "included": False},
            "recovery_dtbo": {"size_bytes": 0, "included": False},
            "dtb": {"size_bytes": 0, "included": False, "reason": "v0 has no DTB field; M30 ADT is embedded in M30LTXNU payload"},
            "layout": "header page then page-aligned kernel; ramdisk and second-stage are empty",
        },
        "images": image_manifest,
    }
    atomic_write(args.out_dir / "manifest.json", (json.dumps(manifest, indent=2) + "\n").encode())
    print(json.dumps({"output_dir": str(args.out_dir), "images": image_manifest}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, struct.error) as exc:
        raise SystemExit(f"PACKAGING FAILED: {exc}") from exc
