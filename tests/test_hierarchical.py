#!/usr/bin/env python
# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file


"""Tests for hierarchical copyright template support"""

import os
import shutil
import tempfile
import unittest

from scripts.copyright_checker import CopyrightChecker


class TestHierarchicalTemplates(unittest.TestCase):
    """Test hierarchical copyright template functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_hierarchical_mode_root_template(self):
        """Test hierarchical mode with template in root"""
        # Create root copyright template
        with open("copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Root Company\n")

        # Create a subdirectory with a test file
        os.makedirs("src")
        with open("src/test.py", "w") as f:
            f.write("print('test')\n")

        checker = CopyrightChecker("copyright.txt", hierarchical=True)
        has_notice, was_modified = checker.check_file("src/test.py", auto_fix=True)

        self.assertTrue(has_notice)
        self.assertTrue(was_modified)

        # Verify the root template was used
        with open("src/test.py", "r") as f:
            content = f.read()
        self.assertIn("Root Company", content)

    def test_hierarchical_mode_subdirectory_override(self):
        """Test subdirectory copyright overrides parent"""
        # Create root copyright template
        with open("copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Root Company\n")

        # Create subdirectory with its own copyright
        os.makedirs("vendor")
        with open("vendor/copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Vendor Company\n")

        # Create test files
        with open("main.py", "w") as f:
            f.write("print('main')\n")
        with open("vendor/lib.py", "w") as f:
            f.write("print('vendor')\n")

        checker = CopyrightChecker("copyright.txt", hierarchical=True)

        # Check root file
        checker.check_file("main.py", auto_fix=True)
        with open("main.py", "r") as f:
            content = f.read()
        self.assertIn("Root Company", content)

        # Check vendor file
        checker.check_file("vendor/lib.py", auto_fix=True)
        with open("vendor/lib.py", "r") as f:
            content = f.read()
        self.assertIn("Vendor Company", content)
        self.assertNotIn("Root Company", content)

    def test_hierarchical_mode_nested_override(self):
        """Test nested directories with multiple levels of overrides"""
        # Root template
        with open("copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Root\n")

        # Level 1
        os.makedirs("lib")
        with open("lib/copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Lib\n")

        # Level 2
        os.makedirs("lib/external")
        with open("lib/external/copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 External\n")

        # Create test files at each level
        with open("root.py", "w") as f:
            f.write("pass\n")
        with open("lib/internal.py", "w") as f:
            f.write("pass\n")
        with open("lib/external/vendor.py", "w") as f:
            f.write("pass\n")

        checker = CopyrightChecker("copyright.txt", hierarchical=True)

        # Check each file
        checker.check_file("root.py", auto_fix=True)
        checker.check_file("lib/internal.py", auto_fix=True)
        checker.check_file("lib/external/vendor.py", auto_fix=True)

        # Verify correct copyrights
        with open("root.py", "r") as f:
            self.assertIn("Root", f.read())
        with open("lib/internal.py", "r") as f:
            self.assertIn("Lib", f.read())
        with open("lib/external/vendor.py", "r") as f:
            self.assertIn("External", f.read())

    def test_hierarchical_mode_no_template_found(self):
        """Test behavior when no copyright template is found"""
        os.makedirs("src")
        with open("src/test.py", "w") as f:
            f.write("print('test')\n")

        checker = CopyrightChecker("copyright.txt", hierarchical=True)
        has_notice, was_modified = checker.check_file("src/test.py", auto_fix=True)

        # File should be considered as having a notice (skipped)
        self.assertTrue(has_notice)
        self.assertFalse(was_modified)

    def test_hierarchical_mode_caching(self):
        """Test that templates are cached for performance"""
        with open("copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Company\n")

        os.makedirs("src")
        with open("src/file1.py", "w") as f:
            f.write("pass\n")
        with open("src/file2.py", "w") as f:
            f.write("pass\n")

        checker = CopyrightChecker("copyright.txt", hierarchical=True)

        # Check both files
        checker.check_file("src/file1.py", auto_fix=True)
        checker.check_file("src/file2.py", auto_fix=True)

        # Cache should have one entry for src directory
        src_path = os.path.abspath("src")
        self.assertIn(src_path, checker.template_cache)

    def test_hierarchical_mode_different_extensions(self):
        """Test hierarchical mode with different file extensions"""
        with open("copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Company\n")
            f.write("[.js]\n// Copyright 2026 Company\n")

        os.makedirs("src")
        with open("src/test.py", "w") as f:
            f.write("pass\n")
        with open("src/test.js", "w") as f:
            f.write("console.log('test');\n")

        checker = CopyrightChecker("copyright.txt", hierarchical=True)

        checker.check_file("src/test.py", auto_fix=True)
        checker.check_file("src/test.js", auto_fix=True)

        with open("src/test.py", "r") as f:
            content = f.read()
            self.assertIn("#", content)
            self.assertIn("Company", content)

        with open("src/test.js", "r") as f:
            content = f.read()
            self.assertIn("//", content)
            self.assertIn("Company", content)

    def test_non_hierarchical_mode_unchanged(self):
        """Test that non-hierarchical mode still works"""
        # Create root template
        with open("copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Company\n")

        # Create subdirectory with different template (should be ignored)
        os.makedirs("src")
        with open("src/copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Other\n")

        with open("src/test.py", "w") as f:
            f.write("pass\n")

        # Non-hierarchical mode - should use root template only
        checker = CopyrightChecker("copyright.txt", hierarchical=False)
        checker.check_file("src/test.py", auto_fix=True)

        with open("src/test.py", "r") as f:
            content = f.read()
            self.assertIn("Company", content)
            self.assertNotIn("Other", content)

    def test_hierarchical_mode_absolute_paths(self):
        """Test hierarchical mode with absolute paths"""
        with open("copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Company\n")

        os.makedirs("src")
        test_file = os.path.join(self.temp_dir, "src", "test.py")
        with open(test_file, "w") as f:
            f.write("pass\n")

        checker = CopyrightChecker("copyright.txt", hierarchical=True)
        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        self.assertTrue(has_notice)
        self.assertTrue(was_modified)

    def test_hierarchical_mode_check_multiple_files(self):
        """Test check_files with hierarchical mode"""
        # Root template
        with open("copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Root\n")

        # Subdirectory template
        os.makedirs("vendor")
        with open("vendor/copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Vendor\n")

        # Create files
        with open("main.py", "w") as f:
            f.write("pass\n")
        with open("vendor/lib.py", "w") as f:
            f.write("pass\n")

        checker = CopyrightChecker("copyright.txt", hierarchical=True)
        passed, failed, modified = checker.check_files(
            ["main.py", "vendor/lib.py"], auto_fix=True
        )

        self.assertEqual(len(passed), 2)
        self.assertEqual(len(modified), 2)
        self.assertEqual(len(failed), 0)

    def test_hierarchical_mode_unsupported_extension(self):
        """Test hierarchical mode with unsupported file extension"""
        with open("copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Company\n")

        os.makedirs("src")
        with open("src/test.txt", "w") as f:
            f.write("text file\n")

        checker = CopyrightChecker("copyright.txt", hierarchical=True)
        has_notice, was_modified = checker.check_file("src/test.txt", auto_fix=True)

        # Should be skipped
        self.assertTrue(has_notice)
        self.assertFalse(was_modified)

    def test_hierarchical_mode_malformed_template_in_subdirectory(self):
        """Test behavior when subdirectory has malformed template"""
        # Valid root template
        with open("copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Root\n")

        # Create subdirectory with malformed template
        os.makedirs("vendor")
        with open("vendor/copyright.txt", "w") as f:
            f.write("Invalid template without sections\n")

        with open("vendor/lib.py", "w") as f:
            f.write("pass\n")

        checker = CopyrightChecker("copyright.txt", hierarchical=True)

        # Should fall back to root template (or skip if parsing fails)
        has_notice, was_modified = checker.check_file("vendor/lib.py", auto_fix=True)

        # File should be skipped or use root template
        self.assertTrue(has_notice)

    def test_hierarchical_mode_empty_template_file(self):
        """Test behavior when subdirectory has empty template"""
        # Valid root template
        with open("copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Root\n")

        # Create subdirectory with empty template
        os.makedirs("vendor")
        with open("vendor/copyright.txt", "w") as f:
            f.write("")  # Empty file

        with open("vendor/lib.py", "w") as f:
            f.write("pass\n")

        checker = CopyrightChecker("copyright.txt", hierarchical=True)
        has_notice, was_modified = checker.check_file("vendor/lib.py", auto_fix=True)

        # Should be skipped (no templates in empty file)
        self.assertTrue(has_notice)
        self.assertFalse(was_modified)

    def test_hierarchical_mode_template_missing_extension(self):
        """Test when subdirectory template doesn't define needed extension"""
        # Root template with .py
        with open("copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Root\n")

        # Subdirectory template with only .js (no .py)
        os.makedirs("vendor")
        with open("vendor/copyright.txt", "w") as f:
            f.write("[.js]\n// Copyright 2026 Vendor\n")

        with open("vendor/lib.py", "w") as f:
            f.write("pass\n")

        checker = CopyrightChecker("copyright.txt", hierarchical=True)
        has_notice, was_modified = checker.check_file("vendor/lib.py", auto_fix=True)

        # Should be skipped (no .py template in nearest file)
        self.assertTrue(has_notice)
        self.assertFalse(was_modified)

    def test_hierarchical_mode_preserves_existing_copyright(self):
        """Test that existing copyrights are preserved in hierarchical mode"""
        # Root template
        with open("copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright {regex:\\d{4}} Root\n")

        # Create file with existing copyright
        os.makedirs("src")
        with open("src/old.py", "w") as f:
            f.write("# Copyright 2020 Root\n\ndef old_function():\n    pass\n")

        checker = CopyrightChecker("copyright.txt", hierarchical=True)
        has_notice, was_modified = checker.check_file("src/old.py", auto_fix=True)

        # Should recognize existing copyright and not modify
        self.assertTrue(has_notice)
        self.assertFalse(was_modified)

        with open("src/old.py", "r") as f:
            content = f.read()
            self.assertIn("2020", content)  # Old year preserved

    def test_hierarchical_mode_with_shebang(self):
        """Test hierarchical mode respects shebang lines"""
        with open("copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Company\n")

        os.makedirs("scripts")
        with open("scripts/tool.py", "w") as f:
            f.write("#!/usr/bin/env python\n\nprint('hello')\n")

        checker = CopyrightChecker("copyright.txt", hierarchical=True)
        checker.check_file("scripts/tool.py", auto_fix=True)

        with open("scripts/tool.py", "r") as f:
            lines = f.readlines()
            self.assertEqual(lines[0].strip(), "#!/usr/bin/env python")
            self.assertIn("Copyright", lines[1])

    def test_hierarchical_mode_preserves_line_endings(self):
        """Test hierarchical mode preserves CRLF line endings"""
        with open("copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Company\n")

        os.makedirs("src")
        # Write file with CRLF
        with open("src/windows.py", "wb") as f:
            f.write(b"print('test')\r\n")

        checker = CopyrightChecker("copyright.txt", hierarchical=True)
        checker.check_file("src/windows.py", auto_fix=True)

        # Read as binary to check line endings
        with open("src/windows.py", "rb") as f:
            content = f.read()
            self.assertIn(b"\r\n", content)  # CRLF preserved

    def test_hierarchical_mode_deep_nesting(self):
        """Test hierarchical mode with very deep directory nesting"""
        # Root template
        with open("copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Root\n")

        # Create deeply nested structure (10 levels)
        path = "a/b/c/d/e/f/g/h/i/j"
        os.makedirs(path)

        # Template at level 5
        with open("a/b/c/d/e/copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Level5\n")

        # File at level 10
        deep_file = os.path.join(path, "deep.py")
        with open(deep_file, "w") as f:
            f.write("pass\n")

        checker = CopyrightChecker("copyright.txt", hierarchical=True)
        checker.check_file(deep_file, auto_fix=True)

        with open(deep_file, "r") as f:
            content = f.read()
            self.assertIn("Level5", content)  # Should find nearest template

    def test_hierarchical_with_git_aware_years(self):
        """Test hierarchical mode combined with Git-aware year management"""
        # Root template with year pattern
        with open("copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright {regex:\\d{4}(-\\d{4})?} Root\n")

        os.makedirs("src")
        with open("src/new.py", "w") as f:
            f.write("pass\n")

        # Enable both hierarchical and git-aware
        checker = CopyrightChecker("copyright.txt", hierarchical=True, git_aware=True)
        checker.check_file("src/new.py", auto_fix=True)

        with open("src/new.py", "r") as f:
            content = f.read()
            self.assertIn("2026", content)
            self.assertIn("Root", content)

    def test_hierarchical_mode_cache_per_directory(self):
        """Test that cache is properly maintained per directory"""
        with open("copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Root\n")

        os.makedirs("dir1")
        os.makedirs("dir2")

        with open("dir1/copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Dir1\n")

        with open("dir1/file1.py", "w") as f:
            f.write("pass\n")
        with open("dir2/file2.py", "w") as f:
            f.write("pass\n")

        checker = CopyrightChecker("copyright.txt", hierarchical=True)

        checker.check_file("dir1/file1.py", auto_fix=True)
        checker.check_file("dir2/file2.py", auto_fix=True)

        # Both directories should be in cache
        dir1_path = os.path.abspath("dir1")
        dir2_path = os.path.abspath("dir2")
        self.assertIn(dir1_path, checker.template_cache)
        self.assertIn(dir2_path, checker.template_cache)

        # dir1 should have its own template, dir2 should have root
        self.assertIsNotNone(checker.template_cache[dir1_path])
        self.assertIsNotNone(checker.template_cache[dir2_path])

    def test_hierarchical_mode_relative_paths(self):
        """Test hierarchical mode with relative paths"""
        with open("copyright.txt", "w") as f:
            f.write("[.py]\n# Copyright 2026 Root\n")

        os.makedirs("src/utils")
        with open("src/utils/helper.py", "w") as f:
            f.write("pass\n")

        checker = CopyrightChecker("copyright.txt", hierarchical=True)

        # Use relative path with ./
        has_notice, was_modified = checker.check_file(
            "./src/utils/helper.py", auto_fix=True
        )

        self.assertTrue(has_notice)
        self.assertTrue(was_modified)


if __name__ == "__main__":
    unittest.main()
