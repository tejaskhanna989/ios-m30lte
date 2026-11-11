#!/usr/bin/env python3
"""Patch config/Makefile to ensure export files are found via VPATH."""
import os

with open('config/Makefile', 'r') as f:
    content = f.read()

# Add VPATH at the top after includes
old = '''include $(MakeInc_def)

# config is not a COMPONENT but we still want to build most files in a TARGET subdir'''

new = '''include $(MakeInc_def)

# Add config source directory to VPATH so export files can be found
VPATH = $(abspath $(SOURCE))

# config is not a COMPONENT but we still want to build most files in a TARGET subdir'''

if old not in content:
    print("WARNING: Could not find insertion point for VPATH")
else:
    content = content.replace(old, new)
    with open('config/Makefile', 'w') as f:
        f.write(content)
    print("Patched config/Makefile to add VPATH")

# Fix EXPORTS_FILES to use basenames (for VPATH lookup)
old_exports = '''EXPORTS_FILES := $(foreach symbolset,$(SYMBOL_COMPONENT_LIST),$(abspath $(SOURCE))/$(symbolset).exports \
	$(abspath $(SOURCE))/$(symbolset).$(EXPORT_SOURCE_ARCH_CONFIG_LC).exports \
	$(notdir $(wildcard $(SOURCE)/$(symbolset).$(EXPORT_SOURCE_ARCH_CONFIG_LC).$(PLATFORM).exports))) \
	Unused.exports'''

new_exports = '''EXPORTS_FILES := $(foreach symbolset,$(SYMBOL_COMPONENT_LIST),$(symbolset).exports \
	$(symbolset).$(EXPORT_SOURCE_ARCH_CONFIG_LC).exports \
	$(notdir $(wildcard $(SOURCE)/$(symbolset).$(EXPORT_SOURCE_ARCH_CONFIG_LC).$(PLATFORM).exports))) \
	Unused.exports'''

if old_exports not in content:
    # Try alternative pattern
    old_exports2 = '''EXPORTS_FILES := $(foreach symbolset,$(SYMBOL_COMPONENT_LIST),$(symbolset).exports \
	$(symbolset).$(EXPORT_SOURCE_ARCH_CONFIG_LC).exports \
	$(notdir $(wildcard $(SOURCE)/$(symbolset).$(EXPORT_SOURCE_ARCH_CONFIG_LC).$(PLATFORM).exports))) \
	Unused.exports'''
    if old_exports2 in content:
        content = content.replace(old_exports2, new_exports)
        print("Patched config/Makefile EXPORTS_FILES to use basenames (alt pattern)")
    else:
        print("WARNING: Could not find EXPORTS_FILES pattern")
else:
    content = content.replace(old_exports, new_exports)
    print("Patched config/Makefile EXPORTS_FILES to use basenames")

with open('config/Makefile', 'w') as f:
    f.write(content)

# Verify
with open('config/Makefile', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[:80]):
        print(f"  {i+1}: {line}")

print("Done")