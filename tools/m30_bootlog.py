#!/usr/bin/env python3
"""M30LTE boot log capture via ramoops pmsg.

The XNU kernel patch 0406-m30-console-pmsg-mirror.patch mirrors the framebuffer
console into the ramoops pmsg zone (0x92404000). After a boot, TWRP exposes that
zone at /sys/fs/pstore/pmsg-ramoops-0. This tool pulls it, decodes records, and
writes a timestamped, append-only log.

Commands:
  start      pull pmsg from a connected device in recovery, decode, append to log
  inspect    show records from a raw pmsg file or the latest capture
  export     export decoded records as text/JSON

Usage:
  python3 tools/m30_bootlog.py start
  python3 tools/m30_bootlog.py inspect
  python3 tools/m30_bootlog.py export --format text -o boot.txt

Offline validation:
  python3 tools/m30_bootlog.py selftest
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

RECORD_MAGIC = 0x6C
HEADER_LEN = 19
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIR = ROOT / "validation" / "bootlog"
PMSG_SYSFS = "/sys/fs/pstore/pmsg-ramoops-0"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def utcnow() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def plausible(data: bytes, pos: int) -> bool:
    if pos < 0 or pos + 2 > len(data):
        return False
    if data[pos] != RECORD_MAGIC:
        return False
    length = data[pos + 1]
    return HEADER_LEN <= length <= 0xFF and pos + length <= len(data)


def decode(data: bytes) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    issues: list[str] = []
    pos = 0
    idx = 0
    while pos < len(data):
        if not plausible(data, pos):
            # resync
            nxt = data.find(bytes([RECORD_MAGIC]), pos + 1)
            if nxt < 0 or nxt >= len(data):
                break
            issues.append(f"gap at {pos:#x}: skipped {nxt - pos} bytes")
            pos = nxt
            continue
        length = data[pos + 1]
        rec = data[pos:pos + length]
        payload = rec[HEADER_LEN:]
        nul = payload.find(b"\0")
        if nul == -1:
            tag, message = "", payload.decode("utf-8", "replace")
        else:
            tag = payload[:nul].decode("utf-8", "replace")
            msg = payload[nul + 1:]
            if msg.endswith(b"\0"):
                msg = msg[:-1]
            message = msg.decode("utf-8", "replace")
        records.append({
            "index": idx,
            "offset": pos,
            "length": length,
            "metadata_hex": rec[2:HEADER_LEN].hex(),
            "tag": tag,
            "message": message,
        })
        idx += 1
        pos += length
    return records, issues


def run_adb(args: list[str]) -> bytes:
    return subprocess.run(["adb"] + args, check=True, capture_output=True).stdout


def cmd_start(args) -> int:
    d = Path(args.dir)
    d.mkdir(parents=True, exist_ok=True)
    ts = utcnow()
    raw = run_adb(["exec-out", f"cat {PMSG_SYSFS}"])
    raw_path = d / f"pmsg-{ts}.bin"
    raw_path.write_bytes(raw)
    records, issues = decode(raw)
    log_path = d / f"bootlog-{ts}.jsonl"
    with log_path.open("a") as f:
        for r in records:
            r["captured_at"] = ts
            r["source_sha256"] = sha(raw)
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"captured {len(raw)} bytes -> {raw_path}")
    print(f"decoded {len(records)} records ({len(issues)} issues) -> {log_path}")
    for r in records[:20]:
        print(f"  [{r['index']:03d}] {r['tag']}: {r['message'][:120]}")
    if len(records) > 20:
        print(f"  ... {len(records)-20} more (see log)")
    return 0


def cmd_inspect(args) -> int:
    p = Path(args.file) if args.file else None
    if p is None:
        logs = sorted(Path(args.dir).glob("pmsg-*.bin"))
        if not logs:
            print("no captures found; run 'start' first", file=sys.stderr)
            return 1
        p = logs[-1]
    data = p.read_bytes()
    records, issues = decode(data)
    print(f"file: {p}  bytes={len(data)}  sha256={sha(data)}")
    print(f"records={len(records)} issues={len(issues)}")
    for r in records:
        print(f"  [{r['index']:03d}] @{r['offset']:#08x} {r['tag']}: {r['message']}")
    for i in issues:
        print(f"  ISSUE: {i}")
    return 0


def cmd_export(args) -> int:
    # gather all jsonl logs in dir
    logs = sorted(Path(args.dir).glob("bootlog-*.jsonl"))
    out: list[dict] = []
    seen: set[str] = set()
    for log in logs:
        for line in log.read_text().splitlines():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            key = (r.get("captured_at"), r.get("offset"), r.get("source_sha256"))
            if key in seen:
                continue
            seen.add(key)
            out.append(r)
    out.sort(key=lambda r: (r.get("captured_at", ""), r.get("offset", 0)))
    if args.format == "json":
        text = json.dumps(out, ensure_ascii=False, indent=2)
    else:
        lines = ["# M30LTE boot log (merged, timestamped)"]
        for r in out:
            lines.append(
                f"[{r.get('captured_at','?')}] [{r['index']:03d}] "
                f"{r.get('tag','')}: {r.get('message','')}"
            )
        text = "\n".join(lines) + "\n"
    if args.output:
        Path(args.output).write_text(text)
        print(f"wrote {args.output} ({len(out)} records)")
    else:
        print(text)
    return 0


def make_synthetic_pmsg() -> bytes:
    """Build a synthetic pmsg zone (header + framed records) for offline tests."""
    buf = bytearray()
    # persistent_ram_buffer header: sig, start, size
    sig = 0x43474244
    data = bytearray()
    for msg in [b"iboot version: m30lte-shim", b"M30 XNU Stage 1: arm_init entered", b"panic: test"]:
        tag = b"XNU"
        rec = bytearray()
        rec.append(RECORD_MAGIC)
        rec_len = HEADER_LEN + len(tag) + 1 + len(msg) + 1
        rec.append(rec_len)
        rec += b"\0" * 17
        rec += tag + b"\0" + msg + b"\0"
        data += rec
    start = (len(data) - HEADER_LEN) % (len(data) - HEADER_LEN or 1)
    # For synthetic: start=0, size=len(data); reader reads data[0:size]
    hdr = struct.pack("<III", sig, 0, len(data))
    return bytes(hdr + data)


def cmd_selftest(args) -> int:
    blob = make_synthetic_pmsg()
    # decoder expects sysfs content (data area only, no header)
    records, issues = decode(blob[12:])
    assert len(records) == 3, f"expected 3 records, got {len(records)}"
    assert not issues, f"unexpected issues: {issues}"
    assert records[0]["tag"] == "XNU"
    assert "m30lte-shim" in records[0]["message"]
    assert records[2]["message"] == "panic: test"
    # corrupt byte should be handled without raising
    bad = blob[12:20] + b"\xff" + blob[21:]
    r2, i2 = decode(bad)
    print("selftest PASS: synthetic pmsg round-trip + defensive decode")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", default=str(DEFAULT_DIR), help="capture directory")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("start")
    ins = sub.add_parser("inspect"); ins.add_argument("--file")
    exp = sub.add_parser("export"); exp.add_argument("--format", choices=["text","json"], default="text"); exp.add_argument("-o", "--output")
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "start":
        return cmd_start(args)
    if args.cmd == "inspect":
        return cmd_inspect(args)
    if args.cmd == "export":
        return cmd_export(args)
    if args.cmd == "selftest":
        return cmd_selftest(args)
    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
