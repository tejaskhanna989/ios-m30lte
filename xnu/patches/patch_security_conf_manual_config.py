#!/usr/bin/env python3
"""Create a minimal security/conf config file to bypass doconf failure."""
import os

# The security/conf config file that doconf would generate
config_content = """# config file for security/conf
# Generated manually to bypass doconf failure

# Build directory
builddir	"."

# Object directory
objectdir	"../../../../../../../BUILD/obj"

# Source directory
sourcedir	"../../../../../../.."

# Standard source files
security/mac_base.c

# MAC framework files (CONFIG_MACF enabled)
security/mac_audit.c
security/mac_data.c
security/mac_label.c
security/mac_necp.c
security/mac_process.c
security/mac_vfs.c
security/mac_vfs_subr.c
security/mac_system.c
security/mac_sysv_sem.c
security/mac_sysv_shm.c
security/mac_sysv_msg.c
security/mac_posix_sem.c
security/mac_posix_shm.c
security/mac_socket.c
security/mac_pipe.c
security/mac_iokit.c
security/mac_file.c
security/mac_priv.c
security/mac_pty.c
security/mac_kext.c
security/mac_mach.c

# Skywalk support
security/mac_skywalk.c
"""

# Ensure directory exists
os.makedirs('security/conf', exist_ok=True)

# Write the config file
with open('security/conf/DEVELOPMENT', 'w') as f:
    f.write(config_content)

print("Created security/conf/DEVELOPMENT config file")

# Now patch the security/conf Makefile to use Makefile.template as fallback
with open('security/conf/Makefile', 'r') as f:
    content = f.read()

# Replace the doconf rule with a fallback to Makefile.template
old_rule = '''$(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile: $(SRCROOT)/SETUP/config/doconf $(OBJROOT)/SETUP/config $(DOCONFDEPS)
	$(_v)$(MKDIR) $(TARGET)/$(CURRENT_KERNEL_CONFIG)
	$(_v)$(SRCROOT)/SETUP/config/doconf -c -cpu $(DOCONF_ARCH_CONFIG_LC) -soc $(CURRENT_MACHINE_CONFIG_LC) -platform $(PLATFORM) -d $(TARGET)/$(CURRENT_KERNEL_CONFIG) -s $(SOURCE) -m $(MASTERCONFDIR) $(DOCONF_SEEF) $(CURRENT_KERNEL_CONFIG)'''

new_rule = '''$(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile: $(SOURCE)/$(CURRENT_KERNEL_CONFIG) $(SOURCE)/Makefile.template
	$(_v)$(MKDIR) $(TARGET)/$(CURRENT_KERNEL_CONFIG)
	$(_v)test -f $(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile || $(CP) $(SOURCE)/Makefile.template $(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile'''

if old_rule not in content:
    print("WARNING: Could not find doconf rule to replace")
else:
    content = content.replace(old_rule, new_rule)
    with open('security/conf/Makefile', 'w') as f:
        f.write(content)
    print("Patched security/conf/Makefile to use Makefile.template as fallback")

print("Done")