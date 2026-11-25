#!/usr/bin/env python3
"""m30touch - v68 synthetic touch injection host utility (debug-only).

This utility speaks the M30TOUCH v1 frame protocol defined in
``validation/input-analysis/v68-synthetic-touch-protocol.md``.  It does NOT
contain a physical Melfas driver and does not itself prove that touch works.

IMPORTANT: the v68 XNU tree has no verified host-to-device command consumer.
By default this tool is in dry-run mode: it validates commands and prints the
frames it would send.  Sending requires BOTH ``--debug-enable`` and an explicit
transport, and the device must implement the documented minimal command
handler (gated by ``m30touchinject=1``).  No connection is assumed.
"""
from __future__ import annotations

import argparse
import os
import signal
import struct
import sys
import time
from dataclasses import dataclass, field
from typing import Iterable

MAGIC = b"M30T"
VERSION = 1
HEADER = struct.Struct("<4sBBBBHHH")  # magic, ver, op, finger, flags, x, y, sum
FRAME_SIZE = HEADER.size

# Logical HID digitizer space used by SweetHIDTouch on ARM64_BOARD_CONFIG_M30LTE.
LOGICAL_W = 1080
LOGICAL_H = 1920
MAX_FINGERS = 10  # SWEET_TOUCH_FINGERS in SweetHID.cpp

OP_DOWN = 1
OP_MOVE = 2
OP_UP = 3
OP_RELEASE_ALL = 4
OP_NAMES = {OP_DOWN: "down", OP_MOVE: "move", OP_UP: "up",
            OP_RELEASE_ALL: "release-all"}
OPS = {name: op for op, name in OP_NAMES.items()}

DEBUG_ENV = "M30TOUCH_DEBUG"


class TouchError(Exception):
    """Invalid command, coordinate, finger, transport, or injection failure."""


def make_frame(op: int, finger: int, x: int = 0, y: int = 0) -> bytes:
    """Build one validated M30TOUCH v1 frame."""
    if op not in OP_NAMES:
        raise TouchError(f"invalid opcode {op}")
    if not 0 <= finger < MAX_FINGERS:
        raise TouchError(f"finger must be 0..{MAX_FINGERS - 1}, got {finger}")
    if not 0 <= x < LOGICAL_W:
        raise TouchError(f"x must be 0..{LOGICAL_W - 1}, got {x}")
    if not 0 <= y < LOGICAL_H:
        raise TouchError(f"y must be 0..{LOGICAL_H - 1}, got {y}")
    body = struct.pack("<4sBBBBHH", MAGIC, VERSION, op, finger, 0, x, y)
    checksum = sum(body) & 0xFFFF
    return body + struct.pack("<H", checksum)


def parse_frame(data: bytes) -> dict:
    """Strict parser: rejects truncation, bad magic/version/flags/checksum."""
    if len(data) != FRAME_SIZE:
        raise TouchError(f"frame must be {FRAME_SIZE} bytes, got {len(data)}")
    magic, ver, op, finger, flags, x, y, checksum = HEADER.unpack(data)
    if magic != MAGIC or ver != VERSION or flags != 0:
        raise TouchError("bad magic/version/flags")
    if op not in OP_NAMES or finger >= MAX_FINGERS:
        raise TouchError("bad opcode or finger")
    if x >= LOGICAL_W or y >= LOGICAL_H:
        raise TouchError("coordinates out of range")
    if (sum(data[:HEADER.size - 2]) & 0xFFFF) != checksum:
        raise TouchError("checksum mismatch")
    return {"op": op, "finger": finger, "x": x, "y": y}


class Transport:
    """Minimal write-only transport interface."""

    name = "base"

    def open(self) -> None:
        pass

    def send(self, frame: bytes) -> None:
        raise NotImplementedError

    def close(self) -> None:
        pass


class DryRunTransport(Transport):
    name = "dry-run"

    def __init__(self) -> None:
        self.frames: list[bytes] = []

    def send(self, frame: bytes) -> None:
        parsed = parse_frame(frame)
        self.frames.append(frame)
        print(f"[dry-run] {OP_NAMES[parsed['op']]} finger={parsed['finger']} "
              f"x={parsed['x']} y={parsed['y']} frame={frame.hex()}")


class MemoryTransport(Transport):
    """In-memory transport for tests and protocol demonstrations."""

    name = "memory"

    def __init__(self, fail_on_send: bool = False) -> None:
        self.frames: list[bytes] = []
        self.fail_on_send = fail_on_send
        self.closed = False

    def send(self, frame: bytes) -> None:
        parse_frame(frame)  # never emit a malformed frame
        if self.fail_on_send:
            raise OSError("transport disconnected")
        self.frames.append(frame)

    def close(self) -> None:
        self.closed = True


class SerialTransport(Transport):
    """Optional UART transport; requires pyserial and a real device node."""

    name = "serial"

    def __init__(self, device: str, baud: int = 115200) -> None:
        self.device = device
        self.baud = baud
        self._port = None

    def open(self) -> None:
        try:
            import serial  # type: ignore
        except ImportError as exc:
            raise TouchError("pyserial not installed; serial transport unavailable") from exc
        self._port = serial.Serial(self.device, self.baud, timeout=1)

    def send(self, frame: bytes) -> None:
        if self._port is None:
            raise TouchError("serial transport not open")
        self._port.write(frame)

    def close(self) -> None:
        if self._port is not None:
            self._port.close()
            self._port = None


class USBTransport(Transport):
    """Proposed vendor-control transport; NOT verified on v68."""

    name = "usb"

    VENDOR_REQUEST = 0x42

    def __init__(self, vid: int, pid: int) -> None:
        self.vid = vid
        self.pid = pid
        self._handle = None

    def open(self) -> None:
        try:
            import usb.core  # type: ignore
        except ImportError as exc:
            raise TouchError("libusb1 not installed; usb transport unavailable") from exc
        self._handle = usb.core.find(idVendor=self.vid, idProduct=self.pid)
        if self._handle is None:
            raise TouchError(f"USB device {self.vid:04x}:{self.pid:04x} not found")

    def send(self, frame: bytes) -> None:
        if self._handle is None:
            raise TouchError("usb transport not open")
        self._handle.ctrl_transfer(0x40, self.VENDOR_REQUEST, 0, 0, frame)

    def close(self) -> None:
        self._handle = None


class SocketTransport(Transport):
    """Unix/TCP transport for lab setups and tests."""

    name = "socket"

    def __init__(self, target: str) -> None:
        self.target = target
        self._sock = None

    def open(self) -> None:
        import socket
        if self.target.startswith("unix:"):
            self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._sock.connect(self.target[5:])
        else:
            host, port = self.target.rsplit(":", 1)
            self._sock = socket.create_connection((host, int(port)), timeout=2)

    def send(self, frame: bytes) -> None:
        if self._sock is None:
            raise TouchError("socket transport not open")
        self._sock.sendall(frame)

    def close(self) -> None:
        if self._sock is not None:
            self._sock.close()
            self._sock = None


@dataclass
class Injector:
    transport: Transport
    finger: int = 0
    active: set[int] = field(default_factory=set)

    def down(self, x: int, y: int) -> None:
        self.transport.send(make_frame(OP_DOWN, self.finger, x, y))
        self.active.add(self.finger)

    def move(self, x: int, y: int) -> None:
        # The kernel's SweetHID state persists across host invocations, so a
        # separate `m30touch move` may legitimately follow a `m30touch down`.
        self.transport.send(make_frame(OP_MOVE, self.finger, x, y))
        self.active.add(self.finger)

    def up(self) -> None:
        self.transport.send(make_frame(OP_UP, self.finger))
        self.active.discard(self.finger)

    def release(self) -> None:
        self.transport.send(make_frame(OP_RELEASE_ALL, self.finger))
        self.active.clear()

    def release_all_best_effort(self) -> None:
        """Interrupt/disconnect path: never leave a synthetic finger stuck down."""
        for finger in sorted(self.active):
            try:
                self.transport.send(make_frame(OP_UP, finger))
            except BaseException:
                pass
        self.active.clear()


def _steps(start: int, end: int, count: int) -> Iterable[int]:
    """Integer interpolation including the endpoint (at least two samples)."""
    count = max(2, count)
    for i in range(1, count + 1):
        yield start + (end - start) * i // count


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="m30touch",
        description="v68 synthetic touch injection (debug-only; dry-run by default)",
    )
    p.add_argument("--finger", type=int, default=0,
                   help=f"finger id 0..{MAX_FINGERS - 1} (default: 0)")
    p.add_argument("--transport", default="dry-run",
                   choices=("dry-run", "memory", "serial", "usb", "socket"))
    p.add_argument("--device", default="", help="serial node, VID:PID, or socket target")
    p.add_argument("--steps", type=int, default=10, help="swipe interpolation steps")
    p.add_argument("--delay-ms", type=int, default=16, help="delay between swipe moves")
    p.add_argument("--debug-enable", action="store_true",
                   help="required to attempt real I/O; default is validation-only")
    sub = p.add_subparsers(dest="command", required=True)

    for name in ("tap", "down", "move"):
        sp = sub.add_parser(name)
        sp.add_argument("x", type=int)
        sp.add_argument("y", type=int)
    sub.add_parser("up")
    sub.add_parser("release")
    swipe = sub.add_parser("swipe")
    swipe.add_argument("x1", type=int)
    swipe.add_argument("y1", type=int)
    swipe.add_argument("x2", type=int)
    swipe.add_argument("y2", type=int)
    return p


def make_transport(args: argparse.Namespace) -> Transport:
    if args.transport == "dry-run":
        return DryRunTransport()
    if args.transport == "memory":
        return MemoryTransport()
    if args.transport == "serial":
        if not args.device:
            raise TouchError("serial transport requires --device")
        return SerialTransport(args.device)
    if args.transport == "usb":
        try:
            vid_s, pid_s = args.device.split(":")
            vid, pid = int(vid_s, 16), int(pid_s, 16)
        except (ValueError, AttributeError) as exc:
            raise TouchError("usb transport requires --device VID:PID") from exc
        return USBTransport(vid, pid)
    if not args.device:
        raise TouchError("socket transport requires --device")
    return SocketTransport(args.device)


def run(args: argparse.Namespace, transport: Transport | None = None) -> int:
    """Execute one command. Returns 0 on success, 1 on injection failure."""
    if args.finger < 0 or args.finger >= MAX_FINGERS:
        raise TouchError(f"finger must be 0..{MAX_FINGERS - 1}")
    if os.environ.get(DEBUG_ENV) == "1":
        args.debug_enable = True
    if args.transport != "dry-run" and not args.debug_enable:
        raise TouchError(
            "real transport requires --debug-enable; dry-run validates without I/O"
        )

    own_transport = transport is None
    tx = transport if transport is not None else make_transport(args)
    inj = Injector(tx, finger=args.finger)
    released = False
    try:
        if own_transport:
            tx.open()
        cmd = args.command
        if cmd == "tap":
            inj.down(args.x, args.y)
            inj.up()
        elif cmd == "down":
            inj.down(args.x, args.y)
        elif cmd == "move":
            inj.move(args.x, args.y)
        elif cmd == "up":
            inj.up()
        elif cmd == "release":
            inj.release()
        elif cmd == "swipe":
            inj.down(args.x1, args.y1)
            xs = list(_steps(args.x1, args.x2, args.steps))
            ys = list(_steps(args.y1, args.y2, args.steps))
            for x, y in zip(xs, ys):
                inj.move(x, y)
                if args.delay_ms:
                    time.sleep(args.delay_ms / 1000.0)
            inj.up()
        else:
            raise TouchError(f"unknown command {cmd}")
        return 0
    except KeyboardInterrupt:
        inj.release_all_best_effort()
        released = True
        raise
    except (OSError, TouchError):
        # Best effort only: a disconnect may prevent any release from arriving.
        inj.release_all_best_effort()
        released = True
        raise
    finally:
        if own_transport:
            tx.close()
        if released and inj.active:
            inj.active.clear()


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return run(args)
    except KeyboardInterrupt:
        print("m30touch: interrupted; best-effort release sent", file=sys.stderr)
        return 130
    except TouchError as exc:
        print(f"m30touch: {exc}", file=sys.stderr)
        return 2
    except (OSError, ImportError) as exc:
        print(f"m30touch: transport failure: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
