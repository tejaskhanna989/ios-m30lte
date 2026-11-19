#!/usr/bin/env python3
"""
Patch darwin-xnu-build's build.sh for M30LTE:
- Set correct ARCHS/VALID_ARCHS/OTHER_CFLAGS for arm64 Cortex-A53
- Add SKIP_PATCHES support
- Enforce strict critical patch policy for M30LTE patches
"""
import sys
from pathlib import Path

path = Path(sys.argv[1])
config = sys.argv[2]

old = 'ARCHS="x86_64 arm64e" VALID_ARCHS="x86_64 arm64e"'
if config in ('A5XELTE', 'HEROLTE', 'M20LTE', 'M30LTE'):
    new = ('ARCHS="arm64" VALID_ARCHS="arm64" OTHER_CFLAGS="-mkernel -nostdinc '
           '-Wno-packed -mcpu=cortex-a53 -march=armv8-a+crypto"')
else:
    new = 'ARCHS="x86_64 arm64e arm64" VALID_ARCHS="x86_64 arm64e arm64"'

text = path.read_text()
assert text.count(old) == 1, 'darwin-xnu-build firehose line changed'
text = text.replace(old, new)

# Add SKIP_PATCHES support
old_patches = (
    'patches() {\n'
    '    running "PATCHING xnu files"\n'
)
new_patches = (
    'patches() {\n'
    '    if [ -n "${SKIP_PATCHES:-}" ]; then\n'
        '        running "Skipping patches (SKIP_PATCHES=1)"\n'
        '        return 0\n'
    '    fi\n'
    '    running "PATCHING xnu files"\n'
)
text = text.replace(old_patches, new_patches)

# Strict critical patch policy
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
new_loop = (
    '        for PATCH in "${PATCH_DIR}"/*.patch; do\n'
    '            PATCH_NAME="$(basename "$PATCH")"\n'
    '            case "$PATCH_NAME" in\n'
    '        0085-a5xelte-board-target.patch|0096-m30lte-a5xelte-h-overrides.patch|0400-m30lte-board-target.patch|0402-m30lte-board-config-header.patch|0403-m30lte-hardware-overrides.patch|9998b-m30-adt-restore.patch|9998c-m30-adt-restore-call.patch|9998d-m30-adt-restore-include.patch)\n'
    '            if ! APPLY_CHECK=$(git apply --check "$PATCH" 2>&1); then\n'
    '                echo "ERROR: critical M30LTE patch failed preflight: $PATCH_NAME" >&2\n'
    '                echo "$APPLY_CHECK" >&2\n'
    '                exit 1\n'
    '            fi\n'
    '            running "Applying critical M30LTE patch: ${PATCH}"\n'
    '            if ! git apply "$PATCH"; then\n'
    '                echo "ERROR: critical M30LTE patch failed to apply: $PATCH_NAME" >&2\n'
    '                exit 1\n'
    '            fi\n'
    '            ;;\n'
    '        *)\n'
    '            if APPLY_CHECK=$(git apply --check "$PATCH" 2>&1); then\n'
    '                running "Applying patch: ${PATCH}"\n'
    '                git apply "$PATCH"\n'
    '            else\n'
    '                warning "Skipping patch ${PATCH} (already upstream, previously applied, or malformed): ${APPLY_CHECK}"\n'
    '            fi\n'
    '            ;;\n'
    '        esac\n'
    '    done\n'
)
assert text.count(old_loop) == 1, 'darwin-xnu-build patch loop changed'
text = text.replace(old_loop, new_loop)
text = text.replace(old_patches, new_patches)

path.write_text(text)
print('firehose:', new)
print('critical patch policy: strict')