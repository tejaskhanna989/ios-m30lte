# v68t-native BOOT-only physical test

All mandatory gates PASS:
- identity SM-M305F / m30lte / M305FDDU8CVK1 / known serial / TWRP
- candidate BOOT SHA256 9c022561c09b53de1ab613b4ca37fb42acd4aaa7899302138c35bdd8298cbe26
- original BOOT backup intact 469c12d2d304ff4b2f07ea89ff1bc329a77f8f73037420aa260c9e68db441e78
- Download Mode detected immediately before write
- target mapping confirmed: BOOT=p12, USERDATA=p28, SYSTEM=p20, RECOVERY=p13

`heimdall flash --BOOT <image> --no-reboot`: exit 0, BOOT upload successful.
No Fastboot, no USERDATA/SYSTEM/RECOVERY write, no backup overwrite.
No reboot/resume performed; device left in Download Mode.
