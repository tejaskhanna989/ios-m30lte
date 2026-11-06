import os

content = """#ifndef _OS_FIREHOSE_BUFFER_PRIVATE_H
#define _OS_FIREHOSE_BUFFER_PRIVATE_H

#include <stdint.h>
#include <stddef.h>

#define FIREHOSE_BUFFER_KERNEL_DEFAULT_CHUNK_COUNT 16
#define FIREHOSE_BUFFER_KERNEL_DEFAULT_IO_PAGES 4
#define FIREHOSE_BUFFER_KERNEL_CHUNK_COUNT FIREHOSE_BUFFER_KERNEL_DEFAULT_CHUNK_COUNT

typedef struct firehose_tracepoint_s *firehose_tracepoint_t;
typedef struct firehose_push_reply_s firehose_push_reply_t;

boolean_t __firehose_kernel_configuration_valid(uint32_t chunk_count, uint32_t io_pages);
boolean_t __firehose_merge_updates(firehose_push_reply_t reply);
vm_offset_t __firehose_buffer_create(size_t *size);

firehose_tracepoint_t __firehose_buffer_tracepoint_reserve(uint64_t stamp, uint64_t stream, uint16_t datalen, uint32_t flags, void *context);
void __firehose_buffer_tracepoint_flush(firehose_tracepoint_t ft, firehose_tracepoint_id_u ftid);
void oslogwakeup(void);

boolean_t __firehose_buffer_tracepoint_try_reserve(uint64_t stamp, uint64_t stream, uint16_t datalen, uint32_t flags, void *context, firehose_tracepoint_t *tp_out);
void __firehose_buffer_tracepoint_commit(firehose_tracepoint_t tp);

#endif /* _OS_FIREHOSE_BUFFER_PRIVATE_H */
"""

os.makedirs('osfmk/arm64', exist_ok=True)
with open('osfmk/arm64/firehose_buffer_private.h', 'w') as f:
    f.write(content)

print("firehose_buffer_private.h created successfully")
