"""Binary checksum pipelines and stream ownership regression tests."""
import contextlib
import hashlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import toolkit

ROOT = Path(__file__).resolve().parents[1]


class ChecksumStdinTests(unittest.TestCase):
    def run_cli(self, payload, *arguments):
        return subprocess.run(
            [sys.executable, str(ROOT / "toolkit.py"), "sha256", "-", *arguments],
            input=payload, capture_output=True, timeout=10,
            env={**os.environ, "PYTHONIOENCODING": "cp1252:strict"},
        )

    def test_empty_binary_and_multichunk_stdin_match_file(self):
        for payload in (b"", bytes(range(256)), bytes(range(256)) * 10000):
            with self.subTest(size=len(payload)), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "sample.bin"
                path.write_bytes(payload)
                result = self.run_cli(payload)
                expected = hashlib.sha256(payload).hexdigest()
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, (expected + "\n").encode("ascii"))
                self.assertEqual(result.stderr, b"")
                self.assertEqual(toolkit.sha256_file(path), expected)

    def test_expected_digest_match_uppercase_and_mismatch(self):
        payload = b"abc\x00\xff\r\n"
        expected = hashlib.sha256(payload).hexdigest()
        for digest in (expected, expected.upper()):
            with self.subTest(digest=digest):
                result = self.run_cli(payload, "--expect", digest)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, (expected + "\n").encode("ascii"))
                self.assertEqual(result.stderr, b"")
        mismatch = self.run_cli(payload, "--expect", "0" * 64)
        self.assertEqual(mismatch.returncode, 1)
        self.assertEqual(mismatch.stdout, b"")
        self.assertIn(b"SHA-256 mismatch", mismatch.stderr)

    def test_malformed_digest_is_rejected_before_stdin_access(self):
        # Any attempt to read this stdin would fail the test immediately.
        class UnreadableStdin:
            @property
            def buffer(self):
                raise AssertionError("stdin accessed before argument validation")

        errors = io.StringIO()
        with patch("sys.stdin", UnreadableStdin()), contextlib.redirect_stderr(errors):
            with self.assertRaises(SystemExit) as raised:
                toolkit.main(["sha256", "-", "--expect", "invalid"])
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("64 hexadecimal characters", errors.getvalue())

    def test_stream_reads_are_bounded_and_do_not_close_source(self):
        class BoundedStream(io.BytesIO):
            def read(self, size=-1):
                if not 0 < size <= 1024 * 1024:
                    raise AssertionError("unbounded read")
                return super().read(size)

        payload = bytes(range(256)) * 10000
        source = BoundedStream(payload)
        self.assertEqual(toolkit.sha256_stream(source), hashlib.sha256(payload).hexdigest())
        self.assertFalse(source.closed)
        self.assertEqual(source.tell(), len(payload))

    def test_cli_uses_binary_buffer_without_closing_stdin(self):
        class BinaryStdin:
            buffer = io.BytesIO(b"\x00\xff\r\n")

            def read(self, *args):
                raise AssertionError("text input must not be read or re-encoded")

        source = BinaryStdin()
        output = io.StringIO()
        with patch("sys.stdin", source), contextlib.redirect_stdout(output):
            self.assertEqual(toolkit.main(["sha256", "-"]), 0)
        self.assertFalse(source.buffer.closed)
        self.assertEqual(output.getvalue(), hashlib.sha256(b"\x00\xff\r\n").hexdigest() + "\n")

    def test_stream_starts_at_current_position_and_handles_short_reads(self):
        class ShortReadStream(io.BytesIO):
            def read(self, size=-1):
                return super().read(min(size, 3))

        source = ShortReadStream(b"prefix:remaining data")
        source.seek(len(b"prefix:"))
        self.assertEqual(toolkit.sha256_stream(source),
                         hashlib.sha256(b"remaining data").hexdigest())
        self.assertFalse(source.closed)

    def test_checksum_still_requires_explicit_input_argument(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "toolkit.py"), "sha256"],
            input=b"not implicitly hashed", capture_output=True, timeout=10,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b"")
        self.assertIn(b"required", result.stderr)

    def test_read_failure_reports_error_and_does_not_close_stdin(self):
        class FailingStream(io.BytesIO):
            def read(self, size=-1):
                raise OSError("simulated stdin read failure")

        source = FailingStream()
        output, errors = io.StringIO(), io.StringIO()
        with patch("sys.stdin", type("Input", (), {"buffer": source})()):
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                self.assertEqual(toolkit.main(["sha256", "-"]), 1)
        self.assertFalse(source.closed)
        self.assertEqual(output.getvalue(), "")
        self.assertIn("simulated stdin read failure", errors.getvalue())

    def test_text_only_stdin_has_clear_error_without_reencoding(self):
        output, errors = io.StringIO(), io.StringIO()
        with patch("sys.stdin", io.StringIO("abc")):
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                self.assertEqual(toolkit.main(["sha256", "-"]), 1)
        self.assertEqual(output.getvalue(), "")
        self.assertIn("binary input stream", errors.getvalue())

    def test_literal_dash_file_still_works_with_explicit_path(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "-"
            path.write_bytes(b"literal dash file")
            result = subprocess.run(
                [sys.executable, str(ROOT / "toolkit.py"), "sha256", "./-"],
                cwd=directory, capture_output=True, timeout=10,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.decode("ascii").strip(), toolkit.sha256_file(path))
            self.assertEqual(path.read_bytes(), b"literal dash file")


if __name__ == "__main__":
    unittest.main()
