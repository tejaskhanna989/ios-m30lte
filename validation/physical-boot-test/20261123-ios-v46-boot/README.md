# v46 physical boot — decisive IRT failure evidence

Device: Samsung Galaxy M30 SM-M305F (`m30lte`), serial `320081735bb166a3`,
TWRP recovery. Package: `validation/ios-candidate-v46-out/shim-boot.img`
SHA256 `831fb5141ef91e90a6b534779f897944bf883a224f4823b86f83cf47390cb826`.

BOOT-only flash succeeded. No BOOT readback. USERDATA, SYSTEM, and RECOVERY
were not rewritten. The device was returned to TWRP and pstore was pulled.

## Raw evidence

- `raw/pre-pmsg-ramoops-0`: pre-flash v45 pstore, SHA256
  `c3a897cba60b96c66ddfec30d533845ed48fa2350b094e079c6603ef7376d4da`.
- `raw/pmsg-ramoops-0`: v46 pstore, 16,372 B, SHA256
  `391ee54587d62b41209660ae10842b051c986bee5232723016e459d3b64df6b8`.
- `decoded-bootlog.txt`: decoded with `tools/m30_bootlog.py inspect`
  (110 records, 1 gap issue).

## Decisive result

No `M30 IRT: patched` marker exists. The durable heartbeat survived the
wrapped ring and repeatedly reports failure:

```text
M30 IRT final: state=4 off=0x0 err=0 sym=0x1e1d3ad84 comp=0 ls=0x4000 nlist_cnt=8705811 nlist_range=146 hits=0 tries=138 fb=0x0 hb=0
...
M30 IRT final: state=4 off=0x0 err=0 sym=0x1e1d3ad84 comp=0 ls=0x4000 nlist_cnt=8705811 nlist_range=146 hits=0 tries=138 fb=0x0 hb=55
```

Periodic full status lines also survived:

```text
M30 IRT status: state=4 off=0x0 err=0 replay=29 comp=0 ls=0x4000 sym=0x1e1d3ad84 img=0x1d1c22000 hits=0 tries=138 symmap=0x22ade8000/0x4000@0x0 fb=0x0 basecnt=1 base0=0x1ecc80000/0x62ac000@0x0
```

Therefore:

- The Cryptex `.symbols` companion was selected (`comp=0`, `ls=0x4000`).
- The image-scoped local-symbol lookup succeeded (`nlist_cnt=8705811`,
  `nlist_range=146`) and found `_internal_release_type` at vmaddr
  `0x1e1d3ad84`.
- No real cache mapping contained that vmaddr (`hits=0` after `tries=138`).
  Only numeric `.0`-`.511` subcache names were tried; dyld4 subcaches can use
  suffixed names such as `.03.development` or `.25.data` from the header's
  subcache-entry array.
- `_internal_release_type` was **not** patched. `off=0x0`, `fb=0x0`, and
  final state `4` (FAILED).

The final captured window does not contain `Early boot complete` or a
SpringBoard code-signing line. It does contain `CRASH backboardd` and an
`NSInvalidArgumentException` from `-[NSURL initFileURLWithPath:]` with a nil
path. This is not the earlier SpringBoardUI assertion, but it is also not
evidence of SpringBoard UI startup.

The heartbeat mechanism itself worked: the decisive state survived into the
final 16 KB pstore window (`hb=0` through `hb=55`).

Next correction: enumerate exact subcache filenames from the main cache
header's `subCacheArrayOffset`/`subCacheArrayCount` before the numeric fallback.
