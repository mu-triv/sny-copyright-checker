#!/usr/bin/env python
# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file


"""Tests for Git-aware year management"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from scripts.copyright_checker import CopyrightChecker


class TestGitAwareYearManagement(unittest.TestCase):
    """Test Git-aware year management features"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary template file
        self.temp_dir = tempfile.mkdtemp()
        self.template_path = os.path.join(self.temp_dir, "copyright.txt")

        with open(self.template_path, "w", encoding="utf-8") as f:
            f.write("""[VARIABLES]
COMPANY = Test Company

[.py]
# Copyright {regex:\\d{4}(-\\d{4})?} {COMPANY}
""")

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_extract_years_single_year(self):
        """Test extracting single year from copyright notice"""
        checker = CopyrightChecker(self.template_path, git_aware=True)
        template = checker.templates[".py"]

        content = "# Copyright 2024 Test Company\n"
        years = template.extract_years(content)

        self.assertIsNotNone(years)
        self.assertEqual(years, (2024, None))

    def test_extract_years_year_range(self):
        """Test extracting year range from copyright notice"""
        checker = CopyrightChecker(self.template_path, git_aware=True)
        template = checker.templates[".py"]

        content = "# Copyright 2020-2024 Test Company\n"
        years = template.extract_years(content)

        self.assertIsNotNone(years)
        self.assertEqual(years, (2020, 2024))

    def test_extract_years_no_copyright(self):
        """Test extracting years when no copyright notice exists"""
        checker = CopyrightChecker(self.template_path, git_aware=True)
        template = checker.templates[".py"]

        content = "# Just a comment\nprint('hello')\n"
        years = template.extract_years(content)

        self.assertIsNone(years)

    def test_get_notice_with_year_range(self):
        """Test generating notice with year range string"""
        checker = CopyrightChecker(self.template_path, git_aware=True)
        template = checker.templates[".py"]

        notice = template.get_notice_with_year("2020-2024")
        self.assertIn("2020-2024", notice)
        self.assertIn("Test Company", notice)

    def test_get_notice_with_single_year_string(self):
        """Test generating notice with single year as string"""
        checker = CopyrightChecker(self.template_path, git_aware=True)
        template = checker.templates[".py"]

        notice = template.get_notice_with_year("2024")
        self.assertIn("2024", notice)
        self.assertNotIn("-", notice)

    def test_get_notice_with_year_int(self):
        """Test generating notice with year as integer (backward compatibility)"""
        checker = CopyrightChecker(self.template_path, git_aware=True)
        template = checker.templates[".py"]

        notice = template.get_notice_with_year(2024)
        self.assertIn("2024", notice)

    @patch("scripts.copyright_checker.subprocess.run")
    @patch("scripts.copyright_checker.datetime")
    def test_determine_copyright_year_new_file_with_git(self, mock_datetime, mock_run):
        """Test year determination for new file in Git"""
        mock_datetime.now.return_value.year = 2026

        # Mock Git log to return 2020 as creation year
        mock_run.side_effect = [
            MagicMock(
                stdout="2020-03-15T10:30:00+01:00\n", stderr="", returncode=0
            ),  # git log
            MagicMock(
                stdout=" M test.py\n", stderr="", returncode=0
            ),  # git status (modified)
        ]

        checker = CopyrightChecker(self.template_path, git_aware=True)
        template = checker.templates[".py"]

        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, "w") as f:
            f.write("print('hello')\n")

        year_str = checker._determine_copyright_year(
            test_file, template, "print('hello')\n"
        )

        # File created in 2020, modified now in 2026 -> should be "2020-2026"
        self.assertEqual(year_str, "2020-2026")

    @patch("scripts.copyright_checker.subprocess.run")
    @patch("scripts.copyright_checker.datetime")
    def test_determine_copyright_year_new_file_unmodified(
        self, mock_datetime, mock_run
    ):
        """Test year determination for new file in Git that's unchanged"""
        mock_datetime.now.return_value.year = 2026

        # Mock Git log to return 2020 as creation year
        mock_run.side_effect = [
            MagicMock(
                stdout="2020-03-15T10:30:00+01:00\n", stderr="", returncode=0
            ),  # git log
            MagicMock(stdout="", stderr="", returncode=0),  # git status (unchanged)
        ]

        checker = CopyrightChecker(
            self.template_path, git_aware=True, per_file_years=True
        )
        template = checker.templates[".py"]

        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, "w") as f:
            f.write("print('hello')\n")

        year_str = checker._determine_copyright_year(
            test_file, template, "print('hello')\n"
        )

        # File created in 2020, not modified -> should be "2020"
        self.assertEqual(year_str, "2020")

    @patch("scripts.copyright_checker.subprocess.run")
    @patch("scripts.copyright_checker.datetime")
    def test_determine_copyright_year_preserve_existing_on_unchanged(
        self, mock_datetime, mock_run
    ):
        """Test preserving existing year when file is unchanged"""
        mock_datetime.now.return_value.year = 2026

        # Mock Git status to show file is unchanged
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)

        checker = CopyrightChecker(
            self.template_path, git_aware=True, per_file_years=True
        )
        template = checker.templates[".py"]

        test_file = os.path.join(self.temp_dir, "test.py")
        content = "# Copyright 2020-2024 Test Company\nprint('hello')\n"

        year_str = checker._determine_copyright_year(test_file, template, content)

        # File has 2020-2024, unchanged -> should preserve "2020-2024"
        self.assertEqual(year_str, "2020-2024")

    @patch("scripts.copyright_checker.subprocess.run")
    @patch("scripts.copyright_checker.datetime")
    def test_determine_copyright_year_extend_on_modified(self, mock_datetime, mock_run):
        """Test extending year range when file is modified"""
        mock_datetime.now.return_value.year = 2026

        # Mock Git status to show file is modified
        mock_run.return_value = MagicMock(
            stdout=" M test.py\n", stderr="", returncode=0
        )

        checker = CopyrightChecker(self.template_path, git_aware=True)
        template = checker.templates[".py"]

        test_file = os.path.join(self.temp_dir, "test.py")
        content = "# Copyright 2020-2024 Test Company\nprint('hello')\n"

        year_str = checker._determine_copyright_year(test_file, template, content)

        # File has 2020-2024, modified in 2026 -> should extend to "2020-2026"
        self.assertEqual(year_str, "2020-2026")

    @patch("scripts.copyright_checker.subprocess.run")
    @patch("scripts.copyright_checker.datetime")
    def test_determine_copyright_year_single_year_extended(
        self, mock_datetime, mock_run
    ):
        """Test extending single year to range when file is modified"""
        mock_datetime.now.return_value.year = 2026

        # Mock Git status to show file is modified
        mock_run.return_value = MagicMock(
            stdout=" M test.py\n", stderr="", returncode=0
        )

        checker = CopyrightChecker(self.template_path, git_aware=True)
        template = checker.templates[".py"]

        test_file = os.path.join(self.temp_dir, "test.py")
        content = "# Copyright 2020 Test Company\nprint('hello')\n"

        year_str = checker._determine_copyright_year(test_file, template, content)

        # File has 2020, modified in 2026 -> should become "2020-2026"
        self.assertEqual(year_str, "2020-2026")

    @patch("scripts.copyright_checker.datetime")
    def test_non_git_aware_uses_current_year(self, mock_datetime):
        """Test that non-Git-aware mode always uses current year"""
        mock_datetime.now.return_value.year = 2026

        checker = CopyrightChecker(self.template_path, git_aware=False)
        template = checker.templates[".py"]

        test_file = os.path.join(self.temp_dir, "test.py")
        content = "print('hello')\n"

        year_str = checker._determine_copyright_year(test_file, template, content)

        # Non-Git-aware mode should always use current year
        self.assertEqual(year_str, "2026")

    @patch("scripts.copyright_checker.subprocess.run")
    @patch("scripts.copyright_checker.datetime")
    def test_determine_copyright_year_no_git_fallback(self, mock_datetime, mock_run):
        """Test fallback to current year when Git is not available"""
        mock_datetime.now.return_value.year = 2026

        # Mock Git command to fail (Git not available)
        mock_run.side_effect = FileNotFoundError("git not found")

        checker = CopyrightChecker(self.template_path, git_aware=True)
        template = checker.templates[".py"]

        test_file = os.path.join(self.temp_dir, "test.py")
        content = "print('hello')\n"

        year_str = checker._determine_copyright_year(test_file, template, content)

        # Git not available, should fallback to current year
        self.assertEqual(year_str, "2026")


class TestYearExtraction(unittest.TestCase):
    """Test year extraction from various copyright formats"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.template_path = os.path.join(self.temp_dir, "copyright.txt")

        with open(self.template_path, "w", encoding="utf-8") as f:
            f.write("""[VARIABLES]
COMPANY = Test Company

[.py]
# Copyright {regex:\\d{4}(-\\d{4})?} {COMPANY}

[.js]
// Copyright {regex:\\d{4}(-\\d{4})?} {COMPANY}
""")

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_extract_years_python_format(self):
        """Test extracting years from Python-style comments"""
        checker = CopyrightChecker(self.template_path, git_aware=True)
        template = checker.templates[".py"]

        test_cases = [
            ("# Copyright 2024 Test Company\n", (2024, None)),
            ("# Copyright 2020-2024 Test Company\n", (2020, 2024)),
            ("# Copyright 1999-2000 Test Company\n", (1999, 2000)),
        ]

        for content, expected in test_cases:
            with self.subTest(content=content):
                years = template.extract_years(content)
                self.assertEqual(years, expected)

    def test_extract_years_javascript_format(self):
        """Test extracting years from JavaScript-style comments"""
        checker = CopyrightChecker(self.template_path, git_aware=True)
        template = checker.templates[".js"]

        test_cases = [
            ("// Copyright 2024 Test Company\n", (2024, None)),
            ("// Copyright 2020-2024 Test Company\n", (2020, 2024)),
        ]

        for content, expected in test_cases:
            with self.subTest(content=content):
                years = template.extract_years(content)
                self.assertEqual(years, expected)

    def test_extract_years_with_surrounding_content(self):
        """Test extracting years when copyright is not at the start"""
        checker = CopyrightChecker(self.template_path, git_aware=True)
        template = checker.templates[".py"]

        content = """#!/usr/bin/env python
# Some header
# Copyright 2020-2024 Test Company
# More content
print('hello')
"""
        years = template.extract_years(content)
        self.assertEqual(years, (2020, 2024))

    @patch("scripts.copyright_checker.subprocess.run")
    @patch("scripts.copyright_checker.datetime")
    def test_git_not_installed(self, mock_datetime, mock_run):
        """Test fallback when Git is not installed"""
        mock_datetime.now.return_value.year = 2026

        # Mock Git command to fail (not installed)
        mock_run.side_effect = FileNotFoundError("git not found")

        checker = CopyrightChecker(self.template_path, git_aware=True)
        template = checker.templates[".py"]

        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, "w") as f:
            f.write("print('hello')\n")

        year_str = checker._determine_copyright_year(
            test_file, template, "print('hello')\n"
        )

        # Should fall back to current year
        self.assertEqual(year_str, "2026")

    @patch("scripts.copyright_checker.subprocess.run")
    @patch("scripts.copyright_checker.datetime")
    def test_file_outside_git_repository(self, mock_datetime, mock_run):
        """Test behavior for files outside Git repository"""
        mock_datetime.now.return_value.year = 2026

        # Mock Git log to fail (not a git repo)
        mock_run.return_value = MagicMock(
            stdout="", stderr="fatal: not a git repository", returncode=128
        )

        checker = CopyrightChecker(self.template_path, git_aware=True)
        template = checker.templates[".py"]

        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, "w") as f:
            f.write("print('hello')\n")

        year_str = checker._determine_copyright_year(
            test_file, template, "print('hello')\n"
        )

        # Should fall back to current year
        self.assertEqual(year_str, "2026")

    @patch("scripts.copyright_checker.subprocess.run")
    @patch("scripts.copyright_checker.datetime")
    def test_year_range_normalization(self, mock_datetime, mock_run):
        """Test that same year range is normalized to single year"""
        mock_datetime.now.return_value.year = 2024

        # Mock Git to return 2024 as creation year
        mock_run.side_effect = [
            MagicMock(stdout="2024-01-15T10:30:00+01:00\n", stderr="", returncode=0),
            MagicMock(stdout="", stderr="", returncode=0),  # unchanged
        ]

        checker = CopyrightChecker(self.template_path, git_aware=True)
        template = checker.templates[".py"]

        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, "w") as f:
            f.write("print('hello')\n")

        year_str = checker._determine_copyright_year(
            test_file, template, "print('hello')\n"
        )

        # File created in 2024, current year is 2024 -> should be "2024", not "2024-2024"
        self.assertEqual(year_str, "2024")

    def test_invalid_year_in_existing_copyright(self):
        """Test handling of invalid year in existing copyright"""
        checker = CopyrightChecker(self.template_path, git_aware=True)
        template = checker.templates[".py"]

        # Copyright with invalid year
        content = "# Copyright 1899 Test Company\n"
        years = template.extract_years(content)

        # Should still extract the year even if it seems invalid
        self.assertEqual(years, (1899, None))

    @patch("scripts.copyright_checker.subprocess.run")
    @patch("scripts.copyright_checker.datetime")
    def test_git_aware_with_renamed_file(self, mock_datetime, mock_run):
        """Test Git-aware year management for renamed files (git mv)"""
        mock_datetime.now.return_value.year = 2026

        # Mock Git log with --follow to track file history across renames
        mock_run.side_effect = [
            MagicMock(
                stdout="2020-03-15T10:30:00+01:00\n", stderr="", returncode=0
            ),  # original creation
            MagicMock(stdout=" M test.py\n", stderr="", returncode=0),  # modified
        ]

        checker = CopyrightChecker(self.template_path, git_aware=True)
        template = checker.templates[".py"]

        test_file = os.path.join(self.temp_dir, "test.py")
        with open(test_file, "w") as f:
            f.write("print('hello')\n")

        year_str = checker._determine_copyright_year(
            test_file, template, "print('hello')\n"
        )

        # Should preserve earliest year from before rename
        self.assertEqual(year_str, "2020-2026")

    @patch("scripts.copyright_checker.subprocess.run")
    @patch("scripts.copyright_checker.datetime")
    def test_existing_copyright_with_future_year(self, mock_datetime, mock_run):
        """Test handling copyright with future year"""
        mock_datetime.now.return_value.year = 2026

        checker = CopyrightChecker(self.template_path, git_aware=True)
        template = checker.templates[".py"]

        # Existing copyright with future year (2030)
        content = "# Copyright 2030 Test Company\nprint('hello')\n"
        years = template.extract_years(content)

        # Should preserve the future year (maybe intentional)
        self.assertEqual(years, (2030, None))

    @patch("scripts.copyright_checker.subprocess.run")
    @patch("scripts.copyright_checker.datetime")
    def test_git_aware_preserves_earliest_year_from_range(
        self, mock_datetime, mock_run
    ):
        """Test that earliest year from existing range is preserved"""
        mock_datetime.now.return_value.year = 2026

        mock_run.side_effect = [
            MagicMock(
                stdout="2022-03-15T10:30:00+01:00\n", stderr="", returncode=0
            ),  # git creation
            MagicMock(stdout=" M test.py\n", stderr="", returncode=0),  # modified
        ]

        checker = CopyrightChecker(self.template_path, git_aware=True)
        template = checker.templates[".py"]

        test_file = os.path.join(self.temp_dir, "test.py")

        # Existing copyright with range starting earlier than Git creation
        existing_content = "# Copyright 2019-2023 Test Company\nprint('old')\n"

        year_str = checker._determine_copyright_year(
            test_file, template, existing_content
        )

        # Should preserve 2019 (earliest from existing) and extend to 2026
        self.assertEqual(year_str, "2019-2026")


if __name__ == "__main__":
    unittest.main()
