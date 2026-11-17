# Diagnosis and experiment record

## Initial observation, 2026-11-16

The owner explicitly reported that cable headphones and Bluetooth audio already worked. Only the internal-speaker failure was the repair target; later headphone listening was regression testing.

The historical handoff mentioned a 6.11 kernel and BIOS F.11. Read-only DMI/package checks instead found kernel 7.0.0-43-generic and BIOS F.06. No BIOS change was made. The hardware identifiers and exact software versions are in the README; serial numbers and host/user names are deliberately omitted here.

SoundWire enumerated two `sdw:m0102p0000v03c01` amplifiers and one `sdw:m025Dp0712v03c01` Realtek codec. All three status files read `Attached`. SOF booted DSP firmware 2.14.1.1. ACPI SmartAmp, UAJ, SmartMic and HID functions were detected. Function topologies included `sof-sdca-1amp-id2.tplg`, `sof-sdca-jack-id0.tplg` and `sof-sdca-mic-id4.tplg`.

Relevant initial kernel messages, with host names/timestamps removed:

```text
slave-tas2783 sdw:0:2:0102:0000:01:c: Direct firmware load for 8EA8-2-C.bin failed with error -2
slave-tas2783 sdw:0:2:0102:0000:01:9: Direct firmware load for 8EA8-2-9.bin failed with error -2
slave-tas2783 sdw:0:2:0102:0000:01:9: error playback without fw download
SDW2-Playback-SmartAmp: ASoC error (-22): at __soc_pcm_hw_params()
```

ALSA had Speaker PCM 2 before any change. The card component string included `cfg-amp:2 spk:tas2783 hs:rt712 mic:rt712`. UCM could parse HiFi and its devices, but PipeWire offered only off/pro-audio card profiles and Dummy Output was active. Local firmware searches found no 8EA8 files. The installed UCM codec init file used four control names without the suffix `Switch`, although `amixer contents` exposed that suffix. `dpkg -V alsa-ucm-conf` initially reported no local modifications.

## Hypotheses assessed

| Hypothesis | Evidence and decision |
| --- | --- |
| No Intel audio/RT712 support | Rejected as primary cause: SOF ran, RT712 was attached and ALSA endpoints existed. |
| No SmartAmp SDCA function | Rejected for this BIOS: both SmartAmp functions were found. |
| 8EB4 ACTMCTL timing failure | Not observed: both amps were attached; no parity/dropout pattern was present in the initial captured log. No timing-register write was attempted. |
| Missing board firmware/name mismatch | Directly established by failed requests, absent files and upstream board-specific firmware. |
| UCM control-name mismatch | Directly established by comparing the installed init file with real mixer controls. Its independent contribution to HiFi profile failure was not isolated from the firmware correction. |
| PipeWire alone | Insufficient: the codec explicitly rejected playback without firmware. |
| Per-unit calibration issue | Unresolved source-review concern, not established as the original cause of silence. |

## Firmware selection and changes

EFI HPSpeakerID had four attribute bytes followed by `0x30` (ASCII `0`). Upstream contains both `8EA8-0-2-*` and `8EA8-1-2-*` files. Only variant 0 was installed. Its file container label identifies the HP 17-inch stereo Sable tuning; variant 1 has a different YC label. The variants are not interchangeable merely because sizes match.

Successful playback with variant 0 is empirical evidence for this unit, not vendor confirmation of HPSpeakerID mapping, thermal/protection behavior or individual calibration. These questions were [reported to the existing upstream thread](https://github.com/thesofproject/linux/issues/5957#issuecomment-6941335315). See [UPSTREAM_STATUS.md](UPSTREAM_STATUS.md).

Two files were fetched from a pinned linux-firmware commit, SHA-256 checked, and their documented container lengths/block boundaries sanity-checked against the codec loader format. Each is 40,746 bytes with 52 firmware chunks. No DSP instructions were disassembled and no blob bytes were changed. Two relative aliases bridge the old driver names to the original filenames. The four UCM BootSequence names were corrected in one separately backed-up text file.

Both persistent corrections were installed before the first hardware reset. This was not a controlled A/B test of each correction alone; do not claim that either alone fully repairs this installation.

## Runtime experiments and recovery

1. Stopped WirePlumber and unbound/rebound only the PCI audio controller to its original driver. Missing-firmware failures ceased and HiFi speaker output appeared after restarting user audio services.
2. The partial hot rebind lost `mic:rt712` from the card component string, although the microphone PCM and controls remained. Restarting PipeWire alone did not restore the tag. No permanent microphone workaround was added.
3. Stopped PipeWire, its sockets and WirePlumber, then unloaded/reloaded the original signed SOF audio module stack without force. The SoundWire machine-helper module was unloaded too. `mic:rt712` returned and HiFi again exposed both capture devices. The root cause of this reprobe-state issue was not proven; source has global per-DAI initialization state, making retained state a plausible explanation.
4. Owner confirmed speaker output using the volume keys. Two short channel-isolated tones were heard, but the first result did not establish side assignment. A second test sent spoken Spanish labels into separate stereo channels; the owner confirmed the correct physical sides.
5. Headphone insertion and automatic routing were observed. Playback to the headphone sink completed, but the owner was not wearing the headphones, so acoustic headphone behavior was unverified at that stage (completed in step 8).
6. Owner physically closed and reopened the lid. Kernel records show `PM: suspend entry (s2idle)` and `PM: suspend exit`. All three SoundWire endpoints remained attached and the owner confirmed correct stereo playback after resume.

Reading amplifier mixer controls while runtime-suspended produced `soc_component_read_no_lock` errors `-16` for registers `0x00800003` and `0x0080001a`. Later awake reads showed both amps at gain value 9 and speaker-volume value 200. These read errors must be retained in the record; they are not evidence of failed firmware transfer or proof of flawless operation. No gain values were written by this repair.

7. Owner manually rebooted. A changed boot ID established that this was a new boot on the same `7.0.0-43-generic` kernel. Both firmware hashes and the corrected UCM hash persisted; all three SoundWire peripherals were Attached. HiFi exposed five sinks and two capture devices, including the internal microphone. Secure Boot remained enabled. The captured boot had zero missing TAS2783-firmware messages, transfer failures, parity messages or TAS2783 ASoC-read errors. The owner reported audible startup/restart audio. No module reload or configuration correction was performed after reboot. A further channel-specific voice test completed; the owner confirmed correct physical sides after reboot.

8. After reboot, the owner connected and wore cable headphones. The jack was detected, isolated speech played through the headphone sink, and the owner confirmed the correct sides without abnormal noise. This completes the acoustic headphone check that was previously pending.

9. With headphones removed, ffplay routed through PulseAudio/PipeWire played speech at sink levels 0.30 and 0.50, then a muted segment and a restored segment at 0.45. The owner confirmed the change in volume, silence and restored output without abnormal noise. All four player calls returned zero and PCM parameters were stereo S32_LE at 48 kHz. This is a brief functional check, not an extended thermal/stability test.

10. In the final part of the session (early 2026-11-17 local time), the owner made Bluetooth headphones available. BlueZ initially showed the single paired audio device disconnected; a normal Connect request succeeded without re-pairing. A2DP/SBC became available. Channel-isolated speech played at sink level 0.30; both calls completed and the owner confirmed the correct sides without dropouts/noise. Recent WirePlumber logs contained no Bluetooth transport failure. No Bluetooth configuration file or profile policy was changed.

11. On 2026-11-17 the owner additionally reported successful YouTube video playback in a browser. Browser identity, video, duration and long-term thermal measurements were not recorded.

## Remaining questions

Extended use and thermal behavior have not been established. Confirm per-transducer coverage if the physical speaker assembly has more transducers than the two audible sides. Perform moderate normal-use/thermal checks without raising limits. The reviewed upstream v7.0 codec source reads calibration using GUID `1f52d2a1-bb3a-457d-bc09-43a3f4310a92`; this machine exposes a 64-byte SmartAmpCalibrationData payload under GUID `53559579-8753-4f5c-9130-e82acfb8d893`. Actual per-unit calibration application was not instrumented or proved. Do not duplicate the EFI variable under another GUID as a guessed fix.
