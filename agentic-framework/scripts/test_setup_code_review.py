"""Regression tests for code review setup."""

import contextlib
import io
import unittest
from pathlib import Path
import sys
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import setup_code_review


class SetupCodeReviewTest(unittest.TestCase):
    """Verify dry-run readiness semantics."""

    def test_dry_run_missing_ocr_does_not_print_ready_hint(self) -> None:
        output = io.StringIO()
        with mock.patch.object(setup_code_review, "ocr_installed", return_value=False), \
                mock.patch.object(setup_code_review.shutil, "which", return_value="npm"), \
                contextlib.redirect_stdout(output):
            setup_code_review.setup(Path("."), dry_run=True)
        self.assertIn("[dry-run] npm install", output.getvalue())
        self.assertNotIn("ocr config provider", output.getvalue())


if __name__ == "__main__":
    unittest.main()
