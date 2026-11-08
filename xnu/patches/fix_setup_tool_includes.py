#!/usr/bin/env python3
"""Fix SETUP tool include paths - Python version to avoid sed corruption."""
import sys
import os

SDKROOT_PATH = os.environ.get('SDKROOT_PATH', '')

# Fix SETUP/kextsymboltool/Makefile
if os.path.exists('SETUP/kextsymboltool/Makefile'):
    with open('SETUP/kextsymboltool/Makefile', 'r') as f:
        content = f.read()
    new_content = f'CFLAGS += -isysroot {SDKROOT_PATH} -I{SDKROOT_PATH}/usr/include\n' + content
    with open('SETUP/kextsymboltool/Makefile', 'w') as f:
        f.write(new_content)
    print("Patched SETUP/kextsymboltool/Makefile")

# Fix SETUP/config/Makefile
if os.path.exists('SETUP/config/Makefile'):
    with open('SETUP/config/Makefile', 'r') as f:
        content = f.read()
    new_content = f'CFLAGS += -isysroot {SDKROOT_PATH} -I{SDKROOT_PATH}/usr/include -I$(SOURCE)\n' + content
    with open('SETUP/config/Makefile', 'w') as f:
        f.write(new_content)
    print("Patched SETUP/config/Makefile")

# Fix externs.c include
if os.path.exists('SETUP/config/externs.c'):
    with open('SETUP/config/externs.c', 'r') as f:
        content = f.read()
    content = content.replace('#include <config.h>', '#include "config.h"')
    with open('SETUP/config/externs.c', 'w') as f:
        f.write(content)
    print("Fixed externs.c include")

print("All SETUP tool include paths fixed")