# CI-only rootfs reassembly and verification (2026-11-21)

## Result: SUCCESS — installation-ready on CI, no local image storage

Workflow: `.github/workflows/ios-root-verify.yml`
Run: `https://github.com/tejaskhanna989/ios-m30lte/actions/runs/44908947654`
Status: `success`, all steps (1–10 + post) green. Commit `d4a17f4`.

## Runner capacity and usage (measured, not assumed)

- Before download: 145 GB total, 88 GB free (prior build run's `df` after cleanup).
- This run's gate: `avail_bytes > 35,000,000,000` — PASS.
- Final `df`: `/dev/mapper/cow-root 145G 77G 68G 54% /` — 68 GB free after verification.
- Peak usage on runner: ~6.2 GB compressed parts + 21.5 GB reassembled image (well under capacity).

## Four-part verification

All four parts downloaded from release `ios-root-20H392-44905109656` and verified
with `sha256sum -c parts-sha256.txt` (all OK):
- part-aa `9d67f673…ad7992`, part-ab `b192cd91…2a2ff3`
- part-ac `c2454ca2…e9805a52`, part-ad `7cfa9af7…010e307f`

## Final image verification (on runner)

- Size: **21,474,836,480 bytes** (exact) — PASS.
- SHA-256: **`5f2e2aa6a80aea489946287d8cc32ef0ff6a1905a0d2923e8d4324163bb699b5`** — PASS.
- HFSX signature `4858` (0x4858) — PASS.
- `fsck.hfsplus -f -n`: `The volume iOSRoot appears to be OK` — PASS.
- `/sbin/launchd`: `-rwxr-xr-x 1 root root 541600 Apr 30 2026` — PASS.
- Only a 269-byte verification manifest was uploaded as an Actions artifact;
  the 20 GiB image stayed on runner storage and was discarded with the runner.

## Transfer / install feasibility

- **No transfer performed**: there is no authorized remote storage destination or
  credentials, and no device is connected to this machine. Streaming directly
  to a connected recovery environment from a GitHub runner is not possible
  without a new external service or credentials — the task forbids introducing
  either without asking.
- The verified image remains available as four release assets on GitHub and can
  be reassembled on a machine with ~21.5 GB free when the user is ready; or a
  future authorized workflow can add a remote destination.
- Device prerequisites are **not satisfied**: no personal-data backup path visible
  locally, no device in recovery, USERDATA mapping/capacity unconfirmed.

## Local storage (honest report)

- Baseline at task start: 41 GB free on `/`.
- After this task: **37 GB free** (`/dev/sda2 116G 74G 37G 67%`).
- No IPSW/DMG/parts/image were downloaded or reassembled locally; only a 269-byte
  manifest artifact was fetched. The 4 GB decrease is from unrelated local growth
  observed during the session (e.g. `~/.local/share/opencode/opencode.db` 1.4 GB,
  Chrome History 166 MB) — not from any heavy operation in this task.
- No cleanup was performed (explicitly prohibited by the task).

## Success condition

The genuine iOS 16.7.16 HFSX root is verified and installation-ready **through CI**
with exact size/hash, HFSX, fsck and launchd checks — without storing the image
locally. Physical installation still requires: verified personal-data backup,
correct M30 in recovery, USERDATA mapping/capacity check, and an independently
verifiable write/readback procedure, plus a fresh explicit authorization for the
exact device operations.
