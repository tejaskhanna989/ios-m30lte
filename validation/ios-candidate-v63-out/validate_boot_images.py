#!/usr/bin/env python3
"""Independent read-only validation of packaged M30 Android boot images."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import tempfile

import adt
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
V0_HEADER_SIZE = 1632
ELFCLASS64 = 2
ELFDATA2LSB = 1
EM_AARCH64 = 183
PT_LOAD = 1
SHT_SYMTAB = 2
LC_SEGMENT_64 = 0x19
LC_UNIXTHREAD = 0x5
LC_DYLD_CHAINED_FIXUPS = 0x80000034
MACH_HEADER_SIZE = 32


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def aligned(value: int, alignment: int) -> int:
    return (value + alignment - 1) // alignment * alignment


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


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
    return Path(os.path.relpath(path.resolve(), out_dir.resolve())).as_posix()


def resolve_manifest_path(value: str, out_dir: Path) -> Path:
    require(isinstance(value, str) and value != "", "manifest path is empty")
    path = Path(value)
    require(not path.is_absolute(), f"manifest path must be relative to out_dir: {value}")
    return (out_dir / path).resolve()


def _read_c_string(blob: bytes, offset: int) -> str:
    require(offset < len(blob), "ELF string offset is invalid")
    end = blob.find(b"\0", offset)
    require(end != -1, "ELF string is not terminated")
    return blob[offset:end].decode("ascii")


def parse_shim_elf(data: bytes) -> dict:
    """Independently parse the shim's linked footprint and binary image."""
    require(len(data) >= 64 and data[:4] == b"\x7fELF", "shim is not an ELF file")
    require(data[4] == ELFCLASS64 and data[5] == ELFDATA2LSB, "shim is not little-endian ELF64")
    require(struct.unpack_from("<H", data, 18)[0] == EM_AARCH64, "shim ELF is not AArch64")

    entry = struct.unpack_from("<Q", data, 24)[0]
    phoff = struct.unpack_from("<Q", data, 32)[0]
    shoff = struct.unpack_from("<Q", data, 40)[0]
    phentsize = struct.unpack_from("<H", data, 54)[0]
    phnum = struct.unpack_from("<H", data, 56)[0]
    shentsize = struct.unpack_from("<H", data, 58)[0]
    shnum = struct.unpack_from("<H", data, 60)[0]
    require(phentsize >= 56 and phnum > 0, "shim ELF program headers are invalid")
    require(shentsize >= 64 and shnum > 0, "shim ELF section headers are invalid")
    require(phoff + phentsize * phnum <= len(data), "shim program headers exceed file")
    require(shoff + shentsize * shnum <= len(data), "shim section headers exceed file")

    load_segments = []
    for index in range(phnum):
        offset = phoff + index * phentsize
        p_type, _flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, _align = struct.unpack_from(
            "<IIQQQQQQ", data, offset
        )
        if p_type == PT_LOAD:
            require(p_offset + p_filesz <= len(data), "shim PT_LOAD segment exceeds file")
            require(p_filesz <= p_memsz, "shim PT_LOAD segment has filesz > memsz")
            load_segments.append(
                {
                    "file_offset": p_offset,
                    "vaddr": p_vaddr,
                    "paddr": p_paddr,
                    "file_size": p_filesz,
                    "memory_size": p_memsz,
                }
            )
    require(load_segments, "shim ELF contains no PT_LOAD segment")

    sections = []
    for index in range(shnum):
        offset = shoff + index * shentsize
        values = struct.unpack_from("<IIQQQQIIQQ", data, offset)
        sh_type = values[1]
        sh_offset = values[4]
        sh_size = values[5]
        sh_link = values[6]
        sh_entsize = values[9]
        require(sh_offset + sh_size <= len(data), "shim ELF section exceeds file")
        sections.append(
            {
                "type": sh_type,
                "offset": sh_offset,
                "size": sh_size,
                "link": sh_link,
                "entry_size": sh_entsize,
            }
        )

    symbols: dict[str, int] = {}
    for section in sections:
        if section["type"] != SHT_SYMTAB:
            continue
        require(section["link"] < len(sections), "shim symbol-table string link is invalid")
        string_section = sections[section["link"]]
        strings = data[string_section["offset"]:string_section["offset"] + string_section["size"]]
        require(section["entry_size"] >= 24, "shim ELF symbol entry is too small")
        for index in range(section["size"] // section["entry_size"]):
            offset = section["offset"] + index * section["entry_size"]
            st_name, _info, _other, _shndx, st_value, _size = struct.unpack_from(
                "<IBBHQQ", data, offset
            )
            name = _read_c_string(strings, st_name)
            if name:
                symbols[name] = st_value
        break

    require("_end" in symbols, "shim ELF lacks _end")
    require("_stack_top" in symbols, "shim ELF lacks _stack_top")
    load_start = min(segment["vaddr"] for segment in load_segments)
    load_file_end = max(segment["vaddr"] + segment["file_size"] for segment in load_segments)
    load_memory_end = max(segment["vaddr"] + segment["memory_size"] for segment in load_segments)
    footprint_end = max(load_memory_end, symbols["_end"])
    require(symbols["_stack_top"] <= footprint_end, "shim stack top exceeds linked footprint")
    require(symbols["_stack_top"] >= load_start, "shim stack top precedes linked load extent")

    image_start = load_start
    image_end = max(segment["vaddr"] + segment["file_size"] for segment in load_segments)
    projected = bytearray(image_end - image_start)
    for segment in load_segments:
        relative = segment["vaddr"] - image_start
        end = relative + segment["file_size"]
        projected[relative:end] = data[
            segment["file_offset"]:segment["file_offset"] + segment["file_size"]
        ]

    return {
        "entry": entry,
        "load_start": load_start,
        "load_file_end": load_file_end,
        "load_memory_end": load_memory_end,
        "footprint_end": footprint_end,
        "stack_top": symbols["_stack_top"],
        "linked_end": symbols["_end"],
        "binary_projection": bytes(projected),
        "load_segments": load_segments,
    }


def parse_payload(payload: bytes) -> dict:
    require(len(payload) >= 0x48 and payload[:8] == b"M30LTXNU", "missing M30LTXNU payload magic")
    version, nsegs = struct.unpack_from("<II", payload, 8)
    require(version == 1, f"unsupported payload version {version}")
    virt_base, entry, adt_off, adt_size, kernel_end, phys_base, mem_size = struct.unpack_from("<7Q", payload, 0x10)
    cmdline = payload[0x48:0x48 + 608].split(b"\0", 1)[0].decode("ascii")
    seg_end = 0x2A8 + 32 * nsegs
    require(seg_end <= len(payload), "payload segment table exceeds payload")
    require(adt_off >= seg_end and adt_off + adt_size <= len(payload), "ADT bounds exceed payload")
    segments = []
    for index in range(nsegs):
        vmaddr, vmsize, file_off, file_size = struct.unpack_from("<4Q", payload, 0x2A8 + 32 * index)
        require(file_off + file_size <= len(payload), f"payload segment {index} exceeds payload bounds")
        segments.append(
            {
                "vmaddr": vmaddr,
                "vmsize": vmsize,
                "file_offset": file_off,
                "file_size": file_size,
            }
        )
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
        "segments": segments,
    }


def parse_macho_layout(data: bytes) -> dict:
    require(len(data) >= MACH_HEADER_SIZE, "source kernel is truncated")
    magic, _cputype, _cpusubtype, _filetype, command_count, command_bytes, _flags, _reserved = struct.unpack_from(
        "<8I", data, 0
    )
    require(magic == 0xFEEDFACF, "source kernel is not a 64-bit Mach-O")
    require(MACH_HEADER_SIZE + command_bytes <= len(data), "Mach-O load commands exceed file")
    offset = MACH_HEADER_SIZE
    segments = []
    entry = None
    chained_fixups = False
    for _index in range(command_count):
        require(offset + 8 <= len(data), "truncated Mach-O load command")
        command, size = struct.unpack_from("<II", data, offset)
        require(size >= 8 and offset + size <= len(data), "invalid Mach-O load-command size")
        if command == LC_SEGMENT_64:
            name, vmaddr, vmsize, fileoff, filesize = struct.unpack_from("<16sQQQQ", data, offset + 8)
            require(fileoff + filesize <= len(data), "Mach-O segment exceeds file")
            segments.append(
                {
                    "name": name.split(b"\0", 1)[0].decode("ascii"),
                    "vmaddr": vmaddr,
                    "vmsize": vmsize,
                    "fileoff": fileoff,
                    "filesize": filesize,
                }
            )
        elif command == LC_UNIXTHREAD:
            entry = struct.unpack_from("<Q", data, offset + 16 + 32 * 8)[0]
        elif command == LC_DYLD_CHAINED_FIXUPS:
            chained_fixups = True
        offset += size
    require(entry is not None, "source Mach-O has no LC_UNIXTHREAD entry point")
    segments = [segment for segment in segments if segment["vmsize"]]
    require(segments and segments[0]["name"] == "__TEXT", "source Mach-O has no __TEXT segment")
    require(not chained_fixups, "independent payload-source check does not support chained fixups")
    return {"segments": segments, "entry": entry}


def adt_dram(blob: bytes) -> tuple[int, int]:
    root, _end = adt.parse(blob)
    chosen = next((child for child in root.children if child.name == "chosen"), None)
    require(chosen is not None, "ADT has no /chosen node")
    dram_base = chosen.prop("dram-base")
    dram_size = chosen.prop("dram-size")
    require(dram_base is not None and len(dram_base) == 8, "ADT has invalid dram-base")
    require(dram_size is not None and len(dram_size) == 8, "ADT has invalid dram-size")
    return struct.unpack("<Q", dram_base)[0], struct.unpack("<Q", dram_size)[0]


def independently_validate_payload_sources(payload: bytes, kernel: bytes, adt_blob: bytes, payload_info: dict) -> None:
    """Check payload semantics without using the payload generator."""
    macho = parse_macho_layout(kernel)
    segments = macho["segments"]
    require(payload_info["segment_count"] == len(segments), "payload segment count differs from source Mach-O")
    expected_virt_base = segments[0]["vmaddr"] & ~(0x2000000 - 1)
    expected_kernel_end = max(segment["vmaddr"] + segment["vmsize"] for segment in segments)
    expected_kernel_end = aligned(expected_kernel_end, 0x4000)
    expected_phys_base, expected_mem_size = adt_dram(adt_blob)
    require(payload_info["virt_base"] == expected_virt_base, "payload virt_base differs from source Mach-O")
    require(payload_info["entry_va"] == macho["entry"], "payload entry differs from source Mach-O")
    require(payload_info["kernel_end_va"] == expected_kernel_end, "payload kernel_end differs from source Mach-O")
    require(payload_info["phys_base"] == expected_phys_base, "payload phys_base differs from source ADT")
    require(payload_info["mem_size"] == expected_mem_size, "payload mem_size differs from source ADT")

    for index, (source, embedded) in enumerate(zip(segments, payload_info["segments"])):
        require(embedded["vmaddr"] == source["vmaddr"], f"payload segment {index} vmaddr differs from source")
        require(embedded["vmsize"] == source["vmsize"], f"payload segment {index} vmsize differs from source")
        require(embedded["file_size"] == source["filesize"], f"payload segment {index} file_size differs from source")
        source_bytes = kernel[source["fileoff"]:source["fileoff"] + source["filesize"]]
        payload_bytes = payload[embedded["file_offset"]:embedded["file_offset"] + embedded["file_size"]]
        require(payload_bytes == source_bytes, f"payload segment {index} bytes differ from source Mach-O")

    adt_offset = payload_info["adt_offset"]
    adt_size = payload_info["adt_size"]
    require(payload[adt_offset:adt_offset + adt_size] == adt_blob, "embedded ADT differs from supplied ADT")


def inspect_image(
    path: Path,
    combined: bytes,
    payload: bytes,
    expected_cmdline: str,
    shim_entry: int,
    payload_offset: int,
) -> dict:
    image = path.read_bytes()
    require(image[:8] == b"ANDROID!", f"{path.name}: invalid Android boot magic")
    require(len(image) >= PAGE_SIZE, f"{path.name}: truncated boot header page")
    fields = struct.unpack_from("<10I", image, 8)
    kernel_size, kernel_addr, ramdisk_size, ramdisk_addr, second_size, second_addr, tags_addr, page_size, version, os_version = fields
    require(version == 0, f"{path.name}: header version {version}, expected 0")
    require(page_size == PAGE_SIZE, f"{path.name}: page size {page_size}, expected {PAGE_SIZE}")
    require(len(image) >= V0_HEADER_SIZE, f"{path.name}: incomplete v0 header")
    require(kernel_addr == KERNEL_ADDR == shim_entry, f"{path.name}: kernel address does not match linked shim entry")
    require(ramdisk_addr == 0, f"{path.name}: unexpected ramdisk address for an empty ramdisk")
    require(second_addr == 0, f"{path.name}: unexpected second-stage address for an empty second stage")
    require(tags_addr == BASE + TAGS_OFFSET, f"{path.name}: tags address mismatch")
    require(kernel_size == len(combined), f"{path.name}: kernel field {kernel_size} != combined size {len(combined)}")
    require(ramdisk_size == 0, f"{path.name}: unexpected non-empty ramdisk ({ramdisk_size} bytes)")
    require(second_size == 0, f"{path.name}: unexpected second-stage component")

    board = image[48:64].split(b"\0", 1)[0].decode("ascii")
    require(board == "m30lte", f"{path.name}: board name mismatch")
    cmdline = image[64:576].split(b"\0", 1)[0].decode("ascii")
    extra_cmdline = image[608:1632].split(b"\0", 1)[0].decode("ascii")
    actual_cmdline = cmdline + extra_cmdline
    require(actual_cmdline == expected_cmdline, f"{path.name}: cmdline mismatch: {actual_cmdline!r}")
    image_id = hashlib.sha1()
    image_id.update(combined)
    image_id.update(struct.pack("<III", len(combined), 0, 0))
    require(image[576:596].hex() == image_id.hexdigest(), f"{path.name}: v0 image ID does not match the kernel component")

    components: dict[str, dict[str, int]] = {
        "header": {"offset": 0, "size_bytes": page_size, "end": page_size}
    }
    cursor = page_size
    for name, size in (
        ("kernel", kernel_size),
        ("ramdisk", ramdisk_size),
        ("second", second_size),
    ):
        start = cursor
        end = start + size
        require(start % page_size == 0, f"{path.name}: {name} start is not page aligned")
        require(end <= len(image), f"{path.name}: {name} range exceeds image")
        components[name] = {"offset": start, "size_bytes": size, "end": end}
        cursor = aligned(end, page_size) if size else start

    require(image[components["kernel"]["offset"]:components["kernel"]["end"]] == combined,
            f"{path.name}: kernel bytes differ from the raw combined input")
    extracted_payload = image[
        components["kernel"]["offset"] + payload_offset:
        components["kernel"]["offset"] + payload_offset + len(payload)
    ]
    require(extracted_payload == payload, f"{path.name}: XNU payload was not preserved byte-for-byte")
    require(components["kernel"]["offset"] + payload_offset + len(payload) <= components["kernel"]["end"],
            f"{path.name}: payload exceeds kernel component")
    require(cursor == len(image), f"{path.name}: trailing/truncated data; expected {cursor}, found {len(image)}")
    require(len(image) <= MAX_BOOT_SIZE, f"{path.name}: image exceeds 32-MiB partition limit")

    header = {
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
        "cmdline": actual_cmdline,
        "image_id_sha1": image[576:596].hex(),
    }
    return {
        "path": path.name,
        "size_bytes": len(image),
        "sha256": sha256(image),
        "header": header,
        "components": components,
        "partition_limit_bytes": MAX_BOOT_SIZE,
        "partition_size_compatible": True,
        "combined_kernel_exact": True,
        "payload_offset_in_kernel": payload_offset,
        "payload_size_bytes": len(payload),
        "payload_sha256": sha256(extracted_payload),
        "structurally_valid_generic_android_v0": True,
        "sboot_compatible": "unknown; no exact SM-M305F acceptance evidence",
    }


def validate(args: argparse.Namespace) -> dict:
    require(args.payload_offset > 0 and args.payload_offset % 0x1000 == 0, "payload offset must be a positive 4-KiB multiple")
    require(args.payload_offset < MAX_BOOT_SIZE, "payload offset exceeds the boot-partition limit")

    kernel = args.kernel.read_bytes()
    kernel_hash = sha256(kernel)
    if args.expected_kernel_sha256:
        require(kernel_hash == args.expected_kernel_sha256.lower(), f"source kernel SHA256 changed: {kernel_hash}")

    shim_elf = args.shim_elf.read_bytes()
    elf = parse_shim_elf(shim_elf)
    require(elf["entry"] == KERNEL_ADDR, f"shim entry 0x{elf['entry']:x} != configured address 0x{KERNEL_ADDR:x}")
    require(elf["load_start"] == KERNEL_ADDR, "shim ELF load extent does not start at the configured address")
    require(
        elf["footprint_end"] <= KERNEL_ADDR + args.payload_offset,
        "shim ELF linked footprint overlaps the embedded payload slot",
    )
    shim = args.shim_image.read_bytes()
    require(shim == elf["binary_projection"], "shim Image is not the byte-exact binary projection of the supplied ELF")

    payload = args.payload.read_bytes()
    payload_hash = sha256(payload)
    if args.expected_payload_sha256:
        require(payload_hash == args.expected_payload_sha256.lower(), f"payload SHA256 changed: {payload_hash}")
    payload_info = parse_payload(payload)
    regenerated_payload, _ = mkpayload.build(args.kernel, args.adt, payload_info["cmdline"])
    require(regenerated_payload == payload, "payload is not the byte-exact output of the supplied kernel + ADT")
    adt_blob = args.adt.read_bytes()
    independently_validate_payload_sources(payload, kernel, adt_blob, payload_info)

    padding_size = args.payload_offset - len(shim)
    require(padding_size >= 0, f"shim exceeds its 0x{args.payload_offset:x} payload slot")
    combined = shim + b"\0" * padding_size + payload
    require((args.out_dir / "combined.bin").read_bytes() == combined, "raw combined.bin does not match shim + pad + payload")

    expectations = {
        "shim-boot.img": "console=null",
        "ios-boot.img": "debug=0xc keepsyms=1",
    }
    images = [
        inspect_image(args.out_dir / name, combined, payload, cmdline, elf["entry"], args.payload_offset)
        for name, cmdline in expectations.items()
    ]

    manifest_path = args.out_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    require(manifest.get("path_base") == "project_root", "manifest does not declare project-root-relative paths")
    require(
        manifest.get("format") == "generic Android boot image v0 generated by mkbootimg; Samsung S-Boot acceptance is unverified",
        "manifest format description mismatch",
    )
    require(manifest.get("partition_limit_bytes") == MAX_BOOT_SIZE, "manifest partition limit mismatch")

    kernel_manifest = manifest["kernel_source"]
    require(resolve_manifest_path(kernel_manifest["path"], args.project_root) == args.kernel.resolve(), "manifest kernel path mismatch")
    require(kernel_manifest["size_bytes"] == len(kernel), "manifest kernel size mismatch")
    require(kernel_manifest["sha256"] == kernel_hash, "manifest kernel hash mismatch")
    if args.expected_kernel_sha256:
        require(kernel_manifest.get("expected_sha256") == args.expected_kernel_sha256.lower(), "manifest expected kernel hash mismatch")
        require(kernel_manifest.get("hash_matches_expected") is True, "manifest does not record the expected kernel hash match")

    shim_manifest = manifest["shim"]
    require(resolve_manifest_path(shim_manifest["image_path"], args.project_root) == args.shim_image.resolve(), "manifest shim image path mismatch")
    require(shim_manifest["size_bytes"] == len(shim), "manifest shim size mismatch")
    require(shim_manifest["sha256"] == sha256(shim), "manifest shim hash mismatch")
    require(resolve_manifest_path(shim_manifest["elf_path"], args.project_root) == args.shim_elf.resolve(), "manifest shim ELF path mismatch")
    require(shim_manifest["elf_size_bytes"] == len(shim_elf), "manifest shim ELF size mismatch")
    require(shim_manifest["elf_sha256"] == sha256(shim_elf), "manifest shim ELF hash mismatch")
    require(shim_manifest["elf_entry"] == hex(elf["entry"]), "manifest shim ELF entry mismatch")
    require(shim_manifest["linked_address"] == hex(KERNEL_ADDR), "manifest linked address mismatch")
    require(shim_manifest.get("image_is_elf_binary_projection") is True, "manifest lacks ELF binary-projection proof")
    require(
        shim_manifest.get("elf_footprint")
        == {
            "load_start": hex(elf["load_start"]),
            "load_file_end": hex(elf["load_file_end"]),
            "load_mem_end": hex(elf["load_memory_end"]),
            "linked_end": hex(elf["linked_end"]),
            "footprint_end": hex(elf["footprint_end"]),
            "stack_top": hex(elf["stack_top"]),
            "size_bytes": elf["footprint_end"] - elf["load_start"],
        },
        "manifest shim ELF footprint mismatch",
    )

    payload_manifest = manifest["payload"]
    require(resolve_manifest_path(payload_manifest["path"], args.project_root) == args.payload.resolve(), "manifest payload path mismatch")
    require(payload_manifest["size_bytes"] == len(payload), "manifest payload size mismatch")
    require(payload_manifest["sha256"] == payload_hash, "manifest payload hash mismatch")
    if args.expected_payload_sha256:
        require(payload_manifest.get("expected_sha256") == args.expected_payload_sha256.lower(), "manifest expected payload hash mismatch")
        require(payload_manifest.get("hash_matches_expected") is True, "manifest does not record the expected payload hash match")
    require(payload_manifest["source_kernel_sha256"] == kernel_hash, "manifest payload source kernel hash mismatch")
    require(resolve_manifest_path(payload_manifest["source_adt"]["path"], args.project_root) == args.adt.resolve(), "manifest payload source ADT path mismatch")
    require(payload_manifest["source_adt"]["size_bytes"] == len(adt_blob), "manifest payload source ADT size mismatch")
    require(payload_manifest["source_adt"]["sha256"] == sha256(adt_blob), "manifest payload source ADT hash mismatch")
    require(payload_manifest.get("regenerated_from_source_kernel_and_adt") is True, "manifest lacks payload regeneration proof")
    expected_payload_fields = {
        "version": payload_info["version"],
        "segment_count": payload_info["segment_count"],
        "virt_base": hex(payload_info["virt_base"]),
        "entry_va": hex(payload_info["entry_va"]),
        "adt_offset": hex(payload_info["adt_offset"]),
        "adt_size": hex(payload_info["adt_size"]),
        "kernel_end_va": hex(payload_info["kernel_end_va"]),
        "phys_base": hex(payload_info["phys_base"]),
        "mem_size": hex(payload_info["mem_size"]),
        "cmdline": payload_info["cmdline"],
    }
    for key, value in expected_payload_fields.items():
        require(payload_manifest.get(key) == value, f"manifest payload {key} mismatch")

    raw_manifest = manifest["raw_combined"]
    require(
        raw_manifest
        == {
            "path": "combined.bin",
            "size_bytes": len(combined),
            "sha256": sha256(combined),
            "shim_offset": 0,
            "shim_size_bytes": len(shim),
            "zero_padding_offset": len(shim),
            "zero_padding_size_bytes": padding_size,
            "payload_offset": args.payload_offset,
            "payload_size_bytes": len(payload),
            "is_android_boot_image": False,
        },
        "manifest raw combined.bin description mismatch",
    )

    require(
        manifest.get("runtime_layout")
        == {
            "kernel_component_load_address": hex(KERNEL_ADDR),
            "shim_elf_footprint_end": hex(elf["footprint_end"]),
            "shim_stack_top": hex(elf["stack_top"]),
            "payload_offset_in_kernel": args.payload_offset,
            "payload_runtime_address": hex(KERNEL_ADDR + args.payload_offset),
            "payload_after_complete_shim_footprint": True,
        },
        "manifest runtime-layout description mismatch",
    )

    components_manifest = manifest["android_boot_components"]
    require(components_manifest["page_size"] == PAGE_SIZE, "manifest page size mismatch")
    require(components_manifest["header_version"] == 0, "manifest header version mismatch")
    require(components_manifest["kernel_address"] == hex(KERNEL_ADDR), "manifest kernel address mismatch")
    require(components_manifest["kernel"] == {"source": "combined.bin", "size_bytes": len(combined)}, "manifest kernel component mismatch")
    require(components_manifest["payload_offset_in_kernel"] == args.payload_offset, "manifest payload kernel offset mismatch")
    require(components_manifest["payload_offset_in_image"] == PAGE_SIZE + args.payload_offset, "manifest payload image offset mismatch")
    require(components_manifest["payload_size_bytes"] == len(payload), "manifest payload component size mismatch")
    for name in ("ramdisk", "second", "recovery_dtbo", "dtb"):
        require(components_manifest[name]["size_bytes"] == 0, f"manifest {name} must be empty")
        require(components_manifest[name]["included"] is False, f"manifest {name} inclusion flag mismatch")

    for image in images:
        image_manifest = manifest["images"][image["path"]]
        require(image_manifest["size_bytes"] == image["size_bytes"], f"manifest identity size mismatch for {image['path']}")
        require(image_manifest["sha256"] == image["sha256"], f"manifest identity hash mismatch for {image['path']}")
        require(image_manifest["cmdline"] == image["header"]["cmdline"], f"manifest cmdline mismatch for {image['path']}")
        require(image_manifest["header_version"] == 0, f"manifest header version mismatch for {image['path']}")
        require(image_manifest["header_fields"] == image["header"], f"manifest header fields mismatch for {image['path']}")
        require(image_manifest["component_layout"] == image["components"], f"manifest component layout mismatch for {image['path']}")

    return {
        "result": "PASS",
        "source_kernel": {
            "path": relative_path(args.kernel, args.project_root),
            "size_bytes": len(kernel),
            "sha256": kernel_hash,
            "expected_sha256": args.expected_kernel_sha256.lower() if args.expected_kernel_sha256 else None,
            "hash_matches_expected": args.expected_kernel_sha256 is None or kernel_hash == args.expected_kernel_sha256.lower(),
        },
        "shim": {
            "image_path": relative_path(args.shim_image, args.project_root),
            "size_bytes": len(shim),
            "sha256": sha256(shim),
            "elf_path": relative_path(args.shim_elf, args.project_root),
            "elf_sha256": sha256(shim_elf),
            "entry": hex(elf["entry"]),
            "linked_and_header_address_match": True,
            "image_is_elf_binary_projection": True,
            "elf_footprint": {
                "load_start": hex(elf["load_start"]),
                "load_file_end": hex(elf["load_file_end"]),
                "load_mem_end": hex(elf["load_memory_end"]),
                "linked_end": hex(elf["linked_end"]),
                "footprint_end": hex(elf["footprint_end"]),
                "stack_top": hex(elf["stack_top"]),
                "size_bytes": elf["footprint_end"] - elf["load_start"],
            },
            "payload_after_complete_elf_footprint": True,
        },
        "raw_combined": {
            "size_bytes": len(combined),
            "sha256": sha256(combined),
            "is_android_boot_image": False,
            "shim_offset": 0,
            "zero_padding_offset": len(shim),
            "zero_padding_size_bytes": padding_size,
            "payload_offset": args.payload_offset,
            "payload_size_bytes": len(payload),
            "payload_sha256": payload_hash,
        },
        "payload_source": {
            "kernel_sha256": kernel_hash,
            "adt_path": relative_path(args.adt, args.project_root),
            "adt_sha256": sha256(adt_blob),
            "regenerated_from_source_kernel_and_adt": True,
            "independently_checked_against_source_macho_and_adt": True,
        },
        "manifest": {
            "path": relative_path(manifest_path, args.project_root),
            "sha256": sha256(manifest_path.read_bytes()),
            "path_base": "project_root",
            "kernel_source_matches": True,
            "payload_source_matches": True,
            "shim_matches": True,
            "elf_footprint_matches": True,
            "runtime_layout_matches": True,
            "header_and_component_metadata_matches": True,
            "image_hashes_match": True,
        },
        "xnu_payload_header": {key: value for key, value in payload_info.items() if key != "segments"},
        "images": images,
        "limitations": [
            "Generic Android boot-image structure does not establish Samsung S-Boot acceptance.",
            "The linked shim address is not proof of actual M30 S-Boot load or entry state.",
            "No physical boot, flash, or device operation was performed.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--shim-image", required=True, type=Path)
    parser.add_argument("--shim-elf", required=True, type=Path)
    parser.add_argument("--payload", required=True, type=Path)
    parser.add_argument("--kernel", required=True, type=Path)
    parser.add_argument("--adt", required=True, type=Path)
    parser.add_argument("--expected-kernel-sha256")
    parser.add_argument("--expected-payload-sha256")
    parser.add_argument("--payload-offset", type=lambda value: int(value, 0), default=DEFAULT_PAYLOAD_OFFSET)
    parser.add_argument("--project-root", required=True, type=Path, help="stable root used by the manifest")
    args = parser.parse_args()

    report = args.out_dir / "validation.json"
    try:
        report.unlink()
    except FileNotFoundError:
        pass

    try:
        result = validate(args)
    except Exception as exc:
        failure = {
            "result": "FAIL",
            "error": str(exc),
            "note": "This report replaces any earlier PASS result for this output directory.",
        }
        atomic_write(report, (json.dumps(failure, indent=2) + "\n").encode())
        print(f"VALIDATION FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    atomic_write(report, (json.dumps(result, indent=2) + "\n").encode())
    print(json.dumps({"result": "PASS", "images": result["images"], "validation": report.name}, indent=2))


if __name__ == "__main__":
    main()
