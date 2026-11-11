#!/usr/bin/env python3
"""Patch security/conf/Makefile to ensure DOCONF_SEEF doesn't interfere with SYS argument."""
import sys

with open('security/conf/Makefile', 'r') as f:
    content = f.read()

# The issue is that DOCONF_SEEF might be set to something that interferes with
# the SYS argument (last positional argument). Ensure it's empty or not used.
# The doconf command should end with $(CURRENT_KERNEL_CONFIG) as the SYS argument.

# Find and ensure DOCONF_SEEF is not interfering
old_doconf = '''$(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile: $(SRCROOT)/SETUP/config/doconf $(OBJROOT)/SETUP/config $(DOCONFDEPS)
	$(_v)$(MKDIR) $(TARGET)/$(CURRENT_KERNEL_CONFIG)
	$(_v)$(SRCROOT)/SETUP/config/doconf -c -cpu $(DOCONF_ARCH_CONFIG_LC) -soc $(CURRENT_MACHINE_CONFIG_LC) -platform $(PLATFORM) -d $(TARGET)/$(CURRENT_KERNEL_CONFIG) -s $(SOURCE) -m $(MASTERCONFDIR) $(DOCONF_SEEF) $(CURRENT_KERNEL_CONFIG)'''

new_doconf = '''$(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile: $(SRCROOT)/SETUP/config/doconf $(OBJROOT)/SETUP/config $(DOCONFDEPS)
	$(_v)$(MKDIR) $(TARGET)/$(CURRENT_KERNEL_CONFIG)
	$(_v)$(SRCROOT)/SETUP/config/doconf -c -cpu $(DOCONF_ARCH_CONFIG_LC) -soc $(CURRENT_MACHINE_CONFIG_LC) -platform $(PLATFORM) -d $(TARGET)/$(CURRENT_KERNEL_CONFIG) -s $(SOURCE) -m $(MASTERCONFDIR) $(CURRENT_KERNEL_CONFIG)'''

if old_doconf not in content:
    print("ERROR: Could not find doconf command")
    sys.exit(1)

content = content.replace(old_doconf, new_doconf)

with open('security/conf/Makefile', 'w') as f:
    f.write(content)

print("Patched security/conf/Makefile to remove DOCONF_SEEF from doconf command")
