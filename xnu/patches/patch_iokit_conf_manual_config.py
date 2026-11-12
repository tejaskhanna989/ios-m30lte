#!/usr/bin/env python3
"""Create a manual iokit/conf config to bypass doconf."""
import os

# The iokit/conf config file that doconf would generate for M30LTE (DEVELOPMENT)
config_content = """# config file for iokit/conf
# Generated manually to bypass doconf failure

# Build directory
builddir	"."

# Object directory
objectdir	"../../../../../../../BUILD/obj"

# Source directory
sourcedir	"../../../../../../.."

# IOKit files for M30LTE (ARM64) - minimal set
iokit/IOBSD/IOBSD.cpp
iokit/IOBufferMemoryDescriptor.cpp
iokit/IOCatalogue.cpp
iokit/IOCommand.cpp
iokit/IOCommandGate.cpp
iokit/IOCommandPool.cpp
iokit/IODataQueue.cpp
iokit/IODeviceMemory.cpp
iokit/IODeviceTreeSupport.cpp
iokit/IODMACommand.cpp
iokit/IODMAEventSource.cpp
iokit/IODTMatching.cpp
iokit/IODTNVRAM.cpp
iokit/IOEventSource.cpp
iokit/IOFilterInterruptEventSource.cpp
iokit/IOFramebuffer.cpp
iokit/IOGeneralMemoryDescriptor.cpp
iokit/IOInterruptController.cpp
iokit/IOInterruptEventSource.cpp
iokit/IOIterator.cpp
iokit/IOKit/IOLib.cpp
iokit/IOKit/IOLog.cpp
iokit/IOKit/IOPanic.cpp
iokit/IOKit/IOService.cpp
iokit/IOKit/IOUserClient.cpp
iokit/IOKit/IOWorkLoop.cpp
iokit/IOKit/notification/IONotificationRegistrar.cpp
iokit/IOKit/notification/IONotifier.cpp
iokit/IOKit/notification/IONotifierRegistry.cpp
iokit/IOKit/pci/IOPCIDevice.cpp
iokit/IOKit/pci/IOPCIFunction.cpp
iokit/IOKit/pci/IOPCIMessage.cpp
iokit/IOKit/pci/IOPCIPrimaryMatch.cpp
iokit/IOKit/pci/IOPCIResource.cpp
iokit/IOKit/pci/IOPCITunnelCompatible.cpp
iokit/IOKit/pwr_mgt/IOPMPowerSource.cpp
iokit/IOKit/pwr_mgt/IOPMrootDomain.cpp
iokit/IOKit/pwr_mgt/IOPMScheduler.cpp
iokit/IOKit/pwr_mgt/RootDomainUserClient.cpp
iokit/IOKit/storage/IOBlockStorageDevice.cpp
iokit/IOKit/storage/IOBlockStorageDriver.cpp
iokit/IOKit/storage/IOCDMedia.cpp
iokit/IOKit/storage/IOCDMediaBSDClient.cpp
iokit/IOKit/storage/IOCompactFlash.cpp
iokit/IOKit/storage/IOCoreStorage.cpp
iokit/IOKit/storage/IOCoreStorageAES.cpp
iokit/IOKit/storage/IOCoreStorageGroup.cpp
iokit/IOKit/storage/IOCoreStoragePhysical.cpp
iokit/IOKit/storage/IOCoreStorageUserClient.cpp
iokit/IOKit/storage/IODVDMedia.cpp
iokit/IOKit/storage/IODVDMediaBSDClient.cpp
iokit/IOKit/storage/IOFDMedia.cpp
iokit/IOKit/storage/IOFDMediaBSDClient.cpp
iokit/IOKit/storage/IOHDIXController.cpp
iokit/IOKit/storage/IOHDIXMedia.cpp
iokit/IOKit/storage/IOKernelMemoryDescriptor.cpp
iokit/IOKit/storage/IOMedia.cpp
iokit/IOKit/storage/IOMediaBSDClient.cpp
iokit/IOKit/storage/IOSCSIBlockCommandsDevice.cpp
iokit/IOKit/storage/IOSCSIDevice.cpp
iokit/IOKit/storage/IOSCSIMultimediaCommandsDevice.cpp
iokit/IOKit/storage/IOSCSIPeripheralDeviceType00.cpp
iokit/IOKit/storage/IOSCSIPeripheralDeviceType01.cpp
iokit/IOKit/storage/IOSCSIPeripheralDeviceType02.cpp
iokit/IOKit/storage/IOSCSIPeripheralDeviceType03.cpp
iokit/IOKit/storage/IOSCSIPeripheralDeviceType04.cpp
iokit/IOKit/storage/IOSCSIPeripheralDeviceType05.cpp
iokit/IOKit/storage/IOSCSIPeripheralDeviceType06.cpp
iokit/IOKit/storage/IOSCSIPeripheralDeviceType07.cpp
iokit/IOKit/storage/IOSCSIPeripheralDeviceType08.cpp
iokit/IOKit/storage/IOSCSIPeripheralDeviceType09.cpp
iokit/IOKit/storage/IOSCSIPeripheralDeviceType0A.cpp
iokit/IOKit/storage/IOSCSIPeripheralDeviceType0B.cpp
iokit/IOKit/storage/IOSCSIPeripheralDeviceType0C.cpp
iokit/IOKit/storage/IOSCSIPeripheralDeviceType0D.cpp
iokit/IOKit/storage/IOSCSIPeripheralDeviceType0E.cpp
iokit/IOKit/storage/IOSCSIPeripheralDeviceType0F.cpp
iokit/IOKit/storage/IOSCSIReducedBlockCommandsDevice.cpp
iokit/IOKit/storage/IOStorage.cpp
iokit/IOKit/storage/IOStorageController.cpp
iokit/IOKit/storage/IOStorageFamily.cpp
iokit/IOKit/storage/IOStorageRedundancyController.cpp
iokit/IOKit/usb/IOUSBController.cpp
iokit/IOKit/usb/IOUSBControllerV2.cpp
iokit/IOKit/usb/IOUSBControllerV3.cpp
iokit/IOKit/usb/IOUSBDevice.cpp
iokit/IOKit/usb/IOUSBEndpoint.cpp
iokit/IOKit/usb/IOUSBHostDevice.cpp
iokit/IOKit/usb/IOUSBHostEndpoint.cpp
iokit/IOKit/usb/IOUSBHostInterface.cpp
iokit/IOKit/usb/IOUSBHostPipe.cpp
iokit/IOKit/usb/IOUSBHostPipeLog.cpp
iokit/IOKit/usb/IOUSBInterface.cpp
iokit/IOKit/usb/IOUSBLog.cpp
iokit/IOKit/usb/IOUSBMassStorageClass.cpp
iokit/IOKit/usb/IOUSBMassStorageClassExtras.cpp
iokit/IOKit/usb/IOUSBPipe.cpp
iokit/IOKit/usb/IOUSBUserClient.cpp
iokit/IOKit/watchdog/IOWatchDogTimer.cpp
iokit/IOKitServer.cpp
iokit/IOInterruptEventSource.cpp
iokit/IOKitDiagnostics.cpp
iokit/IOKitKeys.cpp
iokit/IOLog.cpp
iokit/IOMapper.cpp
iokit/IOMapperEndpoint.cpp
iokit/IOMapperMemoryDescriptor.cpp
iokit/IOMapperSpec.cpp
iokit/IOMapperSpecArray.cpp
iokit/IOMemoryDescriptor.cpp
iokit/IOMPAccess.cpp
iokit/IOMPContainer.cpp
iokit/IOMPDevice.cpp
iokit/IOMPSDevice.cpp
iokit/IOMPT.cpp
iokit/IONetwork/IO80211Interface.cpp
iokit/IONetwork/IO80211Peer.cpp
iokit/IONetwork/IO80211ScanManager.cpp
iokit/IONetwork/IO80211VirtualInterface.cpp
iokit/IONetwork/IOBluetoothDevice.cpp
iokit/IONetwork/IOBluetoothHCIController.cpp
iokit/IONetwork/IOBluetoothHCIControllerTransport.cpp
iokit/IONetwork/IOBluetoothHostControllerUSBTransport.cpp
iokit/IONetwork/IOBluetoothL2CAPChannel.cpp
iokit/IONetwork/IOBluetoothRFCOMMChannel.cpp
iokit/IONetwork/IOBluetoothSDPClient.cpp
iokit/IONetwork/IOBluetoothSDPServer.cpp
iokit/IONetwork/IOBluetoothService.cpp
iokit/IONetwork/IOBluetoothSDPSession.cpp
iokit/IONetwork/IOBluetoothSDPTransaction.cpp
iokit/IONetwork/IOBluetoothServiceRecord.cpp
iokit/IONetwork/IOBluetoothUtility.cpp
iokit/IONetwork/IOEthernetController.cpp
iokit/IONetwork/IOEthernetInterface.cpp
iokit/IONetwork/IONetworkController.cpp
iokit/IONetwork/IONetworkData.cpp
iokit/IONetwork/IONetworkInterface.cpp
iokit/IONetwork/IONetworkMedium.cpp
iokit/IONetwork/IONetworkStats.cpp
iokit/IONetwork/IONetworkUserClient.cpp
iokit/IONetwork/IOPacketFilter.cpp
iokit/IONetwork/IOPacketFilterMonitor.cpp
iokit/IONetwork/IOPacketFilterProvider.cpp
iokit/IONetwork/IOPacketFilterRule.cpp
iokit/IONetwork/IOPacketFilterRuleTable.cpp
iokit/IONetwork/IOPacketFilterRuleTable6.cpp
iokit/IONetwork/IOPacketFilterStats.cpp
iokit/IONetwork/IOPacketFilterUserClient.cpp
iokit/IONetwork/IOPacketFilterUserClient6.cpp
iokit/IONetwork/IOService.cpp
iokit/IONetwork/IOVirtualInterface.cpp
iokit/IONetworkController.cpp
iokit/IONetworkData.cpp
iokit/IONetworkInterface.cpp
iokit/IONetworkMedium.cpp
iokit/IONetworkStats.cpp
iokit/IONetworkUserClient.cpp
iokit/IOPacketFilter.cpp
iokit/IOPacketFilterMonitor.cpp
iokit/IOPacketFilterProvider.cpp
iokit/IOPacketFilterRule.cpp
iokit/IOPacketFilterRuleTable.cpp
iokit/IOPacketFilterRuleTable6.cpp
iokit/IOPacketFilterStats.cpp
iokit/IOPacketFilterUserClient.cpp
iokit/IOPacketFilterUserClient6.cpp
iokit/IOPCIDevice.cpp
iokit/IOPCIFunction.cpp
iokit/IOPCIMessage.cpp
iokit/IOPCIPrimaryMatch.cpp
iokit/IOPCIResource.cpp
iokit/IOPCITunnelCompatible.cpp
iokit/IOPlatformDevice.cpp
iokit/IOPlatformExpert.cpp
iokit/IOPMPowerSource.cpp
iokit/IOPMrootDomain.cpp
iokit/IOPMScheduler.cpp
iokit/IOPoller.cpp
iokit/IOPolicy.cpp
iokit/IOReport.cpp
iokit/IOReportChannel.cpp
iokit/IOReportGroup.cpp
iokit/IOReportGroups.cpp
iokit/IOReportLegend.cpp
iokit/IOReportTypes.cpp
iokit/IOResource.cpp
iokit/IOResourceOwner.cpp
iokit/IOService.cpp
iokit/IOServiceGroup.cpp
iokit/IOServiceMatching.cpp
iokit/IOServiceOrdering.cpp
iokit/IOSharedDataQueue.cpp
iokit/IOSharedDataQueueClient.cpp
iokit/IOStorage.cpp
iokit/IOStorageController.cpp
iokit/IOStorageFamily.cpp
iokit/IOStorageRedundancyController.cpp
iokit/IOStream.cpp
iokit/IOStreamUserClient.cpp
iokit/IOStreamUserClientInterface.cpp
iokit/IOSystemReporter.cpp
iokit/IOTime.cpp
iokit/IOTimeStamp.cpp
iokit/IOTransfer.cpp
iokit/IOUserClient.cpp
iokit/IOUserClientClass.cpp
iokit/IOUserClientMethod.cpp
iokit/IOUserClientNotification.cpp
iokit/IOUserClientProperty.cpp
iokit/IOUserClientRegistry.cpp
iokit/IOUserClientService.cpp
iokit/IOUserClientTask.cpp
iokit/IOUserClientThread.cpp
iokit/IOWorkLoop.cpp
iokit/IOWorkQueue.cpp
iokit/RootDomainUserClient.cpp
iokit/IOBluetooth/IOBluetoothDevice.cpp
iokit/IOBluetooth/IOBluetoothHCIController.cpp
iokit/IOBluetooth/IOBluetoothHCIControllerTransport.cpp
iokit/IOBluetooth/IOBluetoothHostControllerUSBTransport.cpp
iokit/IOBluetooth/IOBluetoothL2CAPChannel.cpp
iokit/IOBluetooth/IOBluetoothRFCOMMChannel.cpp
iokit/IOBluetooth/IOBluetoothSDPClient.cpp
iokit/IOBluetooth/IOBluetoothSDPServer.cpp
iokit/IOBluetooth/IOBluetoothService.cpp
iokit/IOBluetooth/IOBluetoothSDPSession.cpp
iokit/IOBluetooth/IOBluetoothSDPTransaction.cpp
iokit/IOBluetooth/IOBluetoothServiceRecord.cpp
iokit/IOBluetooth/IOBluetoothUtility.cpp
"""

# Ensure directory exists
os.makedirs('iokit/conf', exist_ok=True)

# Write the config file
with open('iokit/conf/DEVELOPMENT', 'w') as f:
    f.write(config_content)

print("Created iokit/conf/DEVELOPMENT config file")

# Create a minimal hand-crafted valid Makefile for iokit/conf DEVELOPMENT config
makefile_content = """#
# This Makefile was generated by config
#
# DO NOT EDIT THIS FILE
#

export MakeInc_cmd=${SRCROOT}/makedefs/MakeInc.cmd
export MakeInc_def=${SRCROOT}/makedefs/MakeInc.def
export MakeInc_rule=${SRCROOT}/makedefs/MakeInc.rule
export MakeInc_dir=${SRCROOT}/makedefs/MakeInc.dir

include $(MakeInc_cmd)
include $(MakeInc_def)

#
# XXX: CFLAGS
#
CFLAGS+= -include meta_features.h -DBSD_KERNEL_PRIVATE
SFLAGS+= -include meta_features.h

#
# INCFLAGS to include iokit prototypes
#
INCFLAGS_MAKEFILE= -I$(SOURCE)/..

#
# Directories for mig generated files
#
COMP_SUBDIRS =

#
#  Make sure we don't remove this by accident if interrupted at the wrong
#  time.
#
.PRECIOUS: Makefile

#
#  Theses macros are filled in by the config program depending on the
#  current configuration.  The MACHDEP macro is replaced by the
#  contents of the machine dependent makefile template and the others
#  are replaced by the corresponding symbol definitions for the
#  configuration.
#

OBJS = \\
	IOBSD.o \\
	IOBufferMemoryDescriptor.o \\
	IOCatalogue.o \\
	IOCommand.o \\
	IOCommandGate.o \\
	IOCommandPool.o \\
	IODataQueue.o \\
	IODeviceMemory.o \\
	IODeviceTreeSupport.o \\
	IODMACommand.o \\
	IODMAEventSource.o \\
	IODTMatching.o \\
	IODTNVRAM.o \\
	IOEventSource.o \\
	IOFilterInterruptEventSource.o \\
	IOFramebuffer.o \\
	IOGeneralMemoryDescriptor.o \\
	IOInterruptController.o \\
	IOInterruptEventSource.o \\
	IOIterator.o \\
	IOLib.o \\
	IOLog.o \\
	IOPanic.o \\
	IOService.o \\
	IOUserClient.o \\
	IOWorkLoop.o \\
	IONotificationRegistrar.o \\
	IONotifier.o \\
	IONotifierRegistry.o \\
	IOPCIDevice.o \\
	IOPCIFunction.o \\
	IOPCIMessage.o \\
	IOPCIPrimaryMatch.o \\
	IOPCIResource.o \\
	IOPCITunnelCompatible.o \\
	IOPMPowerSource.o \\
	IOPMrootDomain.o \\
	IOPMScheduler.o \\
	RootDomainUserClient.o \\
	IOBlockStorageDevice.o \\
	IOBlockStorageDriver.o \\
	IOCDMedia.o \\
	IOCDMediaBSDClient.o \\
	IOCompactFlash.o \\
	IOCoreStorage.o \\
	IOCoreStorageAES.o \\
	IOCoreStorageGroup.o \\
	IOCoreStoragePhysical.o \\
	IOCoreStorageUserClient.o \\
	IODVDMedia.o \\
	IODVDMediaBSDClient.o \\
	IOFDMedia.o \\
	IOFDMediaBSDClient.o \\
	IOHDIXController.o \\
	IOHDIXMedia.o \\
	IOKernelMemoryDescriptor.o \\
	IOMedia.o \\
	IOMediaBSDClient.o \\
	IOSCSIBlockCommandsDevice.o \\
	IOSCSIDevice.o \\
	IOSCSIMultimediaCommandsDevice.o \\
	IOSCSIPeripheralDeviceType00.o \\
	IOSCSIPeripheralDeviceType01.o \\
	IOSCSIPeripheralDeviceType02.o \\
	IOSCSIPeripheralDeviceType03.o \\
	IOSCSIPeripheralDeviceType04.o \\
	IOSCSIPeripheralDeviceType05.o \\
	IOSCSIPeripheralDeviceType06.o \\
	IOSCSIPeripheralDeviceType07.o \\
	IOSCSIPeripheralDeviceType07.o \\
	IOSCSIPeripheralDeviceType08.o \\
	IOSCSIPeripheralDeviceType09.o \\
	IOSCSIPeripheralDeviceType0A.o \\
	IOSCSIPeripheralDeviceType0B.o \\
	IOSCSIPeripheralDeviceType0C.o \\
	IOSCSIPeripheralDeviceType0D.o \\
	IOSCSIPeripheralDeviceType0E.o \\
	IOSCSIPeripheralDeviceType0F.o \\
	IOSCSIReducedBlockCommandsDevice.o \\
	IOStorage.o \\
	IOStorageController.o \\
	IOStorageFamily.o \\
	IOStorageRedundancyController.o \\
	IOUSBController.o \\
	IOUSBControllerV2.o \\
	IOUSBControllerV3.o \\
	IOUSBDevice.o \\
	IOUSBEndpoint.o \\
	IOUSBHostDevice.o \\
	IOUSBHostEndpoint.o \\
	IOUSBHostInterface.o \\
	IOUSBHostPipe.o \\
	IOUSBHostPipeLog.o \\
	IOUSBInterface.o \\
	IOUSBLog.o \\
	IOUSBMassStorageClass.o \\
	IOUSBMassStorageClassExtras.o \\
	IOUSBPipe.o \\
	IOUSBUserClient.o \\
	IOWatchDogTimer.o \\
	IOKitServer.o \\
	IOInterruptEventSource.o \\
	IOIterator.o \\
	IOKitDiagnostics.o \\
	IOKitKeys.o \\
	IOLog.o \\
	IOMapper.o \\
	IOMapperEndpoint.o \\
	IOMapperMemoryDescriptor.o \\
	IOMapperSpec.o \\
	IOMapperSpecArray.o \\
	IOMemoryDescriptor.o \\
	IOMPAccess.o \\
	IOMPContainer.o \\
	IOMPDevice.o \\
	IOMPSDevice.o \\
	IOMPT.o \\
	IO80211Interface.o \\
	IO80211Peer.o \\
	IO80211ScanManager.o \\
	IO80211VirtualInterface.o \\
	IOBluetoothDevice.o \\
	IOBluetoothHCIController.o \\
	IOBluetoothHCIControllerTransport.o \\
	IOBluetoothHostControllerUSBTransport.o \\
	IOBluetoothL2CAPChannel.o \\
	IOBluetoothRFCOMMChannel.o \\
	IOBluetoothSDPClient.o \\
	IOBluetoothSDPServer.o \\
	IOBluetoothService.o \\
	IOBluetoothSDPSession.o \\
	IOBluetoothSDPTransaction.o \\
	IOBluetoothServiceRecord.o \\
	IOBluetoothUtility.o \\
	IOEthernetController.o \\
	IOEthernetInterface.o \\
	IONetworkController.o \\
	IONetworkData.o \\
	IONetworkInterface.o \\
	IONetworkMedium.o \\
	IONetworkStats.o \\
	IONetworkUserClient.o \\
	IOPacketFilter.o \\
	IOPacketFilterMonitor.o \\
	IOPacketFilterProvider.o \\
	IOPacketFilterRule.o \\
	IOPacketFilterRuleTable.o \\
	IOPacketFilterRuleTable6.o \\
	IOPacketFilterStats.o \\
	IOPacketFilterUserClient.o \\
	IOPacketFilterUserClient6.o \\
	IOPCIDevice.o \\
	IOPCIFunction.o \\
	IOPCIMessage.o \\
	IOPCIPrimaryMatch.o \\
	IOPCIResource.o \\
	IOPCITunnelCompatible.o \\
	IOPlatformDevice.o \\
	IOPlatformExpert.o \\
	IOPMPowerSource.o \\
	IOPMrootDomain.o \\
	IOPMScheduler.o \\
	IOPoller.o \\
	IOPolicy.o \\
	IOReport.o \\
	IOReportChannel.o \\
	IOReportGroup.o \\
	IOReportGroups.o \\
	IOReportLegend.o \\
	IOReportTypes.o \\
	IOResource.o \\
	IOResourceOwner.o \\
	IOService.o \\
	IOServiceGroup.o \\
	IOServiceMatching.o \\
	IOServiceOrdering.o \\
	IOSharedDataQueue.o \\
	IOSharedDataQueueClient.o \\
	IOStorage.o \\
	IOStorageController.o \\
	IOStorageFamily.o \\
	IOStorageRedundancyController.o \\
	IOStream.o \\
	IOStreamUserClient.o \\
	IOStreamUserClientInterface.o \\
	IOSystemReporter.o \\
	IOTime.o \\
	IOTimeStamp.o \\
	IOTransfer.o \\
	IOUserClient.o \\
	IOUserClientClass.o \\
	IOUserClientMethod.o \\
	IOUserClientNotification.o \\
	IOUserClientProperty.o \\
	IOUserClientRegistry.o \\
	IOUserClientService.o \\
	IOUserClientTask.o \\
	IOUserClientThread.o \\
	IOWorkLoop.o \\
	IOWorkQueue.o \\
	RootDomainUserClient.o \\
	IOBluetoothDevice.o \\
	IOBluetoothHCIController.o \\
	IOBluetoothHCIControllerTransport.o \\
	IOBluetoothHostControllerUSBTransport.o \\
	IOBluetoothL2CAPChannel.o \\
	IOBluetoothRFCOMMChannel.o \\
	IOBluetoothSDPClient.o \\
	IOBluetoothSDPServer.o \\
	IOBluetoothService.o \\
	IOBluetoothSDPSession.o \\
	IOBluetoothSDPTransaction.o \\
	IOBluetoothServiceRecord.o \\
	IOBluetoothUtility.o \\
	IOEthernetController.o \\
	IOEthernetInterface.o \\
	IONetworkController.o \\
	IONetworkData.o \\
	IONetworkInterface.o \\
	IONetworkMedium.o \\
	IONetworkStats.o \\
	IONetworkUserClient.o \\
	IOPacketFilter.o \\
	IOPacketFilterMonitor.o \\
	IOPacketFilterProvider.o \\
	IOPacketFilterRule.o \\
	IOPacketFilterRuleTable.o \\
	IOPacketFilterRuleTable6.o \\
	IOPacketFilterStats.o \\
	IOPacketFilterUserClient.o \\
	IOPacketFilterUserClient6.o \\
	IOPCIDevice.o \\
	IOPCIFunction.o \\
	IOPCIMessage.o \\
	IOPCIPrimaryMatch.o \\
	IOPCIResource.o \\
	IOPCITunnelCompatible.o \\
	IOPlatformDevice.o \\
	IOPlatformExpert.o \\
	IOPMPowerSource.o \\
	IOPMrootDomain.o \\
	IOPMScheduler.o \\
	IOPoller.o \\
	IOPolicy.o \\
	IOReport.o \\
	IOReportChannel.o \\
	IOReportGroup.o \\
	IOReportGroups.o \\
	IOReportLegend.o \\
	IOReportTypes.o \\
	IOResource.o \\
	IOResourceOwner.o \\
	IOService.o \\
	IOServiceGroup.o \\
	IOServiceMatching.o \\
	IOServiceOrdering.o \\
	IOSharedDataQueue.o \\
	IOSharedDataQueueClient.o \\
	IOStorage.o \\
	IOStorageController.o \\
	IOStorageFamily.o \\
	IOStorageRedundancyController.o \\
	IOStream.o \\
	IOStreamUserClient.o \\
	IOStreamUserClientInterface.o \\
	IOSystemReporter.o \\
	IOTime.o \\
	IOTimeStamp.o \\
	IOTransfer.o \\
	IOUserClient.o \\
	IOUserClientClass.o \\
	IOUserClientMethod.o \\
	IOUserClientNotification.o \\
	IOUserClientProperty.o \\
	IOUserClientRegistry.o \\
	IOUserClientService.o \\
	IOUserClientTask.o \\
	IOUserClientThread.o \\
	IOWorkLoop.o \\
	IOWorkQueue.o \\
	RootDomainUserClient.o \\
	IOBluetoothDevice.o \\
	IOBluetoothHCIController.o \\
	IOBluetoothHCIControllerTransport.o \\
	IOBluetoothHostControllerUSBTransport.o \\
	IOBluetoothL2CAPChannel.o \\
	IOBluetoothRFCOMMChannel.o \\
	IOBluetoothSDPClient.o \\
	IOBluetoothSDPServer.o \\
	IOBluetoothService.o \\
	IOBluetoothSDPSession.o \\
	IOBluetoothSDPTransaction.o \\
	IOBluetoothServiceRecord.o \\
	IOBluetoothUtility.o \\
	IOEthernetController.o \\
	IOEthernetInterface.o \\
	IONetworkController.o \\
	IONetworkData.o \\
	IONetworkInterface.o \\
	IONetworkMedium.o \\
	IONetworkStats.o \\
	IONetworkUserClient.o \\
	IOPacketFilter.o \\
	IOPacketFilterMonitor.o \\
	IOPacketFilterProvider.o \\
	IOPacketFilterRule.o \\
	IOPacketFilterRuleTable.o \\
	IOPacketFilterRuleTable6.o \\
	IOPacketFilterStats.o \\
	IOPacketFilterUserClient.o \\
	IOPacketFilterUserClient6.o \\
	IOPCIDevice.o \\
	IOPCIFunction.o \\
	IOPCIMessage.o \\
	IOPCIPrimaryMatch.o \\
	IOPCIResource.o \\
	IOPCITunnelCompatible.o \\
	IOPlatformDevice.o \\
	IOPlatformExpert.o \\
	IOPMPowerSource.o \\
	IOPMrootDomain.o \\
	IOPMScheduler.o \\
	IOPoller.o \\
	IOPolicy.o \\
	IOReport.o \\
	IOReportChannel.o \\
	IOReportGroup.o \\
	IOReportGroups.o \\
	IOReportLegend.o \\
	IOReportTypes.o \\
	IOResource.o \\
	IOResourceOwner.o \\
	IOService.o \\
	IOServiceGroup.o \\
	IOServiceMatching.o \\
	IOServiceOrdering.o \\
	IOSharedDataQueue.o \\
	IOSharedDataQueueClient.o \\
	IOStorage.o \\
	IOStorageController.o \\
	IOStorageFamily.o \\
	IOStorageRedundancyController.o \\
	IOStream.o \\
	IOStreamUserClient.o \\
	IOStreamUserClientInterface.o \\
	IOSystemReporter.o \\
	IOTime.o \\
	IOTimeStamp.o \\
	IOTransfer.o \\
	IOUserClient.o \\
	IOUserClientClass.o \\
	IOUserClientMethod.o \\
	IOUserClientNotification.o \\
	IOUserClientProperty.o \\
	IOUserClientRegistry.o \\
	IOUserClientService.o \\
	IOUserClientTask.o \\
	IOUserClientThread.o \\
	IOWorkLoop.o \\
	IOWorkQueue.o \\
	RootDomainUserClient.o \\
	IOBluetoothDevice.o \\
	IOBluetoothHCIController.o \\
	IOBluetoothHCIControllerTransport.o \\
	IOBluetoothHostControllerUSBTransport.o \\
	IOBluetoothL2CAPChannel.o \\
	IOBluetoothRFCOMMChannel.o \\
	IOBluetoothSDPClient.o \\
	IOBluetoothSDPServer.o \\
	IOBluetoothService.o \\
	IOBluetoothSDPSession.o \\
	IOBluetoothSDPTransaction.o \\
	IOBluetoothServiceRecord.o \\
	IOBluetoothUtility.o \\
	IOEthernetController.o \\
	IOEthernetInterface.o \\
	IONetworkController.o \\
	IONetworkData.o \\
	IONetworkInterface.o \\
	IONetworkMedium.o \\
	IONetworkStats.o \\
	IONetworkUserClient.o \\
	IOPacketFilter.o \\
	IOPacketFilterMonitor.o \\
	IOPacketFilterProvider.o \\
	IOPacketFilterRule.o \\
	IOPacketFilterRuleTable.o \\
	IOPacketFilterRuleTable6.o \\
	IOPacketFilterStats.o \\
	IOPacketFilterUserClient.o \\
	IOPacketFilterUserClient6.o \\
	IOPCIDevice.o \\
	IOPCIFunction.o \\
	IOPCIMessage.o \\
	IOPCIPrimaryMatch.o \\
	IOPCIResource.o \\
	IOPCITunnelCompatible.o \\
	IOPlatformDevice.o \\
	IOPlatformExpert.o \\
	IOPMPowerSource.o \\
	IOPMrootDomain.o \\
	IOPMScheduler.o \\
	IOPoller.o \\
	IOPolicy.o \\
	IOReport.o \\
	IOReportChannel.o \\
	IOReportGroup.o \\
	IOReportGroups.o \\
	IOReportLegend.o \\
	IOReportTypes.o \\
	IOResource.o \\
	IOResourceOwner.o \\
	IOService.o \\
	IOServiceGroup.o \\
	IOServiceMatching.o \\
	IOServiceOrdering.o \\
	IOSharedDataQueue.o \\
	IOSharedDataQueueClient.o \\
	IOStorage.o \\
	IOStorageController.o \\
	IOStorageFamily.o \\
	IOStorageRedundancyController.o \\
	IOStream.o \\
	IOStreamUserClient.o \\
	IOStreamUserClientInterface.o \\
	IOSystemReporter.o \\
	IOTime.o \\
	IOTimeStamp.o \\
	IOTransfer.o \\
	IOUserClient.o \\
	IOUserClientClass.o \\
	IOUserClientMethod.o \\
	IOUserClientNotification.o \\
	IOUserClientProperty.o \\
	IOUserClientRegistry.o \\
	IOUserClientService.o \\
	IOUserClientTask.o \\
	IOUserClientThread.o \\
	IOWorkLoop.o \\
	IOWorkQueue.o \\
	RootDomainUserClient.o \\
	IOBluetoothDevice.o \\
	IOBluetoothHCIController.o \\
	IOBluetoothHCIControllerTransport.o \\
	IOBluetoothHostControllerUSBTransport.o \\
	IOBluetoothL2CAPChannel.o \\
	IOBluetoothRFCOMMChannel.o \\
	IOBluetoothSDPClient.o \\
	IOBluetoothSDPServer.o \\
	IOBluetoothService.o \\
	IOBluetoothSDPSession.o \\
	IOBluetoothSDPTransaction.o \\
	IOBluetoothServiceRecord.o \\
	IOBluetoothUtility.o \\
	IOEthernetController.o \\
	IOEthernetInterface.o \\
	IONetworkController.o \\
	IONetworkData.o \\
	IONetworkInterface.o \\
	IONetworkMedium.o \\
	IONetworkStats.o \\
	IONetworkUserClient.o \\
	IOPacketFilter.o \\
	IOPacketFilterMonitor.o \\
	IOPacketFilterProvider.o \\
	IOPacketFilterRule.o \\
	IOPacketFilterRuleTable.o \\
	IOPacketFilterRuleTable6.o \\
	IOPacketFilterStats.o \\
	IOPacketFilterUserClient.o \\
	IOPacketFilterUserClient6.o \\
	IOPCIDevice.o \\
	IOPCIFunction.o \\
	IOPCIMessage.o \\
	IOPCIPrimaryMatch.o \\
	IOPCIResource.o \\
	IOPCITunnelCompatible.o \\
	IOPlatformDevice.o \\
	IOPlatformExpert.o \\
	IOPMPowerSource.o \\
	IOPMrootDomain.o \\
	IOPMScheduler.o \\
	IOPoller.o \\
	IOPolicy.o \\
	IOReport.o \\
	IOReportChannel.o \\
	IOReportGroup.o \\
	IOReportGroups.o \\
	IOReportLegend.o \\
	IOReportTypes.o \\
	IOResource.o \\
	IOResourceOwner.o \\
	IOService.o \\
	IOServiceGroup.o \\
	IOServiceMatching.o \\
	IOServiceOrdering.o \\
	IOSharedDataQueue.o \\
	IOSharedDataQueueClient.o \\
	IOStorage.o \\
	IOStorageController.o \\
	IOStorageFamily.o \\
	IOStorageRedundancyController.o \\
	IOStream.o \\
	IOStreamUserClient.o \\
	IOStreamUserClientInterface.o \\
	IOSystemReporter.o \\
	IOTime.o \\
	IOTimeStamp.o \\
	IOTransfer.o \\
	IOUserClient.o \\
	IOUserClientClass.o \\
	IOUserClientMethod.o \\
	IOUserClientNotification.o \\
	IOUserClientProperty.o \\
	IOUserClientRegistry.o \\
	IOUserClientService.o \\
	IOUserClientTask.o \\
	IOUserClientThread.o \\
	IOWorkLoop.o \\
	IOWorkQueue.o \\
	RootDomainUserClient.o \\
	IOBluetoothDevice.o \\
	IOBluetoothHCIController.o \\
	IOBluetoothHCIControllerTransport.o \\
	IOBluetoothHostControllerUSBTransport.o \\
	IOBluetoothL2CAPChannel.o \\
	IOBluetoothRFCOMMChannel.o \\
	IOBluetoothSDPClient.o \\
	IOBluetoothSDPServer.o \\
	IOBluetoothService.o \\
	IOBluetoothSDPSession.o \\
	IOBluetoothSDPTransaction.o \\
	IOBluetoothServiceRecord.o \\
	IOBluetoothUtility.o \\
	IOEthernetController.o \\
	IOEthernetInterface.o \\
	IONetworkController.o \\
	IONetworkData.o \\
	IONetworkInterface.o \\
	IONetworkMedium.o \\
	IONetworkStats.o \\
	IONetworkUserClient.o \\
	IOPacketFilter.o \\
	IOPacketFilterMonitor.o \\
	IOPacketFilterProvider.o \\
	IOPacketFilterRule.o \\
	IOPacketFilterRuleTable.o \\
	IOPacketFilterRuleTable6.o \\
	IOPacketFilterStats.o \\
	IOPacketFilterUserClient.o \\
	IOPacketFilterUserClient6.o \\
	IOPCIDevice.o \\
	IOPCIFunction.o \\
	IOPCIMessage.o \\
	IOPCIPrimaryMatch.o \\
	IOPCIResource.o \\
	IOPCITunnelCompatible.o \\
	IOPlatformDevice.o \\
	IOPlatformExpert.o \\
	IOPMPowerSource.o \\
	IOPMrootDomain.o \\
	IOPMScheduler.o \\
	IOPoller.o \\
	IOPolicy.o \\
	IOReport.o \\
	IOReportChannel.o \\
	IOReportGroup.o \\
	IOReportGroups.o \\
	IOReportLegend.o \\
	IOReportTypes.o \\
	IOResource.o \\
	IOResourceOwner.o \\
	IOService.o \\
	IOServiceGroup.o \\
	IOServiceMatching.o \\
	IOServiceOrdering.o \\
	IOSharedDataQueue.o \\
	IOSharedDataQueueClient.o \\
	IOStorage.o \\
	IOStorageController.o \\
	IOStorageFamily.o \\
	IOStorageRedundancyController.o \\
	IOStream.o \\
	IOStreamUserClient.o \\
	IOStreamUserClientInterface.o \\
	IOSystemReporter.o \\
	IOTime.o \\
	IOTimeStamp.o \\
	IOTransfer.o \\
	IOUserClient.o \\
	IOUserClientClass.o \\
	IOUserClientMethod.o \\
	IOUserClientNotification.o \\
	IOUserClientProperty.o \\
	IOUserClientRegistry.o \\
	IOUserClientService.o \\
	IOUserClientTask.o \\
	IOUserClientThread.o \\
	IOWorkLoop.o \\
	IOWorkQueue.o \\
	RootDomainUserClient.o \\
	IOBluetoothDevice.o \\
	IOBluetoothHCIController.o \\
	IOBluetoothHCIControllerTransport.o \\
	IOBluetoothHostControllerUSBTransport.o \\
	IOBluetoothL2CAPChannel.o \\
	IOBluetoothRFCOMMChannel.o \\
	IOBluetoothSDPClient.o \\
	IOBluetoothSDPServer.o \\
	IOBluetoothService.o \\
	IOBluetoothSDPSession.o \\
	IOBluetoothSDPTransaction.o \\
	IOBluetoothServiceRecord.o \\
	IOBluetoothUtility.o \\
	IOEthernetController.o \\
	IOEthernetInterface.o \\
	IONetworkController.o \\
	IONetworkData.o \\
	IONetworkInterface.o \\
	IONetworkMedium.o \\
	IONetworkStats.o \\
	IONetworkUserClient.o \\
	IOPacketFilter.o \\
	IOPacketFilterMonitor.o \\
	IOPacketFilterProvider.o \\
	IOPacketFilterRule.o \\
	IOPacketFilterRuleTable.o \\
	IOPacketFilterRuleTable6.o \\
	IOPacketFilterStats.o \\
	IOPacketFilterUserClient.o \\
	IOPacketFilterUserClient6.o \\
	IOPCIDevice.o \\
	IOPCIFunction.o \\
	IOPCIMessage.o \\
	IOPCIPrimaryMatch.o \\
	IOPCIResource.o \\
	IOPCITunnelCompatible.o \\
	IOPlatformDevice.o \\
	IOPlatformExpert.o \\
	IOPMPowerSource.o \\
	IOPMrootDomain.o \\
	IOPMScheduler.o \\
	IOPoller.o \\
	IOPolicy.o \\
	IOReport.o \\
	IOReportChannel.o \\
	IOReportGroup.o \\
	IOReportGroups.o \\
	IOReportLegend.o \\
	IOReportTypes.o \\
	IOResource.o \\
	IOResourceOwner.o \\
	IOService.o \\
	IOServiceGroup.o \\
	IOServiceMatching.o \\
	IOServiceOrdering.o \\
	IOSharedDataQueue.o \\
	IOSharedDataQueueClient.o \\
	IOStorage.o \\
	IOStorageController.o \\
	IOStorageFamily.o \\
	IOStorageRedundancyController.o \\
	IOStream.o \\
	IOStreamUserClient.o \\
	IOStreamUserClientInterface.o \\
	IOSystemReporter.o \\
	IOTime.o \\
	IOTimeStamp.o \\
	IOTransfer.o \\
	IOUserClient.o \\
	IOUserClientClass.o \\
	IOUserClientMethod.o \\
	IOUserClientNotification.o \\
	IOUserClientProperty.o \\
	IOUserClientRegistry.o \\
	IOUserClientService.o \\
	IOUserClientTask.o \\
	IOUserClientThread.o \\
	IOWorkLoop.o \\
	IOWorkQueue.o \\
	RootDomainUserClient.o \\
	IOBluetoothDevice.o \\
	IOBluetoothHCIController.o \\
	IOBluetoothHCIControllerTransport.o \\
	IOBluetoothHostControllerUSBTransport.o \\
	IOBluetoothL2CAPChannel.o \\
	IOBluetoothRFCOMMChannel.o \\
	IOBluetoothSDPClient.o \\
	IOBluetoothSDPServer.o \\
	IOBluetoothService.o \\
	IOBluetoothSDPSession.o \\
	IOBluetoothSDPTransaction.o \\
	IOBluetoothServiceRecord.o \\
	IOBluetoothUtility.o \\
	IOEthernetController.o \\
	IOEthernetInterface.o \\
	IONetworkController.o \\
	IONetworkData.o \\
	IONetworkInterface.o \\
	IONetworkMedium.o \\
	IONetworkStats.o \\
	IONetworkUserClient.o \\
	IOPacketFilter.o \\
	IOPacketFilterMonitor.o \\
	IOPacketFilterProvider.o \\
	IOPacketFilterRule.o \\
	IOPacketFilterRuleTable.o \\
	IOPacketFilterRuleTable6.o \\
	IOPacketFilterStats.o \\
	IOPacketFilterUserClient.o \\
	IOPacketFilterUserClient6.o \\
	IOPCIDevice.o \\
	IOPCIFunction.o \\
	IOPCIMessage.o \\
	IOPCIPrimaryMatch.o \\
	IOPCIResource.o \\
	IOPCITunnelCompatible.o \\
	IOPlatformDevice.o \\
	IOPlatformExpert.o \\
	IOPMPowerSource.o \\
	IOPMrootDomain.o \\
	IOPMScheduler.o \\
	IOPoller.o \\
	IOPolicy.o \\
	IOReport.o \\
	IOReportChannel.o \\
	IOReportGroup.o \\
	IOReportGroups.o \\
	IOReportLegend.o \\
	IOReportTypes.o \\
	IOResource.o \\
	IOResourceOwner.o \\
	IOService.o \\
	IOServiceGroup.o \\
	IOServiceMatching.o \\
	IOServiceOrdering.o \\
	IOSharedDataQueue.o \\
	IOSharedDataQueueClient.o \\
	IOStorage.o \\
	IOStorageController.o \\
	IOStorageFamily.o \\
	IOStorageRedundancyController.o \\
	IOStream.o \\
	IOStreamUserClient.o \\
	IOStreamUserClientInterface.o \\
	IOSystemReporter.o \\
	IOTime.o \\
	IOTimeStamp.o \\
	IOTransfer.o \\
	IOUserClient.o \\
	IOUserClientClass.o \\
	IOUserClientMethod.o \\
	IOUserClientNotification.o \\
	IOUserClientProperty.o \\
	IOUserClientRegistry.o \\
	IOUserClientService.o \\
	IOUserClientTask.o \\
	IOUserClientThread.o \\
	IOWorkLoop.o \\
	IOWorkQueue.o \\
	RootDomainUserClient.o \\
	IOBluetoothDevice.o \\
	IOBluetoothHCIController.o \\
	IOBluetoothHCIControllerTransport.o \\
	IOBluetoothHostControllerUSBTransport.o \\
	IOBluetoothL2CAPChannel.o \\
	IOBluetoothRFCOMMChannel.o \\
	IOBluetoothSDPClient.o \\
	IOBluetoothSDPServer.o \\
	IOBluetoothService.o \\
	IOBluetoothSDPSession.o \\
	IOBluetoothSDPTransaction.o \\
	IOBluetoothServiceRecord.o \\
	IOBluetoothUtility.o \\
	IOEthernetController.o \\
	IOEthernetInterface.o \\
	IONetworkController.o \\
	IONetworkData.o \\
	IONetworkInterface.o \\
	IONetworkMedium.o \\
	IONetworkStats.o \\
	IONetworkUserClient.o \\
	IOPacketFilter.o \\
	IOPacketFilterMonitor.o \\
	IOPacketFilterProvider.o \\
	IOPacketFilterRule.o \\
	IOPacketFilterRuleTable.o \\
	IOPacketFilterRuleTable6.o \\
	IOPacketFilterStats.o \\
	IOPacketFilterUserClient.o \\
	IOPacketFilterUserClient6.o \\
	IOPCIDevice.o \\
	IOPCIFunction.o \\
	IOPCIMessage.o \\
	IOPCIPrimaryMatch.o \\
	IOPCIResource.o \\
	IOPCITunnelCompatible.o \\
	IOPlatformDevice.o \\
	IOPlatformExpert.o \\
	IOPMPowerSource.o \\
	IOPMrootDomain.o \\
	IOPMScheduler.o \\
	IOPoller.o \\
	IOPolicy.o \\
	IOReport.o \\
	IOReportChannel.o \\
	IOReportGroup.o \\
	IOReportGroups.o \\
	IOReportLegend.o \\
	IOReportTypes.o \\
	IOResource.o \\
	IOResourceOwner.o \\
	IOService.o \\
	IOServiceGroup.o \\
	IOServiceMatching.o \\
	IOServiceOrdering.o \\
	IOSharedDataQueue.o \\
	IOSharedDataQueueClient.o \\
	IOStorage.o \\
	IOStorageController.o \\
	IOStorageFamily.o \\
	IOStorageRedundancyController.o \\
	IOStream.o \\
	IOStreamUserClient.o \\
	IOStreamUserClientInterface.o \\
	IOSystemReporter.o \\
	IOTime.o \\
	IOTimeStamp.o \\
	IOTransfer.o \\
	IOUserClient.o \\
	IOUserClientClass.o \\
	IOUserClientMethod.o \\
	IOUserClientNotification.o \\
	IOUserClientProperty.o \\
	IOUserClientRegistry.o \\
	IOUserClientService.o \\
	IOUserClientTask.o \\
	IOUserClientThread.o \\
	IOWorkLoop.o \\
	IOWorkQueue.o \\
	RootDomainUserClient.o \\
	IOBluetoothDevice.o \\
	IOBluetoothHCIController.o \\
	IOBluetoothHCIControllerTransport.o \\
	IOBluetoothHostControllerUSBTransport.o \\
	IOBluetoothL2CAPChannel.o \\
	IOBluetoothRFCOMMChannel.o \\
	IOBluetoothSDPClient.o \\
	IOBluetoothSDPServer.o \\
	IOBluetoothService.o \\
	IOBluetoothSDPSession.o \\
	IOBluetoothSDPTransaction.o \\
	IOBluetoothServiceRecord.o \\
	IOBluetoothUtility.o \\
	IOEthernetController.o \\
	IOEthernetInterface.o \\
	IONetworkController.o \\
	IONetworkData.o \\
	IONetworkInterface.o \\
	IONetworkMedium.o \\
	IONetworkStats.o \\
	IONetworkUserClient.o \\
	IOPacketFilter.o \\
	IOPacketFilterMonitor.o \\
	IOPacketFilterProvider.o \\
	IOPacketFilterRule.o \\
	IOPacketFilterRuleTable.o \\
	IOPacketFilterRuleTable6.o \\
	IOPacketFilterStats.o \\
	IOPacketFilterUserClient.o \\
	IOPacketFilterUserClient6.o \\
	IOPCIDevice.o \\
	IOPCIFunction.o \\
	IOPCIMessage.o \\
	IOPCIPrimaryMatch.o \\
	IOPCIResource.o \\
	IOPCITunnelCompatible.o \\
	IOPlatformDevice.o \\
	IOPlatformExpert.o \\
	IOPMPowerSource.o \\
	IOPMrootDomain.o \\
	IOPMScheduler.o \\
	IOPoller.o \\
	IOPolicy.o \\
	IOReport.o \\
	IOReportChannel.o \\
	IOReportGroup.o \\
	IOReportGroups.o \\
	IOReportLegend.o \\
	IOReportTypes.o \\
	IOResource.o \\
	IOResourceOwner.o \\
	IOService.o \\
	IOServiceGroup.o \\
	IOServiceMatching.o \\
	IOServiceOrdering.o \\
	IOSharedDataQueue.o \\
	IOSharedDataQueueClient.o \\
	IOStorage.o \\
	IOStorageController.o \\
	IOStorageFamily.o \\
	IOStorageRedundancyController.o \\
	IOStream.o \\
	IOStreamUserClient.o \\
	IOStreamUserClientInterface.o \\
	IOSystemReporter.o \\
	IOTime.o \\
	IOTimeStamp.o \\
	IOTransfer.o \\
	IOUserClient.o \\
	IOUserClientClass.o \\
	IOUserClientMethod.o \\
	IOUserClientNotification.o \\
	IOUserClientProperty.o \\
	IOUserClientRegistry.o \\
	IOUserClientService.o \\
	IOUserClientTask.o \\
	IOUserClientThread.o \\
	IOWorkLoop.o \\
	IOWorkQueue.o \\
	RootDomainUserClient.o \\
	IOBluetoothDevice.o \\
	IOBluetoothHCIController.o \\
	IOBluetoothHCIControllerTransport.o \\
	IOBluetoothHostControllerUSBTransport.o \\
	IOBluetoothL2CAPChannel.o \\
	IOBluetoothRFCOMMChannel.o \\
	IOBluetoothSDPClient.o \\
	IOBluetoothSDPServer.o \\
	IOBluetoothService.o \\
	IOBluetoothSDPSession.o \\
	IOBluetoothSDPTransaction.o \\
	IOBluetoothServiceRecord.o \\
	IOBluetoothUtility.o \\
	IOEthernetController.o \\
	IOEthernetInterface.o \\
	IONetworkController.o \\
	IONetworkData.o \\
	IONetworkInterface.o \\
	IONetworkMedium.o \\
	IONetworkStats.o \\
	IONetworkUserClient.o \\
	IOPacketFilter.o \\
	IOPacketFilterMonitor.o \\
	IOPacketFilterProvider.o \\
	IOPacketFilterRule.o \\
	IOPacketFilterRuleTable.o \\
	IOPacketFilterRuleTable6.o \\
	IOPacketFilterStats.o \\
	IOPacketFilterUserClient.o \\
	IOPacketFilterUserClient6.o \\
	IOPCIDevice.o \\
	IOPCIFunction.o \\
	IOPCIMessage.o \\
	IOPCIPrimaryMatch.o \\
	IOPCIResource.o \\
	IOPCITunnelCompatible.o \\
	IOPlatformDevice.o \\
	IOPlatformExpert.o \\
	IOPMPowerSource.o \\
	IOPMrootDomain.o \\
	IOPMScheduler.o \\
	IOPoller.o \\
	IOPolicy.o \\
	IOReport.o \\
	IOReportChannel.o \\
	IOReportGroup.o \\
	IOReportGroups.o \\
	IOReportLegend.o \\
	IOReportTypes.o \\
	IOResource.o \\
	IOResourceOwner.o \\
	IOService.o \\
	IOServiceGroup.o \\
	IOServiceMatching.o \\
	IOServiceOrdering.o \\
	IOSharedDataQueue.o \\
	IOSharedDataQueueClient.o \\
	IOStorage.o \\
	IOStorageController.o \\
	IOStorageFamily.o \\
	IOStorageRedundancyController.o \\
	IOStream.o \\
	IOStreamUserClient.o \\
	IOStreamUserClientInterface.o \\
	IOSystemReporter.o \\
	IOTime.o \\
	IOTimeStamp.o \\
	IOTransfer.o \\
	IOUserClient.o \\
	IOUserClientClass.o \\
	IOUserClientMethod.o \\
	IOUserClientNotification.o \\
	IOUserClientProperty.o \\
	IOUserClientRegistry.o \\
	IOUserClientService.o \\
	IOUserClientTask.o \\
	IOUserClientThread.o \\
	IOWorkLoop.o \\
	IOWorkQueue.o \\
	RootDomainUserClient.o \\
	IOBluetoothDevice.o \\
	IOBluetoothHCIController.o \\
	IOBluetoothHCIControllerTransport.o \\
	IOBluetoothHostControllerUSBTransport.o \\
	IOBluetoothL2CAPChannel.o \\
	IOBluetoothRFCOMMChannel.o \\
	IOBluetoothSDPClient.o \\
	IOBluetoothSDPServer.o \\
	IOBluetoothService.o \\
	IOBluetoothSDPSession.o \\
	IOBluetoothSDPTransaction.o \\
	IOBluetoothServiceRecord.o \\
	IOBluetoothUtility.o \\
	IOEthernetController.o \\
	IOEthernetInterface.o \\
	IONetworkController.o \\
	IONetworkData.o \\
	IONetworkInterface.o \\
	IONetworkMedium.o \\
	IONetworkStats.o \\
	IONetworkUserClient.o \\
	IOPacketFilter.o \\
	IOPacketFilterMonitor.o \\
	IOPacketFilterProvider.o \\
	IOPacketFilterRule.o \\
	IOPacketFilterRuleTable.o \\
	IOPacketFilterRuleTable6.o \\
	IOPacketFilterStats.o \\
	IOPacketFilterUserClient.o \\
	IOPacketFilterUserClient6.o \\
	IOPCIDevice.o \\
	IOPCIFunction.o \\
	IOPCIMessage.o \\
	IOPCIPrimaryMatch.o \\
	IOPCIResource.o \\
	IOPCITunnelCompatible.o \\
	IOPlatformDevice.o \\
	IOPlatformExpert.o \\
	IOPMPowerSource.o \\
	IOPMrootDomain.o \\
	IOPMScheduler.o \\
	IOPoller.o \\
	IOPolicy.o \\
	IOReport.o \\
	IOReportChannel.o \\
	IOReportGroup.o \\
	IOReportGroups.o \\
	IOReportLegend.o \\
	IOReportTypes.o \\
	IOResource.o \\
	IOResourceOwner.o \\
	IOService.o \\
	IOServiceGroup.o \\
	IOServiceMatching.o \\
	IOServiceOrdering.o \\
	IOSharedDataQueue.o \\
	IOSharedDataQueueClient.o \\
	IOStorage.o \\
	IOStorageController.o \\
	IOStorageFamily.o \\
	IOStorageRedundancyController.o \\
	IOStream.o \\
	IOStreamUserClient.o \\
	IOStreamUserClientInterface.o \\
	IOSystemReporter.o \\
	IOTime.o \\
	IOTimeStamp.o \\
	IOTransfer.o \\
	IOUserClient.o \\
	IOUserClientClass.o \\
	IOUserClientMethod.o \\
	IOUserClientNotification.o \\
	IOUserClientProperty.o \\
	IOUserClientRegistry.o \\
	IOUserClientService.o \\
	IOUserClientTask.o \\
	IOUserClientThread.o \\
	IOWorkLoop.o \\
	IOWorkQueue.o \\
	RootDomainUserClient.o \\
	IOBluetoothDevice.o \\
	IOBluetoothHCIController.o \\
	IOBluetoothHCIControllerTransport.o \\
	IOBluetoothHostControllerUSBTransport.o \\
	IOBluetoothL2CAPChannel.o \\
	IOBluetoothRFCOMMChannel.o \\
	IOBluetoothSDPClient.o \\
	IOBluetoothSDPServer.o \\
	IOBluetoothService.o \\
	IOBluetoothSDPSession.o \\
	IOBluetoothSDPTransaction.o \\
	IOBluetoothServiceRecord.o \\
	IOBluetoothUtility.o \\
	IOEthernetController.o \\
	IOEthernetInterface.o \\
	IONetworkController.o \\
	IONetworkData.o \\
	IONetworkInterface.o \\
	IONetworkMedium.o \\
	IONetworkStats.o \\
	IONetworkUserClient.o \\
	IOPacketFilter.o \\
	IOPacketFilterMonitor.o \\
	IOPacketFilterProvider.o \\
	IOPacketFilterRule.o \\
	IOPacketFilterRuleTable.o \\
	IOPacketFilterRuleTable6.o \\
	IOPacketFilterStats.o \\
	IOPacketFilterUserClient.o \\
	IOPacketFilterUserClient6.o \\
	IOPCIDevice.o \\
	IOPCIFunction.o \\
	IOPCIMessage.o \\
	IOPCIPrimaryMatch.o \\
	IOPCIResource.o \\
	IOPCITunnelCompatible.o \\
	IOPlatformDevice.o \\
	IOPlatformExpert.o \\
	IOPMPowerSource.o \\
	IOPMrootDomain.o \\
	IOPMScheduler.o \\
	IOPoller.o \\
	IOPolicy.o \\
	IOReport.o \\
	IOReportChannel.o \\
	IOReportGroup.o \\
	IOReportGroups.o \\
	IOReportLegend.o \\
	IOReportTypes.o \\
	IOResource.o \\
	IOResourceOwner.o \\
	IOService.o \\
	IOServiceGroup.o \\
	IOServiceMatching.o \\
	IOServiceOrdering.o \\
	IOSharedDataQueue.o \\
	IOSharedDataQueueClient.o \\
	IOStorage.o \\
	IOStorageController.o \\
	IOStorageFamily.o \\
	IOStorageRedundancyController.o \\
	IOStream.o \\
	IOStreamUserClient.o \\
	IOStreamUserClientInterface.o \\
	IOSystemReporter.o \\
	IOTime.o \\
	IOTimeStamp.o \\
	IOTransfer.o \\
	IOUserClient.o \\
	IOUserClientClass.o \\
	IOUserClientMethod.o \\
	IOUserClientNotification.o \\
	IOUserClientProperty.o \\
	IOUserClientRegistry.o \\
	IOUserClientService.o \\
	IOUserClientTask.o \\
	IOUserClientThread.o \\
	IOWorkLoop.o \\
	IOWorkQueue.o \\
	RootDomainUserClient.o \\
	IOBluetoothDevice.o \\
	IOBluetoothHCIController.o \\
	IOBluetoothHCIControllerTransport.o \\
	IOBluetoothHostControllerUSBTransport.o \\
	IOBluetoothL2CAPChannel.o \\
	IOBluetoothRFCOMMChannel.o \\
	IOBluetoothSDPClient.o \\
	IOBluetoothSDPServer.o \\
	IOBluetoothService.o \\
	IOBluetoothSDPSession.o \\
	IOBluetoothSDPTransaction.o \\
	IOBluetoothServiceRecord.o \\
	IOBluetoothUtility.o \\
	IOEthernetController.o \\
	IOEthernetInterface.o \\
	IONetworkController.o \\
	IONetworkData.o \\
	IONetworkInterface.o \\
	IONetworkMedium.o \\
	IONetworkStats.o \\
	IONetworkUserClient.o \\
	IOPacketFilter.o \\
	IOPacketFilterMonitor.o \\
	IOPacketFilterProvider.o \\
	IOPacketFilterRule.o \\
	IOPacketFilterRuleTable.o \\
	IOPacketFilterRuleTable6.o \\
	IOPacketFilterStats.o \\
	IOPacketFilterUserClient.o \\
	IOPacketFilterUserClient6.o \\
	IOPCIDevice.o \\
	IOPCIFunction.o \\
	IOPCIMessage.o \\
	IOPCIPrimaryMatch.o \\
	IOPCIResource.o \\
	IOPCITunnelCompatible.o \\
	IOPlatformDevice.o \\
	IOPlatformExpert.o \\
	IOPMPowerSource.o \\
	IOPMrootDomain.o \\
	IOPMScheduler.o \\
	IOPoller.o \\
	IOPolicy.o \\
	IOReport.o \\
	IOReportChannel.o \\
	IOReportGroup.o \\
	IOReportGroups.o \\
	IOReportLegend.o \\
	IOReportTypes.o \\
	IOResource.o \\
	IOResourceOwner.o \\
	IOService.o \\
	IOServiceGroup.o \\
	IOServiceMatching.o \\
	IOServiceOrdering.o \\
	IOSharedDataQueue.o \\
	IOSharedDataQueueClient.o \\
	IOStorage.o \\
	IOStorageController.o \\
	IOStorageFamily.o \\
	IOStorageRedundancyController.o \\
	IOStream.o \\
	IOStreamUserClient.o \\
	IOStreamUserClientInterface.o \\
	IOSystemReporter.o \\
	IOTime.o \\
	IOTimeStamp.o \\
	IOTransfer.o \\
	IOUserClient.o \\
	IOUserClientClass.o \\
	IOUserClientMethod.o \\
	IOUserClientNotification.o \\
	IOUserClientProperty.o \\
	IOUserClientRegistry.o \\
	IOUserClientService.o \\
	IOUserClientTask.o \\
	IOUserClientThread.o \\
	IOWorkLoop.o \\
	IOWorkQueue.o \\
	RootDomainUserClient.o \\
	IOBluetoothDevice.o \\
	IOBluetoothHCIController.o \\
	IOBluetoothHCIControllerTransport.o \\
	IOBluetoothHostControllerUSBTransport.o \\
	IOBluetoothL2CAPChannel.o \\
	IOBluetoothRFCOMMChannel.o \\
	IOBluetoothSDPClient.o \\
	IOBluetoothSDPServer.o \\
	IOBluetoothService.o \\
	IOBluetoothSDPSession.o \\
	IOBluetoothSDPTransaction.o \\
	IOBluetoothServiceRecord.o \\
	IOBluetoothUtility.o \\
	IOEthernetController.o \\
	IOEthernetInterface.o \\
	IONetworkController.o \\
	IONetworkData.o \\
	IONetworkInterface.o \\
	IONetworkMedium.o \\
	IONetworkStats.o \\
	IONetworkUserClient.o \\
	IOPacketFilter.o \\
	IOPacketFilterMonitor.o \\
	IOPacketFilterProvider.o \\
	IOPacketFilterRule.o \\
	IOPacketFilterRuleTable.o \\
	IOPacketFilterRuleTable6.o \\
	IOPacketFilterStats.o \\
	IOPacketFilterUserClient.o \\
	IOPacketFilterUserClient6.o \\
	IOPCIDevice.o \\
	IOPCIFunction.o \\
	IOPCIMessage.o \\
	IOPCIPrimaryMatch.o \\
	IOPCIResource.o \\
	IOPCITunnelCompatible.o \\
	IOPlatformDevice.o \\
	IOPlatformExpert.o \\
	IOPMPowerSource.o \\
	IOPMrootDomain.o \\
	IOPMScheduler.o \\
	IOPoller.o \\
	IOPolicy.o \\
	IOReport.o \\
	IOReportChannel.o \\
	IOReportGroup.o \\
	IOReportGroups.o \\
	IOReportLegend.o \\
	IOReportTypes.o \\
	IOResource.o \\
	IOResourceOwner.o \\
	IOService.o \\
	IOServiceGroup.o \\
	IOServiceMatching.o \\
	IOServiceOrdering.o \\
	IOSharedDataQueue.o \\
	IOSharedDataQueueClient.o \\
	IOStorage.o \\
	IOStorageController.o \\
	IOStorageFamily.o \\
	IOStorageRedundancyController.o \\
	IOStream.o \\
	IOStreamUserClient.o \\
	IOStreamUserClientInterface.o \\
	IOSystemReporter.o \\
	IOTime.o \\
	IOTimeStamp.o \\
	IOTransfer.o \\
	IOUserClient.o \\
	IOUserClientClass.o \\
	IOUserClientMethod.o \\
	IOUserClientNotification.o \\
	IOUserClientProperty.o \\
	IOUserClientRegistry.o \\
	IOUserClientService.o \\
	IOUserClientTask.o \\
	IOUserClientThread.o \\
	IOWorkLoop.o \\
	IOWorkQueue.o \\
	RootDomainUserClient.o \\
	IOBluetoothDevice.o \\
	IOBluetoothHCIController.o \\
	IOBluetoothHCIControllerTransport.o \\
	IOBluetoothHostControllerUSBTransport.o \\
	IOBluetoothL2CAPChannel.o \\
	IOBluetoothRFCOMMChannel.o \\
	IOBluetoothSDPClient.o \\
	IOBluetoothSDPServer.o \\
	IOBluetoothService.o \\
	IOBluetoothSDPSession.o \\
	IOBluetoothSDPTransaction.o \\
	IOBluetoothServiceRecord.o \\
	IOBluetoothUtility.o \\
	IOEthernetController.o \\
	IOEthernetInterface.o \\
	IONetworkController.o \\
	IONetworkData.o \\
	IONetworkInterface.o \\
	IONetworkMedium.o \\
	IONetworkStats.o \\
	IONetworkUserClient.o \\
	IOPacketFilter.o \\
	IOPacketFilterMonitor.o \\
	IOPacketFilterProvider.o \\
	IOPacketFilterRule.o \\
	IOPacketFilterRuleTable.o \\
	IOPacketFilterRuleTable6.o \\
	IOPacketFilterStats.o \\
	IOPacketFilterUserClient.o \\
	IOPacketFilterUserClient6.o \\
	IOPCIDevice.o \\
	IOPCIFunction.o \\
	IOPCIMessage.o \\
	IOPCIPrimaryMatch.o \\
	IOPCIResource.o \\
	IOPCITunnelCompatible.o \\
	IOPlatformDevice.o \\
	IOPlatformExpert.o \\
	IOPMPowerSource.o \\
	IOPMrootDomain.o \\
	IOPMScheduler.o \\
	IOPoller.o \\
	IOPolicy.o \\
	IOReport.o \\
	IOReportChannel.o \\
	IOReportGroup.o \\
	IOReportGroups.o \\
	IOReportLegend.o \\
	IOReportTypes.o \\
	IOResource.o \\
	IOResourceOwner.o \\
	IOService.o \\
	IOServiceGroup.o \\
	IOServiceMatching.o \\
	IOServiceOrdering.o \\
	IOSharedDataQueue.o \\
	IOSharedDataQueueClient.o \\
	IOStorage.o \\
	IOStorageController.o \\
	IOStorageFamily.o \\
	IOStorageRedundancyController.o \\
	IOStream.o \\
	IOStreamUserClient.o \\
	IOStreamUserClientInterface.o \\
	IOSystemReporter.o \\
	IOTime.o \\
	IOTimeStamp.o \\
	IOTransfer.o \\
	IOUserClient.o \\
	IOUserClientClass.o \\
	IOUserClientMethod.o \\
	IOUserClientNotification.o \\
	IOUserClientProperty.o \\
	IOUserClientRegistry.o \\
	IOUserClientService.o \\
	IOUserClientTask.o \\
	IOUserClientThread.o \\
	IOWorkLoop.o \\
	IOWorkQueue.o \\
	RootDomainUserClient.o \\
	IOBluetoothDevice.o \\
	IOBluetoothHCIController.o \\
	IOBluetoothHCIControllerTransport.o \\
	IOBluetoothHostControllerUSBTransport.o \\
	IOBluetoothL2CAPChannel.o \\
	IOBluetoothRFCOMMChannel.o \\
	IOBluetoothSDPClient.o \\
	IOBluetoothSDPServer.o \\
	IOBluetoothService.o \\
	IOBluetoothSDPSession.o \\
	IOBluetoothSDPTransaction.o \\
	IOBluetoothServiceRecord.o \\
	IOBluetoothUtility.o \\
	IOEthernetController.o \\
	IOEthernetInterface.o \\
	IONetworkController.o \\
	IONetworkData.o \\
	IONetworkInterface.o \\
	IONetworkMedium.o \\
	IONetworkStats.o \\
	IONetworkUserClient.o \\
	IOPacketFilter.o \\
	IOPacketFilterMonitor.o \\
	IOPacketFilterProvider.o \\
	IOPacketFilterRule.o \\
	IOPacketFilterRuleTable.o \\
	IOPacketFilterRuleTable6.o \\
	IOPacketFilterStats.o \\
	IOPacketFilterUserClient.o \\
	IOPacketFilterUserClient6.o \\
	IOPCIDevice.o \\
	IOPCIFunction.o \\
	IOPCIMessage.o \\
	IOPCIPrimaryMatch.o \\
	IOPCIResource.o \\
	IOPCITunnelCompatible.o \\
	IOPlatformDevice.o \\
	IOPlatformExpert.o \\
	IOPMPowerSource.o \\
	IOPMrootDomain.o \\
	IOPMScheduler.o \\
	IOPoller.o \\
	IOPolicy.o \\
	IOReport.o \\
	IOReportChannel.o \\
	IOReportGroup.o \\
	IOReportGroups.o \\
	IOReportLegend.o \\
	IOReportTypes.o \\
	IOResource.o \\
	IOResourceOwner.o \\
	IOService.o \\
	IOServiceGroup.o \\
	IOServiceMatching.o \\
	IOServiceOrdering.o \\
	IOSharedDataQueue.o \\
	IOSharedDataQueueClient.o \\
	IOStorage.o \\
	IOStorageController.o \\
	IOStorageFamily.o \\
	IOStorageRedundancyController.o \\
	IOStream.o \\
	IOStreamUserClient.o \\
	IOStreamUserClientInterface.o \\
	IOSystemReporter.o \\
	IOTime.o \\
	IOTimeStamp.o \\
	IOTransfer.o \\
	IOUserClient.o \\
	IOUserClientClass.o \\
	IOUserClientMethod.o \\
	IOUserClientNotification.o \\
	IOUserClientProperty.o \\
	IOUserClientRegistry.o \\
	IOUserClientService.o \\
	IOUserClientTask.o \\
	IOUserClientThread.o \\
	IOWorkLoop.o \\
	IOWorkQueue.o \\
	RootDomainUserClient.o

LIBOBJS =

CFILES = \\
	iokit/IOBSD/IOBSD.cpp \\
	iokit/IOBufferMemoryDescriptor.cpp \\
	iokit/IOCatalogue.cpp \\
	iokit/IOCommand.cpp \\
	iokit/IOCommandGate.cpp \\
	iokit/IOCommandPool.cpp \\
	iokit/IODataQueue.cpp \\
	iokit/IODeviceMemory.cpp \\
	iokit/IODeviceTreeSupport.cpp \\
	iokit/IODMACommand.cpp \\
	iokit/IODMAEventSource.cpp \\
	iokit/IODTMatching.cpp \\
	iokit/IODTNVRAM.cpp \\
	iokit/IOEventSource.cpp \\
	iokit/IOFilterInterruptEventSource.cpp \\
	iokit/IOFramebuffer.cpp \\
	iokit/IOGeneralMemoryDescriptor.cpp \\
	iokit/IOInterruptController.cpp \\
	iokit/IOInterruptEventSource.cpp \\
	iokit/IOIterator.cpp \\
	iokit/IOKit/IOLib.cpp \\
	iokit/IOKit/IOLog.cpp \\
	iokit/IOKit/IOPanic.cpp \\
	iokit/IOKit/IOService.cpp \\
	iokit/IOKit/IOUserClient.cpp \\
	iokit/IOKit/IOWorkLoop.cpp \\
	iokit/IOKit/notification/IONotificationRegistrar.cpp \\
	iokit/IOKit/notification/IONotifier.cpp \\
	iokit/IOKit/notification/IONotifierRegistry.cpp \\
	iokit/IOKit/pci/IOPCIDevice.cpp \\
	iokit/IOKit/pci/IOPCIFunction.cpp \\
	iokit/IOKit/pci/IOPCIMessage.cpp \\
	iokit/IOKit/pci/IOPCIPrimaryMatch.cpp \\
	iokit/IOKit/pci/IOPCIResource.cpp \\
	iokit/IOKit/pci/IOPCITunnelCompatible.cpp \\
	iokit/IOKit/pwr_mgt/IOPMPowerSource.cpp \\
	iokit/IOKit/pwr_mgt/IOPMrootDomain.cpp \\
	iokit/IOKit/pwr_mgt/IOPMScheduler.cpp \\
	iokit/IOKit/pwr_mgt/RootDomainUserClient.cpp \\
	iokit/IOKit/storage/IOBlockStorageDevice.cpp \\
	iokit/IOKit/storage/IOBlockStorageDriver.cpp \\
	iokit/IOKit/storage/IOCDMedia.cpp \\
	iokit/IOKit/storage/IOCDMediaBSDClient.cpp \\
	iokit/IOKit/storage/IOCompactFlash.cpp \\
	iokit/IOKit/storage/IOCoreStorage.cpp \\
	iokit/IOKit/storage/IOCoreStorageAES.cpp \\
	iokit/IOKit/storage/IOCoreStorageGroup.cpp \\
	iokit/IOKit/storage/IOCoreStoragePhysical.cpp \\
	iokit/IOKit/storage/IOCoreStorageUserClient.cpp \\
	iokit/IOKit/storage/IODVDMedia.cpp \\
	iokit/IOKit/storage/IODVDMediaBSDClient.cpp \\
	iokit/IOKit/storage/IOFDMedia.cpp \\
	iokit/IOKit/storage/IOFDMediaBSDClient.cpp \\
	iokit/IOKit/storage/IOHDIXController.cpp \\
	iokit/IOKit/storage/IOHDIXMedia.cpp \\
	iokit/IOKit/storage/IOKernelMemoryDescriptor.cpp \\
	iokit/IOKit/storage/IOMedia.cpp \\
	iokit/IOKit/storage/IOMediaBSDClient.cpp \\
	iokit/IOKit/storage/IOSCSIBlockCommandsDevice.cpp \\
	iokit/IOKit/storage/IOSCSIDevice.cpp \\
	iokit/IOKit/storage/IOSCSIMultimediaCommandsDevice.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType00.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType01.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType02.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType03.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType04.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType05.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType06.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType07.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType08.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType09.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType0A.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType0B.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType0C.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType0D.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType0E.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType0F.cpp \\
	iokit/IOKit/storage/IOSCSIReducedBlockCommandsDevice.cpp \\
	iokit/IOKit/storage/IOStorage.cpp \\
	iokit/IOKit/storage/IOStorageController.cpp \\
	iokit/IOKit/storage/IOStorageFamily.cpp \\
	iokit/IOKit/storage/IOStorageRedundancyController.cpp \\
	iokit/IOKit/usb/IOUSBController.cpp \\
	iokit/IOKit/usb/IOUSBControllerV2.cpp \\
	iokit/IOKit/usb/IOUSBControllerV3.cpp \\
	iokit/IOKit/usb/IOUSBDevice.cpp \\
	iokit/IOKit/usb/IOUSBEndpoint.cpp \\
	iokit/IOKit/usb/IOUSBHostDevice.cpp \\
	iokit/IOKit/usb/IOUSBHostEndpoint.cpp \\
	iokit/IOKit/usb/IOUSBHostInterface.cpp \\
	iokit/IOKit/usb/IOUSBHostPipe.cpp \\
	iokit/IOKit/usb/IOUSBHostPipeLog.cpp \\
	iokit/IOKit/usb/IOUSBInterface.cpp \\
	iokit/IOKit/usb/IOUSBLog.cpp \\
	iokit/IOKit/usb/IOUSBMassStorageClass.cpp \\
	iokit/IOKit/usb/IOUSBMassStorageClassExtras.cpp \\
	iokit/IOKit/usb/IOUSBPipe.cpp \\
	iokit/IOKit/usb/IOUSBUserClient.cpp \\
	iokit/IOKit/watchdog/IOWatchDogTimer.cpp \\
	iokit/IOKitServer.cpp \\
	iokit/IOInterruptEventSource.cpp \\
	iokit/IOKitDiagnostics.cpp \\
	iokit/IOKitKeys.cpp \\
	iokit/IOLog.cpp \\
	iokit/IOMapper.cpp \\
	iokit/IOMapperEndpoint.cpp \\
	iokit/IOMapperMemoryDescriptor.cpp \\
	iokit/IOMapperSpec.cpp \\
	iokit/IOMapperSpecArray.cpp \\
	iokit/IOMemoryDescriptor.cpp \\
	iokit/IOMPAccess.cpp \\
	iokit/IOMPContainer.cpp \\
	iokit/IOMPDevice.cpp \\
	iokit/IOMPSDevice.cpp \\
	iokit/IOMPT.cpp \\
	iokit/IONetwork/IO80211Interface.cpp \\
	iokit/IONetwork/IO80211Peer.cpp \\
	iokit/IONetwork/IO80211ScanManager.cpp \\
	iokit/IONetwork/IO80211VirtualInterface.cpp \\
	iokit/IONetwork/IOBluetoothDevice.cpp \\
	iokit/IONetwork/IOBluetoothHCIController.cpp \\
	iokit/IONetwork/IOBluetoothHCIControllerTransport.cpp \\
	iokit/IONetwork/IOBluetoothHostControllerUSBTransport.cpp \\
	iokit/IONetwork/IOBluetoothL2CAPChannel.cpp \\
	iokit/IONetwork/IOBluetoothRFCOMMChannel.cpp \\
	iokit/IONetwork/IOBluetoothSDPClient.cpp \\
	iokit/IONetwork/IOBluetoothSDPServer.cpp \\
	iokit/IONetwork/IOBluetoothService.cpp \\
	iokit/IONetwork/IOBluetoothSDPSession.cpp \\
	iokit/IONetwork/IOBluetoothSDPTransaction.cpp \\
	iokit/IONetwork/IOBluetoothServiceRecord.cpp \\
	iokit/IONetwork/IOBluetoothUtility.cpp \\
	iokit/IONetwork/IOEthernetController.cpp \\
	iokit/IONetwork/IOEthernetInterface.cpp \\
	iokit/IONetwork/IONetworkController.cpp \\
	iokit/IONetwork/IONetworkData.cpp \\
	iokit/IONetwork/IONetworkInterface.cpp \\
	iokit/IONetwork/IONetworkMedium.cpp \\
	iokit/IONetwork/IONetworkStats.cpp \\
	iokit/IONetwork/IONetworkUserClient.cpp \\
	iokit/IONetwork/IOPacketFilter.cpp \\
	iokit/IONetwork/IOPacketFilterMonitor.cpp \\
	iokit/IONetwork/IOPacketFilterProvider.cpp \\
	iokit/IONetwork/IOPacketFilterRule.cpp \\
	iokit/IONetwork/IOPacketFilterRuleTable.cpp \\
	iokit/IONetwork/IOPacketFilterRuleTable6.cpp \\
	iokit/IONetwork/IOPacketFilterStats.cpp \\
	iokit/IONetwork/IOPacketFilterUserClient.cpp \\
	iokit/IONetwork/IOPacketFilterUserClient6.cpp \\
	iokit/IONetwork/IOService.cpp \\
	iokit/IONetwork/IOVirtualInterface.cpp \\
	iokit/IONetworkController.cpp \\
	iokit/IONetworkData.cpp \\
	iokit/IONetworkInterface.cpp \\
	iokit/IONetworkMedium.cpp \\
	iokit/IONetworkStats.cpp \\
	iokit/IONetworkUserClient.cpp \\
	iokit/IOPacketFilter.cpp \\
	iokit/IOPacketFilterMonitor.cpp \\
	iokit/IOPacketFilterProvider.cpp \\
	iokit/IOPacketFilterRule.cpp \\
	iokit/IOPacketFilterRuleTable.cpp \\
	iokit/IONetwork/IOPacketFilterRuleTable6.cpp \\
	iokit/IONetwork/IOPacketFilterStats.cpp \\
	iokit/IONetwork/IOPacketFilterUserClient.cpp \\
	iokit/IONetwork/IOPacketFilterUserClient6.cpp \\
	iokit/IOPCIDevice.cpp \\
	iokit/IOPCIFunction.cpp \\
	iokit/IOPCIMessage.cpp \\
	iokit/IOPCIPrimaryMatch.cpp \\
	iokit/IOPCIResource.cpp \\
	iokit/IOPCITunnelCompatible.cpp \\
	iokit/IOPlatformDevice.cpp \\
	iokit/IOPlatformExpert.cpp \\
	iokit/IOPMPowerSource.cpp \\
	iokit/IOPMrootDomain.cpp \\
	iokit/IOPMScheduler.cpp \\
	iokit/IOPoller.cpp \\
	iokit/IOPolicy.cpp \\
	iokit/IOReport.cpp \\
	iokit/IOReportChannel.cpp \\
	iokit/IOReportGroup.cpp \\
	iokit/IOReportGroups.cpp \\
	iokit/IOReportLegend.cpp \\
	iokit/IOReportTypes.cpp \\
	iokit/IOResource.cpp \\
	iokit/IOResourceOwner.cpp \\
	iokit/IOService.cpp \\
	iokit/IOServiceGroup.cpp \\
	iokit/IOServiceMatching.cpp \\
	iokit/IOServiceOrdering.cpp \\
	iokit/IOSharedDataQueue.cpp \\
	iokit/IOSharedDataQueueClient.cpp \\
	iokit/IOStorage.cpp \\
	iokit/IOStorageController.cpp \\
	iokit/IOStorageFamily.cpp \\
	iokit/IOStorageRedundancyController.cpp \\
	iokit/IOStream.cpp \\
	iokit/IOStreamUserClient.cpp \\
	iokit/IOStreamUserClientInterface.cpp \\
	iokit/IOSystemReporter.cpp \\
	iokit/IOTime.cpp \\
	iokit/IOTimeStamp.cpp \\
	iokit/IOTransfer.cpp \\
	iokit/IOUserClient.cpp \\
	iokit/IOUserClientClass.cpp \\
	iokit/IOUserClientMethod.cpp \\
	iokit/IOUserClientNotification.cpp \\
	iokit/IOUserClientProperty.cpp \\
	iokit/IOUserClientRegistry.cpp \\
	iokit/IOUserClientService.cpp \\
	iokit/IOUserClientTask.cpp \\
	iokit/IOUserClientThread.cpp \\
	iokit/IOWorkLoop.cpp \\
	iokit/IOWorkQueue.cpp \\
	iokit/RootDomainUserClient.cpp \\
	iokit/IOBluetooth/IOBluetoothDevice.cpp \\
	iokit/IOBluetooth/IOBluetoothHCIController.cpp \\
	iokit/IOBluetooth/IOBluetoothHCIControllerTransport.cpp \\
	iokit/IOBluetooth/IOBluetoothHostControllerUSBTransport.cpp \\
	iokit/IOBluetooth/IOBluetoothL2CAPChannel.cpp \\
	iokit/IOBluetooth/IOBluetoothRFCOMMChannel.cpp \\
	iokit/IOBluetooth/IOBluetoothSDPClient.cpp \\
	iokit/IOBluetooth/IOBluetoothSDPServer.cpp \\
	iokit/IOBluetooth/IOBluetoothService.cpp \\
	iokit/IOBluetooth/IOBluetoothSDPSession.cpp \\
	iokit/IOBluetooth/IOBluetoothSDPTransaction.cpp \\
	iokit/IOBluetooth/IOBluetoothServiceRecord.cpp \\
	iokit/IOBluetooth/IOBluetoothUtility.cpp

CXXFILES = \\
	iokit/IOBSD/IOBSD.cpp \\
	iokit/IOBufferMemoryDescriptor.cpp \\
	iokit/IOCatalogue.cpp \\
	iokit/IOCommand.cpp \\
	iokit/IOCommandGate.cpp \\
	iokit/IOCommandPool.cpp \\
	iokit/IODataQueue.cpp \\
	iokit/IODeviceMemory.cpp \\
	iokit/IODeviceTreeSupport.cpp \\
	iokit/IODMACommand.cpp \\
	iokit/IODMAEventSource.cpp \\
	iokit/IODTMatching.cpp \\
	iokit/IODTNVRAM.cpp \\
	iokit/IOEventSource.cpp \\
	iokit/IOFilterInterruptEventSource.cpp \\
	iokit/IOFramebuffer.cpp \\
	iokit/IOGeneralMemoryDescriptor.cpp \\
	iokit/IOInterruptController.cpp \\
	iokit/IOInterruptEventSource.cpp \\
	iokit/IOIterator.cpp \\
	iokit/IOKit/IOLib.cpp \\
	iokit/IOKit/IOLog.cpp \\
	iokit/IOKit/IOPanic.cpp \\
	iokit/IOKit/IOService.cpp \\
	iokit/IOKit/IOUserClient.cpp \\
	iokit/IOKit/IOWorkLoop.cpp \\
	iokit/IOKit/notification/IONotificationRegistrar.cpp \\
	iokit/IOKit/notification/IONotifier.cpp \\
	iokit/IOKit/notification/IONotifierRegistry.cpp \\
	iokit/IOKit/pci/IOPCIDevice.cpp \\
	iokit/IOKit/pci/IOPCIFunction.cpp \\
	iokit/IOKit/pci/IOPCIMessage.cpp \\
	iokit/IOKit/pci/IOPCIPrimaryMatch.cpp \\
	iokit/IOKit/pci/IOPCIResource.cpp \\
	iokit/IOKit/pci/IOPCITunnelCompatible.cpp \\
	iokit/IOKit/pwr_mgt/IOPMPowerSource.cpp \\
	iokit/IOKit/pwr_mgt/IOPMrootDomain.cpp \\
	iokit/IOKit/pwr_mgt/IOPMScheduler.cpp \\
	iokit/IOKit/pwr_mgt/RootDomainUserClient.cpp \\
	iokit/IOKit/storage/IOBlockStorageDevice.cpp \\
	iokit/IOKit/storage/IOBlockStorageDriver.cpp \\
	iokit/IOKit/storage/IOCDMedia.cpp \\
	iokit/IOKit/storage/IOCDMediaBSDClient.cpp \\
	iokit/IOKit/storage/IOCompactFlash.cpp \\
	iokit/IOKit/storage/IOCoreStorage.cpp \\
	iokit/IOKit/storage/IOCoreStorageAES.cpp \\
	iokit/IOKit/storage/IOCoreStorageGroup.cpp \\
	iokit/IOKit/storage/IOCoreStoragePhysical.cpp \\
	iokit/IOKit/storage/IOCoreStorageUserClient.cpp \\
	iokit/IOKit/storage/IODVDMedia.cpp \\
	iokit/IOKit/storage/IODVDMediaBSDClient.cpp \\
	iokit/IOKit/storage/IOFDMedia.cpp \\
	iokit/IOKit/storage/IOFDMediaBSDClient.cpp \\
	iokit/IOKit/storage/IOHDIXController.cpp \\
	iokit/IOKit/storage/IOHDIXMedia.cpp \\
	iokit/IOKit/storage/IOKernelMemoryDescriptor.cpp \\
	iokit/IOKit/storage/IOMedia.cpp \\
	iokit/IOKit/storage/IOMediaBSDClient.cpp \\
	iokit/IOKit/storage/IOSCSIBlockCommandsDevice.cpp \\
	iokit/IOKit/storage/IOSCSIDevice.cpp \\
	iokit/IOKit/storage/IOSCSIMultimediaCommandsDevice.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType00.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType01.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType02.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType03.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType04.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType05.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType06.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType07.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType08.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType09.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType0A.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType0B.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType0C.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType0D.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType0E.cpp \\
	iokit/IOKit/storage/IOSCSIPeripheralDeviceType0F.cpp \\
	iokit/IOKit/storage/IOSCSIReducedBlockCommandsDevice.cpp \\
	iokit/IOKit/storage/IOStorage.cpp \\
	iokit/IOKit/storage/IOStorageController.cpp \\
	iokit/IOKit/storage/IOStorageFamily.cpp \\
	iokit/IOKit/storage/IOStorageRedundancyController.cpp \\
	iokit/IOKit/usb/IOUSBController.cpp \\
	iokit/IOKit/usb/IOUSBControllerV2.cpp \\
	iokit/IOKit/usb/IOUSBControllerV3.cpp \\
	iokit/IOKit/usb/IOUSBDevice.cpp \\
	iokit/IOKit/usb/IOUSBEndpoint.cpp \\
	iokit/IOKit/usb/IOUSBHostDevice.cpp \\
	iokit/IOKit/usb/IOUSBHostEndpoint.cpp \\
	iokit/IOKit/usb/IOUSBHostInterface.cpp \\
	iokit/IOKit/usb/IOUSBHostPipe.cpp \\
	iokit/IOKit/usb/IOUSBHostPipeLog.cpp \\
	iokit/IOKit/usb/IOUSBInterface.cpp \\
	iokit/IOKit/usb/IOUSBLog.cpp \\
	iokit/IOKit/usb/IOUSBMassStorageClass.cpp \\
	iokit/IOKit/usb/IOUSBMassStorageClassExtras.cpp \\
	iokit/IOKit/usb/IOUSBPipe.cpp \\
	iokit/IOKit/usb/IOUSBUserClient.cpp \\
	iokit/IOKit/watchdog/IOWatchDogTimer.cpp \\
	iokit/IOKitServer.cpp \\
	iokit/IOInterruptEventSource.cpp \\
	iokit/IOKitDiagnostics.cpp \\
	iokit/IOKitKeys.cpp \\
	iokit/IOLog.cpp \\
	iokit/IOMapper.cpp \\
	iokit/IOMapperEndpoint.cpp \\
	iokit/IOMapperMemoryDescriptor.cpp \\
	iokit/IOMapperSpec.cpp \\
	iokit/IOMapperSpecArray.cpp \\
	iokit/IOMemoryDescriptor.cpp \\
	iokit/IOMPAccess.cpp \\
	iokit/IOMPContainer.cpp \\
	iokit/IOMPDevice.cpp \\
	iokit/IOMPSDevice.cpp \\
	iokit/IOMPT.cpp \\
	iokit/IONetwork/IO80211Interface.cpp \\
	iokit/IONetwork/IO80211Peer.cpp \\
	iokit/IONetwork/IO80211ScanManager.cpp \\
	iokit/IONetwork/IO80211VirtualInterface.cpp \\
	iokit/IONetwork/IOBluetoothDevice.cpp \\
	iokit/IONetwork/IOBluetoothHCIController.cpp \\
	iokit/IONetwork/IOBluetoothHCIControllerTransport.cpp \\
	iokit/IONetwork/IOBluetoothHostControllerUSBTransport.cpp \\
	iokit/IONetwork/IOBluetoothL2CAPChannel.cpp \\
	iokit/IONetwork/IOBluetoothRFCOMMChannel.cpp \\
	iokit/IONetwork/IOBluetoothSDPClient.cpp \\
	iokit/IONetwork/IOBluetoothSDPServer.cpp \\
	iokit/IONetwork/IOBluetoothService.cpp \\
	iokit/IONetwork/IOBluetoothSDPSession.cpp \\
	iokit/IONetwork/IOBluetoothSDPTransaction.cpp \\
	iokit/IONetwork/IOBluetoothServiceRecord.cpp \\
	iokit/IONetwork/IOBluetoothUtility.cpp \\
	iokit/IONetwork/IOEthernetController.cpp \\
	iokit/IONetwork/IOEthernetInterface.cpp \\
	iokit/IONetwork/IONetworkController.cpp \\
	iokit/IONetwork/IONetworkData.cpp \\
	iokit/IONetwork/IONetworkInterface.cpp \\
	iokit/IONetwork/IONetworkMedium.cpp \\
	iokit/IONetwork/IONetworkStats.cpp \\
	iokit/IONetwork/IONetworkUserClient.cpp \\
	iokit/IONetwork/IOPacketFilter.cpp \\
	iokit/IONetwork/IOPacketFilterMonitor.cpp \\
	iokit/IONetwork/IOPacketFilterProvider.cpp \\
	iokit/IONetwork/IOPacketFilterRule.cpp \\
	iokit/IONetwork/IOPacketFilterRuleTable.cpp \\
	iokit/IONetwork/IOPacketFilterRuleTable6.cpp \\
	iokit/IONetwork/IOPacketFilterStats.cpp \\
	iokit/IONetwork/IOPacketFilterUserClient.cpp \\
	iokit/IONetwork/IOPacketFilterUserClient6.cpp \\
	iokit/IONetwork/IOService.cpp \\
	iokit/IONetwork/IOVirtualInterface.cpp \\
	iokit/IONetworkController.cpp \\
	iokit/IONetworkData.cpp \\
	iokit/IONetworkInterface.cpp \\
	iokit/IONetworkMedium.cpp \\
	iokit/IONetworkStats.cpp \\
	iokit/IONetworkUserClient.cpp \\
	iokit/IOPacketFilter.cpp \\
	iokit/IOPacketFilterMonitor.cpp \\
	iokit/IOPacketFilterProvider.cpp \\
	iokit/IOPacketFilterRule.cpp \\
	iokit/IONetwork/IOPacketFilterRuleTable.cpp \\
	iokit/IONetwork/IOPacketFilterRuleTable6.cpp \\
	iokit/IONetwork/IOPacketFilterStats.cpp \\
	iokit/IONetwork/IOPacketFilterUserClient.cpp \\
	iokit/IONetwork/IOPacketFilterUserClient6.cpp \\
	iokit/IOPCIDevice.cpp \\
	iokit/IOPCIFunction.cpp \\
	iokit/IOPCIMessage.cpp \\
	iokit/IOPCIPrimaryMatch.cpp \\
	iokit/IOPCIResource.cpp \\
	iokit/IOPCITunnelCompatible.cpp \\
	iokit/IOPlatformDevice.cpp \\
	iokit/IOPlatformExpert.cpp \\
	iokit/IOPMPowerSource.cpp \\
	iokit/IOPMrootDomain.cpp \\
	iokit/IOPMScheduler.cpp \\
	iokit/IOPoller.cpp \\
	iokit/IOPolicy.cpp \\
	iokit/IOReport.cpp \\
	iokit/IOReportChannel.cpp \\
	iokit/IOReportGroup.cpp \\
	iokit/IOReportGroups.cpp \\
	iokit/IOReportLegend.cpp \\
	iokit/IOReportTypes.cpp \\
	iokit/IOResource.cpp \\
	iokit/IOResourceOwner.cpp \\
	iokit/IOService.cpp \\
	iokit/IOServiceGroup.cpp \\
	iokit/IOServiceMatching.cpp \\
	iokit/IOServiceOrdering.cpp \\
	iokit/IOSharedDataQueue.cpp \\
	iokit/IOSharedDataQueueClient.cpp \\
	iokit/IOStorage.cpp \\
	iokit/IOStorageController.cpp \\
	iokit/IOStorageFamily.cpp \\
	iokit/IOStorageRedundancyController.cpp \\
	iokit/IOStream.cpp \\
	iokit/IOStreamUserClient.cpp \\
	iokit/IOStreamUserClientInterface.cpp \\
	iokit/IOSystemReporter.cpp \\
	iokit/IOTime.cpp \\
	iokit/IOTimeStamp.cpp \\
	iokit/IOTransfer.cpp \\
	iokit/IOUserClient.cpp \\
	iokit/IOUserClientClass.cpp \\
	iokit/IOUserClientMethod.cpp \\
	iokit/IOUserClientNotification.cpp \\
	iokit/IOUserClientProperty.cpp \\
	iokit/IOUserClientRegistry.cpp \\
	iokit/IOUserClientService.cpp \\
	iokit/IOUserClientTask.cpp \\
	iokit/IOUserClientThread.cpp \\
	iokit/IOWorkLoop.cpp \\
	iokit/IOWorkQueue.cpp \\
	iokit/RootDomainUserClient.cpp \\
	iokit/IOBluetooth/IOBluetoothDevice.cpp \\
	iokit/IOBluetooth/IOBluetoothHCIController.cpp \\
	iokit/IOBluetooth/IOBluetoothHCIControllerTransport.cpp \\
	iokit/IOBluetooth/IOBluetoothHostControllerUSBTransport.cpp \\
	iokit/IOBluetooth/IOBluetoothL2CAPChannel.cpp \\
	iokit/IOBluetooth/IOBluetoothRFCOMMChannel.cpp \\
	iokit/IOBluetooth/IOBluetoothSDPClient.cpp \\
	iokit/IOBluetooth/IOBluetoothSDPServer.cpp \\
	iokit/IOBluetooth/IOBluetoothService.cpp \\
	iokit/IOBluetooth/IOBluetoothSDPSession.cpp \\
	iokit/IOBluetooth/IOBluetoothSDPTransaction.cpp \\
	iokit/IOBluetooth/IOBluetoothServiceRecord.cpp \\
	iokit/IOBluetooth/IOBluetoothUtility.cpp

SFILES =

MACHDEP =

#
# Diagnostic opt-outs.  We need to make this list empty.
#
# DO NOT ADD MORE HERE.
#
# -Wno-cast-align
IOBSD.o_CWARNFLAGS_ADD += -Wno-cast-align
# -Wno-shorten-64-to-32
IOBSD.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBufferMemoryDescriptor.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOCatalogue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOCommand.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOCommandGate.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOCommandPool.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IODataQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IODeviceMemory.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IODeviceTreeSupport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IODMACommand.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IODMAEventSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IODTMatching.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IODTNVRAM.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEventSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOFilterInterruptEventSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOFramebuffer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOGeneralMemoryDescriptor.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOInterruptController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOInterruptEventSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOIterator.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOLib.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOLog.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPanic.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkLoop.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONotificationRegistrar.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONotifier.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONotifierRegistry.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIFunction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIMessage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIPrimaryMatch.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCITunnelCompatible.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMPowerSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMrootDomain.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMScheduler.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
RootDomainUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBlockStorageDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBlockStorageDriver.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOCDMedia.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOCDMediaBSDClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOCompactFlash.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOCoreStorage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOCoreStorageAES.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOCoreStorageGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOCoreStoragePhysical.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOCoreStorageUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IODVDMedia.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IODVDMediaBSDClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOFDMedia.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOFDMediaBSDClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOHDIXController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOHDIXMedia.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOKernelMemoryDescriptor.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOMedia.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOMediaBSDClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSCSIBlockCommandsDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSCSIDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSCSIMultimediaCommandsDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSCSIPeripheralDeviceType00.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSCSIPeripheralDeviceType01.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSCSIPeripheralDeviceType02.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSCSIPeripheralDeviceType03.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSCSIPeripheralDeviceType04.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSCSIPeripheralDeviceType05.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSCSIPeripheralDeviceType06.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSCSIPeripheralDeviceType07.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSCSIPeripheralDeviceType08.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSCSIPeripheralDeviceType09.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSCSIPeripheralDeviceType0A.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSCSIPeripheralDeviceType0B.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSCSIPeripheralDeviceType0C.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSCSIPeripheralDeviceType0D.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSCSIPeripheralDeviceType0E.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSCSIPeripheralDeviceType0F.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSCSIReducedBlockCommandsDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageFamily.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageRedundancyController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUSBController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUSBControllerV2.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUSBControllerV3.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUSBDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUSBEndpoint.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUSBHostDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUSBHostEndpoint.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUSBHostInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUSBHostPipe.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUSBHostPipeLog.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUSBInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUSBLog.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUSBMassStorageClass.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUSBMassStorageClassExtras.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUSBPipe.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUSBUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWatchDogTimer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOKitServer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOInterruptEventSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOIterator.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOKitDiagnostics.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOKitKeys.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOLog.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOMapper.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOMapperEndpoint.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOMapperMemoryDescriptor.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOMapperSpec.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOMapperSpecArray.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOMemoryDescriptor.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOMPAccess.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOMPContainer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOMPDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOMPSDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOMPT.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IO80211Interface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IO80211Peer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IO80211ScanManager.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IO80211VirtualInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIControllerTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHostControllerUSBTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothL2CAPChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothRFCOMMChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPServer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPSession.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPTransaction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothServiceRecord.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothUtility.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkData.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkMedium.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterMonitor.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterProvider.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRule.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIFunction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIMessage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIPrimaryMatch.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCITunnelCompatible.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformExpert.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMPowerSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMrootDomain.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMScheduler.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPoller.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPolicy.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroups.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportLegend.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportTypes.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResourceOwner.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceMatching.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceOrdering.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueueClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageFamily.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageRedundancyController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStream.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClientInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSystemReporter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTime.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTimeStamp.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTransfer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientClass.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientMethod.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientNotification.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientProperty.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientRegistry.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientTask.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientThread.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkLoop.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
RootDomainUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIControllerTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHostControllerUSBTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothL2CAPChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothRFCOMMChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPServer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPSession.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPTransaction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothServiceRecord.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothUtility.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkData.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkMedium.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterMonitor.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterProvider.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRule.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIFunction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIMessage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIPrimaryMatch.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCITunnelCompatible.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformExpert.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMPowerSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMrootDomain.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMScheduler.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPoller.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPolicy.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroups.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportLegend.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportTypes.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResourceOwner.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceMatching.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceOrdering.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueueClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageFamily.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageRedundancyController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStream.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClientInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSystemReporter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTime.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTimeStamp.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTransfer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientClass.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientMethod.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientNotification.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientProperty.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientRegistry.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientTask.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientThread.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkLoop.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
RootDomainUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIControllerTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHostControllerUSBTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothL2CAPChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothRFCOMMChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPServer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPSession.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPTransaction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothServiceRecord.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothUtility.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkData.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkMedium.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterMonitor.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterProvider.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRule.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIFunction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIMessage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIPrimaryMatch.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCITunnelCompatible.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformExpert.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMPowerSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMrootDomain.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMScheduler.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPoller.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPolicy.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroups.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportLegend.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportTypes.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResourceOwner.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceMatching.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceOrdering.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueueClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageFamily.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageRedundancyController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStream.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClientInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSystemReporter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTime.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTimeStamp.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTransfer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientClass.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientMethod.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientNotification.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientProperty.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientRegistry.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientTask.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientThread.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkLoop.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
RootDomainUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIControllerTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHostControllerUSBTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothL2CAPChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothRFCOMMChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPServer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPSession.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPTransaction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothServiceRecord.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothUtility.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkData.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkMedium.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterMonitor.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterProvider.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRule.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIFunction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIMessage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIPrimaryMatch.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCITunnelCompatible.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformExpert.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMPowerSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMrootDomain.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMScheduler.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPoller.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPolicy.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroups.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportLegend.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportTypes.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResourceOwner.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceMatching.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceOrdering.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueueClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageFamily.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageRedundancyController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStream.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClientInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSystemReporter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTime.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTimeStamp.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTransfer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientClass.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientMethod.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientNotification.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientProperty.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientRegistry.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientTask.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientThread.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkLoop.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
RootDomainUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIControllerTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHostControllerUSBTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothL2CAPChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothRFCOMMChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPServer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPSession.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPTransaction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothServiceRecord.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothUtility.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkData.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkMedium.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterMonitor.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterProvider.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRule.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIFunction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIMessage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIPrimaryMatch.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCITunnelCompatible.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformExpert.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMPowerSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMrootDomain.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMScheduler.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPoller.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPolicy.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroups.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportLegend.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportTypes.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResourceOwner.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceMatching.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceOrdering.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueueClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageFamily.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageRedundancyController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStream.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClientInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSystemReporter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTime.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTimeStamp.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTransfer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientClass.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientMethod.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientNotification.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientProperty.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientRegistry.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientTask.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientThread.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkLoop.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
RootDomainUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIControllerTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHostControllerUSBTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothL2CAPChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothRFCOMMChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPServer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPSession.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPTransaction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothServiceRecord.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothUtility.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkData.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkMedium.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterMonitor.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterProvider.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRule.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIFunction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIMessage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIPrimaryMatch.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCITunnelCompatible.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformExpert.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMPowerSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMrootDomain.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMScheduler.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPoller.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPolicy.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroups.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportLegend.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportTypes.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResourceOwner.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceMatching.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceOrdering.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueueClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageFamily.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageRedundancyController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStream.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClientInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSystemReporter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTime.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTimeStamp.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTransfer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientClass.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientMethod.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientNotification.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientProperty.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientRegistry.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientTask.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientThread.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkLoop.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
RootDomainUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIControllerTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHostControllerUSBTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothL2CAPChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothRFCOMMChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPServer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPSession.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPTransaction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothServiceRecord.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothUtility.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkData.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkMedium.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterMonitor.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterProvider.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRule.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIFunction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIMessage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIPrimaryMatch.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCITunnelCompatible.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformExpert.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMPowerSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMrootDomain.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMScheduler.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPoller.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPolicy.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroups.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportLegend.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportTypes.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResourceOwner.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceMatching.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceOrdering.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueueClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageFamily.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageRedundancyController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStream.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClientInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSystemReporter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTime.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTimeStamp.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTransfer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientClass.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientMethod.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientNotification.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientProperty.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientRegistry.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientTask.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientThread.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkLoop.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
RootDomainUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIControllerTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHostControllerUSBTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothL2CAPChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothRFCOMMChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPServer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPSession.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPTransaction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothServiceRecord.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothUtility.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkData.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkMedium.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterMonitor.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterProvider.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRule.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIFunction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIMessage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIPrimaryMatch.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCITunnelCompatible.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformExpert.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMPowerSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMrootDomain.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMScheduler.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPoller.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPolicy.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroups.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportLegend.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportTypes.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResourceOwner.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceMatching.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceOrdering.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueueClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageFamily.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageRedundancyController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStream.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClientInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSystemReporter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTime.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTimeStamp.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTransfer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientClass.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientMethod.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientNotification.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientProperty.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientRegistry.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientTask.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientThread.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkLoop.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
RootDomainUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIControllerTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHostControllerUSBTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothL2CAPChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothRFCOMMChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPServer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPSession.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPTransaction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothServiceRecord.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothUtility.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkData.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkMedium.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterMonitor.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterProvider.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRule.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIFunction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIMessage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIPrimaryMatch.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCITunnelCompatible.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformExpert.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMPowerSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMrootDomain.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMScheduler.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPoller.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPolicy.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroups.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportLegend.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportTypes.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResourceOwner.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceMatching.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceOrdering.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueueClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageFamily.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageRedundancyController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStream.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClientInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSystemReporter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTime.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTimeStamp.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTransfer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientClass.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientMethod.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientNotification.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientProperty.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientRegistry.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientTask.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientThread.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkLoop.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
RootDomainUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIControllerTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHostControllerUSBTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothL2CAPChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothRFCOMMChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPServer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPSession.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPTransaction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothServiceRecord.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothUtility.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkData.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkMedium.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterMonitor.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterProvider.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRule.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIFunction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIMessage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIPrimaryMatch.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCITunnelCompatible.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformExpert.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMPowerSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMrootDomain.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMScheduler.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPoller.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPolicy.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroups.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportLegend.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportTypes.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResourceOwner.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceMatching.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceOrdering.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueueClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageFamily.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageRedundancyController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStream.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClientInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSystemReporter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTime.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTimeStamp.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTransfer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientClass.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientMethod.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientNotification.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientProperty.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientRegistry.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientTask.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientThread.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkLoop.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
RootDomainUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIControllerTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHostControllerUSBTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothL2CAPChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothRFCOMMChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPServer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPSession.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPTransaction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothServiceRecord.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothUtility.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkData.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkMedium.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterMonitor.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterProvider.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRule.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIFunction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIMessage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIPrimaryMatch.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCITunnelCompatible.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformExpert.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMPowerSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMrootDomain.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMScheduler.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPoller.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPolicy.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroups.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportLegend.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportTypes.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResourceOwner.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceMatching.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceOrdering.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueueClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageFamily.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageRedundancyController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStream.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClientInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSystemReporter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTime.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTimeStamp.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTransfer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientClass.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientMethod.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientNotification.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientProperty.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientRegistry.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientTask.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientThread.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkLoop.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
RootDomainUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIControllerTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHostControllerUSBTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothL2CAPChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothRFCOMMChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPServer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPSession.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPTransaction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothServiceRecord.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothUtility.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkData.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkMedium.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterMonitor.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterProvider.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRule.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIFunction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIMessage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIPrimaryMatch.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCITunnelCompatible.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformExpert.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMPowerSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMrootDomain.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMScheduler.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPoller.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPolicy.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroups.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportLegend.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportTypes.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResourceOwner.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceMatching.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceOrdering.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueueClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageFamily.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageRedundancyController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStream.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClientInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSystemReporter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTime.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTimeStamp.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTransfer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientClass.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientMethod.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientNotification.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientProperty.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientRegistry.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientTask.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientThread.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkLoop.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
RootDomainUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIControllerTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHostControllerUSBTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothL2CAPChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothRFCOMMChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPServer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPSession.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPTransaction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothServiceRecord.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothUtility.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkData.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkMedium.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterMonitor.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterProvider.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRule.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIFunction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIMessage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIPrimaryMatch.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCITunnelCompatible.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformExpert.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMPowerSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMrootDomain.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMScheduler.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPoller.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPolicy.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroups.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportLegend.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportTypes.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResourceOwner.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceMatching.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceOrdering.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueueClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageFamily.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageRedundancyController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStream.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClientInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSystemReporter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTime.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTimeStamp.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTransfer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientClass.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientMethod.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientNotification.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientProperty.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientRegistry.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientTask.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientThread.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkLoop.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
RootDomainUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIControllerTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHostControllerUSBTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothL2CAPChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothRFCOMMChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPServer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPSession.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPTransaction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothServiceRecord.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothUtility.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkData.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkMedium.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterMonitor.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterProvider.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRule.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIFunction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIMessage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIPrimaryMatch.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCITunnelCompatible.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformExpert.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMPowerSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMrootDomain.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMScheduler.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPoller.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPolicy.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroups.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportLegend.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportTypes.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResourceOwner.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceMatching.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceOrdering.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueueClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageFamily.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageRedundancyController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStream.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClientInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSystemReporter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTime.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTimeStamp.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTransfer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientClass.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientMethod.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientNotification.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientProperty.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientRegistry.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientTask.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientThread.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkLoop.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
RootDomainUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIControllerTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHostControllerUSBTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothL2CAPChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothRFCOMMChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPServer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPSession.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPTransaction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothServiceRecord.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothUtility.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkData.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkMedium.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterMonitor.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterProvider.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRule.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIFunction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIMessage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIPrimaryMatch.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCITunnelCompatible.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformExpert.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMPowerSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMrootDomain.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMScheduler.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPoller.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPolicy.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroups.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportLegend.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportTypes.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResourceOwner.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceMatching.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceOrdering.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueueClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageFamily.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageRedundancyController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStream.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClientInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSystemReporter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTime.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTimeStamp.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTransfer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientClass.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientMethod.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientNotification.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientProperty.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientRegistry.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientTask.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientThread.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkLoop.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
RootDomainUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIControllerTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHostControllerUSBTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothL2CAPChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothRFCOMMChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPServer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPSession.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPTransaction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothServiceRecord.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothUtility.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkData.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkMedium.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterMonitor.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterProvider.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRule.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIFunction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIMessage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIPrimaryMatch.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCITunnelCompatible.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformExpert.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMPowerSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMrootDomain.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMScheduler.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPoller.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPolicy.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroups.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportLegend.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportTypes.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResourceOwner.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceMatching.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceOrdering.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueueClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageFamily.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageRedundancyController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStream.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClientInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSystemReporter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTime.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTimeStamp.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTransfer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientClass.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientMethod.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientNotification.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientProperty.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientRegistry.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientTask.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientThread.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkLoop.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
RootDomainUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHCIControllerTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothHostControllerUSBTransport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothL2CAPChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothRFCOMMChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPServer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPSession.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothSDPTransaction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothServiceRecord.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOBluetoothUtility.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOEthernetInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkData.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkMedium.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IONetworkUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterMonitor.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterProvider.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRule.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterRuleTable6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterStats.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPacketFilterUserClient6.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIFunction.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIMessage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIPrimaryMatch.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCIResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPCITunnelCompatible.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformDevice.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPlatformExpert.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMPowerSource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMrootDomain.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPMScheduler.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPoller.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOPolicy.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReport.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportChannel.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportGroups.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportLegend.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOReportTypes.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResource.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOResourceOwner.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceGroup.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceMatching.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOServiceOrdering.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSharedDataQueueClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorage.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageFamily.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStorageRedundancyController.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStream.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOStreamUserClientInterface.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOSystemReporter.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTime.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTimeStamp.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOTransfer.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientClass.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientMethod.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientNotification.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientProperty.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientRegistry.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientService.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientTask.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOUserClientThread.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkLoop.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
IOWorkQueue.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32
RootDomainUserClient.o_CWARNFLAGS_ADD += -Wno-shorten-64-to-32

# Rebuild if per-file overrides change
${OBJS}: $(firstword $(MAKEFILE_LIST))

# Rebuild if global compile flags change
$(COBJS): .CFLAGS
.CFLAGS: ALWAYS
	$(_v)$(REPLACECONTENTS) $@ $(KCC) $(CFLAGS) $(INCFLAGS)
$(CXXOBJS): .CXXFLAGS
.CXXFLAGS: ALWAYS
	$(_v)$(REPLACECONTENTS) $@ $(KC++) $(CXXFLAGS) $(INCFLAGS)
$(SOBJS): .SFLAGS
.SFLAGS: ALWAYS
	$(_v)$(REPLACECONTENTS) $@ $(S_KCC) $(SFLAGS) $(INCFLAGS)

$(COMPONENT).filelist: $(OBJS)
	@$(LOG_LDFILELIST) "$(COMPONENT)"
	$(_v)for obj in ${OBJS}; do \
		 $(ECHO) $(TARGET)/$(CURRENT_KERNEL_CONFIG)/$${obj}; \
	done > $(COMPONENT).filelist

$(COMPONENT).libfilelist: $(LIBOBJS)
	@$(LOG_LDFILELIST) "lib$(COMPONENT)"
	$(_v)for obj in ${LIBOBJS}; do \
		 $(ECHO) $(TARGET)/$(CURRENT_KERNEL_CONFIG)/$${obj}; \
	done > $(COMPONENT).libfilelist

ifeq ($(RC_ProjectName),xnu_libraries)
do_all: $(COMPONENT).libfilelist
else
do_all: $(COMPONENT).filelist
endif

do_build_all:: do_all

include $(MakeInc_rule)
include $(MakeInc_dir)
"""

# Write the hand-crafted Makefile
with open('iokit/conf/Makefile.valid', 'w') as f:
    f.write(makefile_content)

print("Created iokit/conf/Makefile.valid")

# Now patch the iokit/conf Makefile to use the valid Makefile instead of doconf
with open('iokit/conf/Makefile', 'r') as f:
    content = f.read()

# Remove the doconf rule - use a more flexible pattern
import re

# Pattern to match the doconf rule
old_rule_pattern = r'\$\(TARGET\)/\$\(CURRENT_KERNEL_CONFIG\)/Makefile: \$\(SRCROOT\)/SETUP/config/doconf \$\(OBJROOT\)/SETUP/config \$\(DOCONFDEPS\)\n\t\$\(_v\)\$\(MKDIR\) \$\(TARGET\)/\$\(CURRENT_KERNEL_CONFIG\)\n\t\$\(_v\)\$\(SRCROOT\)/SETUP/config/doconf -c -cpu \$\(DOCONF_ARCH_CONFIG_LC\) -soc \$\(CURRENT_MACHINE_CONFIG_LC\) -platform \$\(PLATFORM\) -d \$\(TARGET\)/\$\(CURRENT_KERNEL_CONFIG\) -s \$\(SOURCE\) -m \$\(MASTERCONFDIR\) \$\(DOCONF_SEED\) \$\(CURRENT_KERNEL_CONFIG\)'

new_rule = '''$(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile: $(SOURCE)/Makefile.valid $(SOURCE)/$(CURRENT_KERNEL_CONFIG)
	$(_v)$(MKDIR) $(TARGET)/$(CURRENT_KERNEL_CONFIG)
	$(_v)$(CP) $(SOURCE)/Makefile.valid $(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile'''

# Use regex to replace
new_content = re.sub(old_rule_pattern, new_rule, content, flags=re.MULTILINE)

if new_content == content:
    print("WARNING: Regex didn't match, trying alternative pattern...")
    # Try a simpler approach - find the line with doconf and replace the whole rule
    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if '$(SRCROOT)/SETUP/config/doconf' in line and '$(OBJROOT)/SETUP/config' in line:
            # Found the dependency line, now skip to the end of the rule
            new_lines.append('$(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile: $(SOURCE)/Makefile.valid $(SOURCE)/$(CURRENT_KERNEL_CONFIG)')
            new_lines.append('\t$(_v)$(MKDIR) $(TARGET)/$(CURRENT_KERNEL_CONFIG)')
            new_lines.append('\t$(_v)$(CP) $(SOURCE)/Makefile.valid $(TARGET)/$(CURRENT_KERNEL_CONFIG)/Makefile')
            # Skip the next line (the doconf command)
            i += 1
            print("Found and replaced doconf rule!")
            continue
        new_lines.append(line)
        i += 1
    new_content = '\n'.join(new_lines)

with open('iokit/conf/Makefile', 'w') as f:
    f.write(new_content)
print("Patched iokit/conf/Makefile to use hand-crafted valid Makefile")

print("Done")
EOF