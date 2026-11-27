# Development backlog

Keep this list ordered by concrete user value. Recheck current code and existing issues before starting a task; entries are not a daily activity quota.

## Next: opt-in ASCII JSON output

The formatter preserves Unicode, but writing a valid Unicode document to an ASCII-only stdout currently exits with an encoding error. UTF-8 mode is already documented as the default workaround. An explicit `json --ascii` option would let users produce portable JSON escapes when the downstream destination requires ASCII, while preserving the decoded data.

Acceptance criteria: opt-in only; preserve default Unicode output; round-trip non-ASCII keys/values and supplementary characters; retain duplicate-key, constant, overflow and BOM validation; define interaction with `--check`; test an ASCII-only stdout and file/stdin parity. This is a usability feature, not a claim that the documented current encoding behavior is incorrect.

## Delivered: streaming checksum input

[#13](https://github.com/ShashithAdithyaWijerathne/developer-toolkit/issues/13): explicit `sha256 -` with bounded binary reads, existing verification semantics, no stdin ownership transfer, regression tests and pipeline examples.
