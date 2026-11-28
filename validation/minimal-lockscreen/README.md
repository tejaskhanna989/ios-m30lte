# Minimal native iOS lockscreen — isolated experiment

**New strategy (2026-11-28).** Stop version-comparison / framebuffer-counter
forensics. Objective is the smallest native iOS startup configuration that
shows a real lockscreen on the physical Galaxy M30, then add dependencies back
one at a time.

## Safety boundary (non-negotiable)

- USERDATA, SYSTEM and RECOVERY are **never written** by this experiment.
- The accepted baseline (BOOT `629843b5…` / rootfs release `44905109656`,
  image SHA `5f2e2aa6…`) and the original BOOT backup (`469c12d2…`) are never
  modified.
- Every physical step is a **BOOT-only** flash and needs explicit authorization
  at the time. No reboot without separate authorization.
- All userspace minimization is done **offline** from a verified rootfs release
  asset. No Apple binary is modified, faked, or replaced with an Android/other
  UI. The lockscreen, when it appears, must be SpringBoard's own.

## Architecture decision

Use a **ramdisk root** (`rd=md0`) instead of the live USERDATA root:

- `tools/mkpayload.py --ramdisk IMAGE` appends the ramdisk as a payload segment
  and writes `/chosen/memory-map RAMDisk = <phys,size>` into the ADT, which
  `IOFindBSDRoot()` uses to mount `/dev/md0`.
- This is the only way to change the launchd job set without writing USERDATA.
- Reversal is a single BOOT restore from the preserved original image.

Verified input:
- rootfs release `ios-root-20H392-44905109656`, image SHA `5f2e2aa6…` (the
  accepted v68 data volume), 20 GiB HFSX, HFSX signature `4858`.
- launchd inventory: `v73-userdata-evidence/0004e79f_launchd.log` — 212 spawn
  events / 146 unique job names in the known-good userspace boot.

## Milestone

**Actual native lockscreen visible on the physical M30**, observed by the
operator. Process liveness, Apple logo, framebuffer counters, pstore records
and CI are explicitly NOT success criteria.

## Stages

| Stage | Content | Device action |
|---|---|---|
| 0 | Manifest + isolated workspace + manifest test (this directory) | none |
| 1 | Download/verify v68 rootfs, extract allow-listed files, build HFSX ramdisk | none |
| 2 | Package BOOT candidate: current proven shim + kernel + ramdisk, `rd=md0` | none |
| 3 | BOOT-only flash, one boot, observe screen, immediate pstore pull | **authorization required** |
| 4 | If lockscreen appears → milestone reached; freeze candidate | none |
| 5 | Add Stage-B jobs one at a time, repeat stage 3 per addition | authorization each |
| 6 | If no lockscreen → add exactly one missing dependency, repeat | authorization each |

## Why the rootfs baseline is v68, not v79

The v68 image is the only rootfs release tied to an **observed native
lockscreen**. It is used here purely as a verified source of genuine Apple
binaries; the experiment does not write it to USERDATA and does not depend on
its accumulated state. The dyld shared cache and its `.symbols` must be
included so the kernel's existing 0425/0426 fix-ups keep working.

## Reproducibility

Every input is pinned by SHA-256 in `minimal-jobs.json` / `PROVENANCE.md`.
`build_minimal_ramdisk.sh` is deterministic given the verified image and
produces a ramdisk SHA that is recorded with each packaged candidate.

## Status

Stage 0 complete. No device access, no flash, no partition write. Awaiting
authorization for Stage 1 download/build (host-only) is **not** required to
begin Stage 0/1 offline work; no physical action is implied.
