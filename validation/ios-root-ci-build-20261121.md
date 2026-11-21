# iOS 16.7.16 HFSX root built in GitHub Actions (2026-11-21)

## Result: SUCCESS (actual CI run, not a plan)

Workflow: `.github/workflows/ios-root-build.yml`
Run: `44905109656` (all 12 steps success), commit `7e029cd`.
First attempt `44904682195` failed at tool install (shallow apfs-fuse clone
missing `3rdparty/lzfse`); fixed by recursive submodule clone + header check.

## What was actually built and verified in CI

1. Downloaded the official iPhone10,3/10,6 iOS 16.7.16 (20H392) IPSW from
   Apple's CDN and verified SHA-256
   `ece1194f7e233e9109c5790a8d23a4564a10a254e15ec5b09978a343265568fb`.
2. Extracted and size-verified all three genuine DMGs:
   `087-86698-044.dmg` (4,730,814,044 B),
   `087-86593-047.dmg` (2,743,074,816 B),
   `087-86715-047.dmg`.
3. Installed `hfsprogs`, `rsync`, `fuse3` and built `apfs-fuse` from source
   (recursive submodules) on `ubuntu-24.04`.
4. Converted APFS DMGs to case-sensitive journaled HFSX with
   `tools/build_ios_root.sh` (donor method), applied `m30lte-root-tweaks.py`.
5. Validation in CI: `fsck.hfsplus -f -y` + `-f -n` ->
   `The volume iOSRoot appears to be OK`; HFSX signature `0x4858`;
   `/sbin/launchd` executable present.
6. Compressed image and split into four <2 GB parts (GitHub Free artifact
   storage is only 500 MB, so parts were published as release assets).

## Exact outputs

- Release: `ios-root-20H392-44905109656`
  (`https://github.com/tejaskhanna989/ios-m30lte/releases/tag/ios-root-20H392-44905109656`)
- Image: `ios-root-20H392.img` — 21,474,836,480 bytes (20 GiB)
- Image SHA-256: `5f2e2aa6a80aea489946287d8cc32ef0ff6a1905a0d2923e8d4324163bb699b5`
- Release parts (gzip -1, verified against `parts-sha256.txt` and remote digests):
  - `ios-root-20H392.img.gz.part-aa` 1,610,612,736 B
    sha256 `9d67f673752358836fd06694efac0e4acf3948e153ec5e6231b86b72bdad7992`
  - part-ab 1,610,612,736 B sha256 `b192cd91d118279a8005d2b0aa6fe4e8b38254dc7bdfdede5f8c9402ea5a2ff3`
  - part-ac 1,610,612,736 B sha256 `c2454ca281591d49168c9bbfd7b7e5b6b5c031b3bd9f6e4937e23a1de9805a52`
  - part-ad 1,397,232,737 B sha256 `7cfa9af7e9c79e323b2111bb3718de66620f1d299da5c369c7dbdfdf010e307f`
- Manifest asset `manifest.json`, hash asset `parts-sha256.txt`.

Reassemble on a machine with ~20 GB free:
```
gh release download ios-root-20H392-44905109656 -p 'ios-root-20H392.img.gz.part-*'
cat ios-root-20H392.img.gz.part-* | gunzip > ios-root-20H392.img
sha256sum ios-root-20H392.img   # must equal 5f2e2aa6...b699b5
```
The image itself was NOT downloaded to the local PC (34 GB free constraint).

## Remaining steps (physical, need fresh authorization)

1. Verify the verified USERDATA/personal-data backup before any write.
2. With authorization, follow `tools/prepare_userdata_install.sh` using the
   reassembled image; confirm USERDATA capacity >= 21,474,836,480 B and readback.
3. Flash BOOT only with candidate v11
   (`6bdb25d9954afe3c7124619e4381d7c017274e469c39b01561712d873ad1740c`);
   one boot; capture pstore immediately.
4. Expected evidence: `BSD root: emmcroot0`, `hfs: mounted iOSRoot`,
   `load_init_program ... /sbin/launchd`.

## Honest status

A genuine iOS HFSX root filesystem now exists and passed filesystem/content
validation in CI. This does NOT claim launchd or SpringBoard boot on the M30 —
no physical test has been run with this image. All previous candidates, backups,
physical evidence and source preserved. No GitHub settings changed.
