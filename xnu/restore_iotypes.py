#!/usr/bin/env python3
import os

# IOKit IOTypes.h
iokit_path = 'iokit/IOKit/IOTypes.h'
if not os.path.exists(iokit_path):
    print('Restoring iokit/IOKit/IOTypes.h')
    os.makedirs(os.path.dirname(iokit_path), exist_ok=True)
    with open(iokit_path, 'w') as f:
        f.write("""/*
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
driverkit_path = 'iokit/DriverKit/IOTypes.h'
if not os.path.exists(driverkit_path):
    print('Restoring iokit/DriverKit/IOTypes.h')
    os.makedirs(os.path.dirname(driverkit_path), exist_ok=True)
    with open(driverkit_path, 'w') as f:
        f.write("""/*
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

print('IOTypes.h headers restored')