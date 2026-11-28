# Recovered historical patches 0446-0450

These five patches were referenced by the v69 and v70 boot records but were
absent from this tree. They were recovered verbatim on 2026-11-27 from commit
`528bb2760e` ("v70: revert v69 input diagnostics to restore v68 lock screen"),
which GitHub still resolves. Cited commit: `f34c48a870` ("v69: certify
logging-only input diagnostic candidate").

Verify: `sha256sum -c RECOVERED-0446-0450.sha256`

## Why they matter

0446's body (read in full before recovery) only advances a counter and adds a
`<= 4800` guard to the status print:

    ++fb->fDiagTick;
    if ((fb->fDiagTick % 600) == 0 && fb->fDiagTick <= 4800) {

It changes no display counter, staging, notification or power behaviour, which
is what the patch's own comment claims. The v68 -> v70 "logging cap alone caused
a fatal NSException" observation therefore stands as **unexplained**, not as a
mechanism: a print guard cannot raise an Objective-C exception.

0447/0448 add bounded pstore lines on the key and HID paths; 0449/0450 revert
them. None adds a lock, wait, or return-value change.
