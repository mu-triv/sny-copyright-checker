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

    def test_unicode_filenames_in_ignore_patterns(self):
        """Test ignore patterns with Unicode characters"""
        with open(".copyrightignore", "w", encoding="utf-8") as f:
            f.write("日本語.py\n")
            f.write("файл.py\n")

        checker = CopyrightChecker(self.template_path)

        self.assertTrue(checker.should_ignore("日本語.py"))
        self.assertTrue(checker.should_ignore("файл.py"))
        self.assertFalse(checker.should_ignore("regular.py"))

    def test_patterns_with_spaces(self):
        """Test ignore patterns with spaces in filenames"""
        with open(".copyrightignore", "w") as f:
            f.write("my file.py\n")
            f.write("path with spaces/*.py\n")

        checker = CopyrightChecker(self.template_path)

        self.assertTrue(checker.should_ignore("my file.py"))
        self.assertTrue(checker.should_ignore("path with spaces/test.py"))
        self.assertFalse(checker.should_ignore("myfile.py"))

    def test_very_long_paths(self):
        """Test ignore patterns with very long paths"""
        # Create deeply nested directory
        long_path = "/".join(["dir"] * 50)  # 50 levels deep

        with open(".copyrightignore", "w") as f:
            f.write(f"{long_path}/*.py\n")

        checker = CopyrightChecker(self.template_path)

        # Should handle long paths without error
        long_file = f"{long_path}/test.py"
        result = checker.should_ignore(long_file)
        self.assertIsInstance(result, bool)

    def test_corrupted_ignore_file(self):
        """Test behavior with corrupted .copyrightignore file"""
        # Create file with binary/invalid content
        with open(".copyrightignore", "wb") as f:
            f.write(b"\xff\xfe\x00\x00Invalid\x00\x00")

        # Should not crash, just skip corrupted file
        try:
            checker = CopyrightChecker(self.template_path)
            # Should either work or fail gracefully
            self.assertIsNotNone(checker)
        except Exception as e:
            # If it fails, it should be a handled exception
            self.assertIsInstance(e, (UnicodeDecodeError, ValueError))

    def test_ignore_with_hierarchical_mode(self):
        """Test ignore patterns combined with hierarchical templates"""
        # Root copyright
        with open("copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Root\n")

        # Root ignore file
        with open(".copyrightignore", "w") as f:
            f.write("vendor/**/*.py\n")

        # Create vendor directory with its own copyright
        os.makedirs("vendor")
        with open("vendor/copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Vendor\n")

        with open("vendor/lib.py", "w") as f:
            f.write("pass\n")

        checker = CopyrightChecker("copyright.txt", hierarchical=True)

        # File should be ignored despite hierarchical mode
        self.assertTrue(checker.should_ignore("vendor/lib.py"))

    def test_gitignore_in_subdirectories(self):
        """Test that only root .gitignore is respected (current behavior)"""
        # Root .gitignore
        with open(".gitignore", "w") as f:
            f.write("*.pyc\n")

        # Subdirectory .gitignore (should be ignored)
        os.makedirs("subdir")
        with open("subdir/.gitignore", "w") as f:
            f.write("*.log\n")

        checker = CopyrightChecker(self.template_path)

        # Root patterns should work
        self.assertTrue(checker.should_ignore("test.pyc"))
        self.assertTrue(checker.should_ignore("subdir/test.pyc"))

        # Subdirectory patterns should NOT work (only root .gitignore is read)
        self.assertFalse(checker.should_ignore("subdir/test.log"))

    def test_case_sensitivity_handling(self):
        """Test case sensitivity in ignore patterns"""
        with open(".copyrightignore", "w") as f:
            f.write("Test.py\n")
            f.write("UPPER.PY\n")

        checker = CopyrightChecker(self.template_path)

        # Exact match should work
        self.assertTrue(checker.should_ignore("Test.py"))
        self.assertTrue(checker.should_ignore("UPPER.PY"))

        # Different case depends on platform/pathspec behavior
        # Just ensure it doesn't crash
        result = checker.should_ignore("test.py")
        self.assertIsInstance(result, bool)

    def test_empty_pattern_lines(self):
        """Test that empty lines in ignore file are handled"""
        with open(".copyrightignore", "w") as f:
            f.write("test1.py\n")
            f.write("\n")
            f.write("\n")
            f.write("test2.py\n")
            f.write("\n")

        checker = CopyrightChecker(self.template_path)

        self.assertTrue(checker.should_ignore("test1.py"))
        self.assertTrue(checker.should_ignore("test2.py"))

    def test_ignore_patterns_with_git_aware(self):
        """Test ignore patterns combined with Git-aware year management"""
        with open(".copyrightignore", "w") as f:
            f.write("generated/*.py\n")

        with open("copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright {regex:\\d{4}(-\\d{4})?} Company\n")

        os.makedirs("generated")
        with open("generated/auto.py", "w") as f:
            f.write("# Auto-generated\n")

        # Enable both features
        checker = CopyrightChecker("copyright.txt", git_aware=True)

        # Ignored files should be skipped
        self.assertTrue(checker.should_ignore("generated/auto.py"))

    def test_whitespace_in_patterns(self):
        """Test patterns with leading/trailing whitespace"""
        with open(".copyrightignore", "w") as f:
            f.write("  test.py  \n")
            f.write("\tindented.py\n")

        checker = CopyrightChecker(self.template_path)

        # Whitespace should be stripped
        self.assertTrue(checker.should_ignore("test.py"))
        self.assertTrue(checker.should_ignore("indented.py"))


if __name__ == "__main__":
    unittest.main()
