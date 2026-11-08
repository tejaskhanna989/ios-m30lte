#!/usr/bin/env python3
"""Patch SETUP/config/Makefile to skip building if tools already exist."""
import sys

with open('SETUP/config/Makefile', 'r') as f:
    content = f.read()

# Find the do_build_setup target and add a check to skip if config exists
old_target = '''do_build_setup:: config

include $(MakeInc_rule)'''

new_target = '''do_build_setup:: config
	@if [ -f config ] && [ config -nt externs.c ] && [ config -nt main.c ] && [ config -nt mkheaders.c ] && [ config -nt mkioconf.c ] && [ config -nt mkmakefile.c ] && [ config -nt openp.c ] && [ config -nt searchp.c ] && [ config -nt lexer.l ] && [ config -nt parser.y ]; then \
		echo "SETUP tools already up to date, skipping build"; \
	else \
		$(MAKE) config; \
	fi

include $(MakeInc_rule)'''

if old_target in content:
    content = content.replace(old_target, new_target)
    with open('SETUP/config/Makefile', 'w') as f:
        f.write(content)
    print("Patched SETUP/config/Makefile to skip build if tools exist")
else:
    print("ERROR: Could not find do_build_setup target to patch")
    # Try alternative pattern
    alt_target = 'do_build_setup:: config'
    if alt_target in content:
        print("Found alternative pattern, trying different replacement")
        # Find the line after do_build_setup:: config
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip() == 'do_build_setup:: config':
                # Insert after this line
                indent = '	'
                new_lines = lines[:i+1] + [
                    f'{indent}@if [ -f config ] && [ config -nt externs.c ] && [ config -nt main.c ] && [ config -nt mkheaders.c ] && [ config -nt mkioconf.c ] && [ config -nt mkmakefile.c ] && [ config -nt openp.c ] && [ config -nt searchp.c ] && [ config -nt lexer.l ] && [ config -nt parser.y ]; then \\',
                    f'{indent}	echo "SETUP tools already up to date, skipping build"; \\',
                    f'{indent}else \\',
                    f'{indent}	$(MAKE) config; \\',
                    f'{indent}fi'
                ] + lines[i+1:]
                content = '\n'.join(new_lines)
                with open('SETUP/config/Makefile', 'w') as f:
                    f.write(content)
                print("Patched with alternative method")
                break
        else:
            print("ERROR: Could not find do_build_setup target")
            sys.exit(1)

print("Patched SETUP/config/Makefile to skip build if tools exist")