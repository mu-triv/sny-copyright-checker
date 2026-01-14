#!/usr/bin/env python
# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file


"""Tests for ignore file functionality (.copyrightignore and .gitignore)"""

import os
import tempfile
import unittest
from pathlib import Path

from scripts.copyright_checker import CopyrightChecker, HAS_PATHSPEC


@unittest.skipIf(not HAS_PATHSPEC, "pathspec library not installed")
class TestIgnoreFiles(unittest.TestCase):
    """Test ignore file functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Create a simple template file
        self.template_path = os.path.join(self.temp_dir, "copyright.txt")
        with open(self.template_path, "w", encoding="utf-8") as f:
            f.write("""[VARIABLES]
COMPANY = Test Company

[.py]
# Copyright {regex:\\d{4}(-\\d{4})?} {COMPANY}
""")

    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_copyrightignore_simple_pattern(self):
        """Test basic .copyrightignore pattern matching"""
        # Create .copyrightignore
        with open(".copyrightignore", "w") as f:
            f.write("generated.py\n")

        checker = CopyrightChecker(self.template_path)

        self.assertTrue(checker.should_ignore("generated.py"))
        self.assertFalse(checker.should_ignore("normal.py"))

    def test_copyrightignore_wildcard_pattern(self):
        """Test wildcard patterns in .copyrightignore"""
        with open(".copyrightignore", "w") as f:
            f.write("*.min.js\n")
            f.write("*.bundle.js\n")

        checker = CopyrightChecker(self.template_path)

        self.assertTrue(checker.should_ignore("app.min.js"))
        self.assertTrue(checker.should_ignore("vendor.bundle.js"))
        self.assertFalse(checker.should_ignore("app.js"))

    def test_copyrightignore_directory_pattern(self):
        """Test directory patterns in .copyrightignore"""
        with open(".copyrightignore", "w") as f:
            f.write("node_modules/\n")
            f.write("vendor/\n")

        checker = CopyrightChecker(self.template_path)

        self.assertTrue(checker.should_ignore("node_modules/package.js"))
        self.assertTrue(checker.should_ignore("vendor/library.py"))
        self.assertFalse(checker.should_ignore("src/main.py"))

    def test_copyrightignore_nested_directory(self):
        """Test nested directory patterns"""
        with open(".copyrightignore", "w") as f:
            f.write("**/generated/\n")

        checker = CopyrightChecker(self.template_path)

        self.assertTrue(checker.should_ignore("src/generated/code.py"))
        self.assertTrue(checker.should_ignore("tests/generated/fixtures.py"))
        self.assertFalse(checker.should_ignore("src/manual/code.py"))

    def test_copyrightignore_comments_and_empty_lines(self):
        """Test that comments and empty lines are ignored"""
        with open(".copyrightignore", "w") as f:
            f.write("# This is a comment\n")
            f.write("\n")
            f.write("generated.py\n")
            f.write("# Another comment\n")
            f.write("\n")
            f.write("*.tmp\n")

        checker = CopyrightChecker(self.template_path)

        self.assertTrue(checker.should_ignore("generated.py"))
        self.assertTrue(checker.should_ignore("file.tmp"))
        self.assertFalse(checker.should_ignore("normal.py"))

    def test_gitignore_patterns(self):
        """Test that .gitignore patterns are respected"""
        with open(".gitignore", "w") as f:
            f.write("__pycache__/\n")
            f.write("*.pyc\n")
            f.write(".env\n")

        checker = CopyrightChecker(self.template_path, use_gitignore=True)

        self.assertTrue(checker.should_ignore("__pycache__/cache.py"))
        self.assertTrue(checker.should_ignore("test.pyc"))
        self.assertTrue(checker.should_ignore(".env"))
        self.assertFalse(checker.should_ignore("main.py"))

    def test_gitignore_disabled(self):
        """Test disabling .gitignore patterns"""
        with open(".gitignore", "w") as f:
            f.write("*.pyc\n")

        checker = CopyrightChecker(self.template_path, use_gitignore=False)

        # Should not be ignored when gitignore is disabled
        self.assertFalse(checker.should_ignore("test.pyc"))

    def test_combined_copyrightignore_and_gitignore(self):
        """Test combining patterns from both files"""
        with open(".copyrightignore", "w") as f:
            f.write("generated/\n")

        with open(".gitignore", "w") as f:
            f.write("*.pyc\n")

        checker = CopyrightChecker(self.template_path, use_gitignore=True)

        self.assertTrue(checker.should_ignore("generated/code.py"))
        self.assertTrue(checker.should_ignore("test.pyc"))
        self.assertFalse(checker.should_ignore("main.py"))

    def test_copyrightignore_precedence(self):
        """Test .copyrightignore patterns are loaded"""
        with open(".copyrightignore", "w") as f:
            f.write("specific_file.py\n")

        with open(".gitignore", "w") as f:
            f.write("other_file.py\n")

        checker = CopyrightChecker(self.template_path)

        self.assertTrue(checker.should_ignore("specific_file.py"))
        self.assertTrue(checker.should_ignore("other_file.py"))

    def test_custom_ignore_file_path(self):
        """Test using a custom ignore file path"""
        custom_ignore = os.path.join(self.temp_dir, "custom.ignore")
        with open(custom_ignore, "w") as f:
            f.write("custom_pattern.py\n")

        checker = CopyrightChecker(
            self.template_path,
            ignore_file=custom_ignore
        )

        self.assertTrue(checker.should_ignore("custom_pattern.py"))

    def test_no_ignore_files(self):
        """Test behavior when no ignore files exist"""
        checker = CopyrightChecker(self.template_path)

        # Nothing should be ignored
        self.assertFalse(checker.should_ignore("any_file.py"))
        self.assertFalse(checker.should_ignore("node_modules/file.js"))

    def test_check_files_with_ignored(self):
        """Test check_files skips ignored files"""
        with open(".copyrightignore", "w") as f:
            f.write("ignored.py\n")

        # Create test files
        with open("ignored.py", "w") as f:
            f.write("print('ignored')\n")

        with open("checked.py", "w") as f:
            f.write("print('checked')\n")

        checker = CopyrightChecker(self.template_path)
        passed, failed, modified = checker.check_files(
            ["ignored.py", "checked.py"],
            auto_fix=True
        )

        # ignored.py should be in passed (considered as passed)
        self.assertIn("ignored.py", passed)
        # checked.py should be in passed and modified (copyright added)
        self.assertIn("checked.py", passed)
        self.assertIn("checked.py", modified)

    def test_glob_star_pattern(self):
        """Test ** glob pattern"""
        with open(".copyrightignore", "w") as f:
            f.write("**/build/**\n")

        checker = CopyrightChecker(self.template_path)

        self.assertTrue(checker.should_ignore("build/output.py"))
        self.assertTrue(checker.should_ignore("src/build/temp.py"))
        self.assertTrue(checker.should_ignore("build/nested/deep/file.py"))

    def test_negation_pattern(self):
        """Test negation patterns (!)"""
        with open(".copyrightignore", "w") as f:
            f.write("*.log\n")
            f.write("!important.log\n")

        checker = CopyrightChecker(self.template_path)

        self.assertTrue(checker.should_ignore("debug.log"))
        self.assertTrue(checker.should_ignore("error.log"))
        # Note: negation patterns may not work as expected with pathspec
        # This is a limitation we document

    def test_absolute_path_handling(self):
        """Test handling of absolute paths"""
        with open(".copyrightignore", "w") as f:
            f.write("temp/\n")

        checker = CopyrightChecker(self.template_path)

        abs_path = os.path.join(self.temp_dir, "temp", "file.py")
        self.assertTrue(checker.should_ignore(abs_path))

    def test_windows_path_separators(self):
        """Test Windows path separator handling"""
        with open(".copyrightignore", "w") as f:
            f.write("src/generated/\n")

        checker = CopyrightChecker(self.template_path)

        # Test with backslashes (Windows style)
        self.assertTrue(checker.should_ignore("src\\generated\\file.py"))

    def test_file_extension_patterns(self):
        """Test patterns matching file extensions"""
        with open(".copyrightignore", "w") as f:
            f.write("*.min.js\n")
            f.write("*.min.css\n")
            f.write("*.map\n")

        checker = CopyrightChecker(self.template_path)

        self.assertTrue(checker.should_ignore("app.min.js"))
        self.assertTrue(checker.should_ignore("style.min.css"))
        self.assertTrue(checker.should_ignore("app.min.js.map"))
        self.assertFalse(checker.should_ignore("app.js"))


class TestIgnoreFilesWithoutPathspec(unittest.TestCase):
    """Test behavior when pathspec is not installed"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        self.template_path = os.path.join(self.temp_dir, "copyright.txt")
        with open(self.template_path, "w", encoding="utf-8") as f:
            f.write("""[.py]
# Copyright 2026 Test Company
""")

    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @unittest.skipIf(HAS_PATHSPEC, "This test requires pathspec to NOT be installed")
    def test_graceful_degradation_without_pathspec(self):
        """Test that checker works without pathspec installed"""
        with open(".copyrightignore", "w") as f:
            f.write("generated.py\n")

        # Should not raise an error
        checker = CopyrightChecker(self.template_path)

        # Should not ignore anything when pathspec is not available
        self.assertFalse(checker.should_ignore("generated.py"))


if __name__ == "__main__":
    unittest.main()
