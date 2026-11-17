# Technical details

## Playback path

Application → PipeWire → WirePlumber/UCM route selection → ALSA Speaker PCM 2 → SOF DSP function topology → Intel SoundWire link 2 → two TAS2783 smart amplifiers → internal speaker assembly.

The RT712 on link 3 provides headphone/headset and microphone paths. Bluetooth uses BlueZ/PipeWire and is outside the SOF/SoundWire speaker path. No BlueZ configuration was changed.

The signed distribution modules include `snd_sof_pci_intel_ptl`, `snd_soc_sof_sdw`, `snd_soc_sdw_utils`, `soundwire_intel`, `soundwire_bus`, `snd_soc_sdca`, `snd_soc_tas2783_sdw` and `snd_soc_rt712_sdca`. This project installs no `.ko` file and has no per-kernel build output. Three pre-existing distribution kernels were left installed.

## Exact firmware mapping

| Requested by tested kernel | Canonical upstream file | SHA-256 |
| --- | --- | --- |
| 8EA8-2-9.bin | ti/audio/tas2783/8EA8-0-2-0x9.bin | 90b6719dca3114687b3188253ee9be42629854e6490538a78918887be074aa5e |
| 8EA8-2-C.bin | ti/audio/tas2783/8EA8-0-2-0xC.bin | a99e80ce501ddd7c172dbde4471f26428883662184fdbe9f708d4c3aa682bc56 |

The tested driver derives names from PCI subsystem device, link and unique ID. It does not select this speaker variant in its generated request name. The installer gates use on the observed HP EFI value and provides only these two aliases. This value and successful playback do not establish an HP/TI-confirmed tuning mapping or prove per-unit calibration application. It does not create generic aliases for other boards or choose variant 1.

The Linux v7.0 codec source rejects hw_params while `fw_dl_success` is false. Supplying the exact file makes its normal firmware-request/transfer path available. Successful audio is real hardware evidence that the original missing-file obstacle was overcome; the driver was not instrumented to claim a byte-level transfer trace.

## UCM and persistent state

Only `/usr/share/alsa/ucm2/codecs/tas2783/init.conf` changes. Its four BootSequence cset names acquire ` Switch`. `/usr/share/alsa/ucm2/sof-soundwire/tas2783.conf`, RT712 profiles, DSP topologies and SOF firmware remain as shipped.

The installer refuses unexpected UCM contents. Matching canonical firmware and aliases are preserved. Each changed/created file is tracked in a root-owned session manifest; original UCM bytes and mode are retained. Uninstallation preflights all current files so an intervening package update is not silently overwritten.

Distribution package upgrades may replace the UCM correction. Prefer a maintained upstream/package fix when available, and review before reapplying. A new kernel may change firmware naming; the packaged installer intentionally stops for review. Firmware files and aliases are independent of module ABI, so recompilation is not inherently required for a kernel update.

## Scope of source work

This is an integration repair using existing driver and vendor firmware, plus a small configuration-name correction. It is not an original amplifier driver, a port of the 8EB4 timing quirk or a modification of smart-amplifier safety limits. No kernel patch is included for upstream submission because no kernel change was established as necessary for this playback result.
