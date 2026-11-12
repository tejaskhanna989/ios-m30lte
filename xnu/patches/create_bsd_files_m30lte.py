#!/usr/bin/env python3
"""Create bsd/conf/files.m30lte for M30LTE machine config."""
import os
import shutil

# Check if files.m30lte already exists
if os.path.exists('bsd/conf/files.m30lte'):
    print("bsd/conf/files.m30lte already exists")
    exit(0)

# Try to copy from an existing ARM64 machine config
source_files = [
    'bsd/conf/files.t8000',
    'bsd/conf/files.t8001',
    'bsd/conf/files.t8003',
    'bsd/conf/files.t8010',
    'bsd/conf/files.t8015',
    'bsd/conf/files.t8020',
    'bsd/conf/files.t8021',
    'bsd/conf/files.t8030',
    'bsd/conf/files.t8100',
    'bsd/conf/files.t8101',
    'bsd/conf/files.t8103',
    'bsd/conf/files.t8110',
    'bsd/conf/files.t8112',
]

source_file = None
for f in source_files:
    if os.path.exists(f):
        source_file = f
        break

if source_file:
    print(f"Copying {source_file} to bsd/conf/files.m30lte")
    shutil.copy2(source_file, 'bsd/conf/files.m30lte')
else:
    # Create a minimal files.m30lte based on common ARM64 config
    print("No existing files.m30lte source found, creating minimal one")
    content = """# M30LTE machine config - Samsung Galaxy M30 SM-M305F (Exynos 7904)
# Based on ARM64 iPhone config

# Standard BSD files
sys/kern/uipc_domain.c
sys/kern/uipc_mbuf.c
sys/kern/uipc_mbuf2.c
sys/kern/uipc_socket.c
sys/kern/uipc_socket2.c
sys/kern/uipc_usrreq.c
sys/kern/uipc_syscalls.c

# Network
sys/net/if.c
sys/net/if_dl.c
sys/net/if_types.c
sys/net/if_var.h
sys/net/if_media.c
sys/net/if_llc.c
sys/net/if_ethersubr.c
sys/net/raw_cb.c
sys/net/route.c
sys/net/rtsock.c

# INET
sys/netinet/in.c
sys/netinet/in_pcb.c
sys/netinet/in_proto.c
sys/netinet/in_var.h
sys/netinet/ip_input.c
sys/netinet/ip_output.c
sys/netinet/ip_icmp.c
sys/netinet/tcp_input.c
sys/netinet/tcp_output.c
sys/netinet/tcp_subr.c
sys/netinet/tcp_timer.c
sys/netinet/tcp_var.h
sys/netinet/udp_usrreq.c

# Filesystems
sys/fs/vfs_vnops.c
sys/fs/vfs_cache.c
sys/fs/vfs_export.c
sys/fs/vfs_subr.c
sys/fs/vfs_init.c
sys/fs/devfs/devfs_vnops.c
sys/fs/devfs/devfs_subr.c

# ARM64 specific
sys/arm64/arm64/machdep.c
sys/arm64/arm64/pmap.c
sys/arm64/arm64/arm64_mem.c
sys/arm64/arm64/locore.s
sys/arm64/arm64/atc.s

# M30LTE specific - Exynos 7904
sys/arm64/arm64/m30lte/board_config.c
"""
    with open('bsd/conf/files.m30lte', 'w') as f:
        f.write(content)

print("Created bsd/conf/files.m30lte")
