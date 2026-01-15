#!/usr/bin/env python
# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

"""Tests for project-wide vs per-file year management."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from scripts.copyright_checker import CopyrightChecker


class TestProjectYears(unittest.TestCase):
    """Test project-wide vs per-file year modes."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.template_path = os.path.join(self.test_dir, "copyright.txt")

        # Create a simple template
        with open(self.template_path, "w") as f:
            f.write("""[VARIABLES]
YEAR_PATTERN = {regex:\\d{4}(-\\d{4})?}

[.py]
# Copyright {YEAR_PATTERN} Sony Corporation
""")

    def test_project_wide_mode_default(self):
        """Test that project-wide mode is the default."""
        checker = CopyrightChecker(
            self.template_path,
            git_aware=True
        )
        self.assertFalse(checker.per_file_years)

    def test_per_file_mode_enabled(self):
        """Test that per-file mode can be enabled."""
        checker = CopyrightChecker(
            self.template_path,
            git_aware=True,
            per_file_years=True
        )
        self.assertTrue(checker.per_file_years)

    @patch('subprocess.run')
    def test_project_year_retrieval(self, mock_run):
        """Test that project creation year is correctly retrieved."""
        # Mock git log to return project creation date
        mock_run.return_value = Mock(
            stdout="2018-03-15T10:30:00+01:00\n",
            returncode=0
        )

        checker = CopyrightChecker(
            self.template_path,
            git_aware=True,
            per_file_years=False
        )

        test_file = os.path.join(self.test_dir, "test.py")
        year = checker._get_repository_creation_year(test_file)

        self.assertEqual(year, 2018)
        mock_run.assert_called_once()
        # Check that it used --max-count=1 for project query
        call_args = mock_run.call_args[0][0]
        self.assertIn("--max-count=1", call_args)

    @patch('subprocess.run')
    def test_file_year_retrieval(self, mock_run):
        """Test that file creation year is correctly retrieved."""
        # Mock git log to return file creation date
        mock_run.return_value = Mock(
            stdout="2020-06-10T14:20:00+01:00\n",
            returncode=0
        )

        checker = CopyrightChecker(
            self.template_path,
            git_aware=True,
            per_file_years=True
        )

        test_file = os.path.join(self.test_dir, "test.py")
        year = checker._get_file_creation_year(test_file)

        self.assertEqual(year, 2020)
        mock_run.assert_called_once()
        # Check that it used --follow for file tracking
        call_args = mock_run.call_args[0][0]
        self.assertIn("--follow", call_args)

    @patch('subprocess.run')
    def test_project_year_caching(self, mock_run):
        """Test that project year is cached after first retrieval."""
        mock_run.return_value = Mock(
            stdout="2018-03-15T10:30:00+01:00\n",
            returncode=0
        )

        checker = CopyrightChecker(
            self.template_path,
            git_aware=True,
            per_file_years=False
        )

        test_file = os.path.join(self.test_dir, "test.py")

        # First call
        year1 = checker._get_repository_creation_year(test_file)
        # Second call (should use cache)
        year2 = checker._get_repository_creation_year(test_file)

        self.assertEqual(year1, 2018)
        self.assertEqual(year2, 2018)
        # Should only call git once due to caching
        self.assertEqual(mock_run.call_count, 1)

    @patch('subprocess.run')
    @patch('scripts.copyright_checker.datetime')
    def test_project_wide_years_new_file(self, mock_datetime, mock_run):
        """Test that new files get project inception year in project-wide mode."""
        # Mock current year
        mock_datetime.now.return_value = Mock(year=2026)

        # Mock project creation year
        mock_run.return_value = Mock(
            stdout="2018-03-15T10:30:00+01:00\n",
            returncode=0
        )

        checker = CopyrightChecker(
            self.template_path,
            git_aware=True,
            per_file_years=False
        )

        test_file = os.path.join(self.test_dir, "test.py")
        with open(test_file, "w") as f:
            f.write("# Test file\n")

        template = checker.templates[".py"]
        year_str = checker._determine_copyright_year(test_file, template, "")

        # Should use project year (2018) to current year (2026)
        self.assertEqual(year_str, "2018-2026")

    @patch('subprocess.run')
    @patch('scripts.copyright_checker.datetime')
    def test_per_file_years_new_file(self, mock_datetime, mock_run):
        """Test that new files get file creation year in per-file mode."""
        # Mock current year
        mock_datetime.now.return_value = Mock(year=2026)

        # Mock file creation year (different from project year)
        def mock_git_call(*args, **kwargs):
            cmd = args[0]
            if "--follow" in cmd:
                # File creation year
                return Mock(stdout="2023-06-10T14:20:00+01:00\n", returncode=0)
            else:
                # Project creation year
                return Mock(stdout="2018-03-15T10:30:00+01:00\n", returncode=0)

        mock_run.side_effect = mock_git_call

        checker = CopyrightChecker(
            self.template_path,
            git_aware=True,
            per_file_years=True
        )

        test_file = os.path.join(self.test_dir, "test.py")
        with open(test_file, "w") as f:
            f.write("# Test file\n")

        template = checker.templates[".py"]
        year_str = checker._determine_copyright_year(test_file, template, "")

        # Should use file year (2023) to current year (2026)
        self.assertEqual(year_str, "2023-2026")


if __name__ == "__main__":
    unittest.main()
