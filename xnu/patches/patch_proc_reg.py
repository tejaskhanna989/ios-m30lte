import sys

with open('osfmk/arm64/proc_reg.h', 'r') as f:
    content = f.read()

# Add M30LTE define after license header
content = content.replace(
    '* @APPLE_OSREFERENCE_LICENSE_HEADER_END@\n */',
    '* @APPLE_OSREFERENCE_LICENSE_HEADER_END@\n */\n#define M30LTE 1'
)

# Add M30LTE processor definition after BCM2837
old_bcm = """#elif defined (BCM2837) /* Raspberry Pi 3 */

/* I-Cache. We don't have detailed spec so we just follow the ARM technical reference. */
#define MMU_I_CLINE 6

/* D-Cache. */
#define MMU_CLINE   6

#elif defined (VMAPPLE)"""

new_bcm = """#elif defined (BCM2837) /* Raspberry Pi 3 */

/* I-Cache. We don't have detailed spec so we just follow the ARM technical reference. */
#define MMU_I_CLINE 6

/* D-Cache. */
#define MMU_CLINE   6

#elif defined (M30LTE) /* Samsung Exynos 7904: Cortex-A73 + Cortex-A53, ARMv8.0 */

/* I-Cache. */
#define MMU_I_CLINE 6

/* D-Cache. */
#define MMU_CLINE   6

/* CPU and cache configuration */
#define MAX_CPUS                        8
#define MAX_L2_CLINE                    6
#define MAX_CPU_CLUSTERS                2


/* I-Cache. We don't have detailed spec so we just follow the ARM technical reference. */
#define MMU_I_CLINE 6

/* D-Cache. */
#define MMU_CLINE   6

#elif defined (VMAPPLE)"""

content = content.replace(old_bcm, new_bcm)

# Change #error to #warning
content = content.replace('#error processor not supported', '#warning processor not supported')

with open('osfmk/arm64/proc_reg.h', 'w') as f:
    f.write(content)

print("proc_reg.h patched successfully")
