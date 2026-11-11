#!/usr/bin/env python3
"""Patch security/conf/Makefile to ensure SYS is passed correctly to doconf."""
import sys

with open('security/conf/Makefile', 'r') as f:
    content = f.read()

# The doconf command needs to have the SYS passed correctly.
# The issue is that $(CURRENT_KERNEL_CONFIG) might not be expanding correctly
# in the doconf script context. Let's ensure it's passed explicitly.

old_doconf = '''$(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile: $(SRCROOT)/SETUP/config/doconf $(OBJROOT)/SETUP/config $(DOCONFDEPS)
	$(_v)$(MKDIR) $(TARGET)/$(CURRENT_KERNEL_CONFIG)
	$(_v)$(SRCROOT)/SETUP/config/doconf -c -cpu $(DOCONF_ARCH_CONFIG_LC) -soc $(CURRENT_MACHINE_CONFIG_LC) -platform $(PLATFORM) -d $(TARGET)/$(CURRENT_KERNEL_CONFIG) -s $(SOURCE) -m $(MASTERCONFDIR) $(DOCONF_SEEF) $(CURRENT_KERNEL_CONFIG)'''

new_doconf = '''$(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile: $(SRCROOT)/SETUP/config/doconf $(OBJROOT)/SETUP/config $(DOCONFDEPS)
	$(_v)$(MKDIR) $(TARGET)/$(CURRENT_KERNEL_CONFIG)
	$(_v)$(SRCROOT)/SETUP/config/doconf -c -cpu $(DOCONF_ARCH_CONFIG_LC) -soc $(CURRENT_MACHINE_CONFIG_LC) -platform $(PLATFORM) -d $(TARGET)/$(CURRENT_KERNEL_CONFIG) -s $(SOURCE) -m $(MASTERCONFDIR) $(DOCONF_SEEF) -sys $(CURRENT_KERNEL_CONFIG)'''

if old_doconf not in content:
    print("ERROR: Could not find doconf command")
    sys.exit(1)

content = content.replace(old_doconf, new_doconf)

with open('security/conf/Makefile', 'w') as f:
    f.write(content)

print("Patched security/conf/Makefile to add -sys flag to doconf")

# Verify
with open('security/conf/Makefile', 'r') as f:
    content = f.read()
    for i, line in enumerate(content.split('\n')[-20:]):
        print(f"  {line}")