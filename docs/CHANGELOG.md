# Changelog

## 0.1.0-rc3 — 2026-11-17

- Prepared the English publication candidate and third-party/contribution notices.
- Clarified that cable and Bluetooth headphones worked before the speaker repair.
- Added the owner-reported YouTube browser-playback result.
- Preflight all backups and verify new backup hashes before rollback; reject invalid session paths.
- Expanded to eight passing tests, including synthetic install/uninstall and preservation of existing firmware.
- Kept installed firmware/UCM and the running system unchanged.

## 0.1.0-rc2 — 2026-11-16/17

- Verified a fresh manual reboot with unchanged firmware/UCM, original kernel and Secure Boot enabled.
- Confirmed normal HiFi and microphone enumeration without post-boot module reload.
- Captured a clean TAS2783/SoundWire error summary for that boot.
- Owner confirmed startup/restart audio, correct isolated speaker channels after reboot and correct cable-headphone stereo without abnormal noise.
- Verified audible volume changes, silence and recovery using ffplay through PipeWire.
- Added a reproducible short channel-tone tool.
- Verified left/right Bluetooth playback via A2DP/SBC after reboot, with owner listening confirmation.
- Extended thermal/stability checks and kernel updates remain untested.

## 0.1.0-rc1 — 2026-11-16

- Diagnosed exact 8EA8/SpeakerID 0 firmware absence and legacy request-name mismatch.
- Installed two unmodified upstream firmware files with two aliases.
- Corrected four UCM BootSequence switch-control names.
- Restored real HiFi output with stock signed modules and Secure Boot enabled.
- Owner confirmed left/right playback and one successful s2idle resume test.
- Documented partial-hot-rebind microphone-tag loss, successful stock-module recovery, suspended-mixer read errors and calibration uncertainty.
- Added guarded installer, pinned firmware fetch, read-only verifier and sandbox rollback tests.
- Marked reboot/headphone/Bluetooth and extended stability checks as pending. No publication performed.

## 2026-11-17 — upstream communication documentation

Added verified comments on existing ALSA PR #886 and linux issue #5957, Guido Jouret attribution, maintainer/status distinctions and remaining HP tuning/calibration questions. No repair-code or installed-system changes.
