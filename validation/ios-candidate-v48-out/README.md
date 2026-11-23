# iOS candidate v48 — patch the already-resident target page

Baseline: v18 exclusively. 4K config preserved (no 0417). MAIN only @ `9cad56bb`.

## Why this candidate exists

v47 physically proved that the authoritative dyld4 subcache list works:

```text
M30 IRT final: state=2 off=0xa432d84 err=0 sym=0x1e1d3ad84 comp=0 ls=0x4000 nlist_cnt=8705811 nlist_range=146 hits=1 tries=29 sc=42 si=26 fb=0x0 hb=67
```

The main cache header exposed 42 subcache entries (`sc=42`), entry 26 supplied
the real cache file, and `hits=1` resolved `_internal_release_type` to file
offset `0xa432d84`. But the state stayed `HAVE_OFF` (`state=2`) and no
`M30 IRT: patched` marker appeared: the in-memory write never fired.

The most likely reason is that the target page had already been faulted before
the deferred symbol scan learned its file offset, so no later `vm_fault()` ever
visited that vnode. v48 therefore keeps every v47 lookup and adds two narrow
corrections:

1. After the file offset is known, patch the already-resident page directly.
   Resolve the target vnode's VM object with `ubc_getobject()`, look up the page
   with `vm_page_lookup()`, require `VMP_CS_VALIDATED()`, wire the page, write
   `3` through `phystokv()` of its physical page, then unwire it. This is the
   same in-memory-only write as the fault path, after code signing validated
   the page. The backing file is never written.
2. If the pager hands back a different vnode instance for the same file, accept
   it only when both the mount and the vnode id match the target. The fault path
   remains as a fallback.

Status and heartbeat lines now carry `fo=<HAVE_OFF faults>`,
`vh=<target vnode matches>`, `oh=<offset matches>`, and
`pr=<resident-patch result>`. One-shot diagnostics report a missing VM object,
a missing resident page, or an unvalidated page.

All file reads remain `UIO_READ`; the only writes remain in-memory after
`cs_validate_page()` on the target file. No signature, hash, AMFI,
trust-cache, or page-validation check is weakened.

## Hashes

| File | SHA256 |
|---|---|
| kernel | `4022004eb8387a42873698db9bfe4de7df9efb43b84553c126cfd688d0c94200` |
| payload | `18365562c7d8f2354d1476b1f8872ad20f0014c5abfef71084780ff7d50ecaaa` |
| shim-boot.img | `4b56a629e7c1359d98008208bec4e865152e5aff995e896e50dc36c93c07579c` |

Kernel entry remains `0xfffffff007410488`. Shim Image/ELF and the shim region
inside `shim-boot.img` remain byte-identical to the v31 reference.

## Validation

CI `45145845104` GREEN. Buildtree PASS, kernel PASS, platform 9/9, CPU 17/17,
ADT 22/22, packaging PASS, handoff 18/18, all applicable focused tests PASS
(`test_m30_16k_pages.py` intentionally inapplicable). Standalone syntax check
and patch dry-runs against pristine and the v47 buildtree PASS.

## Next physical step

BOOT-only flash; capture pstore. Read the updated heartbeat for either
`M30 IRT: patched ...` / `M30 IRT: patched resident page ...`, or
`M30 IRT final ... pr=...` if it still fails, then inspect the next boot stage.
Do not equate a loaded SpringBoard process with a visible UI.

No UI success claimed; BOOT readback skipped; USERDATA/SYSTEM/RECOVERY untouched.
