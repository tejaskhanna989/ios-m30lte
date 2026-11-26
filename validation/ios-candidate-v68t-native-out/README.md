# Native lock-screen candidate — restore exact v68 runtime configuration

Intervention: keep all source patches (0451 Melfas, 0453/0454 diagnostics) but
boot with the **exact v68 cmdline**, so the Melfas driver and heartbeat remain
compiled-but-dormant. This isolates whether the added runtime boot args/early
hardware probe are what prevents SpringBoard's native lock-screen transition.

- Kernel SHA256: 464b410cf4e6a942a3588d79e06e8a0c3f0e34ef5d211a1ffa2f51f0e2731221
- Payload SHA256: 292800c81ccae7ffeb8a709ab7f4ea66e353e243ddadbd034784e25481bf676a
- BOOT image SHA256: 9c022561c09b53de1ab613b4ca37fb42acd4aaa7899302138c35bdd8298cbe26
- Cmdline: exact v68 (no m30touch / m30touchhid / m30uihb).
- CI kernel: 45758653440 GREEN; structural PASS.
- No physical flash/reboot performed. USERDATA unchanged.
