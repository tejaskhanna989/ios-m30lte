#!/usr/bin/env python3
"""Generate assembly stub patch for all undefined M30LTE kernel symbols.

Modifies the EXISTING osfmk/conf/files.arm64 (patched by 0010) to add the stubs
assembly file. Context lines match the file state after patch 0010.
"""

import sys

symbols_file = '/tmp/undefined_symbols.txt'
output_file = '/home/tejas/Projects/m30lte-ios/xnu/patches/0082-m30lte-lowlevel-stubs.patch'

with open(symbols_file) as f:
    symbols = [line.strip() for line in f if line.strip()]

# Generate assembly stubs
asm_lines = []
for sym in symbols:
    asm_lines.append(f'.globl {sym}')
    asm_lines.append(f'{sym}:')
    asm_lines.append('    ret')

stub_file_lines = len(asm_lines) + 4  # header + .text + blanks

patch_lines = []
patch_lines.append('diff --git a/osfmk/arm64/m30_lowlevel_stubs.s b/osfmk/arm64/m30_lowlevel_stubs.s')
patch_lines.append('new file mode 100644')
patch_lines.append('--- /dev/null')
patch_lines.append('+++ b/osfmk/arm64/m30_lowlevel_stubs.s')
patch_lines.append(f'@@ -0,0 +1,{stub_file_lines} @@')
patch_lines.append('+/*')
patch_lines.append('+ * M30LTE: assembly stub implementations for low-level board-specific')
patch_lines.append('+ * functions normally provided by Apple\'s closed per-SoC libraries.')
patch_lines.append('+ * These symbols must exist at link time; real hardware bring-up will')
patch_lines.append('+ * replace them with proper implementations.')
patch_lines.append('+ */')
patch_lines.append('+')
patch_lines.append('+.text')
patch_lines.append('+')
for line in asm_lines:
    patch_lines.append('+' + line)
patch_lines.append('+')

patch_lines.append('')
patch_lines.append('diff --git a/osfmk/conf/files.arm64 b/osfmk/conf/files.arm64')
patch_lines.append('index b0dad49..0000000 100644')
patch_lines.append('--- a/osfmk/conf/files.arm64')
patch_lines.append('+++ b/osfmk/conf/files.arm64')
patch_lines.append('@@ -43,3 +43,4 @@ osfmk/arm64/arm_vm_init.c	optional config_pmap_ppl')
patch_lines.append(' osfmk/arm64/m30_early.c	standard')
patch_lines.append('+osfmk/arm64/m30_lowlevel_stubs.s	standard')
patch_lines.append(' osfmk/arm64/arm64_hypercall.c	standard')

with open(output_file, 'w') as f:
    f.write('\n'.join(patch_lines) + '\n')

print(f'Generated stubs for {len(symbols)} symbols')
print(f'Written to {output_file}')
