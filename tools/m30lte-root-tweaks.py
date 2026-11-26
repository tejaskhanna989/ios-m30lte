#!/usr/bin/env python3
"""Apply the M30LTE bring-up changes to an iOS root made by tools/mkiosroot.sh.

  sudo m30-root-tweaks.py MOUNTED_ROOT

MOUNTED_ROOT is the HFS+ image mounted read-write (Linux: run
`fsck.hfsplus -fy` on the image, then `mount -t hfsplus -o loop,force`).
Run as root (it writes root/mobile owned files). Idempotent. This is what
turned the plain mkiosroot.sh output into the images that reach the home
screen (image versions v8-v14 in NOTES.md):

  launchd.plist   _PanicOnCrash -> _PanicOnCrasX (a crashing daemon must not
                  panic the system); CommCenter jobs removed (no baseband: it
                  crash-loops and Setup blocks on its CoreTelephony XPC)
  containers      /private/var/containers/{Bundle,Data/System,Shared/SystemGroup,Temp}
                  (on iOS they live on the data volume)
  migration       LastSystemVersion so DataMigration does not run for an hour
                  on every boot
  audio           VirtualAudio HAL plug-in disabled (mediaserverd crash)
  MediaToolbox    StartRecorderServer=false (camera filter prewarm calls a
                  NULL OpenGL function without a GPU -> mediaserverd crash loop)
  SpringBoard     BKNoWatchdogs (one slow CPU path, no scene-create watchdog
                  kills), no cloud-configuration UI
  Setup           skipped: SetupDone, SetupFinishedAllSteps, SetupVersion 11,
                  mini-buddy flags off
  activation      mobileactivationd data ark seeded; the actual Activated state
                  comes from its Hactivation branch, selected by the /chosen
                  security-status properties in tools/mkadt.py
"""
import glob, os, plistlib, re, shutil, stat, sys

BUILD, VERSION = '20H392', '16.7.16'
MOBILE = 501


def load(path):
    with open(path, 'rb') as f:
        return plistlib.load(f)


def save(path, data, uid, gid, mode, fmt=plistlib.FMT_BINARY):
    with open(path, 'wb') as f:
        plistlib.dump(data, f, fmt=fmt)
    os.chown(path, uid, gid)
    os.chmod(path, mode)


def merge_pref(root, name, values):
    """Merge keys into /var/mobile/Library/Preferences/NAME.plist (mobile, 0600)."""
    path = os.path.join(root, 'private/var/mobile/Library/Preferences', name + '.plist')
    data = load(path) if os.path.exists(path) else {}
    data.update(values)
    save(path, data, MOBILE, MOBILE, 0o600)
    print('pref', name, sorted(values))


def launchd(root):
    path = os.path.join(root, 'System/Library/xpc/launchd.plist')
    st = os.stat(path)
    plist = load(path)
    jobs = plist['LaunchDaemons']
    renamed = 0
    for job in jobs.values():
        if '_PanicOnCrash' in job:
            job['_PanicOnCrasX'] = job.pop('_PanicOnCrash')
            renamed += 1
    removed = [k for k, j in jobs.items() if j.get('Label') == 'com.apple.CommCenter']
    for k in removed:
        del jobs[k]
    save(path, plist, st.st_uid, st.st_gid, st.st_mode & 0o7777)
    print(f'launchd.plist: {renamed} _PanicOnCrash renamed, {len(removed)} CommCenter jobs removed')



MCM_META = '.com.apple.mobile_container_manager.metadata.plist'


def fix_container_metadata(root):
    """Align MCMMetadataUUID with the container directory name.

    iOS resolves a daemon's system/data container path from the metadata UUID.
    If it does not name an existing directory, BaseBoard passes a nil path to
    +[NSURL fileURLWithPath:] and backboardd dies with an NSException.  This
    operates on a host-staged rootfs image only, never on the device.
    """
    total = fixed = 0
    for base in ('private/var/containers', 'private/var/mobile/Containers'):
        top = os.path.join(root, base)
        if not os.path.isdir(top):
            continue
        for path, _dirs, files in os.walk(top):
            if MCM_META not in files:
                continue
            meta = os.path.join(path, MCM_META)
            data = load(meta)
            want = os.path.basename(os.path.normpath(path))
            total += 1
            if data.get('MCMMetadataUUID') != want:
                st = os.stat(meta)
                data['MCMMetadataUUID'] = want
                save(meta, data, st.st_uid, st.st_gid, st.st_mode & 0o7777)
                fixed += 1
    print(f'container metadata: {fixed}/{total} MCMMetadataUUID values aligned')
    return fixed, total



def ensure_metadata_uuid_dirs(root):
    """Materialize container directories named by MCMMetadataUUID.

    iOS rewrites the metadata UUID at boot.  If it names a directory that is
    absent from the staged rootfs, BaseBoard/MCM resolves a nil container path,
    Foundation's +[NSURL fileURLWithPath:] raises, and daemons such as lsd
    abort in a loop (see the 2026-11-26 CRASH lsd records).  Create the UUID
    directory as a content copy of the metadata's containing directory so the
    path is valid whichever UUID value the daemon uses.  Host staging only.
    """
    created = 0
    for base in ('private/var/containers', 'private/var/mobile/Containers'):
        top = os.path.join(root, base)
        if not os.path.isdir(top):
            continue
        for path, _dirs, files in os.walk(top):
            if MCM_META not in files:
                continue
            meta = os.path.join(path, MCM_META)
            try:
                data = load(meta)
            except Exception:
                continue
            uuid = data.get('MCMMetadataUUID')
            if not isinstance(uuid, str) or not re.fullmatch(r"[0-9A-Fa-f-]{36}", uuid):
                continue
            target = os.path.normpath(os.path.join(path, '..', uuid))
            # Never copy into the source tree or a path outside its parent.
            if os.path.commonpath([os.path.realpath(path), os.path.realpath(target)]) == os.path.realpath(path):
                continue
            if os.path.dirname(os.path.realpath(target)) != os.path.realpath(os.path.dirname(path)):
                continue
            if os.path.isdir(target):
                continue
            shutil.copytree(path, target, symlinks=True)
            # copytree preserves mode/times but not uid/gid; mirror those too.
            for src_dir, _dirs, files in os.walk(path, followlinks=False):
                rel = os.path.relpath(src_dir, path)
                dst_dir = target if rel == '.' else os.path.join(target, rel)
                for src_name in ['.'] + _dirs + files:
                    sp = src_dir if src_name == '.' else os.path.join(src_dir, src_name)
                    dp = dst_dir if src_name == '.' else os.path.join(dst_dir, src_name)
                    st = os.lstat(sp)
                    if stat.S_ISLNK(st.st_mode):
                        os.chown(dp, st.st_uid, st.st_gid, follow_symlinks=False)
                        continue
                    os.chown(dp, st.st_uid, st.st_gid)
                    os.chmod(dp, stat.S_IMODE(st.st_mode))
            created += 1
    print(f'container UUID directories: {created} created')
    return created

def containers(root):
    # System containers (root-owned) exist in the donor OS volume.
    base = os.path.join(root, 'private/var/containers')
    for sub, uid in (('Bundle', 33), ('Data/System', 0), ('Shared/SystemGroup', 0), ('Temp', 0)):
        d = os.path.join(base, sub)
        if not os.path.isdir(d):
            os.makedirs(d)
            os.chown(d, uid, uid)
            os.chmod(d, 0o755)
            print('mkdir', d)
    # The user container tree lives on /private/var/mobile (USERDATA) on the
    # device and is absent from the IPSW OS volume used for this image.  It is
    # referenced by MCM metadata (e.g. lsd's InternalDaemon container) and by
    # SpringBoard application containers, so create the skeleton with mobile
    # ownership (501:501).  No metadata is fabricated.
    mobile = os.path.join(root, 'private/var/mobile/Containers')
    for sub in ('Bundle', 'Data/Application', 'Data/InternalDaemon',
                'Shared/AppGroup', 'Temp'):
        d = os.path.join(mobile, sub)
        if not os.path.isdir(d):
            os.makedirs(d)
            os.chown(d, 501, 501)
            os.chmod(d, 0o755)
            print('mkdir', d)


def find_container(root, kind, identifier):
    for meta in glob.glob(os.path.join(root, 'private/var/containers', kind, '*',
                                       '.com.apple.mobile_container_manager.metadata.plist')):
        if load(meta).get('MCMMetadataIdentifier') == identifier:
            return os.path.dirname(meta)
    return None


def activation(root):
    c = find_container(root, 'Data/System', 'com.apple.mobileactivationd')
    if c is None:
        print('warning: no mobileactivationd system container in the image; skipped data ark')
        return
    d = os.path.join(c, 'Library/internal')
    os.makedirs(d, exist_ok=True)
    os.chown(d, MOBILE, MOBILE)
    os.chmod(d, 0o755)
    save(os.path.join(d, 'data_ark.plist'), {
        '-ActivationState': 'Activated', '-BrickState': False,
        '-BuildVersion': BUILD, '-ProductVersion': VERSION,
        '-DataMigrationCompleted': True, '-PreSydroDataMigrationCompleted': True,
    }, MOBILE, MOBILE, 0o600)
    print('data ark', d)


def audio(root):
    src = os.path.join(root, 'Library/Audio/Plug-Ins/HAL/VirtualAudio.plugin')
    dst_dir = os.path.join(root, 'Library/Audio/Plug-Ins/HAL.disabled')
    if os.path.exists(src):
        os.makedirs(dst_dir, exist_ok=True)
        shutil.move(src, dst_dir)
        print('VirtualAudio.plugin disabled')
    for conf in glob.glob(os.path.join(root, 'System/Library/Frameworks/MediaToolbox.framework/*/SubServerConfiguration.plist')):
        st = os.stat(conf)
        data = load(conf)
        data['StartRecorderServer'] = False
        save(conf, data, st.st_uid, st.st_gid, st.st_mode & 0o7777, plistlib.FMT_XML)
        print('StartRecorderServer off', os.path.relpath(conf, root))


def main():
    if len(sys.argv) != 2 or not os.path.isdir(os.path.join(sys.argv[1], 'System/Library/xpc')):
        sys.exit(__doc__)
    root = sys.argv[1]
    launchd(root)
    containers(root)
    # Create UUID-named dirs from the original metadata BEFORE rewriting the
    # metadata, because iOS restores those original UUID values at boot.
    ensure_metadata_uuid_dirs(root)
    fix_container_metadata(root)
    activation(root)
    audio(root)
    merge_pref(root, 'com.apple.migration', {
        'LastSystemVersion': BUILD,
        'DMUserDataDisposition': {'SyntheticDidUpgrade': False, 'buildVersion': BUILD}})
    merge_pref(root, 'com.apple.springboard', {
        'BKNoWatchdogs': True,
        'FBLaunchWatchdogExceptions': {'com.apple.purplebuddy': 100.0},
        'MCForceShowCloudConfigurationUI': False})
    merge_pref(root, 'com.apple.purplebuddy', {
        'SetupDone': True, 'SetupFinishedAllSteps': True, 'SetupVersion': 11,
        'daemonizeNeedsToRun': False})
    merge_pref(root, 'com.apple.purplebuddy.notbackedup', {
        k: False for k in ('ShouldRunDiagnosticsMiniBuddy', 'ShouldRunHSA2MiniBuddy',
                           'ShouldRunKeychainSyncMiniBuddy', 'ShouldRunMesaMiniBuddy',
                           'ShouldRunPaymentMiniBuddy', 'ShouldRunStandardMiniBuddy',
                           'SilentICDPUpgrade')})
    merge_pref(root, 'com.apple.managedconfiguration.notbackedup', {
        'LockdownActivationIndicatesCloudConfigurationAvailable': False})


if __name__ == '__main__':
    main()
