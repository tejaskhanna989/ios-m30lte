#!/usr/bin/env python3
"""Fix security/conf/Makefile - correct DOCONF_SEEF typo to DOCONF_SEED."""
import sys

with open('security/conf/Makefile', 'r') as f:
    content = f.read()

# Fix the typo: DOCONF_SEEF -> DOCONF_SEED
old_doconf = '''$(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile: $(SRCROOT)/SETUP/config/doconf $(OBJROOT)/SETUP/config $(DOCONFDEPS)
	$(_v)$(MKDIR) $(TARGET)/$(CURRENT_KERNEL_CONFIG)
	$(_v)$(SRCROOT)/SETUP/config/doconf -c -cpu $(DOCONF_ARCH_CONFIG_LC) -soc $(CURRENT_MACHINE_CONFIG_LC) -platform $(PLATFORM) -d $(TARGET)/$(CURRENT_KERNEL_CONFIG) -s $(SOURCE) -m $(MASTERCONFDIR) $(DOCONF_SEEF) $(CURRENT_KERNEL_CONFIG)'''

new_doconf = '''$(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile: $(SRCROOT)/SETUP/config/doconf $(OBJROOT)/SETUP/config $(DOCONFDEPS)
	$(_v)$(MKDIR) $(TARGET)/$(CURRENT_KERNEL_CONFIG)
	$(_v)$(SRCROOT)/SETUP/config/doconf -c -cpu $(DOCONF_ARCH_CONFIG_LC) -soc $(CURRENT_MACHINE_CONFIG_LC) -platform $(PLATFORM) -d $(TARGET)/$(CURRENT_KERNEL_CONFIG) -s $(SOURCE) -m $(MASTERCONFDIR) $(DOCONF_SEED) $(CURRENT_KERNEL_CONFIG)'''

if old_doconf not in content:
    print("ERROR: Could not find doconf command with DOCONF_SEEF")
    sys.exit(1)

content = content.replace(old_doconf, new_doconf)

with open('security/conf/Makefile', 'w') as f:
    f.write(content)

print("Fixed security/conf/Makefile: DOCONF_SEEF -> DOCONF_SEED")

# Verify
with open('security/conf/Makefile', 'r') as f:
    content = f.read()
    for line in content.split('\n')[-15:]:
        print(f"  {line}")
