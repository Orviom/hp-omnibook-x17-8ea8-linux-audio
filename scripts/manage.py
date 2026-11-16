#!/usr/bin/env python3
"""Conservative firmware/UCM installer for the hardware documented in README.md."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import stat
import tempfile

PROJECT = Path(__file__).resolve().parents[1]
STATE = Path('/var/lib/hp-omnibook-8ea8-audio')
FW = Path('/usr/lib/firmware')
UCM = Path('/usr/share/alsa/ucm2/codecs/tas2783/init.conf')
HASHES = {
    '9': '90b6719dca3114687b3188253ee9be42629854e6490538a78918887be074aa5e',
    'C': 'a99e80ce501ddd7c172dbde4471f26428883662184fdbe9f708d4c3aa682bc56',
}
OLD_UCM = 'fe6a4518913dc2dadc1ae707179dbec7b6e77cfa5df79d961d48ff9c649b4c84'
NEW_UCM = 'a5bf8a18901ddd6b7339c421e74faac1002539420643ba855b2496a48fde6122'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def hardware_check():
    for name, wanted in [('sys_vendor','HP'), ('board_name','8EA8'),
                         ('product_name','HP OmniBook X Laptop 17-de0xxx')]:
        require(Path('/sys/class/dmi/id', name).read_text().strip() == wanted,
                'Unsupported DMI '+name)
    pci = Path('/sys/bus/pci/devices/0000:00:1f.3')
    for name, wanted in [('vendor','0x8086'), ('device','0xe428'),
                         ('subsystem_vendor','0x103c'), ('subsystem_device','0x8ea8')]:
        require((pci/name).read_text().strip() == wanted, 'Unsupported PCI '+name)
    var = Path('/sys/firmware/efi/efivars/HPSpeakerID-c49593a4-d099-419b-a2c3-67e980e61d1e')
    require(var.read_bytes()[4:] == b'0', 'Only ASCII speaker variant 0 was tested')
    require(platform.release() == '7.0.0-43-generic',
            'Untested kernel: review requested firmware names and UCM controls first')

def atomic_write(path, data, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.hp8ea8-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.lexists(temporary):
            os.unlink(temporary)

def matches(path, item):
    if 'link' in item:
        return path.is_symlink() and os.readlink(path) == item['link']
    return path.is_file() and not path.is_symlink() and digest(path.read_bytes()) == item['sha256']

def restore(run):
    manifest = json.loads((run/'manifest.json').read_text())
    backups = {}
    # Preflight every entry before changing anything; do not overwrite later updates.
    for item in manifest:
        path = Path(item['path'])
        if item['existed']:
            backup = run/item['backup']
            require(backup.parent == run and backup.name not in {'.', '..'}
                    and backup.is_file() and not backup.is_symlink(),
                    'Missing or invalid backup: '+str(backup))
            backups[str(path)] = backup.read_bytes()
            if 'old_sha256' in item:
                require(digest(backups[str(path)]) == item['old_sha256'],
                        'Backup integrity check failed: '+str(backup))
        if matches(path, item):
            continue
        if item.get('existed') and path.is_file() and not path.is_symlink():
            old = backups[str(path)]
            if path.read_bytes() == old:  # An interrupted transaction never changed it.
                continue
        require(not item['existed'] and not os.path.lexists(path),
                'Refusing to overwrite a changed file: '+str(path))
    for item in reversed(manifest):
        path = Path(item['path'])
        if item['existed']:
            atomic_write(path, backups[str(path)], item['mode'])
        elif os.path.lexists(path):
            path.unlink()
    atomic_write(run/'STATUS', b'uninstalled\n', 0o600)

def transaction(files, links, state):
    """Apply an already reviewed, collision-checked plan with a rollback manifest."""
    run = state/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    run.mkdir(parents=True, mode=0o700)
    manifest = []
    def record(item):
        manifest.append(item)
        atomic_write(run/'manifest.json', json.dumps(manifest, indent=2).encode(), 0o600)
    try:
        for path, data in files:
            require(not path.is_symlink(), 'Refusing symlink destination: '+str(path))
            existed = path.exists()
            item = {'path':str(path), 'existed':existed, 'sha256':digest(data)}
            if existed:
                require(path.is_file(), 'Destination is not a regular file')
                backup = 'backup-'+str(len(manifest))
                original = path.read_bytes()
                atomic_write(run/backup, original, 0o600)
                item.update(backup=backup, mode=stat.S_IMODE(path.stat().st_mode),
                            old_sha256=digest(original))
            record(item)
            atomic_write(path, data)
        for path, target in links:
            require(not os.path.lexists(path), 'Alias appeared during installation')
            path.parent.mkdir(parents=True, exist_ok=True)
            record({'path':str(path), 'existed':False, 'link':target})
            path.symlink_to(target)
        atomic_write(run/'STATUS', b'installed; validation pending\n', 0o600)
    except Exception:
        if manifest:
            restore(run)
        raise
    return run

def plan():
    hardware_check()
    files, links = [], []
    for uid, checksum in HASHES.items():
        filename = '8EA8-0-2-0x'+uid+'.bin'
        source = PROJECT/'.cache/firmware'/filename
        require(source.is_file() and digest(source.read_bytes()) == checksum,
                'Run scripts/fetch-firmware.py first; missing/invalid '+filename)
        destination = FW/'ti/audio/tas2783'/filename
        if os.path.lexists(destination):
            require(matches(destination, {'sha256':checksum}), 'Firmware collision: '+str(destination))
        else:
            files.append((destination, source.read_bytes()))
        alias = FW/('8EA8-2-'+uid+'.bin')
        target = 'ti/audio/tas2783/'+filename
        if os.path.lexists(alias):
            require(matches(alias, {'link':target}), 'Alias collision: '+str(alias))
        else:
            links.append((alias, target))
    require(not UCM.is_symlink(), 'Unexpected UCM symlink')
    old = UCM.read_bytes()
    if digest(old) != NEW_UCM:
        require(digest(old) == OLD_UCM, 'UCM version differs; review before installation')
        text = old.decode()
        for control in ['Left Spk', 'Right Spk', 'Left Spk2', 'Right Spk2']:
            text = text.replace("name='"+control+"'", "name='"+control+" Switch'")
        require(digest(text.encode()) == NEW_UCM, 'Unexpected resulting UCM')
        files.append((UCM, text.encode()))
    return files, links

def session_path(name):
    require(name and re.fullmatch(r'\d{8}T\d{6}(?:\.\d{6})?Z', name),
            'Specify --session with the exact timestamp directory printed at installation')
    run = STATE/name
    require(run.is_dir() and not run.is_symlink() and run.resolve().parent == STATE.resolve(),
            'Backup session does not exist or is outside the state directory')
    return run

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['plan', 'install', 'uninstall'])
    parser.add_argument('--session', help='Exact existing backup directory name, not a path')
    args = parser.parse_args()
    if args.action == 'uninstall':
        require(os.geteuid() == 0, 'Run with sudo or pkexec')
        run = session_path(args.session)
        restore(run)
        print('Restored backup. Restart audio services; reboot manually when convenient.')
        return
    files, links = plan()
    for path, data in files:
        print('WRITE', path, 'sha256='+digest(data))
    for path, target in links:
        print('LINK', path, '->', target)
    if args.action == 'plan':
        print('No changes made.')
        return
    require(os.geteuid() == 0, 'Run with sudo or pkexec')
    if not files and not links:
        print('All requested files already match. Existing backup ownership is unchanged.')
        return
    run = transaction(files, links, STATE)
    print('Backup:', run)
    print('Installed. Reboot MANUALLY when safe, then follow docs/TESTING.md.')
    print('No kernel, module, bootloader, BIOS, Secure Boot or EFI changes were made.')

if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError) as error:
        raise SystemExit(str(error))
