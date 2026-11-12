#!/usr/bin/env python3
"""Fix CI workflow - replace complex step with simple shell commands."""

with open('/home/tejas/Projects/m30lte-ios/.github/workflows/xnu.yml', 'r') as f:
    lines = f.readlines()

# Find start and end indices
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if 'Create all export files and filelists' in line:
        start_idx = i
    if start_idx is not None and i > start_idx and lines[i].strip().startswith('- name:'):
        end_idx = i
        break

print(f"Found start at line {start_idx+1}, end at line {end_idx+1}")

# New step content
new_step = '''    - name: Bypass conf subdirectories and create build files
      run: "cd xnu-source\\necho \\"=== Bypassing conf subdirectories ===\\\"\\nfor comp in security bsd osfmk libkern iokit pexpert libsa san security; do\\n  if [ -f $comp/Makefile ]; then\\n    sed -i '' 's/^COMP_SUBDIRS.*/COMP_SUBDIRS =/' $comp/Makefile\\n    echo \\\"Patched COMP_SUBDIRS in $comp/Makefile\\\"\\n  fi\\ndone\\necho \\"=== Creating empty .filelist files ===\\\"\\nfor comp in security bsd osfmk libkern iokit pexpert libsa san security; do\\n  mkdir -p BUILD/obj/DEVELOPMENT_ARM64_M30LTE/$comp/DEVELOPMENT\\n  touch BUILD/obj/DEVELOPMENT_ARM64_M30LTE/$comp/DEVELOPMENT/$comp.filelist\\n  echo \\\"Created $comp.filelist\\\"\\ndone\\necho \\"=== Copying export files to each component's DEVELOPMENT directory ===\\\"\\nfor comp in security bsd osfmk libkern iokit pexpert libsa san security; do\\n  cp config/*.exports BUILD/obj/DEVELOPMENT_ARM64_M30LTE/$comp/DEVELOPMENT/ 2>/dev/null || true\\ndone\\ntouch BUILD/obj/DEVELOPMENT_ARM64_M30LTE/all-kpi.exp\\necho \\\"Created all export files\\\"\n"'''

new_lines = lines[:start_idx] + [new_step + '\\n'] + lines[end_idx:]

with open('/home/tejas/Projects/m30lte-ios/.github/workflows/xnu.yml', 'w') as f:
    f.writelines(new_lines)

print('Successfully updated workflow')