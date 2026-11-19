#!/usr/bin/env python3
"""Verify the M30LTE platform-expert matching fix.

Runs the real C preprocessor over iokit/KernelConfigTables.cpp for three
configurations and checks the effective IONameMatch strings:

  M30LTE  (A5XELTE + M30LTE both defined, as CI builds it):
    SweetPlatformExpert IONameMatch must be 'samsung,m30lte'
    AppleCLCD           IONameMatch must be 'm30lte,display'
    SweetBattery        must NOT be compiled
  A5XELTE only:
    SweetPlatformExpert 'samsung,a5xelte', AppleCLCD 'samsung,a5xelte-display'
  Apple D22AP (neither macro):
    none of the Sweet* config entries compiled; IOPanicPlatform remains as
    the unconditional fallback only in the custom table (the KDK supply
    Apple platform experts are separate and unchanged by this patch).

Also checks the linked kernel binary from CI: the SweetPlatformExpert entry
must contain 'samsung,m30lte' (the pre-fix kernel had 'samsung,a5xelte').
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

CONFIG_HEAD = r'''
#define ARM64_BOARD_CONFIG_M30LTE 1
'''

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, bool(ok), detail))


def preprocess(source: Path, macros: dict[str, str]) -> str:
    cmd = ["clang", "-E", "-P", "-x", "c"]
    for k, v in macros.items():
        cmd += [f"-D{k}={v}"]
    cmd += [str(source)]
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def table_for(out: str) -> str:
    # The table is a C string:  const char * gIOKernelConfigTables = "(" ... ")";
    m = re.search(r'gIOKernelConfigTables\s*=\s*"\("(.*?)"\)"\s*;', out, re.S)
    return m.group(0) if m else ""


def name_matches(table: str, classname: str) -> list[str]:
    # Find each block with IOClass = classname, then its IONameMatch.
    found: list[str] = []
    for block in table.split("{"):
        if f"'IOClass'         = {classname}" not in block:
            continue
        m = re.search(r"'IONameMatch'\s*=\s*'([^']+)'", block)
        if m:
            found.append(m.group(1))
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, type=Path,
                    help="patched iokit/KernelConfigTables.cpp")
    ap.add_argument("--kernel", required=True, type=Path,
                    help="linked kernel.development.m30lte")
    args = ap.parse_args()

    src = args.source.read_text()

    # M30LTE config (the exact macro combination used by CI)
    m30 = preprocess(args.source, {
        "ARM64_BOARD_CONFIG_M30LTE": "1",
        "ARM64_BOARD_CONFIG_A5XELTE": "1",
    })
    t = table_for(m30)
    check("M30: SweetPlatformExpert IONameMatch = samsung,m30lte",
          name_matches(t, "SweetPlatformExpert") == ["samsung,m30lte"],
          str(name_matches(t, "SweetPlatformExpert")))
    check("M30: AppleCLCD IONameMatch = m30lte,display",
          name_matches(t, "AppleCLCD") == ["m30lte,display"],
          str(name_matches(t, "AppleCLCD")))
    check("M30: SweetCPU IONameMatch = arm,cortex-a53",
          name_matches(t, "SweetCPU") == ["arm,cortex-a53"],
          str(name_matches(t, "SweetCPU")))
    check("M30: SweetBattery absent", "SweetBattery" not in t)

    # A5XELTE-only config: unchanged behaviour
    a5 = preprocess(args.source, {"ARM64_BOARD_CONFIG_A5XELTE": "1"})
    t = table_for(a5)
    check("A5XELTE-only: SweetPlatformExpert = samsung,a5xelte",
          name_matches(t, "SweetPlatformExpert") == ["samsung,a5xelte"],
          str(name_matches(t, "SweetPlatformExpert")))
    check("A5XELTE-only: AppleCLCD = samsung,a5xelte-display",
          name_matches(t, "AppleCLCD") == ["samsung,a5xelte-display"],
          str(name_matches(t, "AppleCLCD")))

    # Apple D22AP: neither macro -> no Sweet* platform entries
    apple = preprocess(args.source, {})
    t = table_for(apple)
    check("Apple D22AP: no SweetPlatformExpert match entry",
          name_matches(t, "SweetPlatformExpert") == [],
          str(name_matches(t, "SweetPlatformExpert")))
    check("Apple D22AP: IOPanicPlatform fallback still compiled",
          "IOPanicPlatform" in t)

    # Linked kernel: extract serialized config table string
    k = args.kernel.read_bytes()
    i = k.find(b"'IOClass'         = SweetPlatformExpert;")
    if i < 0:
        check("linked kernel config table found", False)
    else:
        block = k[i:i + 300].decode("latin1", "replace")
        m = re.search(r"'IONameMatch'\s*=\s*'([^']+)'", block)
        eff = m.group(1) if m else "(none)"
        check("linked kernel SweetPlatformExpert match = samsung,m30lte",
              eff == "samsung,m30lte", eff)

    failed = 0
    for name, ok, detail in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}: {detail}")
        failed += 0 if ok else 1
    print(f"RESULT: {len(results) - failed}/{len(results)} PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
