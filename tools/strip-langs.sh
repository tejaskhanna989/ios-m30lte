#!/bin/bash
# strip-langs.sh - Remove non-English language packs from iOS rootfs
# Usage: sudo ./strip-langs.sh /path/to/mounted/ios/rootfs
#
# Keeps: Base.lproj, en.lproj, en_AU.lproj, en_CA.lproj, en_GB.lproj,
#        en_IE.lproj, en_IN.lproj, en_NZ.lproj, en_SG.lproj, en_ZA.lproj
# Removes: all other .lproj directories (fr, de, es, it, ja, ko, zh, etc.)
#
# This saves STORAGE space (not RAM). Language packs are only loaded into
# RAM when the system language is set to that language.

set -euo pipefail

ROOT="${1:-}"
if [ -z "$ROOT" ]; then
    echo "Usage: $0 <ios-rootfs-mount-point>"
    echo "Example: sudo $0 /mnt/ios-root"
    exit 1
fi

if [ ! -d "$ROOT" ]; then
    echo "Error: $ROOT is not a directory"
    exit 1
fi

# Count before
BEFORE=$(du -sh "$ROOT" 2>/dev/null | cut -f1)
echo "Rootfs size before: $BEFORE"

# Find all .lproj directories, keep English variants
KEEP_PATTERNS=(
    "Base.lproj"
    "en.lproj"
    "en_AU.lproj"
    "en_CA.lproj"
    "en_GB.lproj"
    "en_IE.lproj"
    "en_IN.lproj"
    "en_NZ.lproj"
    "en_SG.lproj"
    "en_ZA.lproj"
)

# Build find expression: -name "*.lproj" ! -name "Base.lproj" ! -name "en.lproj" ...
FIND_EXPR="\( -name '*.lproj' "
for pat in "${KEEP_PATTERNS[@]}"; do
    FIND_EXPR+="! -name '$pat' "
done
FIND_EXPR+="\)"

echo "Searching for non-English .lproj directories..."

# Collect directories to remove
TO_REMOVE=$(find "$ROOT" -type d $FIND_EXPR 2>/dev/null | sort)

if [ -z "$TO_REMOVE" ]; then
    echo "No non-English .lproj directories found."
    exit 0
fi

COUNT=$(echo "$TO_REMOVE" | wc -l)
echo "Found $COUNT non-English .lproj directories"

# Show what will be removed (first 20)
echo "Examples:"
echo "$TO_REMOVE" | head -20

# Ask for confirmation
echo -n "Remove these $COUNT directories? [y/N]: "
read -r CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "Aborted."
    exit 0
fi

# Remove them
echo "Removing..."
echo "$TO_REMOVE" | while read -r dir; do
    rm -rf "$dir" 2>/dev/null && echo "  removed: $dir" || echo "  failed:  $dir"
done

# Count after
AFTER=$(du -sh "$ROOT" 2>/dev/null | cut -f1)
echo ""
echo "Rootfs size after:  $AFTER"
echo "Done."
