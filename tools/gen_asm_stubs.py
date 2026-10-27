#!/usr/bin/env python3
"""Generate assembly stub patch for all undefined M30LTE kernel symbols."""

import sys

symbols_file = '/tmp/undefined_symbols.txt'
output_file = '/home/tejas/Projects/m30lte-ios/xnu/patches/0082-m30lte-lowlevel-stubs.patch'

with open(symbols_file) as f:
    symbols = [line.strip() for line in f if line.strip()]

# Generate assembly stubs - use .globl with leading underscore (macOS convention)
asm_lines = []
for sym in symbols:
    # sym already has leading underscore (e.g., _set_mmu_ttb)
    asm_lines.append(f'.globl {sym}')
    asm_lines.append(f'{sym}:')
    asm_lines.append('    ret')

# Count lines in the stub file
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
patch_lines.append('index 0000000..0000000')
patch_lines.append('--- /dev/null')
patch_lines.append('+++ b/osfmk/conf/files.arm64')
patch_lines.append('@@ -0,0 +1 @@')
patch_lines.append('+arm64/m30_lowlevel_stubs.s\tstandard')

with open(output_file, 'w') as f:
    f.write('\n'.join(patch_lines) + '\n')

print(f'Generated stubs for {len(symbols)} symbols')
print(f'Written to {output_file}')
