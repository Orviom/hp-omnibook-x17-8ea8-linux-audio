# Upstream communication status

Snapshot: 2026-11-17. This is a documentation update; repair code and installed audio configuration were not changed.

| Component / destination | Action and status | What remains |
| --- | --- | --- |
| ALSA UCM, [Guido Jouret's PR #886](https://github.com/alsa-project/alsa-ucm-conf/pull/886) | [8EA8 evidence posted](https://github.com/alsa-project/alsa-ucm-conf/pull/886#issuecomment-6941275267). Existing PR open/unmerged; our comment is not a maintainer review. | Maintainer review, merge and package delivery. |
| TAS2783 driver / firmware naming, [existing issue #5957](https://github.com/thesofproject/linux/issues/5957) | [Working local repair and HP-specific questions posted](https://github.com/thesofproject/linux/issues/5957#issuecomment-6941335315). Issue open. | TI/HP confirmation of variant selection and preferred maintained HP encoding support; calibration question. |
| linux-firmware | Required unmodified files already present at pinned commit 2f90f4fe5c67f51a8410907aedf911dabb7120ca. | Filename selection and distribution packaging are separate concerns. |
| Generic kernel SPEAKER_ID patch | 9d28c97118d8403cb882e392f948c25a328dc504 accepted into for-7.5, a development branch. | Inspected code does not read HPSpeakerID. No claim it solves this board or is released/distributed. |

## Why these channels

The UCM correction exactly matches Guido's existing contribution; another PR would duplicate it. The original ALSA TAS2783 support is commit 182d0122a7d98cfa5f2d42d3cb8e9e1b8697b69a. Feedback belongs in the existing alsa-ucm-conf PR for the project maintainers, including Jaroslav Kysela.

The driver issue was already moved to the Linux component because it does not concern SOF DSP firmware. An earlier 8EA8 comment existed there. The current Linux MAINTAINERS entry for TI audio codecs names Shenghao Ding, Kevin Lu, Baojun Xu and Sen Wang and linux-sound@vger.kernel.org. We updated that existing technical record and requested guidance instead of broadcasting duplicate mail or proposing an unverified kernel mapping. No SoundWire bus or SOF topology change was established as necessary.

Kernel Bugzilla #222079 is already linked in that issue. Its present content/status could not be reverified because of an access challenge; no new Bugzilla report was created and no current status is inferred.

## Validation and limits

ALSA master cdec3c07cc275e77bde9f6fb1cee49897faa7b03 was examined on an independent branch. Its four corrected init names match the installed working file byte-for-byte and the original raw mixer controls. Both baseline and corrected trees passed the official ucm-validator2 basic configuration check from alsa-tests 53d34b67078540273899e15544e01c6d996f5240; git diff --check passed. A baseline pass demonstrates why this check does not test physical control availability.

Firmware aliases and UCM changes were applied together. We did not isolate either effect. Speaker left/right, volume/mute, one physical suspend/resume, manual reboot and browser playback were confirmed by the owner. Wired and Bluetooth headphones always worked and passed regression checks. Vendor tuning mapping, per-unit calibration and extended thermal behavior remain unverified.

No new patch, Signed-off-by, Tested-by trailer or maintainer approval was fabricated. Guido retains authorship of PR #886. OpenAI Codex assisted with source investigation, commands and writing; José Carmona performed the physical checks. The public comments were explicitly approved by the owner before posting.

## Reproduce the configuration check

Use temporary checkouts, not the installed UCM directory:

```sh
git clone https://github.com/alsa-project/alsa-ucm-conf.git
git clone https://github.com/alsa-project/alsa-tests.git
git -C alsa-ucm-conf checkout cdec3c07cc275e77bde9f6fb1cee49897faa7b03
git -C alsa-tests checkout 53d34b67078540273899e15544e01c6d996f5240
cd alsa-tests/python/ucm-validator2
make configs
```

Follow the pinned validator README and repository validation workflow (`make configs`) with UCM paths pointing at the temporary alsa-ucm-conf checkout. Compare baseline and the four ` Switch` suffix additions in codecs/tas2783/init.conf. A working libasound development-library path is required. Do not run install/rebind/reboot as part of this source check. The submission archive retains the reference delta, sanitized logs and pinned revisions.

## Follow-up

The owner's existing read-only follow-up runs every 24 hours and now includes both upstream threads, reactions, replies, review and state changes. New requests for diagnostics or tests should be evaluated before any physical or installed-system change. Browser GitHub notifications also show replies because the account participated in both threads. No reply is sent automatically.

Communicated means the comments are public. In review requires actual maintainer activity. Accepted requires explicit acceptance, integrated requires a commit/merge in the relevant maintained branch, and distributed requires a released package available to the target distribution. None of the latter stages is implied by our successful local playback.
