#!/usr/bin/env python3
"""Fix MASTER.arm64.m30lte config file - replace #define with options, enable LIBKERN, fix KERNEL_BASE."""
import sys
import re

with open('config/MASTER.arm64.m30lte', 'r') as f:
    content = f.read()

# Replace #define with options
content = content.replace('#define nos_arm_asm 1\n', 'options\tNOS_ARM_ASM\t\t# <nos_arm_asm>\n')
content = content.replace('#define nos_arm_pmap 1\n', 'options\tNOS_ARM_PMAP\t\t# <nos_arm_pmap>\n')

# Fix KERNEL_BASE: remove config_pmap_ppl (conflicts with nos_arm_pmap), add missing standard options
content = content.replace(
    'KERNEL_BASE =    [ arm64 config_pmap_ppl medium msgb_large config_requires_u32_munging config_delay_idle_sleep config_proc_udata_storage config_uexc config_darkboot ARM_EXTRAS_BASE nos_arm_asm nos_arm_pmap ]',
    'KERNEL_BASE =    [ arm64 medium msgb_large config_embedded config_enforce_signed_code config_code_signature_reconstitution config_requires_u32_munging config_delay_idle_sleep config_proc_udata_storage config_uexc config_darkboot ARM_EXTRAS_BASE nos_arm_asm nos_arm_pmap config_amcc ]'
)

# Fix BSD_BASE: add config_imageboot_img4 and config_embedded for filelist generation
content = content.replace(
    'BSD_BASE =       [ mach_bsd sysv_sem sysv_msg sysv_shm config_netboot config_imageboot psynch config_proc_uuid_policy config_coredump pgo config_personas ]',
    'BSD_BASE =       [ mach_bsd sysv_sem sysv_msg sysv_shm config_netboot config_imageboot config_imageboot_img4 config_embedded psynch config_proc_uuid_policy config_coredump pgo config_personas ]'
)

# Uncomment LIBKERN lines
content = re.sub(r'^#\s*(LIBKERN_BASE\s*=)', r'  \1', content, flags=re.MULTILINE)
content = re.sub(r'^#\s*(LIBKERN_RELEASE\s*=)', r'  \1', content, flags=re.MULTILINE)
content = re.sub(r'^#\s*(LIBKERN_DEV\s*=)', r'  \1', content, flags=re.MULTILINE)
content = re.sub(r'^#\s*(LIBKERN_DEBUG\s*=)', r'  \1', content, flags=re.MULTILINE)

# Evaluate C preprocessor directives for M30LTE:
# SOC_CONFIG_t8020 = false (not defined)
# SOC_IS_VIRTUALIZED = false (not defined, -U)
# So: #if SOC_CONFIG_t8020 || SOC_IS_VIRTUALIZED -> FALSE, take #else branch
#     #if SOC_IS_VIRTUALIZED -> FALSE, take #else branch

# HIBERNATION block: #if SOC_CONFIG_t8020 || SOC_IS_VIRTUALIZED -> FALSE -> take #else (empty [ ])
hib_pattern = r'#if SOC_CONFIG_t8020 \|\| SOC_IS_VIRTUALIZED\n#\s*HIBERNATION\s*=\s*\[\s*\]\n#else /\*!\(SOC_CONFIG_t8020 \|\| SOC_IS_VIRTUALIZED\)\*/\n#\s*HIBERNATION\s*=\s*\[\s*\]\n#endif /\*SOC_CONFIG_t8020 \|\| SOC_IS_VIRTUALIZED\*/\n'
hib_replacement = '  HIBERNATION =    [ ]\n'
content = re.sub(hib_pattern, hib_replacement, content)

# PARAVIRT_BASE block: #if SOC_IS_VIRTUALIZED -> FALSE -> take #else (empty [ ])
pv_pattern = r'#if SOC_IS_VIRTUALIZED\n#\s*PARAVIRT_BASE\s*=\s*\[\s*config_pv_ticket\s*\]\n#else\n#\s*PARAVIRT_BASE\s*=\s*\[\s*\]\n#endif /\*SOC_IS_VIRTUALIZED\*/\n'
pv_replacement = '  PARAVIRT_BASE =  [ ]\n'
content = re.sub(pv_pattern, pv_replacement, content)

# Remove any remaining #define that aren't options
content = re.sub(r'^#define\s+\w+\s+.*\n', '', content, flags=re.MULTILINE)

# Remove any remaining #if/#else/#endif that might be malformed
content = re.sub(r'^#if.*\n', '', content, flags=re.MULTILINE)
content = re.sub(r'^#else.*\n', '', content, flags=re.MULTILINE)
content = re.sub(r'^#endif.*\n', '', content, flags=re.MULTILINE)

with open('config/MASTER.arm64.m30lte', 'w') as f:
    f.write(content)

print("Fixed MASTER.arm64.m30lte config file")

with open('config/MASTER.arm64.m30lte', 'r') as f:
    content = f.read()
    print("=== Fixed config file ===")
    print(content)