#!/bin/bash
# M30LTE: add symbols that are exported by the kernel but missing from
# the arm64 export list (needed for check_all_exports to pass).
# This runs from ${WORK_DIR}/xnu/ (cd'd by build.sh before running scripts).
printf '_pmap_claim_reserved_ppl_page\n_pmap_free_reserved_ppl_page\n_pmap_iofilter_protected_write\n_pmap_lookup_in_loaded_trust_caches\n_pmap_lookup_in_static_trust_cache\n_Switch_context\n' >> config/Private.arm64.exports
