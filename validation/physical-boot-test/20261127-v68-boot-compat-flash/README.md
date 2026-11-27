BOOT-only compatibility experiment — 2026-11-27 (NOT an exact v68 reproduction)

Explicitly authorized. Device: m30lte / M305FDDU8CVK1 / serial 320081735bb166a3.
Artifact validation/ios-candidate-v68-out/ios-boot.img SHA256
629843b597fd665b7de6b6578a1605455ef5786ae9e06101b591d13a80bf8c50 — matches
the original v68 physical flash record. Original BOOT backup 469c12d2... intact.
BOOT -> /dev/block/mmcblk0p12 only. No Fastboot, no USERDATA/SYSTEM/RECOVERY write.

heimdall flash --BOOT ... --no-reboot: "BOOT upload successful" at
2026-11-27T18:22:01Z. Device left in Download Mode; NO reboot performed.

Current USERDATA is v79 (4f788a12...), NOT the original 5f2e2aa6... — hence a
compatibility experiment. Resume only on explicit instruction; observe >=15 min;
success requires a visibly rendered native lockscreen.
