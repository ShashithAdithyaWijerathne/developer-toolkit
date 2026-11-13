"""Small, dependency-free developer utilities."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


def reject_constant(value):
    raise ValueError("Non-standard JSON constant: " + value)


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def format_json(text, sort_keys=False):
    """Validate strict JSON and return its formatted representation."""
    value = json.loads(text, parse_constant=reject_constant,
                       object_pairs_hook=reject_duplicate_keys)
    return json.dumps(value, ensure_ascii=False, indent=2,
                      sort_keys=sort_keys, allow_nan=False) + "\n"


def sha256_file(path):
    """Hash a file without loading its entire contents into memory."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_sha256_digest(value):
    """Validate an expected digest before any file is opened."""
    if re.fullmatch(r"[0-9a-fA-F]{64}", value) is None:
        raise argparse.ArgumentTypeError(
            "expected SHA-256 must contain exactly 64 hexadecimal characters"
        )
    return value.lower()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    json_command = commands.add_parser("json", help="Validate and format JSON")
    json_command.add_argument("file", nargs="?", default="-",
                              help="UTF-8 JSON file, or - for stdin")
    json_command.add_argument("--sort-keys", action="store_true")
    hash_command = commands.add_parser("sha256", help="Calculate a file checksum")
    hash_command.add_argument("file")
    hash_command.add_argument("--expect", type=parse_sha256_digest, metavar="DIGEST",
                              help="Fail unless the file matches this SHA-256 digest")
    args = parser.parse_args(argv)

    try:
        if args.command == "json":
            text = (sys.stdin.read() if args.file == "-"
                    else Path(args.file).read_text(encoding="utf-8-sig"))
            output = format_json(text, sort_keys=args.sort_keys)
            sys.stdout.write(output)
        else:
            digest = sha256_file(args.file)
            if args.expect is not None and digest != args.expect:
                raise ValueError("SHA-256 mismatch: expected " + args.expect
                                 + ", got " + digest)
            print(digest)
    except (OSError, UnicodeError, ValueError, RecursionError) as error:
        print("error: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
