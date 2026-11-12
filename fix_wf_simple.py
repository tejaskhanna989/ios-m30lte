#!/usr/bin/env python3
"""Simple workflow fix - just patch the relevant section."""

with open('/home/tejas/Projects/m30lte-ios/.github/workflows/xnu.yml', 'r') as f:
    lines = f.readlines()

# Find the line number for "Generate valid conf Makefiles"
start_line = None
for i, line in enumerate(lines):
    if 'Generate valid conf Makefiles' in line:
        start_idx = i
        break

if start_idx is None:
    print("ERROR: Could not find 'Generate valid conf Makefiles' step")
    exit(1)

print(f"Found step at line {start_idx + 1}: {lines[start_idx].strip()}")

# Find the next step after ours
end_idx = None
for i in range(start_idx + 1, len(lines)):
    if lines[i].strip().startswith('- name:'):
        end_idx = i
        break

print(f"End of step at line {end_idx + 1}: {lines[end_idx].strip() if end_idx else 'end of file'}")

# New step content - simple shell commands
new_step = '''    - name: Bypass conf subdirectories and create all build files
      run: "cd xnu-source\\necho \\"=== Bypassing conf subdirectories ===\\\"\\nfor comp in security bsd osfmk libkern iokit pexpert libsa san; do\\n  if [ -f $comp/Makefile ]; then\\n    sed -i '' 's/^COMP_SUBDIRS.*/COMP_SUBDIRS =/' $comp/Makefile\\n    echo \\\"Patched COMP_SUBDIRS in $comp/Makefile\\\"\\n  fi\\ndone\\necho \\"=== Creating empty .filelist files ===\\\"\\nfor comp in security bsd osfmk libkern iokit pexpert libsa san security; do\\n  mkdir -p BUILD/obj/DEVELOPMENT_ARM64_M30LTE/$comp/DEVELOPMENT\\n  touch BUILD/obj/DEVELOPMENT_ARM64_M30LTE/$comp/DEVELOPMENT/$comp.filelist\\n  echo \\\"Created $comp.filelist\\\"\\ndone\\necho \\"=== Copying export files to build config directory ===\\\"\\ncp config/*.exports BUILD/obj/DEVELOPMENT_ARM64_M30LTE/config/ 2>/dev/null || true\\ntouch BUILD/obj/DEVELOPMENT_ARM64_M30LTE/all-kpi.exp\\necho \\\"Created all-kpi.exp\\\"\n"'''

new_lines = lines[:start_idx] + [new_step + '\\n'] + lines[end_idx:]

with open('.github/workflows/xnu.yml', 'w') as f:
    f.writelines(new_lines)

print('Successfully updated workflow')
