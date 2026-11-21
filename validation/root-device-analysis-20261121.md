# iOS root-device path analysis (2026-11-21, offline, MAIN only)

Evidence basis: CI buildtree/kernel `44686553586` (iOS target), physical v7 evidence.
No new physical operations. Framebuffer text alone is never treated as proof.

## 1. Exact path (source, iOS-targeted XNU)

```
arm_init / kernel_bootstrap
  -> bsd_init()                       bsd/kern/bsd_init.c:477
       | sweet_hfs_register()         :703  (HFS registered via vfs_fsadd)
       | bsd_autoconf()               :801  -> IOKitBSDInit() publishes "IOBSD"
       | inittodr()
       | loop:
           setconf()                  :876
             -> IOFindBSDRoot()        IOKitBSDInit.cpp:660
                  | waitForMatchingService(IOBSD, 30s)   :691  (prints "!BSD" on timeout)
                  | mountAttempts++ -> "mount(N) failed" :700
                  | parse "rd"/"rootdev" into rdBootVar   :719
                  | DT /chosen root-matching              :724
                  | a5xelte_keys_init()                   :787
                  | [M30LTE] a5xelte_touch_probe skipped  :788-790
                  | emmcprobe boot arg -> a5xelte_emmc_probe()  :792-797
                  | rd=="emmcroot0" -> a5xelte_emmc_rootdev()   :799+
                  |    -> emmc_map_host(), emmc_find_root_partition()
                  |    -> bdevsw/cdevsw add, devfs node /dev/emmcroot0
                  |    -> "A5XELTE eMMC: /dev/emmcroot0 ready..."
                  |    -> "BSD root: emmcroot0, major ..., minor ..."
                  | else: IOMedia/Apple_HFS matching -> waitForService loop
                  |    -> on iOS target: panic("Failed to mount root device")
           vfs_mountroot()             bsd_init.c:882 / vfs_subr.c:1210
             -> bdevvp(rootdev), iterate vfsconf; hfs can mount root
             -> on failure: rootdevice[0]=0, loop back to setconf()
```

## 2. Did XNU reach this path on M30? NOT DEMONSTRATED.

- v7 physical evidence: screen hung at `SWEET FB: AppleCLCD ...` /
  `A5XELTE FB: requested 30 Hz ... copy timing on` (user: same as v6).
  That is framebuffer-only evidence; it proves the console was up, not that
  `bsd_init()`/`IOFindBSDRoot()` ran.
- The 0407 `M30 ROOT:` markers exist in the kernel but produced **no physical
  evidence**, because the 0406 pmsg mirror was inert (newline early-return bug;
  fixed in commit e337365).
- `last_kmsg` shows S-Boot loading our image and PINRST, no XNU text (XNU
  console is framebuffer-only). No panic line was recovered.
- Conclusion: whether XNU reaches `IOFindBSDRoot()` is **unknown** until a log
  path works. Do not claim it from framebuffer output.

## 3. Existing eMMC driver and root support (all linked, no new code needed)

- `bsd/dev/a5xelte_emmc.c`: raw block/char device `/dev/emmcroot0`, GPT probe
  (LBA1 header + entries, CRC checks), partition name from `emmcroot`
  (default `SYSTEM`, only SYSTEM/USERDATA accepted), data via PIO reads.
  Register window from ADT `m30lte-emmc` @ 0x13500000 (`M30LTE.h:41-42`).
- Read-only by default: writes require `emmcroot=USERDATA` **and** `emmcwrite=1`.
- `a5xelte_emmc_probe()` gated by `emmcprobe=1` boot arg.
- `rd=emmcroot0` activates `a5xelte_emmc_rootdev()` -> devfs node + `BSD root:`.
- Filesystems: `sweet_hfs` is compiled in (`FILESYS_BASE` includes `sweet_hfs`)
  and registered in `bsd_init` (`SWEET HFS: hfs-627.100.6 registered` in kernel
  strings). `mockfs`, `devfs`, `fdesc` also present. No IOStorageFamily/IOMedia
  (patches 0103/0022 handle the missing-class asserts).

## 4. Exact missing components

1. **No `rd=` in the current cmdline** (`debug=0xc serial=3 cpus=1 keepsyms=1
   maxmem=292`). With no rd, `IOFindBSDRoot()` falls back to "any IOMedia with
   Content=Apple_HFS"; this kernel has no IOMedia class, so no service can match
   -> `waitForService` loop -> iOS-target `panic("Failed to mount root device")`.
   FIX (offline, from existing inputs): add `rd=emmcroot0 emmcprobe=1` to the
   payload cmdline. This activates the already-linked root path.
2. **No genuine iOS root filesystem.** `tools/mkiosroot.sh` requires IPSW
   `OS.dmg`/`SYSTEMOS.dmg`/`APPOS.dmg` plus host tools `apfs-fuse`,
   `mkfs.hfsplus`, `rsync` — none present. The only ramdisk in-tree
   (`out/stock_boot/ramdisk`) is a gzip Android cpio initramfs, not an HFS/APFS
   iOS root. The device's `SYSTEM`/`USERDATA` partitions are Android filesystems
   (ext4/f2fs), not HFS. Even with `rd=emmcroot0`, `vfs_mountroot()` cannot mount
   an iOS root. No partition layout or filesystem contents may be invented.
3. **Diagnostics gap:** fixed by the 0406 newline fix so a future authorized
   test can actually see which `M30 ROOT:` marker is last.

## 5. Implemented (this round)

- Corrected 0406: verified signature `0x43474244` (Linux 4.4.177 and 6.1 pass
  zone sig arg 0 for PMSG), strict header validation (start<=size<=cap, reject
  wrong zone types/DMESG sig, adopt zeroed zone), and hook moved before the
  `\r`/`\n` early returns.
- `tools/test_pmsg_mirror.py`: full offline suite, all cases pass.
- Candidate v8 cmdline: `debug=0xc serial=3 cpus=1 keepsyms=1 maxmem=292
  rd=emmcroot0 emmcprobe=1` — preserves the ramoops reservation, activates the
  eMMC root path, no invented layouts/contents.

## 6. Remaining blockers

- Root **mounting** is not demonstrated and cannot be: no genuine iOS root FS
  assets. `rd=emmcroot0` only proves root-device *selection* in a future test.
- Whether XNU reaches `IOFindBSDRoot()` at all remains unproven until an
  authorized physical test with the fixed mirror recovers a `M30 ROOT:` record.
- No iOS userspace/SpringBoard boot is claimed.
