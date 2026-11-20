#!/usr/bin/env python3
"""Decode M30LTE pstore pmsg records (pmsg-ramoops-0) into readable text.

Framing verified on two independent SM-M305F captures (2250 and 3549 bytes):

    byte 0        : 0x6c record magic
    byte 1        : total record length, u8, including this 19-byte header
    bytes 2..18   : 17 opaque metadata bytes
    bytes 19..N-1 : tag\\0 message\\0

The decoder is defensive: it never trusts a length field before validating it
against the remaining input, reports every malformed/truncated record, and can
resynchronise at the next plausible record boundary. It never raises on bad
input, so it is safe to run on a partially overwritten ramoops zone.

Arch Linux usage:
    python3 decode_pmsg.py pmsg-ramoops-0.bin -o m30-xnu-boot.log
    python3 decode_pmsg.py pmsg-ramoops-0.bin --json report.json --strict
"""

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, asdict
from typing import List, Optional

RECORD_MAGIC = 0x6C
HEADER_LEN = 19          # magic + length + 17 metadata bytes
MIN_RECORD_LEN = HEADER_LEN
MAX_RECORD_LEN = 0xFF    # length is a single byte


@dataclass
class Record:
    index: int
    offset: int
    length: int
    metadata_hex: str
    tag: str
    message: str

    def as_text(self) -> str:
        tag = self.tag or "<no-tag>"
        return f"[{self.index:03d}] @{self.offset:#08x} len={self.length:3d} {tag}: {self.message}"


@dataclass
class Issue:
    offset: int
    kind: str
    detail: str


@dataclass
class DecodeResult:
    input_bytes: int
    input_sha256: str
    records: List[Record]
    issues: List[Issue]
    consumed: int

    @property
    def clean(self) -> bool:
        return not self.issues and self.consumed == self.input_bytes

    def text(self, include_metadata: bool = False) -> str:
        lines = [
            "# M30LTE pstore pmsg decode",
            f"# input_sha256={self.input_sha256}",
            f"# input_bytes={self.input_bytes} records={len(self.records)} "
            f"consumed={self.consumed} clean={self.clean}",
        ]
        for rec in self.records:
            lines.append(rec.as_text())
            if include_metadata:
                lines.append(f"#   metadata={rec.metadata_hex}")
        for issue in self.issues:
            lines.append(f"# ISSUE @{issue.offset:#08x} {issue.kind}: {issue.detail}")
        if not self.clean:
            lines.append("# WARNING: framing was not fully valid; output may be incomplete")
        return "\n".join(lines) + "\n"

    def as_dict(self) -> dict:
        return {
            "input_bytes": self.input_bytes,
            "input_sha256": self.input_sha256,
            "record_count": len(self.records),
            "consumed": self.consumed,
            "clean": self.clean,
            "records": [asdict(r) for r in self.records],
            "issues": [asdict(i) for i in self.issues],
        }


def _plausible(data: bytes, pos: int) -> bool:
    """True if a record can start at pos (magic + valid self-contained length)."""
    if pos < 0 or pos + 2 > len(data):
        return False
    if data[pos] != RECORD_MAGIC:
        return False
    length = data[pos + 1]
    return MIN_RECORD_LEN <= length <= MAX_RECORD_LEN and pos + length <= len(data)


def _resync(data: bytes, start: int) -> Optional[int]:
    """Find the next plausible record boundary at or after start."""
    pos = data.find(bytes([RECORD_MAGIC]), start)
    while pos != -1:
        if _plausible(data, pos):
            return pos
        pos = data.find(bytes([RECORD_MAGIC]), pos + 1)
    return None


def _split_tag_message(payload: bytes) -> (str, str):
    """Split tag\\0message\\0 defensively; never raises on missing NULs."""
    nul = payload.find(b"\x00")
    if nul == -1:
        return payload.decode("utf-8", "replace"), ""
    tag = payload[:nul].decode("utf-8", "replace")
    message = payload[nul + 1:].rstrip(b"\x00").decode("utf-8", "replace")
    return tag, message


def decode(data: bytes) -> DecodeResult:
    """Decode a raw pmsg buffer. Always returns a result; never raises on input."""
    records: List[Record] = []
    issues: List[Issue] = []
    pos = 0
    total = len(data)

    while pos < total:
        remaining = total - pos

        if remaining < 2:
            issues.append(Issue(pos, "truncated_header",
                                f"only {remaining} byte(s) left for a 2-byte framing header"))
            break

        if data[pos] != RECORD_MAGIC:
            issues.append(Issue(pos, "bad_magic",
                                f"expected {RECORD_MAGIC:#04x}, got {data[pos]:#04x}"))
            nxt = _resync(data, pos + 1)
            if nxt is None or nxt <= pos:
                break
            pos = nxt
            continue

        length = data[pos + 1]
        if length < MIN_RECORD_LEN:
            issues.append(Issue(pos, "short_length",
                                f"record length {length} < {MIN_RECORD_LEN}"))
            nxt = _resync(data, pos + 1)
            if nxt is None or nxt <= pos:
                break
            pos = nxt
            continue

        if length > remaining:
            issues.append(Issue(pos, "truncated_record",
                                f"length {length} but only {remaining} byte(s) remain"))
            nxt = _resync(data, pos + 2)
            if nxt is None or nxt <= pos:
                break
            pos = nxt
            continue

        payload = data[pos + HEADER_LEN:pos + length]
        metadata = data[pos + 2:pos + HEADER_LEN]
        tag, message = _split_tag_message(payload)
        records.append(Record(
            index=len(records),
            offset=pos,
            length=length,
            metadata_hex=metadata.hex(),
            tag=tag,
            message=message,
        ))
        pos += length

    return DecodeResult(
        input_bytes=total,
        input_sha256=hashlib.sha256(data).hexdigest(),
        records=records,
        issues=issues,
        consumed=pos,
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", help="raw pmsg-ramoops-0 binary ('-' for stdin)")
    parser.add_argument("-o", "--output", help="write decoded text here (default: stdout)")
    parser.add_argument("--json", dest="json_path", help="write structured validation report here")
    parser.add_argument("--metadata", action="store_true", help="include opaque metadata hex")
    parser.add_argument("--strict", action="store_true",
                        help="exit non-zero unless the buffer is fully clean")
    args = parser.parse_args(argv)

    if args.input == "-":
        data = sys.stdin.buffer.read()
    else:
        with open(args.input, "rb") as fh:
            data = fh.read()

    result = decode(data)
    text = result.text(include_metadata=args.metadata)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text)
    else:
        sys.stdout.write(text)

    if args.json_path:
        with open(args.json_path, "w", encoding="utf-8") as fh:
            json.dump(result.as_dict(), fh, indent=2)
            fh.write("\n")

    return 0 if (not args.strict or result.clean) else 1


if __name__ == "__main__":
    sys.exit(main())
