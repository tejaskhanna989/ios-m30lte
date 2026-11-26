# v78 UI-exact touch BOOT candidate (BOOT-only; USERDATA unchanged)

Source change: `.github/workflows/xnu.yml` gained a `ui_exact=true` switch that
excludes post-v68 diagnostic patches 0453/0454/0455 from the kernel build. The
resulting kernel has the exact v68 framebuffer/UI patch chain (0442-0445) plus
Melfas touch 0451, with no UI heartbeat or lockscreen sampler compiled in
(verified: 0 diagnostic strings). Touch stays enabled by boot args only.

- Kernel SHA256: a6a64f7b19a845ec021d1c33602781e3043aaef15349d82f79137bede33d7a5a
- Payload SHA256: 1485e30e2a3676e016d43c02982e9b9bd22b05af52381ab45da66e37c8e013f4
- BOOT SHA256: 48e45bf786769b5f3da47aafc3b428f29eaa5892bc01656c84af93f0d2883aba
- Cmdline: exact v68 + a5fb_noconsole=1 a5fb_keep_on=1 m30touch=1 m30touchhid=1

USERDATA is unchanged: the v75 image stays in place with the v73 lsd/MCM fix
and SpringBoard container registration. No flash without explicit approval.
