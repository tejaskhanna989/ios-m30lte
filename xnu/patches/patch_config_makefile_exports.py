#!/usr/bin/env python3
"""Patch config/Makefile to copy export files to build directory before all-kpi.exp needs them."""
import os

with open('config/Makefile', 'r') as f:
    content = f.read()

# Find the all-kpi.exp target and add a rule to copy export files before it
old_all_kpi = '''$(OBJPATH)/all-kpi.exp: $(EXPORTS_FILES)
	$(_v)$(KEXT_CREATE_SYMBOL_SET)					\
		$(ARCH_FLAGS_$(CURRENT_ARCH_CONFIG))			\
		-import $(TARGET)/allsymbols				\
		$(foreach symbolset,$(filter-out Private,$(SYMBOL_COMPONENT_LIST)),	\
			-export $(SOURCE)/$(symbolset).exports		\
			-export $(SOURCE)/$(symbolset).$(EXPORT_SOURCE_ARCH_CONFIG_LC).exports)	\
		-output /dev/null $(_vstdout)
	$(_v)$(KEXT_CREATE_SYMBOL_SET)					\
		$(ARCH_FLAGS_$(CURRENT_ARCH_CONFIG))			\
		-import $(TARGET)/allsymbols				\
		$(foreach symbolset,$(filter-out Unsupported,$(SYMBOL_COMPONENT_LIST)),	\
			-export $(SOURCE)/$(symbolset).exports		\
			-export $(SOURCE)/$(symbolset).$(EXPORT_SOURCE_ARCH_CONFIG_LC).exports)	\
		-output /dev/null $(_vstdout)'''

new_all_kpi = '''# Copy export files from config source to build directory
$(TARGET)/%.exports: $(SOURCE)/%.exports
	$(_v)$(CP) $< $@

$(OBJPATH)/all-kpi.exp: $(addprefix $(TARGET)/,$(notdir $(EXPORTS_FILES)))
	$(_v)$(KEXT_CREATE_SYMBOL_SET)					\
		$(ARCH_FLAGS_$(CURRENT_ARCH_CONFIG))			\
		-import $(TARGET)/allsymbols				\
		$(foreach symbolset,$(filter-out Private,$(SYMBOL_COMPONENT_LIST)),	\
			-export $(TARGET)/$(symbolset).exports		\
			-export $(TARGET)/$(symbolset).$(EXPORT_SOURCE_ARCH_CONFIG_LC).exports)	\
		-output /dev/null $(_vstdout)
	$(_v)$(KEXT_CREATE_SYMBOL_SET)					\
		$(ARCH_FLAGS_$(CURRENT_ARCH_CONFIG))			\
		-import $(TARGET)/allsymbols				\
		$(foreach symbolset,$(filter-out Unsupported,$(SYMBOL_COMPONENT_LIST)),	\
			-export $(TARGET)/$(symbolset).exports		\
			-export $(TARGET)/$(symbolset).$(EXPORT_SOURCE_ARCH_CONFIG_LC).exports)	\
		-output /dev/null $(_vstdout)'''

if old_all_kpi not in content:
    print("WARNING: Could not find all-kpi.exp target pattern")
else:
    content = content.replace(old_all_kpi, new_all_kpi)
    print("Patched config/Makefile: added copy rule for export files")

# Fix EXPORTS_FILES to use basenames (since we copy to build dir)
old_exports = '''EXPORTS_FILES := $(foreach symbolset,$(SYMBOL_COMPONENT_LIST),$(abspath $(SOURCE))/$(symbolset).exports \
	$(abspath $(SOURCE))/$(symbolset).$(EXPORT_SOURCE_ARCH_CONFIG_LC).exports \
	$(notdir $(wildcard $(SOURCE)/$(symbolset).$(EXPORT_SOURCE_ARCH_CONFIG_LC).$(PLATFORM).exports))) \
	Unused.exports'''

new_exports = '''EXPORTS_FILES := $(foreach symbolset,$(SYMBOL_COMPONENT_LIST),$(symbolset).exports \
	$(symbolset).$(EXPORT_SOURCE_ARCH_CONFIG_LC).exports \
	$(notdir $(wildcard $(SOURCE)/$(symbolset).$(EXPORT_SOURCE_ARCH_CONFIG_LC).$(PLATFORM).exports))) \
	Unused.exports'''

if old_exports not in content:
    # Try original pattern
    old_exports2 = '''EXPORTS_FILES := $(foreach symbolset,$(SYMBOL_COMPONENT_LIST),$(symbolset).exports \
	$(symbolset).$(EXPORT_SOURCE_ARCH_CONFIG_LC).exports \
	$(notdir $(wildcard $(SOURCE)/$(symbolset).$(EXPORT_SOURCE_ARCH_CONFIG_LC).$(PLATFORM).exports))) \
	Unused.exports'''
    if old_exports2 not in content:
        print("WARNING: Could not find EXPORTS_FILES pattern (using original)")
    else:
        # Already basenames, no change needed
        print("EXPORTS_FILES already uses basenames")
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