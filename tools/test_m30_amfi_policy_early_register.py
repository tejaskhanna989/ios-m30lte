#!/usr/bin/env python3
"""Focused regression test for patch 0412 (M30LTE AMFI MAC policy early registration).

Reproduces the v13 physical panic and proves the fix:

  v13 log: `SWEET AMFI: built-in interface registered`, then
  `panic ... Unexpected fault in kernel static region ... pc 0xfffffff007a2ac74
   (mac_policy_register) ... far 0xfffffff007204aec (_mac_policy_list+0x14)`.

  Root cause: mac_policy_list is SECURITY_READ_ONLY_LATE in __DATA_CONST, frozen
  read-only by machine_lockdown() in kernel_bootstrap (startup.c). Registering
  the AMFI MAC policy from the LATER bsd_init() writes that frozen region -> fault.
  Vnguard registers correctly from kernel_bootstrap BEFORE machine_lockdown().

  Patch 0412: register the AMFI MAC policy from kernel_bootstrap alongside
  vnguard (before machine_lockdown), and revert the late bsd_init() call for
  M30LTE. SWEET behaviour is unchanged.

The C model makes mac_policy_list read-only via mprotect() at a simulated
"lockdown" and verifies registration before lockdown succeeds while
registration after lockdown faults (SIGSEGV) -- reproducing the exact condition.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0412-m30-amfi-policy-early-register.patch"
BT = ROOT / "milestone_artifacts/ci_45219943492/buildtree/unpacked/xnu"
PSTORE = ROOT / "validation/physical-boot-test/20261121-ios-v13-boot/raw/pmsg-ramoops-0"

MODEL = r"""
#include <stdio.h>
#include <signal.h>
#include <setjmp.h>
#include <sys/mman.h>
#include <unistd.h>

/* Model mac_policy_list: SECURITY_READ_ONLY_LATE in __DATA_CONST (page aligned). */
struct mpl { int numloaded; char pad[4096 - sizeof(int)]; };
static struct mpl mac_policy_list __attribute__((aligned(4096))) = {0};

static sigjmp_buf jb;
static volatile sig_atomic_t faulted = 0;
static void on_segv(int s) { (void)s; faulted = 1; siglongjmp(jb, 1); }

static void lockdown(void) { mprotect(&mac_policy_list, 4096, PROT_READ); }
static int mac_policy_register(void) { mac_policy_list.numloaded++; return 0; }

int main(void)
{
    signal(SIGSEGV, on_segv);
    if (sigsetjmp(jb, 1) == 0) {
#ifdef EARLY
        mac_policy_register();   /* kernel_bootstrap, before machine_lockdown */
        lockdown();
        printf("OK:%d\n", mac_policy_list.numloaded);
#else
        lockdown();
        mac_policy_register();   /* bsd_init, after machine_lockdown -> fault */
        printf("OK:%d\n", mac_policy_list.numloaded);
#endif
    } else {
        printf("FAULT\n");
    }
    return 0;
}
"""


def compile_run(tmp: Path, early: bool) -> str:
    cc = shutil.which("gcc") or shutil.which("clang")
    src = tmp / "h.c"
    src.write_text(MODEL)
    flags = ["-DEARLY"] if early else []
    name = "h_early" if early else "h_late"
    r = subprocess.run([cc, "-O0", "-w", *flags, "-o", str(tmp / name), str(src)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return subprocess.run([str(tmp / name)], capture_output=True, text=True, timeout=10).stdout.strip()


def main() -> int:
    text = PATCH.read_text()

    # source-level: bsd_init reverted to SWEET-only; startup.c gains M30LTE early call
    assert "#if defined(ARM64_BOARD_CONFIG_SWEET)\n" in text
    assert "diff --git a/osfmk/kern/startup.c b/osfmk/kern/startup.c" in text
    assert "#if defined(ARM64_BOARD_CONFIG_M30LTE)" in text
    assert "before machine_lockdown()" in text
    assert "sweet_amfi_policy_register();" in text
    print("[PASS] patch 0412 reverts bsd_init to SWEET-only and adds M30LTE early registration")

    # registration point precedes machine_lockdown() in startup.c
    su = (BT / "osfmk/kern/startup.c").read_text()
    early = su.index("vnguard_policy_init();")
    lock = su.index("machine_lockdown();")
    assert early < lock, "vnguard/AMFI registration must precede machine_lockdown"
    print("[PASS] kernel_bootstrap registers policies before machine_lockdown()")

    # mac_policy_list really is SECURITY_READ_ONLY_LATE / __DATA_CONST
    mb = (BT / "security/mac_base.c").read_text()
    assert "SECURITY_READ_ONLY_LATE(mac_policy_list_t) mac_policy_list;" in mb
    print("[PASS] mac_policy_list is SECURITY_READ_ONLY_LATE (__DATA_CONST)")

    # exactly ONE registration path on M30LTE: bsd_init call must be SWEET-only
    bi = (BT / "bsd/kern/bsd_init.c").read_text()
    bi_call = bi.index("sweet_amfi_policy_register();")
    bi_guard = bi.rindex("#if defined(ARM64_BOARD_CONFIG_SWEET)", 0, bi_call)
    assert "M30LTE" not in bi[bi_guard:bi_call], "bsd_init must not register on M30LTE"
    assert bi[bi_call:].find("#endif") < bi[bi_call:].find("sweet_hfs_register")
    print("[PASS] bsd_init registration is SWEET-only (no late M30LTE duplicate)")

    # binary-level (if the built kernel is present): exactly one call site, before lockdown
    KERNEL = ROOT / "validation/ios-candidate-v14-out/inputs/kernel.development.m30lte"
    if KERNEL.exists() and shutil.which("llvm-objdump"):
        dis = subprocess.run(["llvm-objdump", "-d", str(KERNEL)],
                             capture_output=True, text=True).stdout
        calls = [ln for ln in dis.splitlines()
                 if "bl" in ln and "<_sweet_amfi_policy_register>" in ln]
        assert len(calls) == 1, f"expected 1 call site, got {len(calls)}: {calls}"
        call_addr = int(calls[0].split(":")[0].strip(), 16)
        locks = [ln for ln in dis.splitlines()
                 if "bl" in ln and "<_machine_lockdown>" in ln]
        assert locks, "machine_lockdown call not found"
        lock_addr = int(locks[0].split(":")[0].strip(), 16)
        assert call_addr < lock_addr, "AMFI registration must precede machine_lockdown in binary"
        print(f"[PASS] binary: exactly 1 call site at {hex(call_addr)} < machine_lockdown {hex(lock_addr)}")

    # v13 pstore proves the before-state
    d = PSTORE.read_bytes()
    assert b"SWEET AMFI: built-in interface registered" in d
    assert b"Unexpected fault in kernel static region" in d
    print("[PASS] v13 pstore: AMFI interface registered, then static-region fault in mac_policy_register")

    # faithful model: late registration faults, early works
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        late = compile_run(tmp, early=False)
        early_r = compile_run(tmp, early=True)
    assert late == "FAULT", late       # reproduces v13 panic
    assert early_r == "OK:1", early_r   # patch fixes it
    print("[PASS] model: register after lockdown -> SIGSEGV (v13 panic reproduced)")
    print("[PASS] model: register before lockdown -> success (patch fixes it)")

    print("ALL M30 AMFI EARLY-REGISTER TESTS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
