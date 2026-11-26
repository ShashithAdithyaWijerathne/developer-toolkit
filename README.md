# Developer Toolkit

Small, dependency-free command-line utilities for everyday development. Written in Python 3.10 or newer.

## Utilities

| Command | Purpose |
| --- | --- |
| `json` | Validate JSON and format it with two-space indentation |
| `sha256` | Calculate or verify a file's SHA-256 checksum using bounded memory |

## Getting started

Clone this repository and open its directory:

```sh
git clone https://github.com/ShashithAdithyaWijerathne/developer-toolkit.git
cd developer-toolkit
python toolkit.py --help
```

On Windows, use `py -3` instead of `python` when needed. No packages or API keys are required.

### Format JSON

```sh
python toolkit.py json payload.json
python toolkit.py json payload.json --sort-keys
```

Omit the file argument or use `-` to read from standard input. Output goes to stdout; the source file is never modified. Redirect to a **different** filename to save it:

```sh
python toolkit.py json payload.json > formatted.json
```

JSON files are decoded as UTF-8, with an optional byte-order mark. Byte input from standard input is also decoded strictly as UTF-8, independently of the system's standard-stream encoding, and accepts one leading byte-order mark. Piping the same UTF-8 file therefore produces the same result as passing its path. Invalid UTF-8 is rejected before any formatted output is written. BOM characters inside JSON string values are preserved. Duplicate object keys, NaN, Infinity, malformed JSON and numbers that overflow the supported float representation are rejected. Unicode text is preserved. Output uses Python's configured stdout encoding; use UTF-8 mode (`python -X utf8 toolkit.py json payload.json`) when the destination must contain UTF-8 bytes. For exact decimal arithmetic, use an application-specific decimal parser; this formatter uses Python's standard JSON number handling.

### Validate JSON without output

Use `--check` in scripts or CI when you only need a validation result:

```sh
python toolkit.py json payload.json --check
python toolkit.py json - --check
```

Valid input exits with `0` and writes nothing to stdout or stderr. Invalid JSON, invalid UTF-8 and unreadable files keep exit code `1` with an error on stderr and no stdout. The input is never modified. File/stdin BOM handling and all strict validation rules above also apply in check mode, including rejection of duplicate keys, non-standard constants and float overflow. Unicode validation works even when stdout cannot encode the input text because nothing is written to it.

`--sort-keys` may be combined with `--check`, but produces no output. Check mode still parses and formats the document internally using the existing validation path; it is not a streaming or constant-memory JSON validator.

### Calculate a checksum

```sh
python toolkit.py sha256 archive.zip
```

The command prints only the hexadecimal digest. Files are read in 1 MiB chunks. A checksum can detect changed content when compared with a trusted expected digest; it does not establish who created a file.

### Verify a checksum

Use `--expect DIGEST` with a SHA-256 digest obtained from a trusted source:

```sh
python toolkit.py sha256 archive.zip --expect YOUR_64_CHARACTER_HEX_DIGEST
```

Replace the placeholder with the actual digest. A match prints the computed lowercase digest and exits with `0`. A mismatch prints an error to stderr, leaves stdout empty, and exits with `1`, so a script can stop when verification fails.

Expected digests must contain exactly 64 hexadecimal characters; uppercase is accepted. Malformed digests exit with `2` before reading the file. Neither calculation nor verification modifies the input file.

## Exit codes

- `0`: successful operation.
- `1`: a checksum mismatch, invalid input or a file/read/write error handled by the utility.
- `2`: invalid command-line arguments.

## Tests

Run from the repository root:

```sh
python -m unittest discover -s tests -v
```

Coverage includes malformed JSON, duplicate keys, Unicode, optional sorting, BOM input, legacy standard-stream encodings, invalid encoding, known and multi-chunk checksums, stdin, error exits, quiet imports, checksum matches/mismatches, uppercase digests and malformed expected digests, and silent JSON check-mode success/error behavior.

## Continuous integration

[Python tests](https://github.com/ShashithAdithyaWijerathne/developer-toolkit/actions/workflows/tests.yml) runs the regression suite and CLI help on Linux, Windows and macOS with Python 3.10 and 3.14. The matrix exercises the documented minimum version and a newer stable version; it does not test every intermediate Python release.

Checks run on pull requests to `main`, pushes to `main`, and manual dispatch. Jobs use UTF-8 mode consistently for Unicode input/output tests, a read-only repository token, and commit-pinned checkout/setup actions. No dependency installation or secrets are required. Workflow checks do not enforce merge blocking unless repository protection rules require them.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for reproduction steps, validation expectations and co-author attribution.
