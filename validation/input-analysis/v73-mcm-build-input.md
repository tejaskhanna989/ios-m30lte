# v73 — explicit device-derived MCM build input (host-only, no device access)

## Why this exists

CI rootfs `45812788743` proved the IPSW-derived OS volume contains **zero**
`.com.apple.mobile_container_manager.metadata.plist` files. The 595 plists in
`v68-container-metadata-finding.md` were read from device USERDATA *before* the
2026-11-25 write. Consequently the generic helpers in
`tools/m30lte-root-tweaks.py` were no-ops and no earlier artifact carries the
lsd fix. This change supplies the real metadata as an explicit, allow-listed
build input and reconciles it against the staged rootfs.

## Scope — NOT all 595 containers

Only five records with direct evidence in the lsd SIGABRT loop and recovered
`.ips` reports are allow-listed (`tools/mcm_reconcile.py::ALLOWED`):

| Identifier | UUID | Container |
|---|---|---|
| com.apple.lsd | `AAD4FDC5-016A-4A46-8DCD-0C7E85EB53E2` | `private/var/containers/Data/System/6561B268-…` |
| com.apple.lsd | `58B7EA8C-8845-480F-8612-750117473D24` | `private/var/mobile/Containers/Data/InternalDaemon/3EA10E23-…` |
| systemgroup.com.apple.lsd | `DBD5D5E0-E129-471E-A351-0DB73584D03F` | `private/var/containers/Shared/SystemGroup/FDC8A26C-…` |
| systemgroup.com.apple.lsd.iconscache | `4A495630-106A-431F-90E4-393D845BC448` | `private/var/containers/Shared/SystemGroup/systemgroup.com.apple.lsd.iconscache` |
| com.apple.backboardd | `44D68AC1-157C-4411-8726-54E6CD9B4A83` | `private/var/containers/Data/System/F5099506-…` |

The user-container `58B7EA8C-…` is the one used by `-[_LSDefaults userContainerURL]`
in the crash report (process ran as mobile, uid 501). No other container is
copied.

## Provenance and secrecy

- Source: read-only HFS+ catalog + cached metadata plists from the 2026-11-24
  USERDATA inspection, joined by parent file ID in
  `tools/make_mcm_build_input.py`.
- The generated bundle is 4,614 bytes, SHA256
  `84df4250f448aee6ddbd626cfaeba84649ad6bd0181a9099a2fec9e68843ec31`, stored
  at `/home/tejas/opencode-work/mcm-input/lsd-chain.json` with mode 0600 —
  **outside the git worktree**. No device dump is committed.
- CI receives it through the repository secret `MCM_METADATA_B64` (base64 of the
  bundle). GitHub masks secret values in logs. The workflow decodes it only to
  `$RUNNER_TEMP/mcm-input.json`, which is outside `$WORK` and therefore cannot
  become a release asset. No tool prints raw metadata bytes — only identifiers,
  UUIDs, hashes and status.

## Fail-closed behaviour

`tools/mcm_reconcile.py` rejects: unknown UUIDs, identifier/path mismatch, path
traversal, malformed base64/plists, payload hash mismatch, duplicate UUIDs,
conflicting or malformed metadata already in the image, and a UUID path that is
not a directory. Missing container dirs are created with the correct owner
(root for system/shared, 501 for mobile) and 0755; a missing UUID dir is copied
from the container contents with ownership/mode/symlinks preserved. Nothing is
invented: the only UUID→directory mappings permitted are the five above.

With no `MCM_BUILD_INPUT`, the staging tool prints
`MCM_BUILD_INPUT: absent; no MCM reconciliation performed` and the generic
no-op helpers are skipped. The CI gate prints
`NO RECONCILIATION OCCURRED`; `require_mcm_input=true` makes that a hard fail.

## Verification evidence required

1. Build log must contain `MCM_BUILD_INPUT: applied 5 container(s) …` — proves
   the secret was consumed.
2. `tools/verify_mcm_reconciliation.py` must report 5/5 PASS (metadata bytes,
   values, UUID dir, ownership).
3. Image manifest must show a new SHA256 and the same HFSX signature/size.

## Limitations

This is a **build-time** correction only. No physical test has been performed.
Do not claim the lsd loop is fixed until a separately authorized boot shows
`lsd` stable with zero `CRASH lsd` records. Lock-screen and touch remain
unproven and are tracked separately.
