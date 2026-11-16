#!/usr/bin/env python3
"""Read-only status check. Does not prove acoustic, thermal or resume behavior."""
import hashlib
import json
from pathlib import Path
import subprocess

def command(args):
    try:
        result = subprocess.run(args, text=True, capture_output=True, timeout=8)
        return {'exit':result.returncode, 'stdout':result.stdout, 'stderr':result.stderr}
    except (OSError, subprocess.TimeoutExpired) as error:
        return {'error':str(error)}

report = {'soundwire':{}, 'firmware':{}}
for node in Path('/sys/bus/soundwire/devices').glob('sdw:*'):
    report['soundwire'][node.name] = (node/'status').read_text().strip()
for uid in ['9','C']:
    path = Path('/usr/lib/firmware')/('8EA8-2-'+uid+'.bin')
    report['firmware'][path.name] = {'exists':path.exists(),
        'sha256':hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None}
report['kernel'] = command(['uname','-r'])
report['secure_boot'] = command(['mokutil','--sb-state'])
report['cards'] = command(['cat','/proc/asound/cards'])
report['pcm'] = command(['cat','/proc/asound/pcm'])
report['pipewire'] = command(['wpctl','status','-n'])
print(json.dumps(report, indent=2))
print('This output may contain a username or device names. Review before sharing.')
