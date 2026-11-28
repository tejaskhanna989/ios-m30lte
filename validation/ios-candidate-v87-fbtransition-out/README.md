# v87 flashable candidate — bounded framebuffer transition logger

CI run 46138443689 GREEN on commit be64f10e. Same cmdline as accepted v68.
Kernel `9258c524ad258bae5e1fca8855d3c40aa7e192c2e5ad8f3100703c47a9cb42fa`,
payload `cb7c1a58481ba002de61c1a4a58fcd69b015ae91396cb4059460db402cbe1107`,
BOOT `75b4318eed0f18d943a144a2f688732cf6a72eed7a8668dc59d428f16fce583e`.
Patch 0457 logs framebuffer STATE TRANSITIONS only (bounded 3 KiB budget,
40-line cap, 60 s heartbeat, boot arg m30fbtbudget). No functional display
change, no touch boot args, USERDATA untouched.
V68 comparison: same shim/ADT/cmdline; only XNU source differs (0457 plus
diagnostic patches already present in the v68-era baseline).
