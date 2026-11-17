# HP OmniBook X 17 (8EA8): Linux internal speaker repair

**Version 0.1.0-rc3 — initial release candidate, tested on one physical machine.**

This community project documents a working internal-speaker repair for an HP OmniBook X Laptop 17-de0xxx running Linux Mint 22.3. It provides reproducible firmware retrieval, a guarded installer, rollback, diagnostics and a detailed investigation record.

**Cable headphones and Bluetooth audio already worked before this repair.** They were retested to check for regressions. The fault addressed here was silent internal speakers.

The repair uses the existing distribution kernel and signed modules. It installs two pinned variant-0 board firmware files under the names requested by the driver and corrects four ALSA UCM control names. Playback was verified on this unit; HP/TI confirmation of the speaker-ID-to-tuning mapping remains pending. No kernel compilation, replacement module, BIOS change or Secure Boot change is required.

## Tested configuration

| Component | Verified configuration |
| --- | --- |
| Laptop / product SKU | HP OmniBook X Laptop 17-de0xxx / D44KKEA#ABE |
| DMI board / BIOS | 8EA8 / F.06, 2026-06-23 |
| Processor | Intel Core Ultra X7 358H, Panther Lake |
| Distribution / kernel | Linux Mint 22.3 Zena / 7.0.0-43-generic, build 7.0.0-43.43~24.04.1 |
| Audio PCI / subsystem | 8086:e428 / 103c:8ea8 |
| Amplifiers | Two TI TAS2783: SoundWire link 2, manufacturer 0102, part 0000, UID 9 and C |
| Headphone/microphone codec | Realtek RT712: link 3, manufacturer 025d, part 0712 |
| HPSpeakerID | ASCII 0, following four EFI attribute bytes |
| SOF DSP firmware | ADSPFW 2.14.1.1 |
| ALSA UCM package | alsa-ucm-conf 1.2.10-1ubuntu5.15 |
| PipeWire / WirePlumber | 1.0.5-1ubuntu3.3 / 0.4.17-1ubuntu4.1 |
| Secure Boot | Enabled throughout testing |

Only this configuration has been tested. Another laptop with TAS2783 amplifiers is not automatically compatible. The installer rejects untested kernels and unexpected UCM content. AMD ACP systems and HP board 8EB4 are outside the tested scope.

## Problem and solution

Both amplifiers were attached and their SmartAmp functions were recognized. ALSA already exposed Speaker PCM 2, but the driver could not find 8EA8-2-9.bin or 8EA8-2-C.bin and rejected playback without firmware. The initial desktop capture showed Dummy Output.

Upstream linux-firmware already contained the exact variant-0 files, 8EA8-0-2-0x9.bin and 8EA8-0-2-0xC.bin. The repair installs those unmodified files with two legacy-name aliases. It also corrects four UCM BootSequence names to match the kernel controls: Left Spk Switch, Right Spk Switch, Left Spk2 Switch and Right Spk2 Switch.

Both corrections were applied before the first playback experiment; their independent contributions were not isolated. No SoundWire timing patch or amplifier safety-limit change was applied. See [DIAGNOSIS.md](docs/DIAGNOSIS.md) and [TECHNICAL_DETAILS.md](docs/TECHNICAL_DETAILS.md).

## Installation

Requirements: tested hardware/software, Python 3, internet access for the pinned firmware, administrative authentication for installation, and PipeWire utilities for diagnostics/playback tests. Review the plan first.

```sh
python3 scripts/fetch-firmware.py
python3 scripts/manage.py plan
sudo python3 scripts/manage.py install
```

Firmware is downloaded separately with SHA-256 verification and its TI license; it is not bundled. The installer checks DMI, PCI, speaker variant, kernel, firmware hashes and UCM content. It refuses conflicting files and saves originals/manifests under /var/lib/hp-omnibook-8ea8-audio/, outside personal folders.

Installation does not reboot or reload audio automatically. Reboot manually when convenient, then verify playback. The live repair used the session diagnostic helper. The packaged installer was checked using a read-only plan on the repaired machine and synthetic install/uninstall lifecycles in temporary directories; a separate clean-machine installation has not been performed.

## Verification and tested results

```sh
python3 scripts/verify.py
python3 scripts/test-channels.py --target speakers
python3 -m unittest discover -s tests -v
```

The owner confirmed correct speaker left/right assignment, volume changes, mute/recovery, playback after one s2idle suspend/resume cycle and playback after a manual reboot. No post-reboot driver reload was needed. Cable-headphone and Bluetooth A2DP/SBC playback remained functional. The owner also reported successful YouTube video playback in a browser; browser identity, video and duration were not captured.

Eight sandbox tests cover installation, repeated planning, rollback, preserved pre-existing firmware, later file changes, missing/corrupted backups and invalid session paths. They do not establish hardware compatibility on other machines.

Extended thermal/stability testing, per-transducer measurements, individual factory-calibration loading, microphone capture, Bluetooth HFP, kernel upgrades and real-system uninstall/reinstall remain unverified. See [TESTING.md](docs/TESTING.md).

## Uninstallation and updates

```sh
sudo python3 scripts/manage.py uninstall --session BACKUP_DIRECTORY_NAME
```

Use the timestamp directory printed during installation. Before restoring anything, the uninstaller checks current managed files and available backups. New manifests include backup hashes; legacy development-session manifests remain supported. Later package changes or unrelated modifications stop restoration for review. Original kernels/modules are never removed. Reboot manually after removal.

Prefer maintained Mint/Ubuntu updates when they supply the required firmware names and UCM controls. Updates may overwrite the UCM correction or change requested firmware names. Review before reapplying. This repair has no DKMS or module ABI dependency. Recovery commands and known hot-rebind/runtime-mixer limitations are in [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## Upstream, attribution and participation

On 2026-11-17, additional 8EA8 hardware evidence was [posted on Guido Jouret's existing ALSA PR #886](https://github.com/alsa-project/alsa-ucm-conf/pull/886#issuecomment-6941275267), and the working local repair was [reported in the existing TAS2783 firmware thread](https://github.com/thesofproject/linux/issues/5957#issuecomment-6941335315). No duplicate PR or issue was opened. The ALSA patch is Guido's contribution. These reports are communicated, not evidence of maintainer acceptance or distribution availability. See [UPSTREAM_STATUS.md](docs/UPSTREAM_STATUS.md) for status, scope, sources and follow-up.

Firmware was already upstream in [linux-firmware commit 2f90f4fe](https://kernel.googlesource.com/pub/scm/linux/kernel/git/tnguy/firmware/+/2f90f4fe5c67f51a8410907aedf911dabb7120ca). [Kasey Prichard's 8EB4 investigation](https://github.com/kasemeyer/hp-omnibook-tas2783-sdw) was a priority reference, but its kernel patches were not applied or adapted. Its [SOF PR #5904](https://github.com/thesofproject/linux/pull/5904) was open/unmerged when rechecked on 2026-11-17. No upstream patch has been submitted by this project. Full credits and Intel/AMD distinctions are in [SOURCES.md](docs/SOURCES.md).

OpenAI Codex assisted with diagnosis, source review, code and documentation. The owner performed listening, physical suspend/reboot and browser playback checks. No independent maintainer hardware review has been claimed.

This is an independent, unofficial community project, not affiliated with or endorsed by HP, Texas Instruments, Intel, Linux Mint or GitHub. Names identify the tested hardware/services.

Original scripts/documentation use the [MIT license](LICENSE). Third-party components retain their own terms; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Contributions should be respectful, reproducible and privacy-conscious; see [CONTRIBUTING.md](CONTRIBUTING.md).
