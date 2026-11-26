# v68t-uihb first physical boot — read-only pstore

Identity PASS (SM-M305F / m30lte / M305FDDU8CVK1 / known serial / TWRP).
Pstore SHA256 da143fcaee76ca67598405e4b816318afb60c32e981cb71133b7cfc63b39d32d,
16372 bytes, 150 records, clean=False.

Only framebuffer heartbeat records survive: 150 `M30 FB: v=` records from
v=525600 to v=615000, `sw=3 pr=3 copied=3032 cl=1`. No `M30 UI HB`, no
`M30 UI`, no `M30 IRT`, no `SWEET AKS`, no `SWEET FB`, no `M30 TOUCH`, no
NSException records in the surviving window.

This means the 1 Hz heartbeat was not observed in the last ~90 s of pstore.
It cannot distinguish "heartbeat never started" from "wrapped out". A check of
the persistent console ring in USERDATA was attempted but the device was not
connected at that moment; retry requires reconnecting in TWRP (read-only).

No flash, reboot or partition write was performed for this analysis.
