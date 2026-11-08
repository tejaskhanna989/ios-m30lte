#!/usr/bin/env python3
"""Fix MASTER.arm64.m30lte config file - replace #define with options and enable LIBKERN."""
import sys
import re

with open('config/MASTER.arm64.m30lte', 'r') as f:
    content = f.read()

# Replace #define with options
content = content.replace('#define nos_arm_asm 1\n', 'options\tNOS_ARM_ASM\t\t# <nos_arm_asm>\n')
content = content.replace('#define nos_arm_pmap 1\n', 'options\tNOS_ARM_PMAP\t\t# <nos_arm_pmap>\n')

# Uncomment LIBKERN lines
content = re.sub(r'^#\s*(LIBKERN_BASE\s*=)', r'  \1', content, flags=re.MULTILINE)
content = re.sub(r'^#\s*(LIBKERN_RELEASE\s*=)', r'  \1', content, flags=re.MULTILINE)
content = re.sub(r'^#\s*(LIBKERN_DEV\s*=)', r'  \1', content, flags=re.MULTILINE)
content = re.sub(r'^#\s*(LIBKERN_DEBUG\s*=)', r'  \1', content, flags=re.MULTILINE)

# Remove C preprocessor directives that unifdef can't handle for M30LTE
# For M30LTE: SOC_CONFIG_t8020 is not defined, SOC_IS_VIRTUALIZED is undefined (-U)
# So #if SOC_CONFIG_t8020 || SOC_IS_VIRTUALIZED evaluates to FALSE
# Take the #else branch

# Remove HIBERNATION #if/#else/#endif block - keep the #else branch (empty [ ])
hib_pattern = r'#if SOC_CONFIG_t8020 \|\| SOC_IS_VIRTUALIZED\n#\s*HIBERNATION\s*=\s*\[\s*\]\n#else /\*!\(SOC_CONFIG_t8020 \|\| SOC_IS_VIRTUALIZED\)\*/\n#\s*HIBERNATION\s*=\s*\[\s*\]\n#endif /\*SOC_CONFIG_t8020 \|\| SOC_IS_VIRTUALIZED\*/\n'
hib_replacement = '  HIBERNATION =    [ ]\n'
content = re.sub(hib_pattern, hib_replacement, content)

# Remove PARAVIRT_BASE #if/#else/#endif block - keep the #else branch (empty [ ])
pv_pattern = r'#if SOC_IS_VIRTUALIZED\n#\s*PARAVIRT_BASE\s*=\s*\[\s*config_pv_ticket\s*\]\n#else\n#\s*PARAVIRT_BASE\s*=\s*\[\s*\]\n#endif /\*SOC_IS_VIRTUALIZED\*/\n'
pv_replacement = '  PARAVIRT_BASE =  [ ]\n'
content = re.sub(pv_pattern, pv_replacement, content)

# Also handle any remaining #if/#else/#endif that might be in the file
# Remove comment lines that are just preprocessor directive markers
content = re.sub(r'^#if.*\n', '', content, flags=re.MULTILINE)
content = re.sub(r'^#else.*\n', '', content, flags=re.MULTILINE)
content = re.sub(r'^#endif.*\n', '', content, flags=re.MULTILINE)
# Remove any remaining #define that aren't options
content = re.sub(r'^#define\s+\w+\s+.*\n', '', content, flags=re.MULTILINE)

with open('config/MASTER.arm64.m30lte', 'w') as f:
    f.write(content)

print("Fixed MASTER.arm64.m30lte config file")

# Verify
with open('config/MASTER.arm64.m30lte', 'r') as f:
    content = f.read()
    print("=== Fixed config file ===")
    print(content)