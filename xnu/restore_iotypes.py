#!/usr/bin/env python3
import os

def restore_file(path, content):
    if not os.path.exists(path):
        print(f'Restoring {path}')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)

# IOKit IOTypes.h
restore_file('iokit/IOKit/IOTypes.h', """/*
 * Copyright (c) 1998-2000 Apple Computer, Inc. All rights reserved.
 *
 * @APPLE_LICENSE_HEADER_START@
 * 
 * This file contains Original Code and/or Modifications of Original Code
 * as defined in and that are subject to the Apple Public Source License
 * Version 2.0 (the 'License'). You may not use this file except in
 * compliance with the License. Please obtain a copy of the License at
 * http://www.opensource.apple.com/apsl/ and read it before using this file.
 * 
 * @APPLE_LICENSE_HEADER_END@
 */
#ifndef _IOKIT_IOTYPES_H
#define _IOKIT_IOTYPES_H

#include <stdint.h>
#include <mach/mach_types.h>
#include <IOKit/IOReturn.h>

#if KERNEL
#include <libkern/OSTypes.h>
#endif

typedef uint32_t IOItemCount;
typedef uint32_t IOByteCount;
typedef uint64_t IOPhysicalAddress;
typedef uint64_t IOPhysicalLength;
typedef uint32_t IOVirtualAddress;
typedef uint32_t IOVirtualLength;
typedef uint32_t IOLogicalAddress;
typedef uint32_t IOLogicalLength;
typedef uint64_t IOAddressRange;
typedef uint64_t IOMemoryDescriptor;
typedef uint64_t IOMemoryMap;
typedef uint64_t IOService;
typedef uint64_t IOIterator;
typedef uint64_t IOObject;
typedef uint64_t IOCommand;
typedef uint64_t IOCommandGate;
typedef uint64_t IOWorkLoop;
typedef uint64_t IOEventSource;
typedef uint64_t IOInterruptEventSource;
typedef uint64_t IOTimerEventSource;
typedef uint64_t IONotifier;
typedef uint64_t IOMemoryCursor;
typedef uint64_t IOGeneralMemoryDescriptor;
typedef uint64_t IOSubMemoryDescriptor;
typedef uint64_t IOBufferMemoryDescriptor;
typedef uint64_t IOCommandPool;
typedef uint64_t IOCommandQueue;
typedef uint64_t IOCommandQueueInterface;
typedef uint64_t IOCommandQueueCallback;
typedef uint64_t IOCommandQueueCallbackContext;
typedef uint64_t IOCommandQueueCallbackFunction;
typedef uint64_t IOCommandQueueCallbackData;
typedef uint64_t IOCommandQueueCallbackRef;
typedef uint64_t IOCommandQueueCallbackRefCon;
typedef uint64_t IOCommandQueueCallbackRefCon2;
typedef uint64_t IOCommandQueueCallbackRefCon3;
typedef uint64_t IOCommandQueueCallbackRefCon4;
typedef uint64_t IOCommandQueueCallbackRefCon5;
typedef uint64_t IOCommandQueueCallbackRefCon6;
typedef uint64_t IOCommandQueueCallbackRefCon7;
typedef uint64_t IOCommandQueueCallbackRefCon8;
typedef uint64_t IOCommandQueueCallbackRefCon9;
typedef uint64_t IOCommandQueueCallbackRefCon10;
typedef uint64_t IOCommandQueueCallbackRefCon11;
typedef uint64_t IOCommandQueueCallbackRefCon12;
typedef uint64_t IOCommandQueueCallbackRefCon13;
typedef uint64_t IOCommandQueueCallbackRefCon14;
typedef uint64_t IOCommandQueueCallbackRefCon15;
typedef uint64_t IOCommandQueueCallbackRefCon16;

#endif /* _IOKIT_IOTYPES_H */""")

# DriverKit IOTypes.h
restore_file('iokit/DriverKit/IOTypes.h', """/*
 * Copyright (c) 2018-2020 Apple Inc. All rights reserved.
 *
 * @APPLE_LICENSE_HEADER_START@
 * 
 * This file contains Original Code and/or Modifications of Original Code
 * as defined in and that are subject to the Apple Public Source License
 * Version 2.0 (the 'License'). You may not use this file except in
 * compliance with the License. Please obtain a copy of the License at
 * http://www.opensource.apple.com/apsl/ and read it before using this file.
 * 
 * @APPLE_LICENSE_HEADER_END@
 */
#ifndef _DRIVERKIT_IOTYPES_H
#define _DRIVERKIT_IOTYPES_H

#include <stdint.h>
#include <DriverKit/IOReturn.h>

typedef uint32_t IOItemCount;
typedef uint32_t IOByteCount;
typedef uint64_t IOPhysicalAddress;
typedef uint64_t IOPhysicalLength;
typedef uint64_t IOVirtualAddress;
typedef uint64_t IOVirtualLength;
typedef uint64_t IOLogicalAddress;
typedef uint64_t IOLogicalLength;
typedef uint64_t IOAddressRange;
typedef uint64_t IOMemoryDescriptor;
typedef uint64_t IOMemoryMap;
typedef uint64_t IOService;
typedef uint64_t IOIterator;
typedef uint64_t IOObject;
typedef uint64_t IOCommand;
typedef uint64_t IOCommandGate;
typedef uint64_t IOWorkLoop;
typedef uint64_t IOEventSource;
typedef uint64_t IOInterruptEventSource;
typedef uint64_t IOTimerEventSource;
typedef uint64_t IONotifier;
typedef uint64_t IOMemoryCursor;
typedef uint64_t IOGeneralMemoryDescriptor;
typedef uint64_t IOSubMemoryDescriptor;
typedef uint64_t IOBufferMemoryDescriptor;
typedef uint64_t IOCommandPool;
typedef uint64_t IOCommandQueue;
typedef uint64_t IOCommandQueueInterface;
typedef uint64_t IOCommandQueueCallback;
typedef uint64_t IOCommandQueueCallbackContext;
typedef uint64_t IOCommandQueueCallbackFunction;
typedef uint64_t IOCommandQueueCallbackData;
typedef uint64_t IOCommandQueueCallbackRef;
typedef uint64_t IOCommandQueueCallbackRefCon;
typedef uint64_t IOCommandQueueCallbackRefCon2;
typedef uint64_t IOCommandQueueCallbackRefCon3;
typedef uint64_t IOCommandQueueCallbackRefCon4;
typedef uint64_t IOCommandQueueCallbackRefCon5;
typedef uint64_t IOCommandQueueCallbackRefCon6;
typedef uint64_t IOCommandQueueCallbackRefCon7;
typedef uint64_t IOCommandQueueCallbackRefCon8;
typedef uint64_t IOCommandQueueCallbackRefCon9;
typedef uint64_t IOCommandQueueCallbackRefCon10;
typedef uint64_t IOCommandQueueCallbackRefCon11;
typedef uint64_t IOCommandQueueCallbackRefCon12;
typedef uint64_t IOCommandQueueCallbackRefCon13;
typedef uint64_t IOCommandQueueCallbackRefCon14;
typedef uint64_t IOCommandQueueCallbackRefCon15;
typedef uint64_t IOCommandQueueCallbackRefCon16;

#endif /* _DRIVERKIT_IOTYPES_H */""")

# IOKit IOReturn.h
restore_file('iokit/IOKit/IOReturn.h', """/*
 * Copyright (c) 1998-2000 Apple Computer, Inc. All rights reserved.
 *
 * @APPLE_LICENSE_HEADER_START@
 * 
 * This file contains Original Code and/or Modifications of Original Code
 * as defined in and that are subject to the Apple Public Source License
 * Version 2.0 (the 'License'). You may not use this file except in
 * compliance with the License. Please obtain a copy of the License at
 * http://www.opensource.apple.com/apsl/ and read it before using this file.
 * 
 * @APPLE_LICENSE_HEADER_END@
 */
#ifndef _IOKIT_IOR_RETURN_H
#define _IOKIT_IOR_RETURN_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef int32_t IOReturn;

#define kIOReturnSuccess                      0
#define kIOReturnError                        (1 | (1 << 16))
#define kIOReturnNoMemory                     (2 | (1 << 16))
#define kIOReturnNoResources                  (3 | (1 << 16))
#define kIOReturnIPCError                     (4 | (1 << 16))
#define kIOReturnNoDevice                     (5 | (1 << 16))
#define kIOReturnNotPrivileged                (6 | (1 << 16))
#define kIOReturnBadArgument                  (7 | (1 << 16))
#define kIOReturnLockedRead                   (8 | (1 << 16))
#define kIOReturnLockedWrite                  (9 | (1 << 16))
#define kIOReturnExclusiveAccess              (10 | (1 << 16))
#define kIOReturnBadMedia                     (11 | (1 << 16))
#define kIOReturnUnformattedMedia             (12 | (1 << 16))
#define kIOReturnUnsupportedMode              (13 | (1 << 16))
#define kIOReturnUnderrun                     (14 | (1 << 16))
#define kIOReturnOverrun                      (15 | (1 << 16))
#define kIOReturnMessageTooLarge              (16 | (1 << 16))
#define kIOReturnNoBandwidth                  (17 | (1 << 16))
#define kIOReturnNotAligned                   (18 | (1 << 16))
#define kIOReturnBadMedia                     (19 | (1 << 16))
#define kIOReturnTimeout                      (19 | (1 << 16))
#define kIOReturnAborted                      (20 | (1 << 16))
#define kIOReturnBusy                         (21 | (1 << 16))
#define kIOReturnOffline                      (22 | (1 << 16))
#define kIOReturnNotReady                     (23 | (1 << 16))
#define kIOReturnNotAttached                  (24 | (1 << 16))
#define kIOReturnNoChannels                   (25 | (1 << 16))
#define kIOReturnNoSpace                      (26 | (1 << 16))
#define kIOReturnOverrun                      (27 | (1 << 16))
#define kIOReturnCannotLock                   (28 | (1 << 16))
#define kIOReturnNotPermitted                 (29 | (1 << 16))
#define kIOReturnNoPower                      (30 | (1 << 16))
#define kIOReturnNoMedia                      (31 | (1 << 16))
#define kIOReturnMediaWriteProtected          (32 | (1 << 16))
#define kIOReturnNotFound                     (33 | (1 << 16))
#define kIOReturnNotMounted                   (34 | (1 << 16))
#define kIOReturnIOError                      (35 | (1 << 16))
#define kIOReturnCannotAllocateMemory         (36 | (1 << 16))
#define kIOReturnInvalid                      (37 | (1 << 16))
#define kIOReturnNotImplemented               (38 | (1 << 16))
#define kIOReturnUnsupported                  (39 | (1 << 16))
#define kIOReturnBadArgument                  (40 | (1 << 16))
#define kIOReturnBadMedia                     (41 | (1 << 16))
#define kIOReturnCannotAllocateMemory         (42 | (1 << 16))
#define kIOReturnNotImplemented               (43 | (1 << 16))
#define kIOReturnNotPrivileged                (44 | (1 << 16))
#define kIOReturnOffline                      (45 | (1 << 16))
#define kIOReturnBusy                         (46 | (1 << 16))
#define kIOReturnNoDevice                     (47 | (1 << 16))
#define kIOReturnInternalError                (48 | (1 << 16))
#define kIOReturnOverrun                      (49 | (1 << 16))
#define kIOReturnUnderflow                    (50 | (1 << 16))
#define kIOReturnOverflow                     (51 | (1 << 16))
#define kIOReturnBadBuffer                    (52 | (1 << 16))
#define kIOReturnNoMemory                     (53 | (1 << 16))
#define kIOReturnNoResources                  (54 | (1 << 16))
#define kIOReturnWouldBlock                   (55 | (1 << 16))
#define kIOReturnTimeout                      (56 | (1 << 16))
#define kIOReturnAborted                      (57 | (1 << 16))
#define kIOReturnCannotLock                   (58 | (1 << 16))
#define kIOReturnNotPermitted                 (59 | (1 << 16))
#define kIOReturnNoPower                      (60 | (1 << 16))
#define kIOReturnNotImplemented               (61 | (1 << 16))
#define kIOReturnInternalError                (62 | (1 << 16))
#define kIOReturnIOError                      (63 | (1 << 16))

#ifdef __cplusplus
}
#endif

#endif /* _IOKIT_IOR_RETURN_H */""")

# DriverKit IOReturn.h
restore_file('iokit/DriverKit/IOReturn.h', """/*
 * Copyright (c) 2018-2020 Apple Inc. All rights reserved.
 *
 * @APPLE_LICENSE_HEADER_START@
 * 
 * This file contains Original Code and/or Modifications of Original Code
 * as defined in and that are subject to the Apple Public Source License
 * Version 2.0 (the 'License'). You may not use this file except in
 * compliance with the License. Please obtain a copy of the License at
 * http://www.opensource.apple.com/apsl/ and read it before using this file.
 * 
 * @APPLE_LICENSE_HEADER_END@
 */
#ifndef _DRIVERKIT_IOR_RETURN_H
#define _DRIVERKIT_IOR_RETURN_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef int32_t IOReturn;

#define kIOReturnSuccess                      0
#define kIOReturnError                        (1 | (1 << 16))
#define kIOReturnNoMemory                     (2 | (1 << 16))
#define kIOReturnNoResources                  (3 | (1 << 16))
#define kIOReturnIPCError                     (4 | (1 << 16))
#define kIOReturnNoDevice                     (5 | (1 << 16))
#define kIOReturnNotPrivileged                (6 | (1 << 16))
#define kIOReturnBadArgument                  (7 | (1 << 16))
#define kIOReturnLockedRead                   (8 | (1 << 16))
#define kIOReturnLockedWrite                  (9 | (1 << 16))
#define kIOReturnExclusiveAccess              (10 | (1 << 16))
#define kIOReturnBadMedia                     (11 | (1 << 16))
#define kIOReturnUnformattedMedia             (12 | (1 << 16))
#define kIOReturnUnsupportedMode              (13 | (1 << 16))
#define kIOReturnUnderrun                     (14 | (1 << 16))
#define kIOReturnOverrun                      (15 | (1 << 16))
#define kIOReturnMessageTooLarge              (16 | (1 << 16))
#define kIOReturnNoBandwidth                  (17 | (1 << 16))
#define kIOReturnNotAligned                   (18 | (1 << 16))
#define kIOReturnBadMedia                     (19 | (1 << 16))
#define kIOReturnTimeout                      (19 | (1 << 16))
#define kIOReturnAborted                      (20 | (1 << 16))
#define kIOReturnBusy                         (21 | (1 << 16))
#define kIOReturnOffline                      (22 | (1 << 16))
#define kIOReturnNotReady                     (23 | (1 << 16))
#define kIOReturnNotAttached                  (24 | (1 << 16))
#define kIOReturnNoChannels                   (25 | (1 << 16))
#define kIOReturnNoSpace                      (26 | (1 << 16))
#define kIOReturnOverrun                      (27 | (1 << 16))
#define kIOReturnCannotLock                   (28 | (1 << 16))
#define kIOReturnNotPermitted                 (29 | (1 << 16))
#define kIOReturnNoPower                      (30 | (1 << 16))
#define kIOReturnNoMedia                      (31 | (1 << 16))
#define kIOReturnMediaWriteProtected          (32 | (1 << 16))
#define kIOReturnNotFound                     (33 | (1 << 16))
#define kIOReturnNotMounted                   (34 | (1 << 16))
#define kIOReturnIOError                      (35 | (1 << 16))
#define kIOReturnCannotAllocateMemory         (36 | (1 << 16))
#define kIOReturnInvalid                      (37 | (1 << 16))
#define kIOReturnNotImplemented               (38 | (1 << 16))
#define kIOReturnUnsupported                  (39 | (1 << 16))
#define kIOReturnBadArgument                  (40 | (1 << 16))
#define kIOReturnBadMedia                     (41 | (1 << 16))
#define kIOReturnCannotAllocateMemory         (42 | (1 << 16))
#define kIOReturnNotImplemented               (43 | (1 << 16))
#define kIOReturnNotPrivileged                (44 | (1 << 16))
#define kIOReturnOffline                      (45 | (1 << 16))
#define kIOReturnBusy                         (46 | (1 << 16))
#define kIOReturnNoDevice                     (47 | (1 << 16))
#define kIOReturnInternalError                (48 | (1 << 16))
#define kIOReturnOverrun                      (49 | (1 << 16))
#define kIOReturnUnderflow                    (50 | (1 << 16))
#define kIOReturnOverflow                     (51 | (1 << 16))
#define kIOReturnBadBuffer                    (52 | (1 << 16))
#define kIOReturnNoMemory                     (53 | (1 << 16))
#define kIOReturnNoResources                  (54 | (1 << 16))
#define kIOReturnWouldBlock                   (55 | (1 << 16))
#define kIOReturnTimeout                      (56 | (1 << 16))
#define kIOReturnAborted                      (57 | (1 << 16))
#define kIOReturnCannotLock                   (58 | (1 << 16))
#define kIOReturnNotPermitted                 (59 | (1 << 16))
#define kIOReturnNoPower                      (60 | (1 << 16))
#define kIOReturnNotImplemented               (61 | (1 << 16))
#define kIOReturnInternalError                (62 | (1 << 16))
#define kIOReturnIOError                      (63 | (1 << 16))

#ifdef __cplusplus
}
#endif

#endif /* _DRIVERKIT_IOR_RETURN_H */""")

# IOKit IORPC.h
restore_file('iokit/IOKit/IORPC.h', """/*
 * Copyright (c) 1998-2000 Apple Computer, Inc. All rights reserved.
 *
 * @APPLE_LICENSE_HEADER_START@
 * 
 * This file contains Original Code and/or Modifications of Original Code
 * as defined in and that are subject to the Apple Public Source License
 * Version 2.0 (the 'License'). You may not use this file except in
 * compliance with the License. Please obtain a copy of the License at
 * http://www.opensource.apple.com/apsl/ and read it before using this file.
 * 
 * @APPLE_LICENSE_HEADER_END@
 */
#ifndef _IOKIT_IORPC_H
#define _IOKIT_IORPC_H

#include <IOKit/IOReturn.h>
#include <mach/mach_types.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef mach_port_t io_object_t;
typedef mach_port_t io_service_t;
typedef mach_port_t io_connect_t;
typedef mach_port_t io_iterator_t;
typedef mach_port_t io_enumerator_t;
typedef mach_port_t io_registry_entry_t;

typedef enum {
    kIOMessageServiceIsRequestingClose = 0,
    kIOMessageServiceIsTerminated = 1,
    kIOMessageServiceIsRequestingOpen = 2,
    kIOMessageServiceIsTerminating = 3,
    kIOMessageServiceIsRequestingPower = 4,
    kIOMessageServiceIsRequestingClose = 5,
    kIOMessageServiceIsTerminated = 6,
    kIOMessageServiceIsRequestingOpen = 7,
    kIOMessageServiceIsTerminating = 8,
} IOMessageCategory;

typedef struct {
    io_object_t object;
    uint32_t flavor;
    uint32_t count;
    uint32_t data[1];
} IOServiceInterestContent;

typedef IOServiceInterestContent *IOServiceInterestRef;

kern_return_t io_service_open(io_service_t service, task_port_t owningTask, uint32_t type, io_connect_t *connect);
kern_return_t io_service_close(io_connect_t connect);
kern_return_t io_service_add_interest_notification(io_service_t service, io_iterator_t *notification, uint32_t interestType, uint32_t *matching);
kern_return_t io_service_remove_interest_notification(io_iterator_t notification);
kern_return_t io_registry_entry_create_iterator(io_registry_entry_t entry, io_iterator_t *iterator);
kern_return_t io_registry_entry_get_child_entry(io_registry_entry_t entry, io_iterator_t *iterator);
kern_return_t io_registry_entry_get_parent_entry(io_registry_entry_t entry, io_registry_entry_t *parent);
kern_return_t io_registry_entry_get_name(io_registry_entry_t entry, io_name_t name);
kern_return_t io_registry_entry_get_name_in_plane(io_registry_entry_t entry, const io_name_t plane, io_name_t name);
kern_return_t io_registry_entry_get_path(io_registry_entry_t entry, const io_name_t plane, io_string_t path);
kern_return_t io_registry_entry_get_location_in_plane(io_registry_entry_t entry, const io_name_t plane, io_string_t location);
kern_return_t io_registry_entry_search_cf_property(io_registry_entry_t entry, CFStringRef key, CFTypeRef *property);
kern_return_t io_registry_entry_set_cf_property(io_registry_entry_t entry, CFStringRef key, CFTypeRef property);
kern_return_t io_registry_entry_get_property(io_registry_entry_t entry, CFStringRef key, CFTypeRef *property);
kern_return_t io_registry_entry_set_property(io_registry_entry_t entry, CFStringRef key, CFTypeRef property);
kern_return_t io_service_get_matching_services(mach_port_t masterPort, CFDictionaryRef matching, io_iterator_t *existing);
kern_return_t io_service_get_matching_services_with_options(mach_port_t masterPort, uint32_t options, CFDictionaryRef matching, io_iterator_t *existing);
kern_return_t io_iterator_next(io_iterator_t iterator, io_object_t *object);
kern_return_t io_iterator_reset(io_iterator_t iterator);
kern_return_t io_object_conforms_to(io_object_t object, const char *className);
kern_return_t io_object_copy_class(io_object_t object, io_name_t className);
kern_return_t io_object_copy_superclass_for_class(io_name_t className, io_name_t superclassName);
kern_return_t io_object_get_class(io_object_t object, io_name_t className);
kern_return_t io_object_copy_bundle_identifier_for_class(io_name_t className, CFStringRef *bundleIdentifier);
kern_return_t io_object_get_kernel_retained_memory(io_object_t object, uint64_t *memory);
kern_return_t io_object_get_kernel_retained_memory_with_options(io_object_t object, uint32_t options, uint64_t *memory);
kern_return_t io_connect_map_memory(io_connect_t connect, uint32_t memoryType, task_port_t intoTask, mach_vm_address_t *atAddress, mach_vm_size_t *ofSize, uint32_t options);
kern_return_t io_connect_unmap_memory(io_connect_t connect, uint32_t memoryType, task_port_t fromTask, mach_vm_address_t atAddress);
kern_return_t io_connect_method_structureI_structureO(io_connect_t connect, uint32_t selector, const void *inputStruct, size_t inputStructCnt, void *outputStruct, size_t *outputStructCnt);
kern_return_t io_connect_method_scalarI_scalarO(io_connect_t connect, uint32_t selector, const uint64_t *input, uint32_t inputCnt, uint64_t *output, uint32_t *outputCnt);
kern_return_t io_connect_method_scalarI_structureO(io_connect_t connect, uint32_t selector, const uint64_t *input, uint32_t inputCnt, void *outputStruct, size_t *outputStructCnt);
kern_return_t io_connect_method_structureI_scalarO(io_connect_t connect, uint32_t selector, const void *inputStruct, size_t inputStructCnt, uint64_t *output, uint32_t *outputCnt);

#ifdef __cplusplus
}
#endif

#endif /* _IOKIT_IORPC_H */""")

# DriverKit IORPC.h
restore_file('iokit/DriverKit/IORPC.h', """/*
 * Copyright (c) 2018-2020 Apple Inc. All rights reserved.
 *
 * @APPLE_LICENSE_HEADER_START@
 * 
 * This file contains Original Code and/or Modifications of Original Code
 * as defined in and that are subject to the Apple Public Source License
 * Version 2.0 (the 'License'). You may not use this file except in
 * compliance with the License. Please obtain a copy of the License at
 * http://www.opensource.apple.com/apsl/ and read it before using this file.
 * 
 * @APPLE_LICENSE_HEADER_END@
 */
#ifndef _DRIVERKIT_IORPC_H
#define _DRIVERKIT_IORPC_H

#include <DriverKit/IOReturn.h>
#include <mach/mach_types.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef mach_port_t io_object_t;
typedef mach_port_t io_service_t;
typedef mach_port_t io_connect_t;
typedef mach_port_t io_iterator_t;
typedef mach_port_t io_enumerator_t;
typedef mach_port_t io_registry_entry_t;

typedef enum {
    kIOMessageServiceIsRequestingClose = 0,
    kIOMessageServiceIsTerminated = 1,
    kIOMessageServiceIsRequestingOpen = 2,
    kIOMessageServiceIsTerminating = 3,
    kIOMessageServiceIsRequestingPower = 4,
    kIOMessageServiceIsRequestingClose = 5,
    kIOMessageServiceIsTerminated = 6,
    kIOMessageServiceIsRequestingOpen = 7,
    kIOMessageServiceIsTerminating = 8,
} IOMessageCategory;

typedef struct {
    io_object_t object;
    uint32_t flavor;
    uint32_t count;
    uint32_t data[1];
} IOServiceInterestContent;

typedef IOServiceInterestContent *IOServiceInterestRef;

kern_return_t io_service_open(io_service_t service, task_port_t owningTask, uint32_t type, io_connect_t *connect);
kern_return_t io_service_close(io_connect_t connect);
kern_return_t io_service_add_interest_notification(io_service_t service, io_iterator_t *notification, uint32_t interestType, uint32_t *matching);
kern_return_t io_service_remove_interest_notification(io_iterator_t notification);
kern_return_t io_registry_entry_create_iterator(io_registry_entry_t entry, io_iterator_t *iterator);
kern_return_t io_registry_entry_get_child_entry(io_registry_entry_t entry, io_iterator_t *iterator);
kern_return_t io_registry_entry_get_parent_entry(io_registry_entry_t entry, io_registry_entry_t *parent);
kern_return_t io_registry_entry_get_name(io_registry_entry_t entry, io_name_t name);
kern_return_t io_registry_entry_get_name_in_plane(io_registry_entry_t entry, const io_name_t plane, io_name_t name);
kern_return_t io_registry_entry_get_path(io_registry_entry_t entry, const io_name_t plane, io_string_t path);
kern_return_t io_registry_entry_get_location_in_plane(io_registry_entry_t entry, const io_name_t plane, io_string_t location);
kern_return_t io_registry_entry_search_cf_property(io_registry_entry_t entry, CFStringRef key, CFTypeRef *property);
kern_return_t io_registry_entry_set_cf_property(io_registry_entry_t entry, CFStringRef key, CFTypeRef property);
kern_return_t io_registry_entry_get_property(io_registry_entry_t entry, CFStringRef key, CFTypeRef *property);
kern_return_t io_registry_entry_set_property(io_registry_entry_t entry, CFStringRef key, CFTypeRef property);
kern_return_t io_service_get_matching_services(mach_port_t masterPort, CFDictionaryRef matching, io_iterator_t *existing);
kern_return_t io_service_get_matching_services_with_options(mach_port_t masterPort, uint32_t options, CFDictionaryRef matching, io_iterator_t *existing);
kern_return_t io_iterator_next(io_iterator_t iterator, io_object_t *object);
kern_return_t io_iterator_reset(io_iterator_t iterator);
kern_return_t io_object_conforms_to(io_object_t object, const char *className);
kern_return_t io_object_copy_class(io_object_t object, io_name_t className);
kern_return_t io_object_copy_superclass_for_class(io_name_t className, io_name_t superclassName);
kern_return_t io_object_get_class(io_object_t object, io_name_t className);
kern_return_t io_object_copy_bundle_identifier_for_class(io_name_t className, CFStringRef *bundleIdentifier);
kern_return_t io_object_get_kernel_retained_memory(io_object_t object, uint64_t *memory);
kern_return_t io_object_get_kernel_retained_memory_with_options(io_object_t object, uint32_t options, uint64_t *memory);
kern_return_t io_connect_map_memory(io_connect_t connect, uint32_t memoryType, task_port_t intoTask, mach_vm_address_t *atAddress, mach_vm_size_t *ofSize, uint32_t options);
kern_return_t io_connect_unmap_memory(io_connect_t connect, uint32_t memoryType, task_port_t fromTask, mach_vm_address_t atAddress);
kern_return_t io_connect_method_structureI_structureO(io_connect_t connect, uint32_t selector, const void *inputStruct, size_t inputStructCnt, void *outputStruct, size_t *outputStructCnt);
kern_return_t io_connect_method_scalarI_scalarO(io_connect_t connect, uint32_t selector, const uint64_t *input, uint32_t inputCnt, uint64_t *output, uint32_t *outputCnt);
kern_return_t io_connect_method_scalarI_structureO(io_connect_t connect, uint32_t selector, const uint64_t *input, uint32_t inputCnt, void *outputStruct, size_t *outputStructCnt);
kern_return_t io_connect_method_structureI_scalarO(io_connect_t connect, uint32_t selector, const void *inputStruct, size_t inputStructCnt, uint64_t *output, uint32_t *outputCnt);

#ifdef __cplusplus
}
#endif

#endif /* _DRIVERKIT_IORPC_H */""")

print('Headers restored')