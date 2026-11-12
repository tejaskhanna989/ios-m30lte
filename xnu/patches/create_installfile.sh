#!/bin/bash

# Simple installfile replacement for CI builds
# This script mimics the behavior of installfile -c -S -m

SRC_FILE="$1"
DST_FILE="$2"
MODE="$3"

if [ $# -lt 2 ]; then
    echo "Usage: $0 <src_file> <dst_file> [mode]"
    exit 1
fi

# Create directory if it doesn't exist
mkdir -p "$(dirname "$DST_FILE")"

# Copy the file
cp "$SRC_FILE" "$DST_FILE"

# Set permissions if mode is specified
if [ -n "$MODE" ]; then
    chmod "$MODE" "$DST_FILE"
fi

echo "Copied $SRC_FILE to $DST_FILE"