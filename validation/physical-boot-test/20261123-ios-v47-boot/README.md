# v47 physical boot — subcache mapping found, patch not yet applied

Device: Samsung Galaxy M30 SM-M305F (`m30lte`), serial `320081735bb166a3`,
TWRP recovery. Package: `validation/ios-candidate-v47-out/shim-boot.img`
SHA256 `23e131d59da50441967018d523b6b1888db1168f6eaaa339847c2108cbd7374c`.

BOOT-only flash succeeded. No BOOT readback. USERDATA, SYSTEM, and RECOVERY
were not rewritten. The device was returned to TWRP and pstore was pulled.

## Raw evidence

- `raw/pre-pmsg-ramoops-0`: v46 pstore, SHA256
  `391ee54587d62b41209660ae10842b051c986bee5232723016e459d3b64df6b8`.
- `raw/pmsg-ramoops-0`: v47 pstore, 16,372 B, SHA256
  `da5de4e93fc6a37d836b270f670b1d36f98a0c8466c269415e2d5e619cc0797e`.
- `decoded-bootlog.txt`: decoded with `tools/m30_bootlog.py inspect`
  (94 records, 2 gap issues).

## Decisive result

The authoritative subcache enumeration worked. Full status lines report:

```text
M30 IRT status: state=2 off=0xa432d84 err=0 replay=29 comp=0 ls=0x4000 sym=0x1e1d3ad84 img=0x1d1c22000 hits=1 tries=29 sc=42 si=26 symmap=0x22ade8000/0x4000@0x0 fb=0x0 basecnt=1 base0=0x1ecc80000/0x62ac000@0x0
```

The final heartbeat reports:

```text
M30 IRT final: state=2 off=0xa432d84 err=0 sym=0x1e1d3ad84 comp=0 ls=0x4000 nlist_cnt=8705811 nlist_range=146 hits=1 tries=29 sc=42 si=26 fb=0x0 hb=67
```

Therefore:

- The main cache header exposed 42 subcache entries (`sc=42`), and entry 26
  (`si=26`) supplied the real cache file whose mapping contains
  `_internal_release_type`.
- `hits=1` (down from `tries=29`) confirms the mapping succeeded without the
  companion-map fallback (`fb=0x0`).
- The resolved file offset is `off=0xa432d84`, and the worker reached
  `M30_IRT_STATE_HAVE_OFF` (`state=2`).
- There is **no** `M30 IRT: patched` marker. The page write never happened.
  v47 does not confirm `_internal_release_type` patching.

The captured window contains normal userspace code-signing/daemon records
(accessoryupdater, seld, fseventsd, familynotificati, mtmergeprops, peopled),
but no `Early boot complete`, no SpringBoard code-signing line, no
SpringBoardUI assertion, and no UI/lock-screen evidence.

## Next correction

The remaining `HAVE_OFF` stall can be one of:

1. the fault hook never sees another page fault in the target vnode after the
   offset is resolved, or
2. the pager returns a different vnode instance than `vnode_open()` and the
   pointer-only target gate rejects it.

v48 adds strict `(mount, vnode id)` identity matching plus HAVE_OFF fault,
target-match, and offset-match counters in the heartbeat. It also patches the
already-resident page directly after the offset is known: resolve the target
vnode's VM object, require the page to be code-signing validated, wire it, and
write only the in-memory page. This covers the likely case where the target
page was faulted before the deferred symbol scan finished. No file write and no
security check is weakened.
