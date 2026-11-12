#!/usr/bin/env python3
"""Fix copy all export files step - copy to each component's DEVELOPMENT directory."""
with open('/home/tejas/Projects/m30lte-ios/xnu/patches/patch_all_conf_makefiles.py', 'r') as f:
    content = f.read()

old = 'cfiles, cxxfiles, sfiles = parse_cfiles_from_makefile(os.path.join(conf_dir, "Makefile"))'
new = 'cfiles = parse_cfiles_from_makefile(os.path.join(conf_dir, "Makefile"))'

if old in content:
    content = content.replace(old, new, 1)
    with open('/home/tejas/Projects/m30lte-ios/xnu/patches/patch_all_conf_makefiles.py', 'w') as f:
        f.write(content)
    print('Fixed!')
else:
    print('Could not find old string')
    print('Looking for:', repr(old))
