# iOS candidate v12 — genuine iOS root mount achieved (2026-11-21)

## Authorization and actions

Explicit authorization: flash v12 BOOT only, verify BOOT readback, preserve USERDATA
(no rewrite/format), one boot, capture pstore on recovery return, no retry.
Work on `main` @ `101c045`. Device re-confirmed: `m30lte`, samsung, `M305FDDU8CVK1`,
serial `320081735bb166a3`, TWRP `3.4.03.0.0-UNOFFICIAL`.

- v12 SHA-256 verified `fccd2422d16ba9adc3d0d3bd8474f6d4e488f81086df35abdfeb7be7a8d1dd41`.
- `heimdall flash --BOOT ... --no-reboot` → "BOOT upload successful".
- **BOOT readback was not performed**: the user booted the device directly before a
  readback could be issued ("i have booted it u just recover the XNU log"). Do not
  claim a BOOT readback happened.
- One boot occurred (user-initiated). No retry, no reflash. SYSTEM/RECOVERY untouched.
- Local rootfs image preserved (`~/Downloads/ios-root-20H392.img`, not deleted).

## Raw evidence (captured immediately on recovery return)

- `raw/pmsg-ramoops-0` SHA `2b243c96ff3c7fe06ffed83cdade1297818ae42a430f4a58267f0755e74f4b38`
  (16,372 B, 198 XNU records, 1 seam issue) — original raw preserved.
- `raw/pre-pmsg-ramoops-0` (pre-boot baseline), `raw/pstore-listing.txt`,
  `last_kmsg-postboot.txt`, `dmesg-postboot.txt`.

## Result — MAJOR MILESTONE

The `emmcwrite=1` fix worked. The genuine iOS 16.7.16 HFSX root **mounted successfully**:
```
A5XELTE eMMC: /dev/emmcroot0 ready, GPT USERDATA writable
BSD root: emmcroot0, major 1, minor 0
hfs: Initializing the journal (joffset 0xa2000 sz 0x800000)...
hfs: mounted iOSRoot on device b(1, 0)
A5XELTE: root volume is not authenticated (error 25); continuing unsealed
load_init_program: attempting to load /usr/appleinternal/sbin/launchd.development
load_init_program: attempting to load /sbin/launchd
```
This is the first genuine iOS root mount on the M30. The old EROFS journal blocker is
fixed. `launchd` load was attempted (path /sbin/launchd present in the image).

## New blocker — launchd code-signing panic

```
panic(cpu 0): Kernel data abort. pc 0xfffffff0077d9770 lr 0xfffffff0077d89b0
esr 0x96000007 far 0x1a0 (null+0x1a0 deref)
Panicked task pid 1: init; Panicked thread backtrace through:
  accelerate_entitlement_queries (pc 0xfffffff0077d9770)
  ubc_cs_blob_add (lr 0xfffffff0077d89b0)
  load_code_signature, parse_machfile, load_machfile
Device: D22 / iPhone10,3; boot args include emmcwrite=1 (confirmed in pmsg)
```
Symbolicated with the v12 kernel. This is a **kernel code-signing / AMFI entitlement
crash during launchd Mach-O load**, not a filesystem/root problem. The null+0x1a0
access in `accelerate_entitlement_queries` suggests a missing AMFI/entitlement service
or uninitialized code-signing blob state — the same area the donor handled with
`launchd_unsecure_cache=1` / `cs_enforcement_disable=1` / AMFI work.

## Honest status

- Genuine iOS HFSX root mounted ✓ (proven by pmsg).
- `load_init_program` reached and `/sbin/launchd` load attempted ✓.
- **launchd did NOT successfully boot** — kernel panicked in code-signing path.
- No SpringBoard, no iOS userspace running. Do not claim otherwise.
- BOOT readback not verified (user booted before it). Do not claim it.

## Next step (needs fresh authorization; not implemented here)

Investigate the AMFI/code-signing panic: donor evidence used boot-args
`launchd_unsecure_cache=1 cs_enforcement_disable=1` and an AppleMobileFileIntegrity
IOService. This kernel is genuine iOS target, so `launchd_unsecure_cache` may not be
compiled — must verify before relying on it. No physical ops performed for this doc.
