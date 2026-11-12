#!/usr/bin/env python3
"""Single comprehensive patch to fix XNU build issues:
1. Patch all component Makefiles to bypass conf subdirectory builds
2. Copy all export files to build directory
3. Create empty .filelist and all-kpi.exp files
"""
import os
import shutil
import re

components = [
    'security', 'bsd', 'osfmk', 'libkern', 'iokit', 'pexpert', 'libsa', 'san'
]


def parse_cfiles_from_makefile(makefile_path):
    """Parse CFILES from component Makefile."""
    if not os.path.exists(makefile_path):
        return []
    with open(makefile_path, 'r') as f:
        content = f.read()
    match = re.search(r'CFILES\s*=\s*\\', content)
    if not match:
        return []
    remaining = content[match.end():]
    cfiles = re.findall(r'(\S+\.c)', remaining)
    return cfiles


def patch_component_makefile(component_dir):
    """Patch component Makefile to bypass conf subdirectory builds."""
    makefile_path = os.path.join(component_dir, 'Makefile')
    if not os.path.exists(makefile_path):
        print(f"WARNING: {makefile_path} not found")
        return False

    with open(makefile_path, 'r') as f:
        content = f.read()

    if '# M30LTE: conf bypassed' in content:
        print(f"  Already patched {makefile_path}")
        return True

    cfiles = parse_cfiles_from_makefile(makefile_path)
    objs = [f.replace('.c', '.o') for f in cfiles]

    bypass_lines = []
    bypass_lines.append("")
    bypass_lines.append("# M30LTE: bypass conf subdirectory")
    bypass_lines.append("COMP_SUBDIRS =")
    bypass_lines.append("")

    if objs:
        bypass_lines.append("OBJS = \\")
        for obj in objs:
            bypass_lines.append("\t" + obj + " \\")
        bypass_lines[-1] = bypass_lines[-1].rstrip(" \\")
    else:
        bypass_lines.append("OBJS =")
    bypass_lines.append("")

    if cfiles:
        bypass_lines.append("CFILES = \\")
        for cf in cfiles:
            bypass_lines.append("\t" + cf + " \\")
        bypass_lines[-1] = bypass_lines[-1].rstrip(" \\")
    else:
        bypass_lines.append("CFILES =")
    bypass_lines.append("")

    bypass_lines.append("")
    bypass_lines.append("$(COBJS): .CFLAGS")
    bypass_lines.append(".CFLAGS: ALWAYS")
    bypass_lines.append("\t$(_v)$(REPLACECONTENTS) $@ $(KCC) $(CFLAGS) $(INCFLAGS)")
    bypass_lines.append("")
    bypass_lines.append("$(OBJS): $(firstword $(MAKEFILE_LIST))")
    bypass_lines.append("")
    bypass_lines.append("$(COMPONENT).filelist: $(OBJS)")
    bypass_lines.append("\t@$(LOG_LDFILELIST) \"$(COMPONENT)\"")
    bypass_lines.append("\t$(_v)for obj in ${OBJS}; do \\")
    bypass_lines.append("\t\t $(ECHO) $(TARGET)/$(CURRENT_KERNEL_CONFIG)/$${obj}; \\")
    bypass_lines.append("\tdone > $(COMPONENT).filelist")
    bypass_lines.append("")
    bypass_lines.append("$(COMPONENT).libfilelist:")
    bypass_lines.append("\t@$(LOG_LDFILELIST) \"lib$(COMPONENT)\"")
    bypass_lines.append("\t$(_v)touch $(COMPONENT).libfilelist")
    bypass_lines.append("")

    comp_pattern = re.compile(r'COMP_SUBDIRS\s*=.*\n(?:\s+.*\n)*')
    content = comp_pattern.sub('COMP_SUBDIRS =\n', content, 1)

    include_marker = 'include $(MakeInc_rule)'
    if include_marker in content:
        content = content.replace(include_marker, '\n'.join(bypass_lines) + '\n' + include_marker, 1)
    else:
        content = content.rstrip() + '\n' + '\n'.join(bypass_lines) + '\n'

    with open(makefile_path, 'w') as f:
        f.write(content)
    print(f"  Patched {makefile_path}")
    return True


def main():
    for component in components:
        print(f"\nProcessing {component}/...")
        makefile_path = os.path.join(component, 'Makefile')
        patch_component_makefile(makefile_path)

    build_dir = "BUILD/obj/DEVELOPMENT_ARM64_M30LTE"
    for comp in components:
        fl_path = os.path.join(build_dir, comp, 'DEVELOPMENT', f'{comp}.filelist')
        os.makedirs(os.path.dirname(fl_path), exist_ok=True)
        with open(fl_path, 'w') as f:
            f.write("")
        print(f"  Created {fl_path}")

    build_cfg = os.path.join("BUILD", "obj", "DEVELOPMENT_ARM64_M30LTE", "config")
    os.makedirs(build_cfg, exist_ok=True)
    if os.path.exists("config"):
        for f in os.listdir("config"):
            if f.endswith('.exports'):
                shutil.copy2(os.path.join("config", f), os.path.join(build_cfg, f))
                print(f"  Copied config/{f}")

    ak_path = os.path.join("BUILD", "obj", "DEVELOPMENT_ARM64_M30LTE", "all-kpi.exp")
    open(ak_path, 'w').close()
    print(f"  Created {ak_path}")

    print("\nDone")


if __name__ == '__main__':
    main()