# v85 — Strict patch provenance (priority 1)

Status: implemented, tested locally, CI pending. Read-only w.r.t. device and
w.r.t. the accepted v68 baseline.

## The defect (confirmed)

`tools/patch_build_sh.py` rewrote darwin-xnu-build's patch loop to:

    if APPLY_CHECK=$(git apply --check "$PATCH" 2>&1); then
        running "Applying patch: ${PATCH}"
        git apply "$PATCH"
    else
        warning "Skipping patch ${PATCH} (already upstream, previously applied, or malformed)"
    fi

Three consequences, all now demonstrated:

1. A patch that does not apply is **silently skipped** and the build continues.
2. The build log then contains no record that the patch was ever expected, so
   **the applied patch set cannot be reconstructed from the artifacts**.
3. CI verified applied-ness for only `0442`–`0445`. Patches `0446`–`0455` were
   never checked at all.

This is the mechanism that allowed v70 to ship an eleven-patch build documented
as six (see `v84-joint-verdict.md`, section D2).

## What changed

**`tools/patch_build_sh.py`** — the tolerant loop is replaced with a strict one:

- every patch is recorded as `order / name / sha256 / status`;
- any patch that does not apply **fails the build** unless it is named in
  `M30_PATCH_ALLOW_SKIP`;
- duplicate patch names fail the build;
- a `FAILED` sentinel row is written to the manifest before exit, so CI catches
  the failure even if shell `set -e` semantics would swallow the subshell exit;
- `SKIP_PATCHES=1` still works but now writes an explicitly empty manifest
  rather than silently returning.

**`tools/verify_patch_provenance.py`** — CI gate comparing the manifest to
`xnu/patches-minimal/`. Fails on: missing/empty manifest, `FAILED` row,
undocumented patch, phantom patch, SHA-256 drift, duplicate, apply-order drift,
unjustified skip, and stale allow-list entry.

**`xnu/patches-minimal/SKIP-ALLOWLIST.txt`** — the only place a skip may be
justified. Currently empty: every patch is expected to apply.

**`.github/workflows/xnu.yml`** — the `0442`–`0445` grep loop is replaced by
(a) `verify_patch_provenance.py` with the kernel hash, and (b) an independent
assertion that the set of `Applying patch:` lines in `build.log` equals the set
of `*.patch` on disk. The manifest, its report and `build.log` now ship inside
the `xnu-kernel-*` artifact, so a kernel cannot be consumed without its
provenance.

**`.github/workflows/ios-root-tests.yml`** — runs `test_patch_provenance.py`
(26 tests).

## Test results

`tools/test_patch_provenance.py`: **26 tests, PASS.**

They exercise the *generated shell*, not a Python re-implementation: a scratch
git repo is patched with a good and a bad patch and the real loop is executed.
Verified behaviours: clean apply; unlisted failure aborts the build with a
`FAILED` manifest row; allow-listed skip passes and records `allowed-skip`;
order and SHA-256 are recorded correctly; duplicate names are rejected.
Plus all ten verifier failure classes and three real-tree consistency checks.

Pre-existing suite: 16 pass, 28 fail — all 28 from absent
`milestone_artifacts/ci_*` buildtrees. No new failures introduced.

## Honest limitations

- **Not yet validated against a real buildtree.** The archived
  `kb20278/xnu-buildtree/buildtree.tgz` is from an older generation
  (`SweetFramebuffer.cpp`, `sweet_sample.c`) than the current patch set
  (`M30Framebuffer.cpp`, `m30lte_touch.c`): 171 of 176 patches fail to peel
  against it. Local patch-application verification is therefore impossible, and
  the CI build is the first real test.
- The allow-list is empty, so if any patch legitimately does not apply to the
  current buildtree, the first CI run will fail loudly. **That is the intended
  behaviour** — it is the finding we currently lack.

## What remains unresolved

Whether every patch in the tree actually applies to the pinned
`darwin-xnu-build` revision. This change does not answer that; it makes the
answer impossible to miss.
