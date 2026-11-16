# Troubleshooting and recovery

## Missing firmware or legacy filename

```sh
journalctl -k -b -o cat | rg 'tas2783|firmware|PARITY'
ls -l /usr/lib/firmware/8EA8-2-9.bin /usr/lib/firmware/8EA8-2-C.bin
sha256sum /usr/lib/firmware/8EA8-2-9.bin /usr/lib/firmware/8EA8-2-C.bin
```

Compare requests exactly, including case, speaker variant and `0x`. Do not point a request at firmware for a different board. Re-run the read-only plan only on the supported hardware/version. A missing filename is distinct from `FW download failed`, bus parity errors or an unattached amp.

## Dummy Output or no HiFi

```sh
aplay -l
amixer -c 0 controls
alsaucm -c hw:0 dump text
wpctl status -n
```

Confirm actual card number before using `-c 0`. On the tested machine, Speaker is PCM 2 and UCM must use real Switch-suffixed control names. Parsing a UCM verb alone does not prove that all its runtime sequences or firmware are usable. Once drivers have settled, restart user audio services if appropriate:

```sh
systemctl --user restart pipewire pipewire-pulse wireplumber
```

This interrupts active audio. Do not run it repeatedly as a substitute for finding a missing firmware file.

## Hot rebind loses internal microphone

The initial PCI-only rebind lost `mic:rt712`; restarting userspace did not restore it. A full non-forced reload of the stock audio modules restored the tag in the development session. This is not a persistent fix shipped by the installer. Prefer a normal manual reboot when convenient over repeated PCI unbind/rebind experiments. Do not force module removal and do not replace signed modules based on this observation alone.

## Mixer reads return -16

Reading TAS2783 volume registers while runtime-suspended generated `soc_component_read_no_lock` errors. The same controls were readable while awake. These errors are recorded as a known limitation; this project does not disable power management or suppress errors. Report the exact context separately from missing firmware, streaming errors and audible defects.

## Rollback

```sh
sudo python3 scripts/manage.py uninstall --session BACKUP_DIRECTORY_NAME
```

This restores original UCM bytes and mode, removes only the unchanged files/aliases created by that session, and keeps the backup manifest. It does not remove a matching pre-existing firmware file that the installer merely reused. If a later update changed a managed file, restoration stops before any changes. Inspect the original backup and current package version rather than deleting that protection.

No boot configuration or kernel module on disk is modified, so the previous distribution kernels remain available from GRUB's advanced options. No automatic reboot or Secure Boot change is part of recovery. Legacy development-session manifests are also supported.

## Private evidence

Public material should exclude full journal dumps, host/user names, Bluetooth addresses, DMI serial/UUID values, unreviewed ACPI dumps and per-unit EFI calibration data. The development session retained these locally under its private work directory; they are not bundled here. Sanitized excerpts in DIAGNOSIS.md describe only the relevant observations.
