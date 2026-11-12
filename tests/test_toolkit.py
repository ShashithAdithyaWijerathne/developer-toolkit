"""Run with python -m unittest discover -s tests -v."""
import contextlib
import hashlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from toolkit import format_json, main, sha256_file

ROOT = Path(__file__).resolve().parents[1]


class JsonTests(unittest.TestCase):
    def test_nested_json_and_unicode_round_trip(self):
        text = '{"name":"පොල්","items":[1,true,null,{"count":2}]}'
        import json
        formatted = format_json(text)
        self.assertEqual(json.loads(formatted), json.loads(text))
        self.assertIn("පොල්", formatted)
        self.assertTrue(formatted.endswith("\n"))

    def test_sort_keys_is_optional(self):
        self.assertLess(format_json('{"z":1,"a":2}').index('"z"'),
                        format_json('{"z":1,"a":2}').index('"a"'))
        ordered = format_json('{"z":1,"a":2}', sort_keys=True)
        self.assertLess(ordered.index('"a"'), ordered.index('"z"'))

    def test_rejects_invalid_or_ambiguous_input(self):
        for text in ("", "{", '{"x":1,}', "NaN", "Infinity", "-Infinity",
                     '{"x":1,"x":2}', '{"nested":{"x":1,"x":2}}', "1e999"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                format_json(text)

    def test_scalar_values_are_valid_json(self):
        for text in ("null", "true", "42", '"hello"', "[]"):
            self.assertEqual(format_json(text), text + "\n")


class ChecksumTests(unittest.TestCase):
    def test_known_digest_and_multiple_chunks(self):
        for data in (b"", b"abc", bytes(range(256)) * 10000):
            with self.subTest(length=len(data)), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "sample.bin"
                path.write_bytes(data)
                self.assertEqual(sha256_file(path), hashlib.sha256(data).hexdigest())

    def test_missing_file_reports_error(self):
        output, errors = io.StringIO(), io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                code = main(["sha256", str(Path(directory) / "missing")])
        self.assertEqual(code, 1)
        self.assertEqual(output.getvalue(), "")
        self.assertIn("error:", errors.getvalue())


class CliTests(unittest.TestCase):
    def test_json_from_stdin_and_error_exit(self):
        for text, expected in (('{"x":1}', 0), ('{"x":}', 1)):
            with self.subTest(text=text):
                result = subprocess.run(
                    [sys.executable, str(ROOT / "toolkit.py"), "json"],
                    input=text, capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, expected)
                if expected:
                    self.assertEqual(result.stdout, "")
                    self.assertIn("error:", result.stderr)
                else:
                    self.assertEqual(result.stdout, '{\n  "x": 1\n}\n')

    def test_utf8_bom_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.json"
            path.write_text('{"ok":true}', encoding="utf-8-sig")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(["json", str(path)]), 0)
            self.assertEqual(output.getvalue(), '{\n  "ok": true\n}\n')

    def test_bad_encoding_has_no_partial_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_bytes(b"\xff")
            output, errors = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                self.assertEqual(main(["json", str(path)]), 1)
            self.assertEqual(output.getvalue(), "")
            self.assertIn("error:", errors.getvalue())

    def test_import_is_quiet(self):
        result = subprocess.run([sys.executable, "-c", "import toolkit"],
                                cwd=ROOT, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
