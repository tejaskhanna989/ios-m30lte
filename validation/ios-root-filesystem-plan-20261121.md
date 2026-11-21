# iOS 16 root filesystem plan (2026-11-21, offline, MAIN)

## 1. Exact filesystem requirements (established from evidence)

The v10 physical boot proved (recovered pmsg, 216 records):
```
M30 ROOT: A5XELTE keys/emmc stage (rdBootVar='emmcroot0')
A5XELTE eMMC: GPT SYSTEM first=442368 sectors=7798784 read-only
A5XELTE eMMC: /dev/emmcroot0 ready, GPT SYSTEM read-only
BSD root: emmcroot0, major 1, minor 0
hfs_ValidateHFSPlusVolumeHeader: unknown Volume Signature : 80b8
hfs_mount: hfs_mountfs returned error=22 for device unknown-dev
cannot mount root, errno = 19
```
- `rd=emmcroot0` works; GPT parsing works; `/dev/emmcroot0` is created; it is
  selected as BSD root. The mount fails only because the selected partition
  (SYSTEM, default) is **Android ext4**, not an Apple filesystem.
- `hfs_ValidateHFSPlusVolumeHeader` (`bsd/sweet_hfs/core/hfs_vfsutils.c`) accepts
  `kHFSPlusSigWord = 0x482B` (HFS+, version 4) and `kHFSXSigWord = 0x4858`
  (HFSX, version 5). Anything else returns EINVAL — hence `0x80b8`.
- The genuine iOS 16 IPSW root is **APFS** (LZBITMAP-compressed), but APFS is
  **not** in open-source XNU: the buildtree has only `kern_apfs_reflock.c`
  (a lock primitive), no APFS filesystem. Do **not** assume HFS+ can mount APFS.

## 2. Proven viable path (from the donor M20LTE project, same XNU 8796)

The donor achieved a **real** iOS 16.7.16 (20H392) iPhone X root mount, launchd,
SpringBoard and Setup GUI by converting APFS DMGs into a case-sensitive **HFSX**
image:
- IPSW: **iPhone10,3 / D22AP, iOS 16.7.16 (20H392)**.
- DMGs: OS rootfs `087-86698-044.dmg`, SystemOS cryptex `087-86593-047.dmg`,
  AppOS cryptex `087-86715-047.dmg`.
- `tools/mkiosroot.sh OS.dmg SYSTEMOS.dmg APPOS.dmg OUT.img 20G` (apfs-fuse
  decompresses LZBITMAP; mkfs.hfsplus -J builds journaled HFSX; hard-links the
  SystemOS dyld shared cache to `/System/Library/Caches/com.apple.dyld`;
  adds `/private/var/keybags/systembag.kb`).
- `tools/m30lte-root-tweaks.py MOUNTED_ROOT` adds the M30/M20 bring-up fixes
  (launchd.plist panic-key rename, containers dirs, migration marker,
  VirtualAudio/MediaToolbox/SpringBoard/Setup/activation tweaks).
- The image is flashed to **USERDATA**, and booted with
  `rd=emmcroot0 emmcroot=USERDATA` (plus rootrw/wdt args).
- Donor result: `hfs: mounted iOSRoot`, `load_init_program /sbin/launchd`,
  launchd spawns ~60 services via xpcproxy, SpringBoard/Setup GUI rendered.

**This kernel already has HFSX support, so no kernel change is required for the
root mount.** The remaining work is asset acquisition + image build + flashing.

## 3. Assets: none present locally (require user action)

`tools/verify_ios_root_assets.py` (read-only) reports:
- No `.ipsw` or `.dmg` anywhere under the repo or `/home/tejas`.
- Host tools `apfs-fuse`, `mkfs.hfsplus`, `fsck.hfsplus`, `rsync` all MISSING.
- Build scripts `tools/mkiosroot.sh`, `tools/m30lte-root-tweaks.py` present.
- Required: the genuine iPhone X 16.7.16 (20H392) IPSW from Apple (or the three
  DMGs), and the host tools installed. No personalization bypass is used; the
  cryptexes are copied from the legitimately downloaded IPSW.

## 4. Implemented (this round)

- `tools/test_ios_root_path.py`: logic tests verified against the shipped
  buildtree constants — HFS+ 0x482B/v4 and HFSX 0x4858/v5 accepted; observed
  0x80b8 (ext4) rejected with EINVAL; wrong version/bad blocksize/truncated
  header rejected; `rd=emmcroot0` selects SYSTEM/USERDATA and rejects invalid;
  mount failure maps to errno 19 retry loop. ALL PASS.
- `tools/verify_ios_root_assets.py`: reports exact missing external inputs.
- Candidate v11: same kernel as v10 (HFSX support already present) with cmdline
  `rd=emmcroot0 emmcroot=USERDATA emmcprobe=1` so the root device points at the
  partition where the genuine HFSX image must be flashed — instead of SYSTEM.

## 5. Honest status / blockers

- **Can this kernel genuinely mount an iOS root?** YES — technically: it has
  HFSX support and the donor proved the identical kernel generation mounts a
  genuine iOS HFSX root. But **no genuine iOS root image exists locally**, so
  no mount has been demonstrated on this M30 build.
- **Missing external inputs (your action):** the IPSW/DMGs, the host tools, and
  fresh authorization to build+flash the HFSX image to USERDATA.
- **Not claimed:** no successful root mount on v10/v11, no launchd, no
  SpringBoard, no iOS userspace boot.

## 6. Next required physical verification (fresh authorization)

1. Provide the iPhone X 16.7.16 (20H392) IPSW/DMGs and install host tools.
2. Build the HFSX image (mkiosroot.sh + m30lte-root-tweaks.py), verify it
   contains `/sbin/launchd` and a valid HFSX header.
3. Flash it to USERDATA (authorized), boot candidate v11, capture pmsg.
4. Expected: `BSD root: emmcroot0`, `hfs: mounted ...`, `load_init_program`.
   Only then may a real launchd/SpringBoard boot be claimed.
