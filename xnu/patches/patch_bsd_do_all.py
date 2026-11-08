#!/usr/bin/env python3
"""Patch bsd/Makefile do_all target to propagate SRCROOT and SETUP to sub-makes."""
import sys
import re

with open('bsd/Makefile', 'r') as f:
    content = f.read()

# Find all targets in the Makefile
targets = re.findall(r'^([a-zA-Z0-9_]+):', content, re.MULTILINE)
print("=== All targets in Makefile ===")
for t in targets:
    print(f"  {t}")

# Find the do_all target (it might be do_all or do_all:)
do_all_match = re.search(r'^do_all[:\s]', content, re.MULTILINE)
if not do_all_match:
    print("No do_all target found!")
    sys.exit(1)

# Find the do_all target section
do_all_start = content.find('do_all:')
if do_all_start == -1:
    do_all_start = content.find('do_all :')
if do_all_start == -1:
    print("Could not find do_all target")
    sys.exit(1)

print(f"Found do_all at position {do_all_start}")

# Find the do_all target body - look for the sub-make invocation
# The do_all target typically has a sub-make invocation with OBJPATH
# Let's search for the pattern more broadly

# Find OBJPATH in the context of do_all
objpath_matches = list(re.finditer(r'OBJPATH\s*=', content))
print(f"Found {len(objpath_matches)} OBJPATH occurrences:")
for m in objpath_matches:
    start = max(0, m.start() - 200)
    end = min(len(content), m.end() + 200)
    print(f"  At {m.start()}: ...{content[start:end]}...")

# Use a more robust approach: find the do_all target and its body
# The do_all target typically looks like:
# do_all: $(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile
# 	$(_v)${MAKE} \
# 		-C $(TARGET)/$(CURRENT_KERNEL_CONFIG)			\
# 		-f $(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile		\
# 		...
# 		OBJPATH=${OBJPATH}					\
# 		build_all

# Let's use a more flexible regex to find the do_all target and its body
pattern = re.compile(
    r'(do_all\s*:\s*\$\(TARGET\)/\$\(CURRENT_KERNEL_CONFIG\)/Makefile\s*\n'
    r'(?:\s.*?\\\n)*'
    r'\s+OBJPATH\s*=\s*\$\{OBJPATH\}\s*\\\n'
    r'(?:\s.*?\\\n)*'
    r'\s+build_all)',
    re.MULTILINE | re.DOTALL
)

match = pattern.search(content)
if match:
    print("Found do_all target with OBJPATH")
    # Insert SRCROOT and SETUP after OBJPATH line
    start = match.start()
    end = match.end()
    matched_text = match.group(0)
    
    # Insert after OBJPATH line
    new_text = re.sub(
        r'(OBJPATH\s*=\s*\$\{OBJPATH\}\s*\\\\\n)',
        r'\1SRCROOT=${SRCROOT}					\\\\nSETUP=${SRCROOT}/SETUP					\\\\n',
        matched_text
    )
    
    new_content = content[:start] + new_text + content[end:]
    
    with open('bsd/Makefile', 'w') as f:
        f.write(new_content)
    print("Patched bsd/Makefile successfully!")
else:
    print("Could not find do_all target with OBJPATH pattern!")
    # Debug: print the do_all area
    idx = content.find('do_all')
    if idx >= 0:
        print(content[idx:idx+1000])
    sys.exit(1)

# Verify the patch
with open('bsd/Makefile', 'r') as f:
    content = f.read()

if 'SRCROOT=${SRCROOT}' in content and 'SETUP=${SRCROOT}/SETUP' in content:
    print("Patched bsd/Makefile successfully!")
    idx = content.find('do_all')
    if idx >= 0:
        print("=== Patched do_all target ===")
        print(content[idx:idx+800])
else:
    print("WARNING: SRCROOT/SETUP not found in patched content")
    idx = content.find('do_all')
    if idx >= 0:
        print(content[idx:idx+800])
    sys.exit(1)