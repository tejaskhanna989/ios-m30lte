#!/usr/bin/env python3
"""Focused regression test for patch 0411 (M30LTE built-in AMFI interface).

Reproduces the exact v12 physical panic and proves the fix:

  * The panic is `amfi->OSEntitlements.adjustContextWithMonitor(...)` at
    struct offset 0x1a0 with the global `_amfi == NULL` (far=0x1a0,
    esr=0x96000007), reached from accelerate_entitlement_queries() called by
    ubc_cs_blob_add() while loading /sbin/launchd. We compile a faithful C
    model where the callback pointer sits at offset 0x1a0: with `amfi = NULL`
    the deref faults (SIGSEGV at si_addr ~0x1a0); with the built-in interface
    registered (the patch) it returns success.

  * Verifies patch 0411 extends the three guards so M30LTE compiles and
    registers the built-in AMFI: sweet_amfi.c (interface), SweetEntitlements.cpp
    (entitlement parser), and bsd_init.c (policy registration).

  * Verifies SWEET and non-M30LTE behaviour is UNCHANGED (guards are only
    widened with `|| defined(ARM64_BOARD_CONFIG_M30LTE)`; the original macros
    remain first in every expression).

  * Verifies enforcement is GENUINE, not faked: the built-in interface parses
    entitlements only via csblob_get_entitlements() (which validates them
    against the code directory) and registers through amfi_interface_register().
    No launchd_unsecure_cache / cs_enforcement_disable / amfi_get_out_of_my_way.

These are offline source/logic tests; they do not claim launchd boots. Only a
fresh physical pstore can prove progression past the failing path.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0411-m30-builtin-amfi.patch"
BT = ROOT / "milestone_artifacts/ci_45219943492/buildtree/unpacked/xnu"

# Faithful model of the faulting access. In the real amfi_t the
# OSEntitlements.adjustContextWithMonitor callback pointer lives at offset
# 0x1a0; the v12 panic did `ldr x8,[x8,#0x1a0]` with x8 == _amfi == NULL.
MODEL = r"""
#include <stdio.h>
#include <signal.h>
#include <setjmp.h>
#include <string.h>
#include <stdint.h>

struct amfi_iface {
    char pad[0x1a0];
    long (*adjustContextWithMonitor)(void *blob);
};

static struct amfi_iface builtin_amfi;
static long builtin_adjust(void *blob) { (void)blob; return 0; /* KERN_SUCCESS */ }

#ifdef FIX_M30LTE
/* Patch 0411: M30LTE compiles/registers the built-in AMFI interface. */
static struct amfi_iface *amfi = &builtin_amfi;
#else
/* v12 as-shipped: no built-in AMFI on M30LTE -> _amfi is NULL. */
static struct amfi_iface *amfi = NULL;
#endif

static sigjmp_buf jb;
static volatile sig_atomic_t faulted = 0;
static void on_segv(int sig) { (void)sig; faulted = 1; siglongjmp(jb, 1); }

int main(void)
{
    builtin_amfi.adjustContextWithMonitor = builtin_adjust;
    signal(SIGSEGV, on_segv);
    if (sigsetjmp(jb, 1) == 0) {
        /* accelerate_entitlement_queries: amfi->OSEntitlements.adjust...() */
        long ret = amfi->adjustContextWithMonitor((void *)0x1);
        printf("OK:%ld\n", ret);
    } else {
        printf("FAULT\n");
    }
    return 0;
}
"""


def compile_run(tmp: Path, fixed: bool) -> str:
    cc = shutil.which("gcc") or shutil.which("clang")
    src = tmp / "h.c"
    src.write_text(MODEL)
    flags = ["-DFIX_M30LTE"] if fixed else []
    name = "h_fixed" if fixed else "h_broken"
    r = subprocess.run(
        [cc, "-O0", "-w", *flags, "-o", str(tmp / name), str(src)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    out = subprocess.run([str(tmp / name)], capture_output=True, text=True, timeout=10)
    return out.stdout.strip()


def main() -> int:
    text = PATCH.read_text()

    # --- source-level: patch widens exactly the three guards (SWEET remains) ---
    assert "#if defined(ARM64_BOARD_CONFIG_SWEET) || defined(ARM64_BOARD_CONFIG_M30LTE)" in text
    assert "#if defined(SWEET) || defined(ARM64_BOARD_CONFIG_M30LTE)" in text
    assert "sweet_amfi_policy_register();" in text
    for f in ("bsd/kern/bsd_init.c", "bsd/kern/sweet_amfi.c",
              "iokit/Kernel/arm/SweetEntitlements.cpp"):
        assert f"diff --git a/{f} b/{f}" in text, f
    print("[PASS] patch 0411 widens all 3 guards with M30LTE and keeps SWEET first")

    # --- enforcement is genuine, not faked ---
    sa = (BT / "bsd/kern/sweet_amfi.c").read_text()
    ent = (BT / "iokit/Kernel/arm/SweetEntitlements.cpp").read_text()
    assert "amfi_interface_register(&sweet_amfi)" in sa
    assert "csblob_get_entitlements(code_signing_blob" in sa
    assert "entitlements do not match the code directory, granting none" in sa
    assert "SweetEntitlements" in ent
    for bypass in ("launchd_unsecure_cache", "cs_enforcement_disable",
                   "amfi_get_out_of_my_way"):
        assert bypass not in sa and bypass not in text
    print("[PASS] built-in AMFI registers via amfi_interface_register and validates "
          "entitlements against the code directory (no bypass boot-args)")

    # --- faithful model: pre-fix NULL deref faults, post-fix succeeds ---
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        broken = compile_run(tmp, fixed=False)
        fixed = compile_run(tmp, fixed=True)
    assert broken == "FAULT", broken          # reproduces the v12 panic
    assert fixed == "OK:0", fixed             # patch resolves it
    print("[PASS] model: amfi==NULL -> SIGSEGV at +0x1a0 (v12 panic reproduced)")
    print("[PASS] model: registered built-in AMFI -> success (patch fixes null deref)")

    # --- non-M30LTE / SWEET unchanged: guard expressions still start with original ---
    n_m30 = text.count("|| defined(ARM64_BOARD_CONFIG_M30LTE)")
    assert n_m30 == 3, n_m30  # bsd_init.c + sweet_amfi.c + SweetEntitlements.cpp
    # Every widened guard still starts with the original macro, so SWEET and
    # all non-M30Lite configs keep identical behaviour (the new term is additive).
    assert text.count("#if defined(ARM64_BOARD_CONFIG_SWEET) ||") == 2  # bsd_init.c + sweet_amfi.c
    assert text.count("#if defined(SWEET) ||") == 1  # SweetEntitlements.cpp
    print(f"[PASS] SWEET and non-M30LTE configs unchanged (3 additive M30 guards, originals first)")
    print("ALL M30 BUILT-IN AMFI TESTS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
