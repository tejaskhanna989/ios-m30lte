# iOS candidate v58 — SpringBoard visibility

Baseline: v57 (`55a0c810`). v58 source: `8724a1a0`. MAIN only. This candidate
does not change the validated CS readback fix or weaken any security check. It
makes the next physical boot able to show whether SpringBoard launches.

## Why this candidate exists

v57 fixed the 16K CS readback deadlock and produced healthy counters
(`csblk=30025 csfail=12 csvok=192519`, IRT `state=3`), but the captured pstore
had **no** SpringBoard/backboardd records. That absence is not evidence:
the 0426 heartbeat wrote 30 full + 180 compact records every 2 s into a 16 KB
ring, overwriting the SpringBoard window. The Apple logo seen by the user is a
strong UI observation but is not proof of a lock screen or SpringBoard.

v58 makes two small, evidence-driven changes:

1. Patch `0435` reduces the IRT heartbeat to 5 full + 18 compact records
   (compact every 10 s), leaving most of the pmsg ring for crash-scan and
   sampler records. The durable IRT/CS counters remain.
2. Patch `0435` starts the existing M30LTE-compiled process sampler from the
   eMMC root device path. It samples `SpringBoard,backboardd` at 90 s and then
   every 120 s with PC/LR/backtrace (`SMP ...` records). Previously the sampler
   was only started in the unused SWEET UFS path.

All v57 code-signing, AMFI, trust-cache, page-validation and IRT patch behavior
is preserved. The payload cmdline changes from `cpus=1` to `cpus=6` (the
historical home-screen bring-up used 6 cores) and adds `sweetfb_noconsole=1`
so kernel text stops drawing over the GUI. The ADT is unchanged; its activation
properties were verified to be correct 4-byte zeros.

## CI history

| Run | Result |
|---|---|
| `45219943492` | v55 GREEN; physically rejected |
| `45230106038` | v57 GREEN; CS fix validated |
| `45245697689` | v58 GREEN; 0435 applied |

CI `45245697689` was GREEN for source `8724a1a0`, built with
`XNU_TARGET=iphoneos`, M30LTE, DEVELOPMENT. The log explicitly applied
`0435-m30-springboard-visibility.patch`; iOS target selection passed and the
Cortex-A53 LSE count was 0.

## Hashes

| File | SHA256 |
|---|---|
| buildtree `osfmk/vm/vm_fault.c` | `9193cd37cf769a68b362dffe8a48c3d7b443cd7a7202d409ea941ab7bac5339a` |
| buildtree `bsd/dev/a5xelte_emmc.c` | `d15f61b44050bafb36162bb3124c9a2b4dd355c04f91b2a76cba4e5e133c6bbe` |
| linked kernel | `5aaacba0ffe49ba021c86f8fd491aba9ff6f65a5514f7b7a2db0e8b1b5693cd2` |
| M30LTXNU payload | `90f5e612a144e7e42411c664bca92820189e4cf0533eaa5794ccf3e74d6fcf8f` |
| `combined.bin` | `1b86d4590f1b9c80927d4f345e695116dfda7758841acd23116e1c309fe2c1bf` |
| `shim-boot.img` (BOOT-flash candidate) | `2ef2e3a09cb501fb4b4ed4dd8e888441fe7d5895f29fb6b73397be1d982f783d` |
| `ios-boot.img` | `88300d77aa45a57f3a8ca387e39fbd26f570ddf2421472801936f481b449a3ed` |

## Validation

- `verify_m30_buildtree.py`: PASS, critical patches reverse-apply.
- `verify_m30_kernel.py`: PASS (6 checks).
- `verify_platform_match.py`: 9/9 PASS.
- `validate_boot_images.py`: PASS.
- `verify_handoff_v58.py`: 22/22 PASS (includes cpus=6 and
  `sweetfb_noconsole=1` cmdline checks).
- Focused tests: all applicable PASS, including
  `test_m30_springboard_visibility.py` and all v55/v57 CS tests.
  `test_m30_16k_pages.py` remains intentionally inapplicable without 0417.
- CI Cortex-A53 compatibility: PASS (0 LSE instructions).
- No QEMU result is claimed as evidence.

## Physical step and acceptance

Only `shim-boot.img` may be flashed to BOOT with Heimdall, after positive
device identity and Download Mode confirmation. Never USERDATA/SYSTEM/RECOVERY;
never Fastboot; no BOOT readback.

After boot: capture pstore **early** (~90 s) and again after the full window,
so the reduced heartbeat plus the `SMP SpringBoard`/`SMP backboardd` sampler
records can be seen. Take a screen photo if a lock screen appears. Acceptance
requires a visible, persistent lock screen on the physical M30 plus supporting
logs — not an Apple logo, not IRT state=3, and not a briefly existing process.
