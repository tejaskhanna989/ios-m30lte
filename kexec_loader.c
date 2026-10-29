/* kexec-hardboot loader: load M30LTXNU payload from Android via kexec syscall */
#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <linux/reboot.h>

#ifndef SYS_kexec_load
#define SYS_kexec_load 104  /* try common variants */
#endif

struct kexec_segment {
    unsigned long buf, bufsz, mem, memsz;
};

struct payload_hdr {
    char magic[8];
    uint32_t version, nsegs;
    uint64_t virt_base, entry_va, adt_off, adt_size, kernel_end;
    uint64_t phys_base, mem_size;
    char cmdline[608];
};

struct payload_seg {
    uint64_t vmaddr, vmsize, file_off, file_size;
};

int main(void) {
    const char *path = "/data/local/tmp/payload.bin";
    int fd = syscall(SYS_openat, AT_FDCWD, path, O_RDONLY, 0);
    if (fd < 0) { perror("openat"); return 1; }

    struct payload_hdr hdr;
    ssize_t nr = read(fd, &hdr, sizeof(hdr));
    if (nr != sizeof(hdr)) { printf("short read: %zd\n", nr); return 1; }

    printf("magic: %.8s version=%u nsegs=%u\n", hdr.magic, hdr.version, hdr.nsegs);
    printf("virt_base=0x%lx entry_va=0x%lx\n", hdr.virt_base, hdr.entry_va);
    printf("phys_base=0x%lx mem_size=0x%lx kernel_end=0x%lx\n",
           hdr.phys_base, hdr.mem_size, hdr.kernel_end);

    off_t fsize = lseek(fd, 0, SEEK_END);
    lseek(fd, 0, SEEK_SET);
    void *file_buf = mmap(NULL, fsize, PROT_READ, MAP_PRIVATE, fd, 0);
    if (file_buf == MAP_FAILED) { perror("mmap"); return 1; }

    struct kexec_segment *segs = calloc(hdr.nsegs, sizeof(struct kexec_segment));
    char *base = (char *)file_buf;
    for (uint32_t i = 0; i < hdr.nsegs; i++) {
        struct payload_seg *ps = (struct payload_seg *)(base + 0x2a8 + 32 * i);
        segs[i].buf = (unsigned long)(base + ps->file_off);
        segs[i].bufsz = ps->file_size;
        segs[i].mem = ps->vmaddr;
        segs[i].memsz = ps->vmsize;
        printf("seg %d: mem=0x%lx memsz=0x%lx bufsz=0x%lx\n",
               i, segs[i].mem, segs[i].memsz, segs[i].bufsz);
    }

    /* kexec_load(nr_segments, segments, flags) - flags 0 */
    long ret = syscall(SYS_kexec_load, (long)hdr.nsegs, (long)segs, 0L);
    printf("kexec_load returned: %ld\n", ret);
    if (ret != 0) { perror("kexec_load"); return 1; }

    printf("Calling kexec reboot...\n");
    syscall(SYS_reboot, LINUX_REBOOT_CMD_KEXEC, 0, 0, 0);
    printf("kexec reboot returned (should not happen)\n");
    return 0;
}
