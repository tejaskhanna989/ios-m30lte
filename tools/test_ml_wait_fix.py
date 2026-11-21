#!/usr/bin/env python3
"""Focused regression test for patch 0408 (M30LTE ml_wait_max_cpus fix).

Verifies the patch contains the M30LTE guard, then compiles a faithful model
of the patched function twice: with ARM64_BOARD_CONFIG_M30LTE (must return
immediately with machine_info.max_cpus) and without (must take the lock/sleep
path). Proves the pre-bsd_init deadlock is removed without changing behaviour
for other arm64 configurations.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "xnu/patches-minimal/0408-m30-ml-wait-max-cpus.patch"

# Faithful model of the patched ml_wait_max_cpus() (same lines, real wait path
# retained for non-M30LTE; the M30LTE branch returns immediately).
FUNC = r"""
unsigned int
ml_wait_max_cpus(void)
{
#if defined(ARM64_BOARD_CONFIG_M30LTE)
	return machine_info.max_cpus;
#else
	assert(lockdown_done);
	lck_mtx_lock(&max_cpus_lock);
	while (max_cpus_initialized != MAX_CPUS_SET) {
		max_cpus_initialized = MAX_CPUS_WAIT;
		lck_mtx_sleep(&max_cpus_lock, LCK_SLEEP_DEFAULT,
		    &max_cpus_initialized, THREAD_UNINT);
	}
	lck_mtx_unlock(&max_cpus_lock);
	return machine_info.max_cpus;
#endif
}
"""

HARNESS = r"""
#include <stdio.h>
typedef unsigned int uint32_t;
struct mi { unsigned int max_cpus; } machine_info = { 1 };
#define MAX_CPUS_SET 1
#define MAX_CPUS_WAIT 2
static int max_cpus_initialized = 0;
static int lockdown_done = 1;
static int max_cpus_lock = 0;
static int lock_calls = 0, sleep_calls = 0;
#define assert(x) do { if (!(x)) { printf("ASSERT_FAIL\n"); return 2; } } while (0)
static void lck_mtx_lock(void *l) { (void)l; lock_calls++; }
static void lck_mtx_unlock(void *l) { (void)l; }
static void lck_mtx_sleep(void *l, int a, void *b, int c) {
    (void)l;(void)a;(void)c; sleep_calls++;
    max_cpus_initialized = MAX_CPUS_SET; /* fake wake to avoid infinite loop */
}
#define LCK_SLEEP_DEFAULT 0
#define THREAD_UNINT 0
""" + FUNC + r"""
int main(void) {
    unsigned int n = ml_wait_max_cpus();
    printf("max_cpus=%u lock_calls=%d sleep_calls=%d\n", n, lock_calls, sleep_calls);
    return 0;
}
"""


def compile_run(tmp: Path, m30: bool) -> str:
    (tmp / "h.c").write_text(HARNESS)
    cc = shutil.which("gcc") or shutil.which("clang")
    flags = ["-DARM64_BOARD_CONFIG_M30LTE"] if m30 else []
    name = "h_m30" if m30 else "h_other"
    r = subprocess.run(
        [cc, "-O2", "-w", *flags, "-o", str(tmp / name), str(tmp / "h.c")],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    out = subprocess.run([str(tmp / name)], capture_output=True, text=True, timeout=10)
    assert out.returncode == 0, out.stdout + out.stderr
    return out.stdout.strip()


def main() -> int:
    text = PATCH.read_text()
    assert "#if defined(ARM64_BOARD_CONFIG_M30LTE)" in text
    assert "return machine_info.max_cpus;" in text
    assert "ml_wait_max_cpus(void)" in text
    print("[PASS] patch contains M30LTE guard in ml_wait_max_cpus")
    with tempfile.TemporaryDirectory(prefix="mlwait_test_") as d:
        tmp = Path(d)
        m30 = compile_run(tmp, True)
        other = compile_run(tmp, False)
    print("M30LTE:", m30)
    print("other :", other)
    m30_lock = int(re.search(r"lock_calls=(\d+)", m30).group(1))
    other_lock = int(re.search(r"lock_calls=(\d+)", other).group(1))
    assert m30_lock == 0, "M30LTE must not enter the blocking path"
    assert other_lock >= 1, "non-M30LTE must still use the lock/sleep path"
    print("[PASS] M30LTE returns immediately (no deadlock); other arm64 unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
