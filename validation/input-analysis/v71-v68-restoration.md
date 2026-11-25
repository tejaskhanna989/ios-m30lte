# v71 — exact v68 source baseline restoration (facts only)

## Reference

Known-good display baseline: commit `64831cab` (`v68: capture and decode pstore after lock-screen observation`).
The v68 candidate was built from GREEN CI `45529035057` and physically displayed a
persistent iOS lock screen (wallpaper, clock, date, unlock controls).

All work remains on `main`. No branch was created or switched. The v69/v70
commits and their physical evidence remain in shared history; nothing was reset
or rewritten.

## Changes after v68 that affected source/build behavior

`git diff --name-status 64831cab..HEAD -- .github tools xnu` identified exactly:

- `.github/workflows/xnu.yml` — modified for the v69/v70 diagnostic patch chain
  and hashes.
- `tools/verify_m30_buildtree.py` — modified for overlay-aware patch provenance.
- `tools/verify_m30_kernel.py` — modified for register-agnostic GPIO offset
  verification.
- `tools/test_v69_input_diagnostics.py` — added v69 diagnostic regression test.
- `tools/test_v70_lock_screen_restore.py` — added v70 restore regression test.
- `xnu/patches-minimal/0446-m30-framebuffer-status-quiet.patch` — added.
- `xnu/patches-minimal/0447-m30-key-input-diag.patch` — added.
- `xnu/patches-minimal/0448-m30-hid-event-diag.patch` — added.
- `xnu/patches-minimal/0449-m30-revert-key-input-diag.patch` — added.
- `xnu/patches-minimal/0450-m30-revert-hid-event-diag.patch` — added.

## Restoration performed

The working tree was restored from `64831cab` for:

- `.github/workflows/xnu.yml`
- `tools/`
- `xnu/patches-minimal/`

This restores the workflow, verifiers, tests and patch set to the exact v68
state. Files added after v68 in those paths were removed from the working tree;
they remain recoverable in Git history.

Verification:

- `git diff --stat 64831cab -- .github tools xnu` is empty after restoration.
- `.github/workflows/xnu.yml` parses as valid YAML.
- Focused v68 test sweep: 24 PASS / 1 known unrelated FAIL
  (`tools/test_m30_16k_pages.py` expects absent `0417-m30-16k-pages.patch`).
- Framebuffer, SpringBoard visibility, stderr capture, AMFI, code-signing,
  CS_VALID and full-page validation tests remain present and PASS.

No runtime touchscreen change has been made in this restoration commit.
