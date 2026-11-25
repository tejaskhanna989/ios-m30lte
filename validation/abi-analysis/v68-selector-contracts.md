# v68 selector ABI evidence from genuine iOS 16.7.16 binaries

Status: evidence only. No kernel patch, candidate, CI kernel build or BOOT
write is justified by this document alone. No lock-screen claim is made.

## Provenance

- Source: genuine HFSX root release `ios-root-20H392-44905109656`, root SHA-256
  `5f2e2aa6a80aea489946287d8cc32ef0ff6a1905a0d2923e8d4324163bb699b5`.
- Extraction: `ios-abi-extract.yml` CI run `45524224404` (GREEN), artifact
  `ios-abi-evidence`, downloaded locally under `/tmp/opencode/abi-evidence3`.
- Binary: `extracted/IOMobileFramebuffer` (Mach-O 64-bit arm64 dylib),
  `__TEXT,__text` VMA `0x1af2230f8`, size `0xa218`.
- Disassembly: `llvm-objdump -d --macho --symbolize-operands`; local copy
  `/tmp/opencode/abi-evidence3/iomfb-objdump.txt`. Selected function bodies
  copied verbatim to `/tmp/opencode/abi-evidence3/iomfb-key-functions.txt`.
- Call-shape observations are from v67 pstore
  `validation/physical-boot-test/20261125-ios-v67-boot/decoded-pmsg.txt`.
  That logger records counts and sizes only, not scalar values or output bytes.

## IOKit call convention used by IOMobileFramebuffer

IOMobileFramebuffer calls three distinct IOKit entry points directly from the
dyld shared cache (addresses in the extracted binary):

- `0x1afb974bc`: 10-argument `IOConnectCallMethod` shape:
  connection, selector, scalar-input array, scalar count, struct-input pointer,
  struct-input size, scalar-output array, scalar-output-count pointer,
  struct-output pointer, struct-output-size pointer.
- `0x1afb974c8`: 6-argument scalar method shape:
  connection, selector, scalar-input array, scalar count, scalar-output array,
  scalar-output-count pointer.
- `0x1afb974d4`: 6-argument struct method shape:
  connection, selector, struct-input pointer, struct-input size,
  struct-output pointer, struct-output-size pointer.

A follow-up extraction run `45526096416` adds IOKit and explicit symbol
lookups for these three functions so the addresses can be confirmed by symbol
name rather than register shape alone.

## Selector 79 (`0x4f`): GetBlock

- Public wrapper `_IOMobileFramebufferGetBlock` at `0x1af2258a0` verifies the
  object and dispatches through the function table slot at object offset
  `0x8d8`; it returns `0xe00002c7` for a null object/slot.
- `_kern_GetBlock` at `0x1af224cac` builds a scalar-input array:
  - scalar[0] = 32-bit block ID (w1, zero-extended to 64 bits),
  - scalar[1] = current byte offset (starts at 0),
  - scalar[2..] = optional 32-bit extra arguments copied from the caller's
    `uint32_t *` array; scalar count is `2 + extra_count`.
- It calls `IOConnectCallMethod` with selector `0x4f`, no struct input, no
  scalar output, and a struct output at `destination + offset`. Each request
  is capped at `0x1000` bytes; the output-size cell is set to
  `min(remaining, 0x1000)`, then advanced by `0x1000` after each successful
  call. The loop exits when the offset reaches the requested size.
- The IOKit return code is propagated. If the requested size is zero, the
  wrapper returns `kIOReturnSuccess` without issuing a call.
- Therefore selector 79 is a **chunked byte-array read of a numbered block**.
  A 1,580-byte output is not, by itself, proof of a display-mode structure.
  The block ID and output meaning are not present in the v67 pstore record.

Observed v67 shape: `79 in 2/0 out 0/1580 -> 0x0` and
`79 in 2/0 out 0/40 -> 0x0`: exactly two scalar inputs (block ID + offset),
no struct input, no scalar output, and structure outputs of 1,580 and 40
bytes. These are consistent with this contract.

## Selector 74 (`0x4a`): SupportedFrameInfo

- Public wrapper `_IOMobileFramebufferSupportedFrameInfo` at `0x1af226350`
  returns a cached CFDictionary from object offset `0x5f0` when the key at
  `0x8f8` is initialized; otherwise it returns NULL.
- `_kern_SupportedFrameInfo` at `0x1af227c60` issues `IOConnectCallMethod`
  with one scalar input (an info type), one scalar output (a 32-bit count
  written to the caller's `uint32_t *`), and a 64-byte structure output whose
  size cell is initialized to `0x40`. The IOKit return code is propagated.
- Observed v67 shape `74 in 1/0 out 1/64 -> 0x0` matches this contract.
- Selector `0x49` (`ChangeFrameInfo`) is a different call: two scalar inputs
  `[3, id]` and no structures.

## Selector 84 (`0x54`): SetContrast

- `_kern_SetContrast` at `0x1af228854` stores the caller's 32-bit float in a
  stack slot and calls the 6-argument struct-method entry point `0x1afb974d4`
  with selector `0x54`, a 4-byte struct input, and no outputs.
- Observed v67 shape `84 in 0/4 out 0/0 -> 0x0` matches this contract.

## Selector 50 (`0x32`): SetBrightnessCorrection

- `_kern_SetBrightnessCorrection` at `0x1af224b78` calls the scalar-method
  entry point `0x1afb974c8` with two scalar inputs: the caller's 32-bit
  correction value and a cached correction word from object offset `0x660`.
- Observed v67 shape `50 in 2/0 out 0/0 -> 0x0` matches this contract.

## Selector 68 (`0x44`): SetParameter

- `_kern_SetParameter` at `0x1af223e54` validates parameter ID <= `0x13` and a
  non-null value array when the count is nonzero. Parameter ID 8 with one
  value <= 1 is handled locally by storing to object offset `0x664` and does
  not issue an IOKit call.
- All other cases call `IOConnectCallMethod` with selector `0x44`, one scalar
  input (parameter ID), and a struct input of `count * 8` bytes. The IOKit
  return code is propagated.
- Observed v67 shape `68 in 1/8 out 0/0 -> 0x0` is one parameter ID and one
  64-bit value.

## Selector 55 (`0x37`): SetMatrix

- `_IOMobileFramebufferSetMatrix` at `0x1af2237d0` requires a non-null matrix
  pointer, places the caller's matrix kind in one scalar input, and calls
  `IOConnectCallMethod` with a 72-byte (`0x48`) struct input and no outputs.
- `_IOMobileFramebufferGetMatrix` at `0x1af223384` uses selector `0x36` and
  requires both a scalar output and a 72-byte structure output; it checks the
  returned structure size is `0x48`.
- Observed v67 shape `55 in 1/72 out 0/0 -> 0x0` matches SetMatrix.

## What remains unknown

- The block IDs passed in the two selector-79 calls, and the byte layout of
  those blocks. The v67 pstore logger did not record scalar values.
- The actual field meanings of the 64-byte SupportedFrameInfo structure, and
  which info type the observed call requested.
- Whether any of these responses caused the observed post-four-present stall.
  Their current zero-filled success responses are not proven to be the cause.

No synthetic response should be implemented from these facts alone. A safe
next diagnostic is to log scalar inputs and output sizes for these selectors
without changing any returned bytes, then observe a real boot before deciding
on a content change.
