# v62 physical BOOT-only test — MAIN only

## Candidate
- Source: `b667f247` (`v62 source: compact UI liveness telemetry`)
- CI: `45356410574` GREEN, source `b667f247`, `XNU_TARGET=iphoneos`, M30LTE,
  DEVELOPMENT; LSE count 0.
- Kernel SHA256: `45aff1b01f85b1dbe5a77903050005333eb858980cd1118465c3f11f02bda13d`
- Payload SHA256: `e1c41dd83ee70cafc7af9ab91c8c20ed5320ee54a87392434790870d99d39bd0`
- `shim-boot.img` SHA256: `7798b211ebc9773df3225732e572dc18d091d2805cc1f7be72f967fbdd0913c7`

## Identity and write gate
Verified in TWRP before any write:
- `ro.boot.em.model=SM-M305F`
- `ro.product.device=m30lte`
- `ro.serialno=320081735bb166a3`
- `ro.boot.serialno=320081735bb166a3`
- `ro.bootloader=M305FDDU8CVK1`
- `ro.twrp.boot=1`
- `adb devices -l`: `320081735bb166a3 recovery ... device:m30lte`
- Download Mode: `heimdall detect` -> `Device detected`

Only `BOOT` was flashed with Heimdall (`--BOOT`, `--no-reboot`). USERDATA,
SYSTEM and RECOVERY were not written; no Fastboot was used.

## Timeline (UTC / IST)
- Identity check: `10:27Z` / `15:57 IST`
- Download Mode confirmed: `10:27Z` / `15:57 IST`
- BOOT flash: `10:27:49Z..10:27:54Z` / `15:57:49..15:57:54 IST`
- Resume: `10:28:01Z` / `15:58:01 IST`
- Pstore capture after recovery return: `10:48Z` / `16:18 IST` (~20 min boot)

## Evidence hashes
- Raw pstore `raw/pmsg-ramoops-0`:
  `2bc2179e27603d997ebe97851b7e0dd7eccdb878c56b8838f211d763004a85e7`
- `decoded-pmsg.txt`:
  `bf29d162620da67980eeb924aa60a2936816de280a075759adb73aa84819c002`
- `decode-pmsg-report.json`:
  `f33fe3dbed2fec86ab43b9df4f43dbba283454e3f5749f3883526691ea8f6144`
- `decoded-bootlog.txt`:
  `65801d7fe712554dff8c7002574565687bd588bd6794a433a24b1ab2e1dfbdd9`

## Result from pstore
- Compact telemetry line survived: `M30 UI: sb=27 bb=57 reason=none`.
  SpringBoard pid 27 and backboardd pid 57 were alive with no captured NS
  reason at that sample.
- `SMP SpringBoard[27] slide 0x3f420000 mh 0x100008000`.
  Main-thread sample: pc `0x201a31030`, lr `0x201a42b18`; unslid
  `0x1c2611030` / `0x1c2622b18` — the same location as the v60 long run.
- IRT final full record: `state=3`, counters
  `csblk=3948 csfail=9 csvok=36811 cfa=4 cfi=5 cfp=0`.
- Backboardd actively used the framebuffer: `SWEET FB: display on`, created a
  `1080x2340` surface, multiple FB/SURFACE selectors.
- Only crash in the captured window: `driverkitd[68] sig 9` (killed). No
  SpringBoard or backboardd crash, no `NSInternal`, no `state=4`.
- The 16 KB ring still wrapped heavily (many repeated ATS/securityd lines), so
  only one compact UI line survived; it still proved both UI processes alive.

## Visual result
No lock-screen success is claimed from logs, process PIDs, framebuffer activity,
or IRT state. Visual confirmation is required.
