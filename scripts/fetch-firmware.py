#!/usr/bin/env python3
"""Fetch only the exact tested upstream firmware and its license; no installation."""
import base64
import hashlib
from pathlib import Path
import urllib.request

COMMIT = '2f90f4fe5c67f51a8410907aedf911dabb7120ca'
BASE = 'https://kernel.googlesource.com/pub/scm/linux/kernel/git/tnguy/firmware/+/'+COMMIT+'/'
FILES = {
    'ti/audio/tas2783/8EA8-0-2-0x9.bin': '90b6719dca3114687b3188253ee9be42629854e6490538a78918887be074aa5e',
    'ti/audio/tas2783/8EA8-0-2-0xC.bin': 'a99e80ce501ddd7c172dbde4471f26428883662184fdbe9f708d4c3aa682bc56',
    'LICENCE.ti-tspa': '5bc52a8ad08b531ee17fb3c35b8f83c8649c9aecfb6ce7a7975ee62d840f4c9b',
}
out = Path(__file__).resolve().parents[1]/'.cache/firmware'
out.mkdir(parents=True, exist_ok=True)
for name, expected in FILES.items():
    with urllib.request.urlopen(BASE+name+'?format=TEXT', timeout=30) as response:
        data = base64.b64decode(response.read(), validate=True)
    checksum = hashlib.sha256(data).hexdigest()
    if expected and checksum != expected:
        raise SystemExit('Integrity check failed: '+name)
    (out/Path(name).name).write_bytes(data)
    print(Path(name).name, len(data), checksum)
print('Firmware remains subject to LICENCE.ti-tspa. Read that file before use.')
