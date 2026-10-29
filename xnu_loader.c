/*
 * xnu_loader.c - Kernel module to load M30LTXNU payload and jump to XNU
 * Runs from within Android/TWRP kernel, bypassing ABL signature verification.
 */
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/uaccess.h>
#include <linux/mm.h>
#include <linux/slab.h>
#include <linux/dma-mapping.h>
#include <linux/vmalloc.h>
#include <asm/pgtable.h>
#include <asm/system.h>
#include <asm/barrier.h>
#include <asm/cpufeature.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("m30lte-ios");
MODULE_DESCRIPTION("Load XNU kernel from Android via kexec-hardboot module");

struct payload_hdr {
    char magic[8];
    uint32_t version, nsegs;
    uint64_t virt_base, entry_va, adt_off, adt_size, kernel_end;
    uint64_t phys_base, mem_size;
    char cmdline[608];
} __attribute__((packed));

struct payload_seg {
    uint64_t vmaddr, vmsize, file_off, file_size;
} __attribute__((packed));

static void __attribute__((noreturn)) jump_to_xnu(void *entry)
{
    unsigned long sctlr;

    /* Disable interrupts */
    local_irq_disable();
    local_fiq_disable();

    /* Read SCTLR_EL1 */
    asm volatile ("mrs %0, sctlr_el1" : "=r" (sctlr));

    /* Disable MMU (clear M bit), keep I-cache */
    sctlr &= ~(1UL << 0);  /* M = 0 */
    sctlr &= ~(1UL << 2);  /* C = 0 (disable data cache) */
    sctlr &= ~(1UL << 12); /* I = 0 (disable instruction cache) */
    sctlr &= ~(1UL << 11); /* SPAN = 0 */

    asm volatile ("msr sctlr_el1, %0" : : "r" (sctlr));
    asm volatile ("isb");

    /* Jump to XNU entry point */
    asm volatile ("br %0" : : "r" (entry));

    /* Should never reach here */
    while (1) {
        asm volatile ("wfe");
    }
}

static int __init xnu_loader_init(void)
{
    struct file *f;
    mm_segment_t oldfs;
    struct payload_hdr hdr;
    struct payload_seg *segs = NULL;
    char *file_buf = NULL;
    loff_t pos = 0;
    ssize_t nr;
    int i;
    void *entry = NULL;

    printk(KERN_INFO "=== XNU Loader: Starting ===\n");

    oldfs = get_fs();
    set_fs(KERNEL_DS);

    f = filp_open("/data/local/tmp/payload.bin", O_RDONLY, 0);
    if (IS_ERR(f)) {
        printk(KERN_ERR "XNU Loader: Failed to open payload.bin\n");
        set_fs(oldfs);
        return -1;
    }

    nr = kernel_read(f, 0, (char *)&hdr, sizeof(hdr), &pos);
    if (nr != sizeof(hdr)) {
        printk(KERN_ERR "XNU Loader: Failed to read header (%zd)\n", nr);
        filp_close(f, NULL);
        set_fs(oldfs);
        return -1;
    }

    printk(KERN_INFO "XNU Loader: magic=%.8s version=%u nsegs=%u\n",
           hdr.magic, hdr.version, hdr.nsegs);
    printk(KERN_INFO "XNU Loader: virt_base=0x%llx entry_va=0x%llx\n",
           hdr.virt_base, hdr.entry_va);
    printk(KERN_INFO "XNU Loader: phys_base=0x%llx mem_size=0x%llx\n",
           hdr.phys_base, hdr.mem_size);

    if (memcmp(hdr.magic, "M30LTXNU", 8) != 0) {
        printk(KERN_ERR "XNU Loader: Invalid magic\n");
        filp_close(f, NULL);
        set_fs(oldfs);
        return -1;
    }

    segs = kmalloc_array(hdr.nsegs, sizeof(struct payload_seg), GFP_KERNEL);
    if (!segs) {
        printk(KERN_ERR "XNU Loader: Failed to allocate seg array\n");
        filp_close(f, NULL);
        set_fs(oldfs);
        return -1;
    }

    pos = 0x2a8;
    for (i = 0; i < hdr.nsegs; i++) {
        nr = kernel_read(f, pos, (char *)(segs + i), sizeof(struct payload_seg), &pos);
        if (nr != sizeof(struct payload_seg)) {
            printk(KERN_ERR "XNU Loader: Failed to read seg %d\n", i);
            break;
        }
        printk(KERN_INFO "XNU Loader: seg %d: vmaddr=0x%llx vmsize=0x%llx file_off=0x%llx file_size=0x%llx\n",
               i, segs[i].vmaddr, segs[i].vmsize, segs[i].file_off, segs[i].file_size);
    }

    /* Read entire file into vmalloc buffer */
    pos = 0;
    file_buf = vmalloc(hdr.mem_size);
    if (!file_buf) {
        printk(KERN_ERR "XNU Loader: Failed to vmalloc file buffer\n");
        kfree(segs);
        filp_close(f, NULL);
        set_fs(oldfs);
        return -1;
    }

    nr = kernel_read(f, 0, file_buf, hdr.mem_size, &pos);
    printk(KERN_INFO "XNU Loader: Read %zd bytes into file buffer\n", nr);

    /* Copy segments to their target addresses using identity mapping */
    /* The kernel's direct map covers physical memory at PAGE_OFFSET */
    for (i = 0; i < hdr.nsegs; i++) {
        char *src = file_buf + segs[i].file_off;
        /* Target address: use virt_base offset + segment vmaddr offset */
        /* XNU segments are at virtual addresses, we need to map them */
        /* For now, just copy to physical address based on phys_base */
        unsigned long phys_dest = hdr.phys_base + (segs[i].vmaddr - hdr.virt_base);
        char *dest = (char *)phys_to_virt(phys_dest);
        unsigned long j;

        printk(KERN_INFO "XNU Loader: Copying seg %d to phys 0x%lx\n", i, phys_dest);

        for (j = 0; j < segs[i].file_size; j++) {
            dest[j] = src[j];
        }
    }

    entry = (void *)hdr.entry_va;
    printk(KERN_INFO "XNU Loader: Jumping to entry 0x%llx\n", hdr.entry_va);

    vfree(file_buf);
    kfree(segs);
    filp_close(f, NULL);
    set_fs(oldfs);

    jump_to_xnu(entry);

    /* Never returns */
    return 0;
}

static void __exit xnu_loader_exit(void)
{
    printk(KERN_INFO "XNU Loader: Module exit (should not reach)\n");
}

module_init(xnu_loader_init);
module_exit(xnu_loader_exit);
