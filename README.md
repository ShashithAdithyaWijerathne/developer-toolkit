# Developer Toolkit

Small, dependency-free command-line utilities for everyday development. Written in Python 3.10 or newer.

## Utilities

| Command | Purpose |
| --- | --- |
| `json` | Validate JSON and format it with two-space indentation |
| `sha256` | Calculate or verify SHA-256 for a file or binary stdin using bounded memory |

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

### Produce ASCII-escaped JSON

Use `--ascii` when the destination requires ASCII JSON text:

```sh
python toolkit.py json payload.json --ascii
python toolkit.py json - --ascii --sort-keys
```

Non-ASCII keys and values are emitted as JSON Unicode escapes, including surrogate pairs for supplementary characters such as emoji. Parsing the result restores the same data; default output still preserves Unicode characters directly. For example, the JSON string `"café"` becomes `"caf\u00e9"` with `--ascii`.

This option controls JSON escaping, not input decoding or Python's stdout codec. Input must still be UTF-8, with the same optional BOM and strict validation rules. An ASCII-configured stdout can encode the escaped text; choosing a different output codec remains the caller's responsibility. Source files are not modified. `--ascii` can be combined with `--sort-keys` and `--check`; check mode remains silent. Python callers can use `format_json(text, ensure_ascii=True)` for the same escaping behavior.

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

### Hash a binary pipeline

Use an explicit `-` instead of a filename to calculate or verify the bytes arriving on stdin:

```sh
python -c "import sys; sys.stdout.buffer.write(b'abc')" | python toolkit.py sha256 -
python -c "import sys; sys.stdout.buffer.write(b'abc')" | python toolkit.py sha256 - --expect ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
```

Both commands print the SHA-256 digest of `abc`. The utility hashes bytes without text decoding, newline conversion or re-encoding, using 1 MiB reads for stdin as well as files. It does not close stdin. Ensure the producing command and shell preserve the intended bytes; text pipelines and older shells may transform data before it reaches Python. For an existing file, passing its path avoids these upstream transformations.

The file-or-dash argument remains required. Use `./-` to hash a file literally named `-`. Matching, mismatching, malformed-digest and read-error exit codes are the same for files and stdin. Embedded callers must supply a stdin with a binary `buffer`; a text-only replacement is rejected rather than guessed or re-encoded. Python callers may use `sha256_stream(binary_source)` to hash from the source's current position, without closing it.

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

Checksum stream tests also cover empty and arbitrary binary stdin, file/pipe parity, bounded reads, stream ownership, read failures, text-only stdin rejection and literal dash filenames.

JSON escaping tests cover ASCII-only stdout, Unicode keys/values and emoji round trips, file/stdin BOM parity, sorting, unchanged Unicode defaults, check-mode silence and strict error handling.

## Continuous integration

[Python tests](https://github.com/ShashithAdithyaWijerathne/developer-toolkit/actions/workflows/tests.yml) runs the regression suite and CLI help on Linux, Windows and macOS with Python 3.10 and 3.14. The matrix exercises the documented minimum version and a newer stable version; it does not test every intermediate Python release.

Checks run on pull requests to `main`, pushes to `main`, and manual dispatch. Jobs use UTF-8 mode consistently for Unicode input/output tests, a read-only repository token, and commit-pinned checkout/setup actions. No dependency installation or secrets are required. Workflow checks do not enforce merge blocking unless repository protection rules require them.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for reproduction steps, validation expectations and co-author attribution.

See [BACKLOG.md](BACKLOG.md) for the small prioritized development backlog and acceptance criteria.
