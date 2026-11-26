# v68t-sweetsample diagnostic BOOT flash + automatic resume

All gates PASS:
- exact SM-M305F / m30lte / M305FDDU8CVK1 / known serial / TWRP identity
- original BOOT backup intact 469c12d2d304ff4b2f07ea89ff1bc329a77f8f73037420aa260c9e68db441e78
- candidate BOOT SHA256 2dbd2ffaf3112b132278244b5d35dc256320fb0775427f173439ff4fa714b7d2
- Download Mode detected immediately before write
- BOOT target mapped to p12; USERDATA/SYSTEM/RECOVERY untouched

`heimdall flash --BOOT <image> --no-reboot`: exit 0.
`heimdall print-pit --resume`: exit 0, device rebooted (explicitly authorized).
No Fastboot; no backup overwrite.
