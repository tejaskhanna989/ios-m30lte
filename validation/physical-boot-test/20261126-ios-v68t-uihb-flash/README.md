# v68t-uihb BOOT-only flash

- Image SHA256 gate PASS: 6611ba722e5661453fc9e618ae6393e321d0eb65d8f88fd119825b73ad8c645b
- Identity gate PASS: SM-M305F / m30lte / M305FDDU8CVK1 / known serial / TWRP
- Download Mode detect PASS; `heimdall flash --BOOT <image> --no-reboot`, exit 0.
- No USERDATA/SYSTEM/RECOVERY write, no Fastboot, no backup change.
- No reboot/resume performed; device left in Download Mode.
