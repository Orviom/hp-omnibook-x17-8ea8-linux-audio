# Testing and limits

Test session: 2026-11-16 through the early hours of 2026-11-17 (Europe/Madrid). Versions are fixed in README.md. Status is **release candidate**, not full stability certification.

| Check | Result/evidence |
| --- | --- |
| Exact board, PCI and speaker variant | Verified read-only on the physical machine. |
| Secure Boot | Enabled before changes; no signing/BIOS setting changed. |
| Two amps and RT712 | All report Attached before repair, after suspend/resume and after a subsequent manual reboot. |
| Firmware files | Both pinned SHA-256 sums match. |
| Actual internal sound | Owner confirmed volume-key feedback. |
| Left/right assignment | Owner confirmed spoken labels from correct sides. |
| Every individual transducer | Not separately established beyond two audible sides/two enumerated amps. |
| PipeWire playback | Channel-specific pw-play commands completed successfully. |
| Volume/mute | Owner confirmed a spoken sequence at sink volumes 0.30 and 0.50, an inaudible muted segment, and successful restoration at 0.45, without abnormal noise. |
| Noise/distortion | No anomaly reported in the short tests; not an extended audio-quality test. |
| Moderate-volume temperature/stability | Pending. Tests were short and low volume. |
| Original headphone baseline | Cable headphones and Bluetooth audio already worked before the speaker repair. Later checks were regression tests. |
| Cable headphone detection | Jack control and automatic default routing verified. |
| Headphone acoustic output | Verified after reboot: owner wore cable headphones and confirmed both isolated voice channels on the correct sides without abnormal noise. Initial pre-reboot non-listening test is not counted. |
| Bluetooth regression | Verified after reboot using one previously paired headphone device, A2DP/SBC, sink volume 0.30. Owner confirmed correct isolated left/right playback without cuts/noise; both pw-play calls exited 0 and no recent WirePlumber transport errors were found. Headset microphone/HFP not tested. |
| Internal mic enumeration | Restored after a complete stock audio-module reload; audio capture not tested. |
| Physical s2idle suspend/resume | One lid-close cycle recorded; owner confirmed correct stereo playback after resume. |
| Runtime idle/reopen | Several short playback operations succeeded; mixer reads while suspended logged -16. |
| Reboot persistence | Verified new boot ID, unchanged kernel/firmware/UCM, HiFi with both capture routes, three Attached endpoints, and owner-reported startup/restart audio. Owner also confirmed both isolated speaker channels on their correct sides after reboot. No manual driver reload was needed. |
| GUI/common applications | Volume feedback and pw-play verified; ffplay via PulseAudio/PipeWire also completed all four volume/mute phases. PCM was MMAP_INTERLEAVED, S32_LE, two channels, 48 kHz during playback. Owner additionally reported successful YouTube video playback on 2026-11-17. Browser identity, video and duration were not captured. |
| Kernel update | Not tested. No module build is installed; installer refuses unreviewed kernels. |
| Rollback software | Eight sandbox tests passed: synthetic install/uninstall lifecycles, preserved pre-existing firmware, original mode restoration, interrupted transactions, later-update collision refusal, missing/corrupted backup refusal and session-path validation. |
| Real-system uninstall/reinstall | Not performed; current audible repair was preserved. |
| Packaged installer | Firmware fetch and read-only plan tested. Live initial changes used the session diagnostic helper, not this new packaged installer. |

## Reproduction procedure

1. Run `python3 scripts/verify.py`; check all three endpoints and the two firmware hashes. The raw output may contain user/device names and is not automatically safe to publish.
2. Select internal speakers and start at low volume. Run `python3 scripts/test-channels.py --target speakers`, or play a stereo file with genuinely isolated channels; hear left-only and right-only content from the expected sides. The helper generates short tones, not the spoken labels used in the live session. Do not infer channel assignment from a stereo device label.
3. Verify mute, unmute and several moderate volume changes. Stop on distortion, sharp clicks or unusual temperature. Do not raise amplifier gain/safety limits.
4. Insert cable headphones and listen to both sides while wearing them. Check output selection and return to speakers when unplugged. Check an available Bluetooth audio device separately.
5. Save work, physically suspend/resume and repeat stereo, headphone and microphone checks. One successful cycle does not establish long-term reliability.
6. Reboot manually, compare boot ID/kernel/package versions, check boot logs for missing firmware/transfer/parity failures, and repeat playback before any manual module reload. This distinguishes boot persistence from the already demonstrated hot-reload result.
7. Record each pending result explicitly, including failures. Do not turn an expected result into a verified one.

Developer regression tests require no privileges and use temporary directories only:

```sh
python3 -m unittest discover -s tests -v
```
