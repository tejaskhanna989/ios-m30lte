# Deeper SpringBoard backtrace symbolication

All extraction was read-only on the physical M30 in TWRP. Identity verified
before the read: `SM-M305F`, `m30lte`, serial `320081735bb166a3`, bootloader
`M305FDDU8CVK1`, `ro.twrp.boot=1`. No USERDATA write.

Source: the genuine iOS 16.7.16 (20H392) dyld local-symbol table via
`tools/m30_hfsx_read.py symbols`. Raw result: `deep-symbols.json`.

## v62 `SMP SpringBoard t0` backtrace

Slide `0x3f420000`. Nearest preceding local symbols (code section 1 unless
noted):

| Address | Nearest symbol | Offset |
|---|---|---|
| `0x1c2622b18` (LR) | `_do_compat` / `fprintf_stderr` | `+0x18c` / `+0x2e8` |
| `0x1c2622db8` | `_do_compat` (same libsystem stderr region) | `+0x42c` |
| `0x1c2611524` | `_mach_msg_destroy_port` | `+0x1b8` |
| `0x1cd0e7ad4` | `___51-[VUIPlaybackManager _registerStateMachineHandlers]_block_invoke_5.682` | `+0x60` |
| `0x1cd0ea590` | `-[VUIPlaybackManager activePlayer]` | `+0x8` |
| `0x1cd0eb374` | `-[VUIMediaLibraryApplicationController shouldWarnAboutPlaybackQualityForRentalMediaItem:]` | `+0x20` |
| `0x1cd119040` | `___59-[VUIMediaInfoFetchController loadImageAtIndex:completion:]_block_invoke` | `+0xac` |
| `0x1cd11837c` | `-[VUIMediaInfoFetchController _prewarmIndices]` | `+0xc0` |
| `0x1ccfb8780` | `+[NSObject(SafeInitializer) ik_invocationforSelectorString:argumentsPointerValue:].cold.1` | `+0x24` |
| `0x1ccf5964c` | `-[IKDOMDocument createComment:]` | `+0x48` |

Frames `0x1e1a97a4c`, `0x1e1a97db8`, `0x1e1a97d8c` resolve only to
`__swift_FORCE_LOAD_$...$_NotesSupport` pointer symbols (section 16, `n_type=30`)
and `0x1e1abc190` to a PaperKit ivar symbol (section 31). Those are data/stub
symbols, not code, so their nearest-symbol attribution is not reliable.

## Interpretation

The code frames are overwhelmingly **media playback UI** (`VUIPlaybackManager`,
`VUIMediaLibraryApplicationController`, `VUIMediaInfoFetchController`) and
**IKit/PaperKit/NotesSupport** app frameworks — not SpringBoard's lock-screen
or CoverSheet code. Either the sampled stack is stale/misattributed, or
SpringBoard is inside a media/Now Playing UI path. Neither case supports the
earlier "serial console blocks stderr" hypothesis, which v63 already rejected.

Conclusion: symbolication alone cannot identify the message being written to
fd 2. The next candidate therefore adds a bounded, read-only diagnostic that
captures the actual stderr bytes from SpringBoard/backboardd into the same
`XNU:` pstore ring (`xnu/patches-minimal/0441-m30-stderr-capture.patch`), while
keeping the v62 kernel, `serial=3`, and all security state unchanged.
