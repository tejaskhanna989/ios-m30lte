# Repository consolidation report (2026-11-21)

Goal: make `/home/tejas/Projects/m30lte-ios/` the single organized home of the
project. Branch `main`, HEAD before consolidation `d1dcac5`. No physical device
operations, no GitHub settings changes, no branch changes.

## 1. Completed relocation (the requested move)

`/home/tejas/v9-immediate-pstore/` →
`validation/physical-boot-test/20261121-ios-v9-flash/recovery-capture/`

| File | SHA-256 before | SHA-256 after | Result |
|---|---|---|---|
| `pmsg-ramoops-0` | `9ed6020f…08c5ca` | `9ed6020f…08c5ca` | unchanged |
| `pmsg-decoded.txt` | `74d57b9a…8fe2` | `74d57b9a…8fe2` | unchanged |

Moved with `mv` (bytes preserved), not copied. The external directory is now
empty. The two earlier duplicate copies in the parent evidence directory
(`pmsg-recovered-raw.bin`, `pmsg-recovered-decoded.txt`) were confirmed
byte-identical (`cmp`) and removed, leaving **one canonical copy** of each file.
References in `validation/bsd-progress-analysis-20261121.md`,
`validation/ios-candidate-v10-out/README.md` and
`validation/physical-boot-test/20261121-ios-v9-flash/README.md` now point to
the canonical `recovery-capture/` paths, and a provenance README was added
there.

Validation after relocation: canonical hashes exact; `tools/m30_bootlog.py
inspect` decodes 93 records, 72 XNU, 0 issues; decoded companion consistent;
`validate-repo.py` tool/shell syntax PASS (7 pre-existing patch-sequence gaps,
unchanged by this work); `test_bsd_progress.py`, `test_pmsg_mirror.py`,
`m30_bootlog.py selftest` all PASS.

## 2. Other project-related files/folders found OUTSIDE the repo (report only — NOT moved)

| Path | What it is | Decision |
|---|---|---|
| `/home/tejas/ios-m20lte-donor/` | Separate git repo for the A5XELTE/M20LTE donor, with its own upstream remote (`madesh-ops/ios-m20lte`), history and progress docs | **Left in place** — a distinct upstream repository; moving it would break its git identity. Its findings are already incorporated into this repo's patches/docs. |
| `/home/tejas/exynos-usbdl/` | Exynos USB-download tool source/build (`exynos-usbdl*.c`) | Left — third-party tool, not project evidence |
| `/home/tejas/odin4/`, `/home/tejas/samloader`, `/home/tejas/samloader-rs/` | Samsung firmware download/flash tools | Left — tooling, not project evidence |
| `/home/tejas/cm.bin`, `cm_4mb.bin`, `cm_small.bin`, `pit.bin` (0 B) | Samsung/Exynos binary blobs (`1e ab ad 10` header on the cm*.bin files); `pit.bin` is empty | Left — external blobs, not candidate/evidence artifacts |
| `/tmp/issue_single_boot_v9.sh`, `/tmp/capture_v9_evidence.sh`, `/tmp/vnew/`, `/tmp/mrc_*.c`, `/tmp/pmsg_mirror_test_*`, `/tmp/iostart_*.cpp`, `/tmp/bsd*.c`, etc. | Scratch harnesses/temp copies generated during patch development and testing | Left — derived/regenerable, not evidence; committed tests recreate their logic |
| `/home/tejas/Downloads/`, `Documents/`, `Desktop/` | Personal/credential files (PDFs, images, password/token files) | **Not touched** — unrelated and sensitive |

## 3. Inside the repo but intentionally untracked

`milestone_artifacts/ci_*` — approximately **2.8 GB** of downloaded CI build
trees and kernel artifacts (11 directories). They are already inside the repo
tree but left untracked because of size; their authoritative hashes, CI run IDs
and verification results are recorded in committed docs (`NOTES.md`, candidate
READMEs, validation reports). Not committed during consolidation; nothing
deleted. `milestone_artifacts/SHA256SUMS_MILESTONES.txt` remains tracked.

**Published to GitHub (2026-11-21):** all 11 CI runs are now available as
release assets at
`https://github.com/tejaskhanna989/ios-m30lte/releases/tag/ci-milestones-20261121`
(tag `ci-milestones-20261121`, 12 assets, ~993 MB). Each `ci_<run>.tar.gz`
contains the complete `milestone_artifacts/ci_<run>/` directory (raw CI
downloads plus unpacked build tree). Also included: `SHA256SUMS_MILESTONES.txt`
(original per-artifact hashes) and `ASSET_SHA256.txt` (hashes of the release
tarballs). Remote asset digests were verified against the local manifest — all
12 match. This publishes the artifacts without adding ~2.8 GB to the git
history (two source files exceed GitHub's 100 MB per-file commit limit).

## 4. Explicitly not changed

Backups (`m30-boot-original/boot.img`), all candidates v2-v10, physical evidence
directories, XNU/shim source, iOS 16 target, `maxmem=292`, verified shim region,
GitHub settings. No physical operations.
