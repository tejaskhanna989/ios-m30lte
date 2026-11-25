# v68 native Melfas MSS100 touch evidence

## Board evidence (read from the physical SM-M305F)
- `i2c@13870000/mms_ts@48`, compatible `melfas,mms_ts`
- firmware `tsp_melfas/mss100_m30.fw`
- bus `samsung,s3c2440-i2c`, MMIO `0x13870000`, size `0x100`
- 7-bit I2C address `0x48`
- IRQ GPA0-0 / GPIO 6 / Linux IRQ 243, level-triggered
- `melfas,event_info = <8 12>` (format 8, 12-byte events)
- `melfas,max_x_y = <4095 4095>`
- HID logical space on M30LTE build: 1080x1920 (framebuffer 1080x2340)

## Source provenance
Samsung Exynos 7904 kernel (m30lte board), commit
`554e05f367dfa36c2eefcf1dfaea64946ee6a76f`:
- `drivers/input/touchscreen/melfas_mss100/melfas_mss100_reg.h` SHA256
  `8d42c742804bdf3e58bd354ca9b3df0e9bbc616f9dcf2f5f84124cef420d6b4b`
- `melfas_mss100.c` SHA256
  `9c48c725dc866c2aa5795fdaacf56259f041291edd0d2096791e255420f6efca`
- `melfas_mss100_mod.c` SHA256
  `304b6abd68a8cc05aa9142da4d1e1afd73ffc4f95c8a08bcca0197f26b1c68d2`
- `melfas_mss100_cmd.c` SHA256
  `45db9b4cffb70d6eed0c4031205bb8c68abe1ed7f7016205d9c9c3f9174b5cf9`
- `arch/arm64/boot/dts/exynos/exynos7904-m30lte_common.dtsi` SHA256
  `ba57182a99448a01db3a0b73885174c5b80b8c197d57d32cbf6c3e9cc454cea7`

Sources are cached under `/tmp/opencode/melfas-evidence/` (not committed).

## MIP 4.0 registers / protocol
- `[0x06,0x00]` status: `0xA0` READY, `0x05` NONE, `0x77` LOG.
- `[0x02,0x10]` packet info: `size = b & 0x7f`, `category = b >> 7`.
- `[0x02,0x11]` packet data.
- Format 8 (`EVENT_FORMAT_WITH_PRESSURE_2BYTE`), 12-byte packets:
  `type = (p[0]&0xf0)>>4`, `id = (p[0]&0x0f)-1`, `down = p[1]&1`,
  `x = ((p[2]&0x0f)<<8)|p[3]`, `y = (((p[2]>>4)&0x0f)<<8)|p[4]`.

## Driver policy
- M30LTE-only source, compiled only when `ARM64_BOARD_CONFIG_M30LTE` is set.
- Opt-in boot arg `m30touch=1`; HID delivery separately gated by `m30touchhid=1`
  so probe/diagnostics can be tested without dispatching events.
- Bounded I2C transfers, bounded worker loops, 8-error stop, no controller
  config/firmware/NVM writes.
- IRQ: XNU routing of IRQ 243 is **not proven**; the driver samples GPA0-0
  through ALIVE/GPA0DAT (`0x11cb0000 + 0x4`) in the bounded worker and counts
  line edges. This is a diagnostic sampler, not an interrupt handler.
- Contact timeout releases prevent stuck fingers when packets stop.
- Raw 0..4095 axes scaled to 1080x1920 for `sweet_hid_touch()`.

## Limits
No physical touch proof exists. Only a CI-reviewed candidate plus an approved
physical boot with contact logs and a touch action above IOHID can establish
support.
