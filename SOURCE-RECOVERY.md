# Exact source recovery — completed 2026-09-13

The original `graph-bridge-real-delivery.zip` is recovered into [atlas/](atlas/README.md). All 25 files preserve original bytes; all 24 entries in its historical manifest match. The [recovery manifest](verification/source-recovery.json) records original members and hashes.

## Recovered and checked

- [x] Complete 119-row table with exact 91 existence / 28 nonexistence partition.
- [x] Complete 141-edge ledger and eight transport definitions.
- [x] 211-endpoint index derived from actual edge `from` / `to` fields.
- [x] Recorded case agreements, disagreements, evidence and scope.
- [x] Original source, audit, logs and manifest.
- [x] Bundled transport checker, separate finite checker and synthetic connectivity self-test: three passing scripts.

## Remaining authority work

- [ ] Independently establish the frozen Brouwer-table version/date and audit external catalogue dependencies.
- [ ] Resolve connectivity with the actual live database; the replay uses a synthetic fixture.
- [ ] Review universal transport statements beyond the finite cases, including six one-sided positive-case checks.

Zero recorded disagreements describes finite checks. The historical typing audit is preserved; no missing rejected-edge ledger is invented from its prose.

The historical delivery summary claims 23 manifested files, while the manifest contains 24 entries and the archive contains 25 files including the manifest. Original bytes are unchanged.

Run `python verification/verify_release.py --replay`. The dated [replay receipt](verification/replay-2026-09-13.json) records arguments, exits and outputs.
