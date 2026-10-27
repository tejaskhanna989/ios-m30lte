#!/usr/bin/env python3
"""Generate assembly stubs patch for M30LTE kernel undefined symbols.

Assembly labels have no type information, so they won't conflict with
existing C declarations in XNU headers. The linker will resolve them
at link time.
"""

symbols_file = '/tmp/undefined_symbols.txt'
output_file = '/home/tejas/Projects/m30lte-ios/xnu/patches/0082-m30lte-lowlevel-stubs.patch'

with open(symbols_file) as f:
    symbols = [line.strip() for line in f if line.strip()]

# Build assembly stub content
asm_lines = []
asm_lines.append('/*')
asm_lines.append(' * M30LTE: assembly stub implementations for low-level board-specific')
asm_lines.append(' * functions normally provided by Apple\'s closed per-SoC libraries.')
asm_lines.append(' * Assembly labels have no type info, so they won\'t conflict with')
asm_lines.append(' * existing C declarations. Real hardware bring-up will replace them.')
asm_lines.append(' */')
asm_lines.append('')
asm_lines.append('.text')
asm_lines.append('')

for sym in symbols:
    asm_lines.append(f'.globl {sym}')
    asm_lines.append(f'{sym}:')
    asm_lines.append('    ret')
    asm_lines.append('')

asm_line_count = len(asm_lines)

# ---- Build patch ----
patch_lines = []

# Part 1: New file m30_lowlevel_stubs.s
patch_lines.append('diff --git a/osfmk/arm64/m30_lowlevel_stubs.s b/osfmk/arm64/m30_lowlevel_stubs.s')
patch_lines.append('new file mode 100644')
patch_lines.append('--- /dev/null')
patch_lines.append('+++ b/osfmk/arm64/m30_lowlevel_stubs.s')
patch_lines.append(f'@@ -0,0 +1,{asm_line_count} @@')
for line in asm_lines:
    patch_lines.append('+' + line)

# Part 2: Modify files.arm64 - add stubs after m30_early.c
# After patch 0010, m30_early.c is at line 44, arm64_hypercall.c at line 45
patch_lines.append('')
patch_lines.append('diff --git a/osfmk/conf/files.arm64 b/osfmk/conf/files.arm64')
patch_lines.append('--- a/osfmk/conf/files.arm64')
patch_lines.append('+++ b/osfmk/conf/files.arm64')
patch_lines.append('@@ -44,2 +44,3 @@')
patch_lines.append(' osfmk/arm64/m30_early.c	standard')
patch_lines.append('+osfmk/arm64/m30_lowlevel_stubs.s	standard')
patch_lines.append(' osfmk/arm64/arm64_hypercall.c	standard')

patch_text = '\n'.join(patch_lines) + '\n'

with open(output_file, 'w') as f:
    f.write(patch_text)

print(f'Generated assembly stubs for {len(symbols)} symbols')
print(f'Patch written to {output_file}')
print(f'Patch has {len(patch_lines)} lines')
