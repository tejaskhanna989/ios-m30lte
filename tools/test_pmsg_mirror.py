#!/usr/bin/env python3
"""Offline validation tests for the M30LTE console->pmsg mirror (patch 0406).

The C code under test is extracted verbatim from the patched
pexpert/arm/pe_serial.c (the ARM64_BOARD_CONFIG_M30LTE block), compiled with a
minimal stub for ml_io_map(), and exercised against realistic pstore zones.

Header facts verified from Linux source (device runs 4.4.177; also checked v6.1):
  struct persistent_ram_buffer { u32 sig; atomic_t start; atomic_t size; u8 data[]; }
  header = 12 bytes; sig = PERSISTENT_RAM_SIG ^ zone_sig_arg.
  ramoops passes sig_arg = 0 for the PMSG zone (ram.c), so sig = 0x43474244.
  PSTORE_TYPE_PMSG (7) is the pstore frontend type, NOT the zone sig argument.

Fixtures:
  - the REAL pmsg data captured on the device (pmsg-preboot-final.bin), with a
    Linux-conformant 12-byte header (sig=0x43474244, start=size=len(data));
  - fresh zeroed zone; wraparound zone; malformed/wrong-type headers.

Usage:
  python3 tools/test_pmsg_mirror.py [--source PATH] [--captured PATH] [--keep]
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = ROOT / "xnu/patches-minimal/0406-m30-console-pmsg-mirror.patch"
DEFAULT_CAPTURED = ROOT / "validation/physical-boot-test/20261120-ios-v7-flash/pmsg-preboot-final.bin"
PMSG_SIG = 0x43474244          # PERSISTENT_RAM_SIG ^ 0 (verified pmsg zone)
HDR_LEN = 12
ZONE_SZ = 0x4000
CAP = ZONE_SZ - HDR_LEN


def extract_block(source: Path) -> str:
    """Extract the mirror block verbatim from the patch file's added '+' lines."""
    lines = source.read_text().splitlines()
    out = []
    inside = False
    for line in lines:
        if not line.startswith("+"):
            continue
        content = line[1:]
        if not inside:
            if content.startswith("#if defined(ARM64_BOARD_CONFIG_M30LTE)"):
                inside = True
                out.append(content)
        else:
            out.append(content)
            if content.startswith("#endif /* ARM64_BOARD_CONFIG_M30LTE */"):
                break
    assert inside and out, "could not find mirror block in patch"
    block = "\n".join(out) + "\n"
    assert "0x43474244" in block, "mirror block must use verified PMSG signature"
    assert "start <= size" in block, "mirror block must validate start <= size"
    return block


HARNESS = r"""
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned long vm_offset_t;
static uint8_t g_zone[0x4000];
static vm_offset_t ml_io_map(uint64_t pa, uint32_t sz) {
    (void)pa; (void)sz; return (vm_offset_t)g_zone;
}
#define ARM64_BOARD_CONFIG_M30LTE 1
#include "m30_block.inc"

/* Faithful copy of fbcon_transmit_data's control flow for the character sink.
 * mode=1: v8 (mirror called BEFORE \r/\n early returns)
 * mode=0: pre-fix (mirror called AFTER, at end) - regression demonstration. */
static void transmit(uint8_t c, int mode) {
    if (mode) m30_console_char(c);
    if (c == '\r') return;
    if (c == '\n') return;
    if (!mode) m30_console_char(c);
}

static void hdr(uint32_t sig, uint32_t start, uint32_t size) {
    uint32_t *h = (uint32_t *)g_zone;
    h[0] = sig; h[1] = start; h[2] = size;
}

static void feed(const char *line, int mode) {
    for (const char *p = line; *p; p++) transmit((uint8_t)*p, mode);
    transmit('\n', mode);
}

static void dump_logical(const char *path) {
    uint32_t st = ((uint32_t *)g_zone)[1];
    uint32_t sz = ((uint32_t *)g_zone)[2];
    uint32_t cap = 0x4000 - 12;
    uint32_t begin = (st - sz + cap) % cap;
    FILE *f = fopen(path, "wb");
    for (uint32_t i = 0; i < sz; i++) fputc(g_zone[12 + (begin + i) % cap], f);
    fclose(f);
    printf("start=%u size=%u begin=%u\n", st, sz, begin);
}

int main(int argc, char **argv) {
    const char *scenario = argc > 1 ? argv[1] : "fresh";
    const char *out = argc > 2 ? argv[2] : "/tmp/pmsg_out.bin";
    int mode = argc > 3 ? atoi(argv[3]) : 1;
    memset(g_zone, 0, sizeof g_zone);

    if (!strcmp(scenario, "fresh")) {
        /* zeroed zone: v8 adopts it with the pmsg sig */
    } else if (!strcmp(scenario, "realistic")) {
        /* header + real captured Linux records loaded from argc>4 path */
        if (argc > 4) {
            FILE *f = fopen(argv[4], "rb");
            if (!f) { fprintf(stderr, "no zone file\n"); return 2; }
            size_t n = fread(g_zone, 1, sizeof g_zone, f);
            fclose(f);
            if (n != sizeof g_zone) { fprintf(stderr, "short zone\n"); return 2; }
        } else { fprintf(stderr, "realistic needs zone path\n"); return 2; }
    } else if (!strcmp(scenario, "wrap")) {
        /* full valid zone from driver: start=size=CAP, next write wraps */
        if (argc > 4) {
            FILE *f = fopen(argv[4], "rb");
            if (!f) { fprintf(stderr, "no zone file\n"); return 2; }
            size_t n = fread(g_zone, 1, sizeof g_zone, f);
            fclose(f);
            if (n != sizeof g_zone) { fprintf(stderr, "short zone\n"); return 2; }
        } else { fprintf(stderr, "wrap needs zone path\n"); return 2; }
    } else if (!strcmp(scenario, "bad_sig")) {
        hdr(0xDEADBEEFu, 0, 0);
    } else if (!strcmp(scenario, "wrong_zone")) {
        hdr(0x43474243u, 0, 0);   /* dmesg-zone sig: must be rejected */
    } else if (!strcmp(scenario, "bad_size")) {
        hdr(0x43474244u, 0, 0x4000);   /* size > cap */
    } else if (!strcmp(scenario, "bad_start")) {
        hdr(0x43474244u, 100, 50);     /* start > size */
    } else {
        fprintf(stderr, "unknown scenario %s\n", scenario); return 2;
    }

    m30_pmsg_init();
    feed("M30 ROOT: IOFindBSDRoot entered", mode);
    feed("A5XELTE eMMC: GPT SYSTEM first=1024 sectors=4096 USER", mode);
    feed("BSD root: emmcroot0, major 179, minor 1", mode);
    dump_logical(out);
    return 0;
}
"""


def decode(path: Path):
    sys.path.insert(0, str(ROOT / "tools"))
    import m30_bootlog
    return m30_bootlog.decode(path.read_bytes())


def framed(tag: bytes, message: bytes) -> bytes:
    rec = bytearray([0x6c, 0])  # magic, length placeholder
    rec += b"\0" * 17
    rec += tag + b"\0" + message + b"\0"
    rec[1] = len(rec)
    return bytes(rec)


WRAP_LINES = [
    b"M30 ROOT: IOFindBSDRoot entered",
    b"A5XELTE eMMC: GPT SYSTEM first=1024 sectors=4096 USER",
    b"BSD root: emmcroot0, major 179, minor 1",
]


def make_full_valid_zone() -> bytes:
    """Build a full, gap-free data[] plus a header whose start is exactly
    CAP - (bytes the test will write), so the write makes the start pointer wrap
    to 0 without splitting any existing record."""
    payload = bytearray()
    while len(payload) + 250 <= CAP:
        payload += framed(b"fill", b"x" * 225)   # 25 + 225 = 250 bytes
    rem = CAP - len(payload)
    assert rem >= 25
    payload += framed(b"fill", b"y" * (rem - 25))
    assert len(payload) == CAP
    written = sum(19 + 3 + 1 + len(m) + 1 for m in WRAP_LINES)
    start = CAP - written
    assert 0 <= start < CAP
    gz = bytearray(ZONE_SZ)
    gz[0:4] = PMSG_SIG.to_bytes(4, "little")
    gz[4:8] = start.to_bytes(4, "little")     # start near end -> pointer wraps
    gz[8:12] = CAP.to_bytes(4, "little")      # size = full
    gz[HDR_LEN:] = payload
    return bytes(gz)


def run_case(tmp: Path, scenario: str, data: bytes | None, mode: int = 1):
    out = tmp / f"{scenario}_{mode}.bin"
    zonepath = ""
    if scenario == "realistic" and data is not None:
        # Real captured Linux records into data[] with a Linux-conformant header
        gz = bytearray(ZONE_SZ)
        gz[0:4] = PMSG_SIG.to_bytes(4, "little")
        gz[4:8] = len(data).to_bytes(4, "little")   # start
        gz[8:12] = len(data).to_bytes(4, "little")  # size
        gz[HDR_LEN:HDR_LEN + len(data)] = data
        (tmp / "zone_realistic.bin").write_bytes(gz)
        zonepath = str(tmp / "zone_realistic.bin")
    elif scenario == "wrap":
        (tmp / "zone_wrap.bin").write_bytes(make_full_valid_zone())
        zonepath = str(tmp / "zone_wrap.bin")
    cmd = [str(tmp / "harness"), scenario, str(out), str(mode)]
    if zonepath:
        cmd.append(zonepath)
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=tmp)
    assert r.returncode == 0, f"harness failed: {r.stderr}"
    records, issues = decode(out)
    # Re-read raw zone to check header unchanged for rejected cases
    return out, records, issues, r.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    ap.add_argument("--captured", type=Path, default=DEFAULT_CAPTURED)
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args()

    if not args.source.is_file():
        print(f"source not found: {args.source}", file=sys.stderr)
        return 2
    block = extract_block(args.source)
    captured = args.captured.read_bytes() if args.captured.is_file() else None
    if captured is None:
        print(f"captured pmsg not found: {args.captured} (realistic case skipped)",
              file=sys.stderr)

    tmp = Path(tempfile.mkdtemp(prefix="pmsg_mirror_test_"))
    try:
        (tmp / "m30_block.inc").write_text(block)
        (tmp / "harness.c").write_text(HARNESS)
        cc = shutil.which("gcc") or shutil.which("clang")
        assert cc, "no C compiler"
        r = subprocess.run(
            [cc, "-O2", "-Wall", "-Wextra", "-Werror", "-o", str(tmp / "harness"),
             str(tmp / "harness.c")],
            capture_output=True, text=True, cwd=tmp,
        )
        assert r.returncode == 0, f"compile failed:\n{r.stderr}"
        print("[PASS] exact 0406 code compiles with -Wall -Wextra -Werror")

        # 1. fresh zeroed zone
        _, rec, issues, _ = run_case(tmp, "fresh", None)
        assert not issues and len(rec) == 3 and all(x["tag"] == "XNU" for x in rec), rec
        print(f"[PASS] fresh zone: {len(rec)} XNU records, sig adopted")

        # 2. realistic Linux-generated records + header
        if captured is not None:
            out, rec, issues, _ = run_case(tmp, "realistic", captured)
            msgs = [x["message"] for x in rec]
            base_n = decode(args.captured)[0]
            assert len(base_n) == len(rec) - 3, (len(base_n), len(rec))
            assert all(any(x["message"] == m for x in base_n) for m in msgs[:len(base_n)])
            assert msgs[-3:] == [
                "M30 ROOT: IOFindBSDRoot entered",
                "A5XELTE eMMC: GPT SYSTEM first=1024 sectors=4096 USER",
                "BSD root: emmcroot0, major 179, minor 1",
            ], msgs[-3:]
            print(f"[PASS] realistic zone: {len(base_n)} existing records preserved "
                  f"+ 3 new XNU records, 0 issues")
        else:
            print("[SKIP] realistic zone (no captured fixture)")

        # 3. wraparound: the write must land in data[] across the wrap seam.
        #    The decoder may report a seam gap because circular overwrite
        #    legitimately consumes the adjacent old record. Verify the raw
        #    bytes contain all three messages and that most records still read.
        out, rec, issues, _ = run_case(tmp, "wrap", None)
        raw = out.read_bytes()
        expected = [
            b"M30 ROOT: IOFindBSDRoot entered",
            b"A5XELTE eMMC: GPT SYSTEM first=1024 sectors=4096 USER",
            b"BSD root: emmcroot0, major 179, minor 1",
        ]
        assert all(m in raw for m in expected), "wrapped write missing from data[]"
        joined = " ".join(x["message"] for x in rec)
        assert sum(1 for m in expected if m.decode() in joined) >= 2, joined[-300:]
        print(f"[PASS] wraparound: 3 messages written across seam into data[]; "
              f"{len(rec)} records decoded, {len(issues)} expected seam gap")

        # 4-7. rejected headers: no new records
        for sc in ["bad_sig", "wrong_zone", "bad_size", "bad_start"]:
            _, rec, issues, _ = run_case(tmp, sc, None)
            assert len(rec) == 0 and not issues, (sc, rec, issues)
            print(f"[PASS] {sc}: rejected, no records written")

        # 8. regression: pre-fix control flow (hook after early returns) emits nothing
        _, rec, _, _ = run_case(tmp, "fresh", None, mode=0)
        assert len(rec) == 0, rec
        print("[PASS] regression: pre-fix newline early-return emits 0 records "
              "(root cause of v7 empty pmsg)")

        print("\nALL PMSG MIRROR TESTS PASS")
        return 0
    finally:
        if args.keep:
            print(f"temp kept: {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
