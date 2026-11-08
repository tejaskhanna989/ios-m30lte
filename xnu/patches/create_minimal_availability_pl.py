#!/usr/bin/env python3
"""Minimal availability.pl for M30LTE XNU build - Python version.

Handles --ios and --macosx flags for _symbol_aliasing.sh generation.
"""

import sys

def main():
    if len(sys.argv) > 1:
        platform = sys.argv[1]
    else:
        platform = ''

    if platform == '--ios':
        # iOS versions for M30LTE (iOS 16/17/18 era)
        versions = [
            "16.0", "16.1", "16.2", "16.3", "16.4", "16.5", "16.6",
            "17.0", "17.1", "17.2", "17.3", "17.4", "17.5",
            "18.0"
        ]
    elif platform == '--macosx':
        # macOS versions
        versions = [
            "13.0", "13.1", "13.2", "13.3", "13.4", "13.5", "13.6",
            "14.0", "14.1", "14.2", "14.3", "14.4", "14.5",
            "15.0"
        ]
    else:
        # Default: print nothing (should not happen in normal build)
        versions = []

    for v in versions:
        print(v)

if __name__ == '__main__':
    main()