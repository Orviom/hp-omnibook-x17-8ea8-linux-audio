# v0.1.0-rc3 — publication candidate

Prepared on 2026-11-17 for an initial public release candidate. The owner authorized public publication on 2026-11-17.

## Scope and results

Restore internal-speaker playback on the tested HP OmniBook X 17-de0xxx / 8EA8 / speaker variant 0 with the distribution kernel and signed modules. Cable and Bluetooth headphones already worked and were checked for regressions.

The owner confirmed speaker channel assignment, volume/mute/recovery, playback after one s2idle suspend/resume and a manual reboot, and cable-headphone/Bluetooth A2DP-SBC playback without reported abnormal noise or cuts. Successful YouTube browser playback was also reported. Firmware/UCM persisted and Secure Boot remained enabled.

The installed repair is unchanged from rc2. This candidate strengthens backup preflight and session-path validation, adds lifecycle/corruption tests, clarifies the headphone baseline and prepares public documentation. It makes no new installed-system changes.

## Automated checks and limits

Eight tests passed in temporary directories, including synthetic install/uninstall lifecycles and preservation of pre-existing firmware. The hardware-guarded plan proposes no changes on the repaired machine. No separate clean-machine installation or real-system rollback test was performed.

One configuration tested. Extended thermal/stability behavior, future kernels, individual calibration loading, per-transducer measurements, microphone capture and Bluetooth HFP remain unverified. See TESTING.md and DIAGNOSIS.md.

## Package

English source/documentation, MIT license for original work, third-party notices and source checksums. No firmware binaries, compiled kernel modules, private logs, calibration payloads, credentials or personal paths are included.
