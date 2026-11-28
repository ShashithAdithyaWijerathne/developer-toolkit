"""Opt-in JSON escaping for destinations with restricted character encodings."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from toolkit import format_json

ROOT = Path(__file__).resolve().parents[1]
DATA = {"සිංහල": "පොල්", "emoji": "🚀", "nested": ["café", "\\u1234", "\ufeffkept"]}
PAYLOAD = json.dumps(DATA, ensure_ascii=False).encode("utf-8")


class JsonAsciiTests(unittest.TestCase):
    def run_json(self, payload, *arguments, encoding="ascii:strict"):
        return subprocess.run(
            [sys.executable, str(ROOT / "toolkit.py"), "json", *arguments],
            input=payload, capture_output=True, timeout=10,
            env={**os.environ, "PYTHONIOENCODING": encoding},
        )

    def test_ascii_stdin_round_trips_unicode_and_supplementary_characters(self):
        for args in (("--ascii",), ("-", "--ascii")):
            with self.subTest(args=args):
                result = self.run_json(PAYLOAD, *args)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, b"")
                self.assertTrue(result.stdout.isascii())
                self.assertEqual(json.loads(result.stdout), DATA)
                self.assertIn(b"\\ud83d\\ude80", result.stdout)
                self.assertTrue(result.stdout.endswith(b"\n"))

    def test_bom_file_and_stdin_sort_identically_without_modifying_file(self):
        payload = b"\xef\xbb\xbf" + PAYLOAD
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unicode input.json"
            path.write_bytes(payload)
            file_result = self.run_json(None, str(path), "--ascii", "--sort-keys")
            pipe_result = self.run_json(payload, "-", "--ascii", "--sort-keys")
            self.assertEqual(file_result.returncode, 0, file_result.stderr)
            self.assertEqual(pipe_result.returncode, 0, pipe_result.stderr)
            self.assertEqual(file_result.stdout, pipe_result.stdout)
            self.assertEqual(file_result.stderr + pipe_result.stderr, b"")
            self.assertEqual(json.loads(file_result.stdout), DATA)
            self.assertEqual(list(json.loads(file_result.stdout)), sorted(DATA))
            self.assertEqual(path.read_bytes(), payload)

    def test_default_unicode_output_is_unchanged(self):
        result = self.run_json(PAYLOAD, encoding="utf-8:strict")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("පොල්".encode("utf-8"), result.stdout)
        self.assertIn("🚀".encode("utf-8"), result.stdout)
        self.assertEqual(json.loads(result.stdout), DATA)

    def test_formatter_api_keeps_default_and_exposes_keyword_only_option(self):
        text = PAYLOAD.decode("utf-8")
        self.assertIn("පොල්", format_json(text))
        escaped = format_json(text, True, ensure_ascii=True)
        self.assertTrue(escaped.isascii())
        self.assertEqual(json.loads(escaped), DATA)
        self.assertEqual(list(json.loads(escaped)), sorted(DATA))

    def test_check_mode_stays_silent_with_ascii_and_sorting(self):
        for args in (("--ascii", "--check"), ("-", "--ascii", "--sort-keys", "--check")):
            with self.subTest(args=args):
                result = self.run_json(PAYLOAD, *args)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, b"")
                self.assertEqual(result.stderr, b"")

    def test_ascii_does_not_relax_strict_validation(self):
        invalid = (b"{", b'{"a":1,"\\u0061":2}', b"NaN", b"Infinity",
                   b'{"nested":[1e999]}', b'{"x":"\xff"}',
                   b'\xef\xbb\xbf\xef\xbb\xbf{}')
        for payload in invalid:
            for extra in ((), ("--check",)):
                with self.subTest(payload=payload, extra=extra):
                    result = self.run_json(payload, "--ascii", *extra)
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(result.stdout, b"")
                    self.assertIn(b"error:", result.stderr)
                    self.assertNotIn(b"Traceback", result.stderr)

    def test_missing_file_keeps_read_error(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_json(None, str(Path(directory) / "missing.json"), "--ascii")
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, b"")
            self.assertIn(b"error:", result.stderr)
            self.assertNotIn(b"Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
