# Diagnostic candidate v68t-uihb

CI `45679768064` GREEN (0451 Melfas + 0453 UI heartbeat gates PASS).
Cmdline = exact v68 + m30touch=1 + m30touchhid=1 + m30uihb=1.

- Kernel SHA256: 15be91377f7350a82e06e09c690d9aae36dd8bd10e006c62b5e4b8a0e34808c9
- Payload SHA256: ab84d3233880cfe515f123a6e86966ec599b3fcd81127d96160999ad92a985e5
- BOOT image SHA256: 6611ba722e5661453fc9e618ae6393e321d0eb65d8f88fd119825b73ad8c645b
- Structural PASS; handoff verifier includes m30uihb=1 and heartbeat string.
- USERDATA unchanged; BOOT-only physical test authorized by user.
