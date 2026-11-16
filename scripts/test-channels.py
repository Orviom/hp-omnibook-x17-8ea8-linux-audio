#!/usr/bin/env python3
"""Play two short, low-level isolated tones through an explicitly selected sink."""
import argparse
import json
import math
from pathlib import Path
import struct
import subprocess
import tempfile
import time
import wave

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--target', choices=['speakers', 'headphones'], required=True)
args = parser.parse_args()
description = 'Speaker' if args.target == 'speakers' else 'Headphones'
objects = json.loads(subprocess.check_output(['pw-dump'], text=True, timeout=8))
nodes = [o for o in objects
         if o.get('info', {}).get('props', {}).get('media.class') == 'Audio/Sink'
         and o['info']['props'].get('device.profile.description') == description
         and o['info']['props'].get('alsa.id') == 'sofsoundwire']
if len(nodes) != 1:
    raise SystemExit('Expected exactly one matching sof-soundwire sink; no playback attempted')
target = nodes[0]['info']['props']['node.name']
cache = Path(__file__).resolve().parents[1]/'.cache'
cache.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='channel-test-', dir=cache) as temporary:
    for label, channel, frequency in [('LEFT', 0, 660), ('RIGHT', 1, 880)]:
        rate, seconds = 48000, 2
        data = bytearray()
        for i in range(rate*seconds):
            fade = max(0, min(1, i/(rate*.05), (rate*seconds-1-i)/(rate*.05)))
            value = round(32767*.12*fade*math.sin(2*math.pi*frequency*i/rate))
            data.extend(struct.pack('<hh', value if channel == 0 else 0,
                                    value if channel == 1 else 0))
        filename = Path(temporary)/(label+'.wav')
        with wave.open(str(filename), 'wb') as output:
            output.setnchannels(2)
            output.setsampwidth(2)
            output.setframerate(rate)
            output.writeframes(data)
        print(label+' channel, '+str(frequency)+' Hz', flush=True)
        subprocess.run(['pw-play', '--target', target, str(filename)], check=True, timeout=12)
        time.sleep(.5)
print('Command completion does not confirm physical channel assignment. Record the listening result.')
