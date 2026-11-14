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

print('Headers restored')