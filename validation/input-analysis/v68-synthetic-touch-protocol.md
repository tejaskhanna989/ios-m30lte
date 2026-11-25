# M30TOUCH v1 — v68 synthetic touch injection protocol and transport gap

## 1. What was verified in the restored v68 source

At baseline `6689d234ed8d4378552a4c31212d71fdb08228dd`:

- `sweet_hid_touch(int finger, int down, int x, int y)` exists in
  `iokit/Kernel/arm/hid/SweetHID.cpp` (line ~566) and calls
  `gSweetTouch->touch(finger, down != 0, x, y)` when the service is registered.
  Its digitizer service is registered in `KernelConfigTables.cpp`; events flow
  through `IOHIDEventServiceUserClient` queues to user clients (backboardd) and
  then SpringBoard/UIKit.
- `SweetHIDTouch::touch()` clamps `x` to `0..1079` and `y` to `0..fLogicalH-1`;
  on `ARM64_BOARD_CONFIG_M30LTE` the compiled branch uses `fLogicalW=1080`,
  `fLogicalH=1920`. Finger limit is `SWEET_TOUCH_FINGERS = 10`.
- The user client exposes only open/close/copyEvent/setElementValue/
  copyMatchingEvent. There is **no** userspace injection selector, so an
  existing HID user client cannot inject events by itself.
- `M30LTE.h` defines `SWEET=1`, so `bsd/dev/sweet_usb.c` is compiled for M30.
  Its DWC3 gadget handles USB **standard** control requests only. In the OUT
  data stage it explicitly starts a 64-byte receive but ignores the bytes
  (`/* OUT data is not used here */`). Its live-log thread streams console
  text **to** the host. Therefore USB currently provides log output, not a
  host-to-device command channel.
- `pexpert/arm/pe_serial.c` implements `serial_getc()` / `uart_getc()` and
  `receive_data` callbacks, but no M30 code polls them for commands. Serial
  input is not a verified command channel.
- There is no adbd or equivalent Android input command service in the v68
  source. Do not assume ADB works.

**Conclusion:** there is no verified, safe host-to-device command transport in
v68. This task therefore delivers the host utility and a strict protocol
specification; it does **not** claim a working injected event path.

## 2. Wire format (all little-endian, 14 bytes)

| Offset | Size | Field | Meaning |
|---|---|---|---|
| 0x00 | 4 | magic | `M30T` |
| 0x04 | 1 | version | `1` |
| 0x05 | 1 | opcode | 1 down, 2 move, 3 up, 4 release-all |
| 0x06 | 1 | finger | `0..9` |
| 0x07 | 1 | flags | must be `0` |
| 0x08 | 2 | x | `0..1079` |
| 0x0a | 2 | y | `0..1919` |
| 0x0c | 2 | checksum | sum of bytes `0x00..0x0b`, masked to 16 bits |

No strings, no variable length, no arbitrary memory addresses, no kernel
command passthrough. Unknown opcodes, non-zero flags, bad checksums, invalid
fingers and out-of-range coordinates must be rejected without calling HID.

## 3. Host utility

`tools/m30touch.py` implements:

```
m30touch [--finger N] [--transport dry-run|memory|serial|usb|socket]
         [--device PATH] [--steps N] [--delay-ms N] [--debug-enable]
         tap X Y | down X Y | move X Y | up | release | swipe X1 Y1 X2 Y2
```

- Default is **dry-run**: validates arguments and prints the exact frames.
- Real I/O requires `--debug-enable` (or `M30TOUCH_DEBUG=1`) **and** an explicit
  transport. This is the debug-only production-disabled gate.
- `tap` sends DOWN then UP. `swipe` sends DOWN, interpolated MOVE frames, UP.
- Interrupt and transport-failure paths send a best-effort UP for every active
  finger; a disconnect may still prevent delivery.
- Coordinates are validated against the HID logical space (1080x1920), not the
  1080x2340 framebuffer, because `SweetHIDTouch::touch()` consumes the former.

## 4. Minimal device-side work still required (not implemented here)

One of these transports must be added before the utility can inject anything;
both must be gated by a dedicated boot arg `m30touchinject=1` and disabled by
default:

1. **USB vendor control OUT (smallest change).** Extend `ud_setup()` in
   `bsd/dev/sweet_usb.c`: accept vendor requests (`bmRequestType & 0x40`),
   receive the 14-byte frame in the existing ep0 OUT buffer, validate it with
   the same rules as the host parser, map opcode to `sweet_hid_touch()`:
   down/move use `down=1`, up/release use `down=0`, release-all iterates
   fingers `0..9`. Call only from the existing `ud_thread` context; bound work
   to one frame per request and never block waiting for host input.
2. **Serial polled commands.** Add a small debug thread that reads bytes with
   `serial_getc()` and assembles the same 14-byte frame; must time out and
   never stall boot.

Neither is implemented in this change. No physical flash, reboot or device
operation was performed.

## 5. Evidence limits

A passing host test proves only command/frame correctness. It does **not** prove
that frames reached XNU, that `sweet_hid_touch()` was called, that SpringBoard
responded, or that the physical Melfas touchscreen works. Those require the
device-side transport plus a separately approved physical test.
