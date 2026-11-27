#!/usr/bin/env python3
"""Focused checks for bounded Mach service registration/access tracing."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0456-m30-mach-service-trace.patch"
TREE = Path("/home/tejas/opencode-work/v74-ci-buildtree/extracted/xnu")


def main() -> None:
    assert PATCH.is_file(), "0456 Mach service trace patch missing"
    text = PATCH.read_text()
    assert 'm30svctrace' in text, "trace must be boot-arg gated"
    assert text.count('m30svctrace') >= 2, "both hooks must use the same gate"
    assert 'M30 SVC REG' in text and 'M30 SVC SEND' in text
    assert 'm30_pmsg_diag_line' in text, "must use the durable pstore sink"
    assert 'm30_svc_reg_lines < 24' in text
    assert 'm30_svc_send_lines < 48' in text
    assert 'config_service_port_info' in text
    # Diagnostic-only: no changes to return values, locks or service semantics.
    for banned in ('return KERN_', 'ip_mq_lock', 'ip_mq_unlock', 'kalloc', 'zalloc'):
        added = [l for l in text.splitlines() if l.startswith('+') and banned in l]
        assert not added, f"patch changes behaviour via {banned}"
    if (TREE / "osfmk/ipc/mach_port.c").is_file():
        r = subprocess.run(["git", "apply", "--check", str(PATCH)], cwd=TREE,
                           capture_output=True, text=True)
        assert r.returncode == 0, (r.stdout + r.stderr)
        print("[PASS] 0456 applies to current CI build tree")
    print("[PASS] Mach service trace is gated, bounded, durable-sink only")


if __name__ == "__main__":
    main()
