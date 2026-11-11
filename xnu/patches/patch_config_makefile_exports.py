#!/usr/bin/env python3
"""Patch config/Makefile to copy export files to build directory."""
import os

with open('config/Makefile', 'r') as f:
    content = f.read()

# Add a rule to copy export files to build directory
# Find the all-kpi.exp target and add a prerequisite to copy export files
old = '''$(OBJPATH)/all-kpi.exp: $(EXPORTS_FILES)
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

new = '''# Copy export files to build directory
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

if old not in content:
    print("WARNING: Could not find all-kpi.exp target")
else:
    content = content.replace(old, new)
    with open('config/Makefile', 'w') as f:
        f.write(content)
    print("Patched config/Makefile to copy export files to build directory")

# Verify
with open('config/Makefile', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[:80]):
        print(f"  {i+1}: {line}")

print("Done")