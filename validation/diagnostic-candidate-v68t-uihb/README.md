# Diagnostic-only candidate: v68t + UI heartbeat (0453)

This is a **source/build diagnostic candidate**, NOT a flashable image. No new
BOOT image was built or packaged; the existing v68t candidate hashes are
preserved unchanged.

- Base source: v68t (patch 0451 Melfas driver unchanged).
- New patch: `0453-m30-ui-heartbeat.patch` (diagnostic only, disabled by default).
- Enable with boot arg `m30uihb=1`; one bounded line per second for at most
  1800 samples (30 minutes).
- Format:
  `M30 UI HB: sb=<pid> bb=<pid> reason=<reason> irt=<state> hid=unknown scene=unknown surface=unknown`
- Measured: SpringBoard PID, backboardd PID, crash reason, IRT state.
- Unknown (no safe existing API): HID client count, lock-screen scene state,
  lock-screen surface identity.

## Preserved v68t candidate hashes (not replaced)
- BOOT: `a5c05b020fa81203ebca3eaecfe2234ab3babaf11d8d857b5739a91b6cbe52e4`
- Payload: `45aae173f85a19b965a00826af03a3176ce2fd525944137115879c74c10718e9`
- Kernel: `5e898ee0ec7bffee85c5b49cfcda82ff5d0624762233b438a778f26861f83758`

## Morning decision
If CI is green, the user may choose to build/package this diagnostic kernel or
keep the current v68t candidate. No physical flash or reboot is authorized here.
