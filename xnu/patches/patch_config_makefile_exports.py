#!/usr/bin/env python3
"""Patch config/Makefile to add config directory to VPATH."""
import os

with open('config/Makefile', 'r') as f:
    content = f.read()

# Add VPATH to include the config source directory
old = '''include $(MakeInc_def)

# config is not a COMPONENT but we still want to build most files in a TARGET subdir'''

new = '''include $(MakeInc_def)

# Add config source directory to VPATH so export files can be found
VPATH = $(abspath $(SOURCE))

# config is not a COMPONENT but we still want to build most files in a TARGET subdir'''

if old not in content:
    print("WARNING: Could not find insertion point")
else:
    content = content.replace(old, new)
    with open('config/Makefile', 'w') as f:
        f.write(content)
    print("Patched config/Makefile to add VPATH")

# Also fix EXPORTS_FILES to use absolute paths
old = '''EXPORTS_FILES := $(foreach symbolset,$(SYMBOL_COMPONENT_LIST),$(symbolset).exports \
	$(symbolset).$(EXPORT_SOURCE_ARCH_CONFIG_LC).exports \
	$(notdir $(wildcard $(SOURCE)/$(symbolset).$(EXPORT_SOURCE_ARCH_CONFIG_LC).$(PLATFORM).exports))) \
	Unused.exports'''

new = '''EXPORTS_FILES := $(foreach symbolset,$(SYMBOL_COMPONENT_LIST),$(abspath $(SOURCE))/$(symbolset).exports \
	$(abspath $(SOURCE))/$(symbolset).$(EXPORT_SOURCE_ARCH_CONFIG_LC).exports \
	$(notdir $(wildcard $(SOURCE)/$(symbolset).$(EXPORT_SOURCE_ARCH_CONFIG_LC).$(PLATFORM).exports))) \
	Unused.exports'''

if old not in content:
    print("WARNING: Could not find EXPORTS_FILES pattern")
else:
    content = content.replace(old, new)
    with open('config/Makefile', 'w') as f:
        f.write(content)
    print("Patched config/Makefile to use absolute paths for export files")

# Verify
with open('config/Makefile', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[:60]):
        print(f"  {i+1}: {line}")

print("Done")