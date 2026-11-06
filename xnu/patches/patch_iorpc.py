import sys

file_path = 'iokit/DriverKit/IORPC.h'

try:
    with open(file_path, 'r') as f:
        content = f.read()
except FileNotFoundError:
    print(f"File not found: {file_path}")
    sys.exit(1)

# Add kernelContent field to IORPC struct
old_struct = """struct IORPC {
	IORPCMessageMach * message;
	IORPCMessageMach * reply;
	uint32_t           sendSize;
	uint32_t           replySize;
};"""

new_struct = """struct IORPC {
	IORPCMessageMach * message;
	IORPCMessageMach * reply;
	uint32_t           sendSize;
	uint32_t           replySize;
	void *             kernelContent;  // Added for Xcode 26 compatibility
};"""

if old_struct in content:
    content = content.replace(old_struct, new_struct)
    with open(file_path, 'w') as f:
        f.write(content)
    print("Patched IORPC.h successfully")
else:
    print("Could not find IORPC struct to patch")
    sys.exit(1)
