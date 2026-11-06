import os
import sys

def patch_file(filepath):
    """Patch a single file to add kernelContent to IORPC and fix OSObject.iig.cpp"""
    # Skip fakeroot and build directories
    if 'fakeroot' in filepath or 'BUILD/obj' in filepath or 'buildtree' in filepath:
        return False
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except:
        return False
    
    modified = False
    
    # Patch IORPC struct
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
        modified = True
    
    # Patch OSObject.iig.cpp references - use proper cast for IORPCMessage*
    if 'rpc.kernelContent' in content:
        content = content.replace('rpc.kernelContent', '(IORPCMessage*)nullptr')
        modified = True
    if '.kernelContent = ' in content:
        content = content.replace('.kernelContent = ', '/* .kernelContent = */ ')
        modified = True
    
    if modified:
        try:
            with open(filepath, 'w') as f:
                f.write(content)
            return True
        except PermissionError:
            return False
    return False

def main():
    patched = 0
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in ('fakeroot', 'BUILD', 'buildtree', '.git')]
        for f in files:
            if f.endswith('.h') or f.endswith('.cpp') or f.endswith('.c'):
                filepath = os.path.join(root, f)
                if patch_file(os.path.join(root, f)):
                    patched += 1
    print(f"Patched {patched} files")

if __name__ == '__main__':
    main()
