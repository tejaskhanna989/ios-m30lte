#!/usr/bin/env python3
"""Fix MASTER.arm64.m30lte config file - replace #define with options."""
import sys

with open('config/MASTER.arm64.m30lte', 'r') as f:
    content = f.read()

# Replace #define with options
content = content.replace('#define nos_arm_asm 1\n', 'options\tNOS_ARM_ASM\t\t# <nos_arm_asm>\n')
content = content.replace('#define nos_arm_pmap 1\n', 'options\tNOS_ARM_PMAP\t\t# <nos_arm_pmap>\n')

with open('config/MASTER.arm64.m30lte', 'w') as f:
    f.write(content)

print("Fixed MASTER.arm64.m30lte config file")

# Verify
with open('config/MASTER.arm64.m30lte', 'r') as f:
    content = f.read()
    print(content[:500])