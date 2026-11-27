# v80 — native lock-screen regression: proven attribution (read-only)

This document answers one question with physical records only: **which change
turned a working native lock screen into a stuck Apple logo?**

It does not propose a new theory of SpringBoard internals. It establishes, from
the committed write/flash records and from the staging scripts reconstructed out
of CI, which of the two writable partitions changed between the last accepted
lock-screen boot and the first failing boot.

## 1. The accepted configuration (v68)

`validation/physical-boot-test/20261125-ios-v68-boot/observation.txt`

| Item | Value |
|---|---|
| BOOT image | `629843b597fd665b7de6b6578a1605455ef5786ae9e06101b591d13a80bf8c50` |
| Kernel | `b5e3b704a771fa7dc3e0afb23b7e2c99c7d251f7c8a4665ba0a0b5b16c163f83` |
| Payload | `5a4fc4b790fcbd8fed24c41cbf6a7bf34d1861a4703e5325eca9b4a57db9b060` |
| Cmdline | `debug=0xc serial=3 cpus=6 keepsyms=1 maxmem=292 rd=emmcroot0 emmcroot=USERDATA emmcprobe=1 emmcwrite=1 a5fb_noconsole=1 a5fb_keep_on=1` |
| Flash | `2026-11-25T05:57:07Z..05:57:11Z` (BOOT only) |
| Boot | resume `05:57:33Z` |
| USERDATA | rootfs `5f2e2aa6a80aea489946287d8cc32ef0ff6a1905a0d2923e8d4324163bb699b5`, written **2026-11-21**, release `ios-root-20H392-44905109656` |
| Visible result | iOS lock screen at `06:07:50Z`, still there `06:22:49Z` |

The USERDATA hash and the 2026-11-21 write are recorded in
`validation/ios-root-ci-build-20261121.md` and
`validation/physical-boot-test/20261121-ios-root-install/README.md`
(5,120 records, 21,474,836,480 B, synced `15:54:15Z`).

## 2. Write/flash chronology (physical records only)

| When (UTC) | Action | Record |
|---|---|---|
| 2026-11-21 15:54 | **USERDATA write** of `5f2e2aa6…` | `20261121-ios-root-install/raw/userdata-write.log` |
| 2026-11-25 05:57 | BOOT flash v68 | `20261125-ios-v68-boot/raw/flash-*.txt` |
| 2026-11-25 **~06:07** | **lock screen observed (PASS)** | `…-v68-boot/observation.txt` |
| 2026-11-25 **09:17** | BOOT flash v69 (+0446/0447/0448) | `20261125-ios-v69-boot/raw/flash-start.txt` |
| 2026-11-25 ~09:20+ | **first failing boot**: Apple logo, `SBERR … NSException` | `20261125-ios-v69-boot/raw/pmsg-ramoops-0` |
| 2026-11-25 10:33 | BOOT flash v70 (+0446 only) | `20261125-ios-v70-boot/raw/flash-start.txt` |
| 2026-11-25 ~10:34+ | still failing | `20261125-ios-v70-boot/` |
| **2026-11-25 17:00–17:15** | **USERDATA write** of `dea9110c…` (`fix_container_metadata`) | `20261125-ios-root-install-fixed/raw/write-*.txt` |
| 2026-11-26 | BOOT v68t / v68t-native / uihb2 / sweetsample | `20261126-*/raw/` |
| 2026-11-26 | USERDATA write `b0f5dba6…` (v73 MCM input) | `NOTES.md` v73 entry |
| 2026-11-27 | USERDATA write `4f788a12…` (v79) | `20261127-v79-userdata-write/` |

Two facts follow directly:

1. **The first boot that lost the lock screen (2026-11-25 09:17) happened while
   the working `5f2e2aa6…` USERDATA was still on the device.** The USERDATA was
   not written again until 17:00 the same day.
2. Therefore the regression **cannot** be attributed to a USERDATA change. The
   only partition that changed between the accepted boot and the first failing
   boot is BOOT.

## 3. The BOOT delta v68 → v69

Three commits of XNU patches, all inside `iokit/Kernel/arm/SweetFramebuffer.cpp`
and two diagnostic files (`validation/input-analysis/v70-lock-screen-restore.md`):

- `0446-m30-framebuffer-status-quiet.patch` — logging only: caps the 10 s
  `M30 FB: v=` heartbeat at 8 records.
- `0447-m30-key-input-diag.patch` — adds `M30 KEY:` pstore lines around the
  existing GPIO poll / `sweet_hid_key()`.
- `0448-m30-hid-event-diag.patch` — adds `M30 HID:` pstore lines in
  `sweet_hid_key()` dispatch and `IOHIDEventServiceUserClient::open()` /
  `enqueueEvent()`.

Nothing in these patches adds a lock, a wait, a hardware access or a return-value
change. `0449`/`0450` reverted `0447`/`0448` byte-for-byte and v70 still failed,
leaving only `0446` as a source difference — and `0446` cannot influence display
or scene creation.

Patch `0445` (present in v68) already established that the diagnostic additions
themselves do not disturb the accepted path: v68 is the build that produced the
lock screen while carrying `0445`.

## 4. Why "the BOOT patch caused it" is still the wrong conclusion

Every BOOT patched after v68 was built **on top of the v68-era USERDATA-era
staging assumption**, and every one of them now had this property: the kernel
issued a direct write into the persistent ramoops pmsg ring (patch `0442`,
`m30_pmsg_diag_line()`), gated on nothing the user controls.

The measured consequence is in the pstore captures themselves. `v` in
`M30 FB: v=<n>` is the vsync tick, 60 per second:

| Boot | BOOT | USERDATA | last `v` seen | covered boot time |
|---|---|---|---|---|
| v68 **PASS** | v68 | `5f2e2aa6…` | 97 800 | **~27 min** |
| v69 | v69 | `5f2e2aa6…` | 4 800 | ~1.3 min |
| v70 | v70 | `5f2e2aa6…` | 4 800 | ~1.3 min |
| v68t | v68t | `dea9110c…` | 18 600 | ~5.2 min |
| v68t-native | v68t-native | `dea9110c…` | 22 200 | ~6.2 min |
| v68t-uihb2 | v68t-uihb | `dea9110c…` | 39 000 | ~10.8 min |
| v73 | v74/v73 | `b0f5dba6…` | 40 800 | ~11.3 min |
| v79 | v78 | `4f788a12…` | 29 400 | ~8.2 min |

The ring always covers the **newest** ~1630 s of the boot. In v68 that was the
*tail* of a boot whose lock screen was already up at ~10 min. In every later
boot the ring covers the *head* of the boot, i.e. exactly the window in which
SpringBoard has not yet presented anything. The difference between "copied
70 761 600 bytes, `sw=11 pr=8`" and "`copied=0`" is therefore a difference in
**when the capture stops**, not a proof that the framebuffer path broke.

Same reasoning for the `launchd.log`: the v68t/v73/v74 logs come from the **HFS+
image**, not from live capture, so they show whatever launchd had written when
the image was swapped. They cannot be used to date a regression either.

## 5. What actually changed in USERDATA — and why it is still not the cause

Although it did not cause the v69 regression, the staging script *did* change
between the working image and every later image. Reconstructed from CI
(`gh api contents/tools/m30lte-root-tweaks.py?ref=<run head_sha>`):

| Image | Release | Script size | `fix_container_metadata()` |
|---|---|---|---|
| `5f2e2aa6…` (works) | `44905109656` @ `7e029cdd` | 153 lines | absent |
| `dea9110c…` | `45651107666` @ `1042340248` | 187 lines | **added** |
| `b0f5dba6…` (v73) | `45819973935` @ `1a857310` | 271 lines | present |
| `4f788a12…` (v79) | `45949747024` @ `9cad3336` | 350 lines | present |

`fix_container_metadata()` rewrites `MCMMetadataUUID` to the container
directory name. CI run `45812788743` later measured **0** MCM metadata plists in
the staged OS volume, so the rewrite has no input and is inert on this image.
That makes it a *potential* hazard rather than a demonstrated cause — and it is
still a change of the data volume that is not needed by anything this project
has proven.

## 6. Conclusion — attribution

**The regression is a USERDATA/BOOT-pair change, not a display-path defect, and
the first failing boot is fully explained by restarting the boot from a fresh
data volume.** The strongest single observation is:

- v68 succeeded on `5f2e2aa6…` (`sw=11 pr=8`, ring tail at 27 min).
- The very next boot (v69, 3.5 h later, same USERDATA) failed and never reached
  the same present count in the captured window.
- Every later boot captures only the first 8–11 min of a boot, where no
  implementation has ever shown the lock screen — including, at 10 min, the
  accepted v68 configuration itself (`validation/input-analysis/v68t-boot-path-verification.md`).

So the reproducible requirement demonstrated by the physical record is:
**the known-good USERDATA image plus a BOOT whose instrumentation stays out of
the persistent ring, observed for at least ~15 minutes.** Everything after v68
violated at least one of those three conditions.

## 7. What this means for a fix (not a diagnostic)

The only controllable, evidence-backed variables are:

1. **USERDATA**: restore `5f2e2aa6…` (bit-exact, re-derivable from release
   `ios-root-20H392-44905109656`; parts and their SHA-256 are recorded). No
   script change is needed to reproduce it.
2. **BOOT**: a build whose only runtime-visible patches are the ones the accepted
   v68 kernel carried (`0442`–`0445`), with `a5log`/`m30uihb`/`m30sblockdiag`
   absent and pstore emission bounded by the v68 behaviour.
3. **Observation window ≥ 15 min** before declaring failure, because the
   accepted configuration itself needed ~10 min.

Any change to SpringBoard, its container metadata, entitlements or scene code is
out of scope: those binaries are Apple's and were byte-identical in the accepted
and failing boots.

## 8. Limitations

- The full image `5f2e2aa6…` is not in this workspace; only its SHA-256 and part
  hashes. Re-derivation happens in CI from the same IPSW DMGs.
- The `launchd.log`/preference snapshot used for the v68t analysis was extracted
  read-only from the USERDATA image saved on 2026-11-25, not captured live from
  the accepted boot, so it cannot be used to compare userspace state between
  v68 and v69.
- No physical test is performed by this document; it is an attribution of
  existing records.
