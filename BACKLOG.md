# Development backlog

Keep this list ordered by concrete user value. Recheck current code and existing issues before starting a task; entries are not a daily activity quota.

## Next: readable duplicate-key diagnostics

Verified with input `{"line\nbreak":1,"line\nbreak":2}`: the duplicate key is decoded before being inserted directly into the diagnostic, so its newline splits the error across lines. Quoting and escaping the key would make unusual keys unambiguous in terminals and logs. This is a diagnostic readability task; it does not change duplicate-key detection.

Acceptance criteria: keep exit code 1 and no stdout; render keys unambiguously on one diagnostic line using escaped control characters; cover newline, tab, quote, backslash and non-ASCII keys under restricted stderr encodings; preserve the original decoded key for duplicate comparison and test both formatting/check modes. Check existing issues before implementation.

## Delivered: opt-in ASCII JSON output

[#15](https://github.com/ShashithAdithyaWijerathne/developer-toolkit/issues/15): `json --ascii` emits Unicode escapes for restricted destinations while preserving default Unicode output, decoded data, strict validation, sorting and silent check mode. Includes ASCII-stdout and file/stdin regression tests.

## Delivered: streaming checksum input

[#13](https://github.com/ShashithAdithyaWijerathne/developer-toolkit/issues/13): explicit `sha256 -` with bounded binary reads, existing verification semantics, no stdin ownership transfer, regression tests and pipeline examples.
