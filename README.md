# Developer Toolkit

Small, dependency-free command-line utilities for everyday development. Written in Python 3.10 or newer.

## Utilities

| Command | Purpose |
| --- | --- |
| `json` | Validate JSON and format it with two-space indentation |
| `sha256` | Calculate a file's SHA-256 checksum using bounded memory |

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

JSON files are decoded as UTF-8, with an optional byte-order mark. Duplicate object keys, NaN, Infinity, malformed JSON and numbers that overflow the supported float representation are rejected. Unicode text is preserved. For exact decimal arithmetic, use an application-specific decimal parser; this formatter uses Python's standard JSON number handling.

### Calculate a checksum

```sh
python toolkit.py sha256 archive.zip
```

The command prints only the hexadecimal digest. Files are read in 1 MiB chunks. A checksum can detect changed content when compared with a trusted expected digest; it does not establish who created a file.

## Exit codes

- `0`: successful operation.
- `1`: invalid input or a file/read/write error handled by the utility.
- `2`: invalid command-line arguments.

## Tests

Run from the repository root:

```sh
python -m unittest discover -s tests -v
```

Coverage includes malformed JSON, duplicate keys, Unicode, optional sorting, BOM input, invalid encoding, known and multi-chunk checksums, stdin, error exits and quiet imports.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for reproduction steps, validation expectations and co-author attribution.
