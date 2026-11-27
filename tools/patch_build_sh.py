#!/usr/bin/env python3
"""Patch the darwin-xnu-build build.sh for M30LTE, with strict patch policy.

Changes made to the upstream build script
-----------------------------------------
1. ARM64 / Cortex-A53 flags for the M30LTE board config.
2. ``SKIP_PATCHES`` escape hatch (kept, but it now produces an explicit,
   auditable marker instead of silently returning).
3. **Strict patch loop.** The upstream loop applies a patch if it can and
   otherwise prints ``warning "Skipping patch ..."`` and continues.  That makes
   a build's real patch set unknowable from its log, and it is the defect that
   produced the v70 composition mismatch.  The replacement loop:
     - records name, SHA-256, status and apply order for every patch;
     - fails the build on any patch that does not apply, unless the patch is
       named in ``$M30_PATCH_ALLOW_SKIP`` (which must be justified in
       ``xnu/patches-minimal/SKIP-ALLOWLIST.txt``);
     - fails on duplicate patch names;
     - writes the manifest to ``$PATCH_MANIFEST`` for CI to verify.

The manifest is TSV: ``order<TAB>name<TAB>sha256<TAB>status``.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

APPLY_STATUS = "applied"
SKIP_STATUS = "allowed-skip"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def strict_loop() -> str:
    """Return the bash replacement for the upstream patch loop.

    Two safety properties that matter:

    * ``exit 1`` runs inside the ``( cd ... )`` subshell, which only fails the
      build if ``set -e`` propagates.  We therefore ALSO append a ``FAILED``
      sentinel line to the manifest, so CI can fail the build even when shell
      semantics would swallow it.  The manifest is the authoritative record.
    * Every branch writes exactly one manifest line, so a count mismatch is
      detectable after the fact.
    """
    manifest = '${PATCH_MANIFEST:-/tmp/m30-patch-manifest.tsv}'
    return f"""        MF="{manifest}"
                : > "$MF"
                M30_PATCH_ORDER=0
                M30_PATCH_APPLIED=0
                M30_PATCH_SKIPPED=0
                M30_PATCH_SEEN=""
                for PATCH in "${{PATCH_DIR}}"/*.patch; do
                    [ -e "$PATCH" ] || continue
                    PATCH_NAME="$(basename "$PATCH")"
                    M30_PATCH_ORDER=$((M30_PATCH_ORDER + 1))
                    PATCH_SHA="$(shasum -a 256 "$PATCH" | cut -d' ' -f1)"
                    case " $M30_PATCH_SEEN " in
                    *" $PATCH_NAME "*)
                        echo "ERROR: duplicate patch name: $PATCH_NAME" >&2
                        printf '%s\t%s\t%s\t%s\n' "$M30_PATCH_ORDER" "$PATCH_NAME" "$PATCH_SHA" "FAILED" >> "$MF"
                        exit 1
                        ;;
                    esac
                    M30_PATCH_SEEN="$M30_PATCH_SEEN $PATCH_NAME"
                    if APPLY_CHECK=$(git apply --check "$PATCH" 2>&1); then
                        running "Applying patch: ${{PATCH}}"
                        if git apply "$PATCH"; then
                            M30_PATCH_APPLIED=$((M30_PATCH_APPLIED + 1))
                            printf '%s\t%s\t%s\t%s\n' "$M30_PATCH_ORDER" "$PATCH_NAME" "$PATCH_SHA" "applied" >> "$MF"
                        else
                            echo "ERROR: patch passed --check but failed to apply: $PATCH_NAME" >&2
                            printf '%s\t%s\t%s\t%s\n' "$M30_PATCH_ORDER" "$PATCH_NAME" "$PATCH_SHA" "FAILED" >> "$MF"
                            exit 1
                        fi
                    else
                        ALLOWED=0
                        for ALLOWED_NAME in ${{M30_PATCH_ALLOW_SKIP:-}}; do
                            if [ "$ALLOWED_NAME" = "$PATCH_NAME" ]; then ALLOWED=1; fi
                        done
                        if [ "$ALLOWED" = "1" ]; then
                            warning "Allowed skip of $PATCH_NAME (see SKIP-ALLOWLIST.txt)"
                            M30_PATCH_SKIPPED=$((M30_PATCH_SKIPPED + 1))
                            printf '%s\t%s\t%s\t%s\n' "$M30_PATCH_ORDER" "$PATCH_NAME" "$PATCH_SHA" "allowed-skip" >> "$MF"
                        else
                            echo "ERROR: patch failed to apply and is not allow-listed: $PATCH_NAME" >&2
                            echo "$APPLY_CHECK" >&2
                            printf '%s\t%s\t%s\t%s\n' "$M30_PATCH_ORDER" "$PATCH_NAME" "$PATCH_SHA" "FAILED" >> "$MF"
                            exit 1
                        fi
                    fi
                done
                running "Patch manifest: $M30_PATCH_APPLIED applied, $M30_PATCH_SKIPPED allowed-skip"
        """


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(f"usage: {argv[0]} <build.sh> <machine_config>", file=sys.stderr)
        return 2
    path = Path(argv[1])
    config = argv[2]

    old = 'ARCHS="x86_64 arm64e" VALID_ARCHS="x86_64 arm64e"'
    if config in ("A5XELTE", "HEROLTE", "M20LTE", "M30LTE"):
        new = ('ARCHS="arm64" VALID_ARCHS="arm64" OTHER_CFLAGS="-mkernel -nostdinc '
               '-Wno-packed -mcpu=cortex-a53 -march=armv8-a+crypto"')
    else:
        new = 'ARCHS="x86_64 arm64e arm64" VALID_ARCHS="x86_64 arm64e arm64"'

    text = path.read_text()
    if text.count(old) != 1:
        print("ERROR: darwin-xnu-build firehose line changed", file=sys.stderr)
        return 1
    text = text.replace(old, new)

    old_patches = 'patches() {\n    running "PATCHING xnu files"\n'
    if text.count(old_patches) != 1:
        print("ERROR: patches() entry point changed", file=sys.stderr)
        return 1
    new_patches = (
        'patches() {\n'
        '    if [ -n "${SKIP_PATCHES:-}" ]; then\n'
        '        running "Skipping ALL patches (SKIP_PATCHES=1) - manifest will be empty"\n'
        '        : > "${PATCH_MANIFEST:-/tmp/m30-patch-manifest.tsv}"\n'
        '        return 0\n'
        '    fi\n'
        '    running "PATCHING xnu files"\n'
    )
    text = text.replace(old_patches, new_patches)

    old_loop = (
        '        for PATCH in "${PATCH_DIR}"/*.patch; do\n'
        '            if APPLY_CHECK=$(git apply --check "$PATCH" 2>&1); then\n'
        '                running "Applying patch: ${PATCH}"\n'
        '                git apply "$PATCH"\n'
        '            else\n'
        '                warning "Skipping patch ${PATCH} (already upstream, previously applied, or malformed): ${APPLY_CHECK}"\n'
        '            fi\n'
        '        done\n'
    )
    if text.count(old_loop) != 1:
        print("ERROR: darwin-xnu-build patch loop changed", file=sys.stderr)
        return 1
    text = text.replace(old_loop, strict_loop())

    path.write_text(text)
    print("firehose:", new)
    print("patch policy: strict (fail-closed, manifest at $PATCH_MANIFEST)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
