# Contributing

Constructive reviews, reproducible diagnostics and narrowly scoped patches are welcome. Discuss technical evidence respectfully and credit upstream work. This is an independent community project; do not claim vendor or maintainer endorsement.

Before reporting another model as compatible, provide its model, DMI board, PCI/subsystem IDs, speaker variant, kernel, UCM version and actual test results. Distinguish headphone regression checks from the internal-speaker repair. Shared codec names alone do not establish compatibility.

For code changes, run `python3 -m unittest discover -s tests -v`. Keep firmware files, caches, backup manifests, personal paths, serial numbers, Bluetooth addresses, full unreviewed logs and per-unit calibration data out of commits. Sanitize diagnostic excerpts before posting.

Describe what changed, why it is needed, how it was tested and what remains unverified. Disclose material AI assistance and distinguish suggestions from executed tests. Do not upload third-party firmware or patches without reviewing licenses and preserving required attribution.

Changes to hardware limits, calibration or supported configurations require technical evidence. Avoid destructive experiments and forced module removal. A software test passing is not a listening result.

Interactions must follow [GitHub's Community Guidelines](https://docs.github.com/en/site-policy/github-terms/github-community-guidelines) and [Acceptable Use Policies](https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-policies). Do not spam unrelated projects or publish another person's private information.
