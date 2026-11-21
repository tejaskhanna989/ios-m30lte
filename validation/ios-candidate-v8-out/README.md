# iOS candidate v8 — corrected pmsg mirror + root-device selection args

Isolated candidate. v6, v7, all backups and all physical evidence preserved.

## What changed vs v7

| Item | v7 | v8 |
|---|---|---|
| Kernel SHA256 | `23ea642e…98206e` | `4b97d5e4…b7528379` |
| 0406 mirror | inert (newline early-return bug) | **fixed**: hook at top of `fbcon_transmit_data`, strict header validation |
| Payload cmdline | `... maxmem=292` | `... maxmem=292 rd=emmcroot0 emmcprobe=1` |
| pmsg signature | `0x43474244` (unchanged — verified correct) | same |

### Signature correction

An earlier claim that the PMSG signature should be `0x43474243` was **wrong** and
is retracted. Linux `fs/pstore/ram.c` passes zone sig argument 0 for the pmsg
zone in both the device kernel 4.4.177 and upstream v6.1, so
`sig = PERSISTENT_RAM_SIG ^ 0 = 0x43474244`. `PSTORE_TYPE_PMSG (7)` is the
pstore *frontend* type, not the zone sig argument. The real v7 failure was the
newline early-return. v8 keeps `0x43474244` and adds validation: reject wrong
zone types / corrupt headers (`start <= size <= cap`), adopt a zeroed zone.

### Root-device change

`rd=emmcroot0 emmcprobe=1` activates the already-linked
`a5xelte_emmc_probe()` / `a5xelte_emmc_rootdev()` path, which probes the GPT and
creates `/dev/emmcroot0`, replacing the no-`rd` fallback that waits on IOMedia
(absent in this kernel) and panics `Failed to mount root device` on iOS target.
Read-only by default (`emmcroot=SYSTEM`, `emmcwrite` unset) — no writes. No
partition layout or filesystem contents invented.

## Constraints preserved

- genuine iOS target (`XNU_TARGET_OS_IOS`, verified in CI);
- `maxmem=292` ramoops reservation (`avail_end = 0x92400000`);
- shim region byte-identical to physically proven v5/v6/v7:
  `864370f63a4208a41675e739d4bdb295f53ea3aea8ac58ef81b09f875d15211a`;
- no OSX target, no physical operations.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `4b97d5e4228151d5806e3ed9b688489596f55fcb9e470f8d1c2a0cb6b7528379` |
| payload | `9c57b0254f5bdcf026234d670aebe8bea664368b53560086d09cb1a1fce59508` |
| combined.bin | `255f2976ef0820b3ee9ed494054859598a93ac8f89b3c45aea1d5d6cc54d0951` |
| shim-boot.img | `c9f6d20de46ef1681ea98184e93c50614062666636f2faeb88aeb90fb9901c2c` |
| ios-boot.img | `e11c0e58398237eacf13545a69c12a775cdbd03a0a8259f39f7f2169d93e949d` |

## Validation (all offline)

- CI `44879419830`: **success**, `ios_define_present=True osx_define_present=False
  target=iphoneos`, LSE instructions = 0.
- buildtree **PASS**, kernel verifier **PASS** (6), platform **9/9**, CPU fallback
  **17/17**, ADT restore **22/22**, handoff **18/18**, packaging **PASS**.
- `test_pmsg_mirror.py`: **ALL PASS** — exact patch code compiles `-Werror`;
  fresh zone 3/3; real captured Linux records 33 preserved + 3 new, 0 issues;
  wraparound written across seam; bad signature / wrong zone / bad size /
  bad start all rejected with 0 records; pre-fix regression emits 0 records.
- `m30_bootlog.py selftest`: PASS. GIC audit 5/6 (known inapplicable DAIF check).
  `validate-repo.py`: 26 tools + 17 shell scripts syntax OK (7 pre-existing
  patch-sequence gaps unrelated to v8).

## Blockers

- Root **mounting** still not demonstrated: no genuine iOS root filesystem
  assets (IPSW DMGs, `apfs-fuse`, `mkfs.hfsplus`, `rsync` absent). Device SYSTEM
  partition is Android ext4/f2fs, not HFS. `rd=emmcroot0` only enables root
  *device selection*, not a mount.
- Whether XNU reaches `IOFindBSDRoot()` is still unproven; v8's fixed mirror
  would reveal it on a future **authorized** physical test (not performed).
- No iOS userspace / SpringBoard boot is claimed.

Detailed analysis: `validation/root-device-analysis-20261121.md`.
