#!/usr/bin/env python3
"""Focused tests for the m30touch host utility and M30TOUCH v1 protocol."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import m30touch as mt  # noqa: E402


class InterruptTransport(mt.MemoryTransport):
    def __init__(self, interrupt_after: int):
        super().__init__()
        self.interrupt_after = interrupt_after
        self.interrupted = False

    def send(self, frame: bytes) -> None:
        if not self.interrupted and len(self.frames) >= self.interrupt_after:
            self.interrupted = True
            raise KeyboardInterrupt("simulated interruption")
        super().send(frame)


class M30TouchTests(unittest.TestCase):
    def args(self, *argv):
        return mt.build_parser().parse_args(list(argv))

    def test_tap_and_parsed_frames(self):
        tx = mt.MemoryTransport()
        self.assertEqual(mt.run(self.args("tap", "540", "960"), tx), 0)
        parsed = [mt.parse_frame(f) for f in tx.frames]
        self.assertEqual([p["op"] for p in parsed], [mt.OP_DOWN, mt.OP_UP])
        self.assertEqual((parsed[0]["x"], parsed[0]["y"]), (540, 960))
        self.assertEqual(parsed[1]["finger"], 0)

    def test_down_move_up_across_invocations(self):
        tx = mt.MemoryTransport()
        for argv in (("--finger", "2", "down", "10", "20"),
                     ("--finger", "2", "move", "100", "200"),
                     ("--finger", "2", "up")):
            self.assertEqual(mt.run(self.args(*argv), tx), 0)
        ops = [mt.parse_frame(f)["op"] for f in tx.frames]
        self.assertEqual(ops, [mt.OP_DOWN, mt.OP_MOVE, mt.OP_UP])

    def test_swipe_sequence(self):
        tx = mt.MemoryTransport()
        argv = ("--steps", "3", "--delay-ms", "0",
                "swipe", "540", "1500", "540", "500")
        self.assertEqual(mt.run(self.args(*argv), tx), 0)
        ops = [mt.parse_frame(f)["op"] for f in tx.frames]
        self.assertEqual(ops[0], mt.OP_DOWN)
        self.assertEqual(ops[-1], mt.OP_UP)
        self.assertEqual(ops[1:-1], [mt.OP_MOVE] * 3)
        ys = [mt.parse_frame(f)["y"] for f in tx.frames[1:-1]]
        self.assertEqual(ys, [1166, 833, 500])

    def test_coordinate_boundaries_and_rejection(self):
        for x, y in ((0, 0), (1079, 1919)):
            tx = mt.MemoryTransport()
            self.assertEqual(mt.run(self.args("tap", str(x), str(y)), tx), 0)
        for x, y in ((1080, 0), (0, 1920), (-1, 0), (0, -1)):
            with self.assertRaises(mt.TouchError):
                mt.run(self.args("tap", str(x), str(y)), mt.MemoryTransport())

    def test_invalid_finger_ids(self):
        for finger in (-1, 10, 99):
            with self.assertRaises(mt.TouchError):
                mt.run(self.args("--finger", str(finger), "tap", "1", "1"),
                       mt.MemoryTransport())

    def test_malformed_and_incomplete_commands(self):
        for argv in (("tap", "x", "1"), ("tap", "1"), ("swipe", "1", "2", "3"),
                     ("bogus",)):
            with self.assertRaises(SystemExit):
                self.args(*argv)

    def test_interrupted_sequence_releases(self):
        tx = InterruptTransport(interrupt_after=2)
        with self.assertRaises(KeyboardInterrupt):
            mt.run(self.args("--steps", "5", "--delay-ms", "0",
                             "swipe", "100", "100", "900", "900"), tx)
        ops = [mt.parse_frame(f)["op"] for f in tx.frames]
        self.assertEqual(ops[-1], mt.OP_UP)
        self.assertNotIn(mt.OP_RELEASE_ALL, ops)

    def test_transport_disconnect(self):
        tx = mt.MemoryTransport(fail_on_send=True)
        with self.assertRaises(OSError):
            mt.run(self.args("tap", "540", "960"), tx)
        self.assertEqual(tx.frames, [])

    def test_debug_disabled_production_configuration(self):
        args = self.args("--transport", "memory", "tap", "540", "960")
        with self.assertRaises(mt.TouchError):
            mt.run(args)
        # With --debug-enable, the same transport is usable.
        tx = mt.MemoryTransport()
        args = self.args("--transport", "memory", "--debug-enable",
                         "tap", "540", "960")
        self.assertEqual(mt.run(args, tx), 0)

    def test_protocol_parser_rejects_malformed_frames(self):
        frame = mt.make_frame(mt.OP_DOWN, 0, 540, 960)
        self.assertEqual(len(frame), mt.FRAME_SIZE)
        self.assertEqual(mt.parse_frame(frame)["op"], mt.OP_DOWN)
        for bad in (frame[:-1], frame + b"\x00",
                    frame[:len(frame) - 1] + bytes([frame[-1] ^ 1]),
                    b"XXXX" + frame[4:]):
            with self.assertRaises(mt.TouchError):
                mt.parse_frame(bad)

    def test_multi_finger(self):
        tx = mt.MemoryTransport()
        for op, finger, x, y in ((mt.OP_DOWN, 0, 10, 10),
                                 (mt.OP_DOWN, 1, 20, 20),
                                 (mt.OP_MOVE, 1, 30, 30),
                                 (mt.OP_UP, 0, 0, 0),
                                 (mt.OP_UP, 1, 0, 0)):
            tx.send(mt.make_frame(op, finger, x, y))
        parsed = [mt.parse_frame(f) for f in tx.frames]
        self.assertEqual([p["finger"] for p in parsed], [0, 1, 1, 0, 1])
        self.assertEqual(len({p["finger"] for p in parsed}), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
