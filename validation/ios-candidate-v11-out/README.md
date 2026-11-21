# iOS candidate v11 — USERDATA root-device target

Isolated candidate. v6-v10, backups and all physical evidence preserved.
No physical operations performed.

## What changed vs v10

Only the payload cmdline (kernel source is unchanged — HFSX support already
present in `sweet_hfs`):

- v10: `debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292 rd=emmcroot0 emmcprobe=1`
- v11: `debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292 rd=emmcroot0 emmcroot=USERDATA emmcprobe=1`

`emmcroot=USERDATA` points `/dev/emmcroot0` at USERDATA, where a genuine iOS
HFSX root image must be flashed, instead of the Android ext4 SYSTEM partition
that produced `hfs_ValidateHFSPlusVolumeHeader: unknown Volume Signature : 80b8`
on v10. Preserved: iOS 16 target, `maxmem=292`, proven shim
(`864370f6…d15211a`), 0406/0407/0408/0409/0410 patches.

**IMPORTANT:** v11 does NOT contain a root filesystem. It can only mount iOS
once a genuine HFSX image (built from the iPhone X 16.7.16/20H392 IPSW) is
flashed to USERDATA. The image and host tools are missing locally — see
`tools/verify_ios_root_assets.py` and
`validation/ios-root-filesystem-plan-20261121.md`.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `4a21c7709e3e841df5204436d708a6a4165db15b5f448765c4f6369f2b516332` |
| payload | `275e0d452b07a491c232472ae95654fbcce50eb72a11cf632c88785487a294eb` |
| combined.bin | `dc29d0021a278ae0fba4905f0edb0054e9bc8d59349e1be3e315f0de3b610ae3` |
| shim-boot.img | `6bdb25d9954afe3c7124619e4381d7c017274e469c39b01561712d873ad1740c` |
| ios-boot.img | `c1f3c2a50f3694f2e8cad0289ceb7714846ee7e02a8d8f1ae42229a0b7248f0a` |

## Validation (offline)

CI `44899258929` success, iOS target confirmed, LSE=0. Buildtree PASS, kernel
PASS, platform 9/9, CPU 17/17, ADT 22/22, handoff 18/18, packaging PASS,
GIC 5/6 (documented inapplicable DAIF check). `test_ios_root_path.py`,
`test_bsd_progress.py`, `test_pmsg_mirror.py`, `test_ml_wait_fix.py`, bootlog
selftest all PASS. `verify_ios_root_assets.py` correctly reports missing
external inputs (exit 1).

## Status

Technically ready to mount a genuine HFSX iOS root **once the root image is
provided and flashed to USERDATA**. No root mount, launchd or SpringBoard is
claimed. No physical test performed. Fresh authorization required.
