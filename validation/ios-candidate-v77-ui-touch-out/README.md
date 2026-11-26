# v77 UI+touch BOOT candidate (BOOT-only; no USERDATA change)

Fixes the console-overlay defect introduced in the v76 attempt: the XNU console
is muted at GUI handoff (`a5fb_noconsole=1`) so SpringBoard/BackBoard can take
the screen, while `a5fb_keep_on=1` is preserved from the accepted v68 baseline.
Touch stays enabled via `m30touch=1 m30touchhid=1` and is unchanged otherwise.

Kernel: 5e898ee0ec7bffee85c5b49cfcda82ff5d0624762233b438a778f26861f83758
(CI 45663503730, v68 XNU + Melfas 0451; no sampler, no UI heartbeat in cmdline).
Cmdline invariants are enforced by tools/test_boot_ui_cmdline.py.

USERDATA is NOT changed: keep the v75 image already written, which carries the
v73 lsd/MCM correction and the SpringBoard container registration.
