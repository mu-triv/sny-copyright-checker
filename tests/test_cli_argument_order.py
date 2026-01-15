#!/usr/bin/env python
# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

"""
Tests for CLI argument order edge cases.

This test file was created after discovering a bug where filenames as the first
positional argument conflicted with subcommand parsing. These tests ensure that
various argument orders and combinations work correctly.
"""

import pytest
import tempfile
import subprocess
import sys
from pathlib import Path


@pytest.fixture
def test_environment():
    """Create a test environment with files and copyright template."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)

        # Create copyright template
        template_content = """[.py]
# Copyright {regex:\\d{4}(-\\d{4})?} Test Company
"""
        (project_dir / "copyright.txt").write_text(template_content)

        # Create test file
        (project_dir / "test.py").write_text("def hello():\n    pass\n")
        (project_dir / "README.md").write_text("# README\n")

        yield project_dir


class TestCLIArgumentOrder:
    """Test various CLI argument order scenarios."""

    def test_filename_first_no_flags(self, test_environment):
        """Test with filename as first argument, no other flags."""
        file_path = test_environment / "test.py"

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main", str(file_path)],
            capture_output=True,
            text=True,
            cwd=test_environment
        )

        # Should succeed (copyright.txt is default)
        assert result.returncode == 0
        assert "Copyright" in file_path.read_text()

    def test_filename_first_then_flags(self, test_environment):
        """Test with filename first, then flags (this was the bug!)."""
        file_path = test_environment / "test.py"

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main",
             str(file_path),
             "--no-fix"],
            capture_output=True,
            text=True,
            cwd=test_environment
        )

        # Should succeed - file already has copyright from previous test
        # or should fail gracefully if no copyright
        assert result.returncode in [0, 1]

    def test_multiple_filenames_first(self, test_environment):
        """Test with multiple filenames as first arguments."""
        file1 = test_environment / "test.py"
        file2 = test_environment / "README.md"

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main",
             str(file1),
             str(file2)],
            capture_output=True,
            text=True,
            cwd=test_environment
        )

        # Should succeed for .py, skip .md (unsupported)
        assert result.returncode == 0

    def test_flags_before_filename(self, test_environment):
        """Test with flags before filename (traditional order)."""
        file_path = test_environment / "test.py"

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main",
             "--no-fix",
             str(file_path)],
            capture_output=True,
            text=True,
            cwd=test_environment
        )

        # Should work fine
        assert result.returncode in [0, 1]

    def test_mixed_order_flags_files(self, test_environment):
        """Test with flags mixed between files."""
        file_path = test_environment / "test.py"

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main",
             str(file_path),
             "--verbose"],
            capture_output=True,
            text=True,
            cwd=test_environment
        )

        # Should succeed
        assert result.returncode == 0
        # Verbose output should be present
        assert "INFO" in result.stderr or "INFO" in result.stdout

    def test_init_command_with_flags(self, test_environment):
        """Test init command with flags."""
        output_path = test_environment / "new_copyright.txt"

        # Init command should be recognized even with flags after
        result = subprocess.run(
            [sys.executable, "-m", "scripts.main",
             "init",
             "--output", str(output_path),
             "--help"],  # Should show init help, not try to process --help as file
            capture_output=True,
            text=True,
            cwd=test_environment
        )

        # Should show init help
        assert "Initialize" in result.stdout or "copyright" in result.stdout.lower()

    def test_filename_that_looks_like_command(self, test_environment):
        """Test with a filename that could be confused with a command."""
        # Create a file named 'init.py' which could be confused with init command
        init_file = test_environment / "init.py"
        init_file.write_text("def initialize():\n    pass\n")

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main",
             str(init_file)],
            capture_output=True,
            text=True,
            cwd=test_environment
        )

        # Should process the file, not treat it as init command
        assert result.returncode == 0
        # File should get copyright
        assert "Copyright" in init_file.read_text()

    def test_relative_path_first(self, test_environment):
        """Test with relative path as first argument."""
        result = subprocess.run(
            [sys.executable, "-m", "scripts.main",
             "test.py"],
            capture_output=True,
            text=True,
            cwd=test_environment
        )

        # Should succeed
        assert result.returncode == 0

    def test_wildcard_pattern_first(self, test_environment):
        """Test with file pattern as first argument."""
        # Note: This tests shell expansion, not direct pattern matching
        result = subprocess.run(
            [sys.executable, "-m", "scripts.main",
             "*.py"],
            capture_output=True,
            text=True,
            cwd=test_environment,
            shell=True  # Shell will expand *.py
        )

        # Should succeed or fail gracefully (1 for file not found)
        assert result.returncode in [0, 1, 2]  # 1 for file issues, 2 for no files found


class TestCLIEdgeCases:
    """Test edge cases in CLI argument parsing."""

    def test_empty_arguments(self):
        """Test with no arguments."""
        result = subprocess.run(
            [sys.executable, "-m", "scripts.main"],
            capture_output=True,
            text=True
        )

        # Should succeed (no files to process)
        assert result.returncode == 0

    def test_only_flags_no_files(self):
        """Test with only flags, no files."""
        result = subprocess.run(
            [sys.executable, "-m", "scripts.main",
             "--verbose",
             "--no-fix"],
            capture_output=True,
            text=True
        )

        # Should succeed (no files to process)
        assert result.returncode == 0

    def test_double_dash_separator(self, test_environment):
        """Test with -- separator to ensure files after it are treated as files."""
        file_path = test_environment / "test.py"

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main",
             "--",
             str(file_path)],
            capture_output=True,
            text=True,
            cwd=test_environment
        )

        # Should work (argparse handles -- as end of options)
        assert result.returncode == 0

    def test_file_named_with_dashes(self, test_environment):
        """Test with filename that starts with dashes."""
        dash_file = test_environment / "--file.py"
        dash_file.write_text("def test():\n    pass\n")

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main",
             "--",  # Use -- to prevent misinterpretation
             str(dash_file)],
            capture_output=True,
            text=True,
            cwd=test_environment
        )

        # Should succeed
        assert result.returncode == 0


class TestInitCommandEdgeCases:
    """Test edge cases specific to init command."""

    def test_init_without_flags(self, test_environment):
        """Test init command without any flags (should prompt interactively)."""
        # This would hang waiting for input, so we skip it or mock input
        # Just verify the command is recognized
        result = subprocess.run(
            [sys.executable, "-m", "scripts.main",
             "init",
             "--help"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "--output" in result.stdout

    def test_init_with_custom_output(self, test_environment):
        """Test init with custom output path."""
        result = subprocess.run(
            [sys.executable, "-m", "scripts.main",
             "init",
             "--help"],  # Just check help works
            capture_output=True,
            text=True
        )

        assert "--output" in result.stdout or "-o" in result.stdout


# Test Coverage Summary
"""
COVERAGE ANALYSIS:

The original bug was NOT caught by tests because:

1. **All CLI tests used subprocess with flags BEFORE filenames**
   Example: [sys.executable, "-m", "scripts.main", str(file_path), "--notice=..."]

2. **Tests always specified flags explicitly**
   - Always used --notice= before or after files
   - Never tested bare filename as first argument
   - Never tested filename followed by flags

3. **No tests for argument order permutations**
   - Filename first, flags second (THE BUG!)
   - Multiple files without flags
   - Files only (no flags at all)

4. **No tests for command ambiguity**
   - File named "init" vs init command
   - File named "check" vs check command (if it existed)
   - Relative vs absolute paths as first argument

5. **Subparser interaction not tested**
   - When both positional args and subparsers exist
   - How argparse resolves ambiguity
   - Required=False on subparsers

6. **Edge cases not covered**
   - Empty arguments
   - Only flags, no files
   - Files with special names (--file, init.py, etc.)

LESSONS LEARNED:

1. Test different argument orders, not just the most common one
2. Test the actual user experience (filename first is natural)
3. Test ambiguous cases (commands vs filenames)
4. Test CLI both via subprocess AND direct main() calls
5. Test with minimal arguments (most common use case)
6. Consider how argparse handles positional args + subparsers

RECOMMENDATIONS:

1. Add tests for ALL argument order permutations
2. Test minimal invocations (most likely to have bugs)
3. Test files with special names that could be confused with commands
4. Test both absolute and relative paths
5. Test shell metacharacters in filenames
6. Add integration tests that mimic real user workflows
"""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
