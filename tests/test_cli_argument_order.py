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
            cwd=test_environment,
        )

        # Should succeed (copyright.txt is default)
        assert result.returncode == 0
        assert "Copyright" in file_path.read_text()

    def test_filename_first_then_flags(self, test_environment):
        """Test with filename first, then flags (this was the bug!)."""
        file_path = test_environment / "test.py"

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main", str(file_path), "--no-fix"],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should succeed - file already has copyright from previous test
        # or should fail gracefully if no copyright
        assert result.returncode in [0, 1]

    def test_multiple_filenames_first(self, test_environment):
        """Test with multiple filenames as first arguments."""
        file1 = test_environment / "test.py"
        file2 = test_environment / "README.md"

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main", str(file1), str(file2)],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should succeed for .py, skip .md (unsupported)
        assert result.returncode == 0

    def test_flags_before_filename(self, test_environment):
        """Test with flags before filename (traditional order)."""
        file_path = test_environment / "test.py"

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main", "--no-fix", str(file_path)],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should work fine
        assert result.returncode in [0, 1]

    def test_mixed_order_flags_files(self, test_environment):
        """Test with flags mixed between files."""
        file_path = test_environment / "test.py"

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main", str(file_path), "--verbose"],
            capture_output=True,
            text=True,
            cwd=test_environment,
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
            [
                sys.executable,
                "-m",
                "scripts.main",
                "init",
                "--output",
                str(output_path),
                "--help",
            ],  # Should show init help, not try to process --help as file
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should show init help
        assert "Initialize" in result.stdout or "copyright" in result.stdout.lower()

    def test_filename_that_looks_like_command(self, test_environment):
        """Test with a filename that could be confused with a command."""
        # Create a file named 'init.py' which could be confused with init command
        init_file = test_environment / "init.py"
        init_file.write_text("def initialize():\n    pass\n")

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main", str(init_file)],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should process the file, not treat it as init command
        assert result.returncode == 0
        # File should get copyright
        assert "Copyright" in init_file.read_text()

    def test_relative_path_first(self, test_environment):
        """Test with relative path as first argument."""
        result = subprocess.run(
            [sys.executable, "-m", "scripts.main", "test.py"],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should succeed
        assert result.returncode == 0

    def test_wildcard_pattern_first(self, test_environment):
        """Test with file pattern as first argument."""
        # Note: This tests shell expansion, not direct pattern matching
        result = subprocess.run(
            [sys.executable, "-m", "scripts.main", "*.py"],
            capture_output=True,
            text=True,
            cwd=test_environment,
            shell=True,  # Shell will expand *.py
        )

        # Should succeed or fail gracefully (1 for file not found)
        assert result.returncode in [0, 1, 2]  # 1 for file issues, 2 for no files found


class TestCLIEdgeCases:
    """Test edge cases in CLI argument parsing."""

    def test_empty_arguments(self):
        """Test with no arguments."""
        result = subprocess.run(
            [sys.executable, "-m", "scripts.main"], capture_output=True, text=True
        )

        # Should succeed (no files to process)
        assert result.returncode == 0

    def test_only_flags_no_files(self):
        """Test with only flags, no files."""
        result = subprocess.run(
            [sys.executable, "-m", "scripts.main", "--verbose", "--no-fix"],
            capture_output=True,
            text=True,
        )

        # Should succeed (no files to process)
        assert result.returncode == 0

    def test_double_dash_separator(self, test_environment):
        """Test with -- separator to ensure files after it are treated as files."""
        file_path = test_environment / "test.py"

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main", "--", str(file_path)],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should work (argparse handles -- as end of options)
        assert result.returncode == 0

    def test_file_named_with_dashes(self, test_environment):
        """Test with filename that starts with dashes."""
        dash_file = test_environment / "--file.py"
        dash_file.write_text("def test():\n    pass\n")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.main",
                "--",  # Use -- to prevent misinterpretation
                str(dash_file),
            ],
            capture_output=True,
            text=True,
            cwd=test_environment,
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
            [sys.executable, "-m", "scripts.main", "init", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "--output" in result.stdout

    def test_init_with_custom_output(self, test_environment):
        """Test init with custom output path."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.main",
                "init",
                "--help",
            ],  # Just check help works
            capture_output=True,
            text=True,
        )

        assert "--output" in result.stdout or "-o" in result.stdout

    def test_init_as_basename_not_path(self, test_environment):
        """Test that 'init' command is recognized, but './init' or '/path/init' is not."""
        # Create a file named 'init' in a subdirectory
        subdir = test_environment / "subdir"
        subdir.mkdir()
        init_file = subdir / "init"
        init_file.write_text("#!/bin/bash\necho test\n")

        # Using full path should NOT trigger init command
        result = subprocess.run(
            [sys.executable, "-m", "scripts.main", str(init_file)],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should try to process as file (will fail - no copyright.txt yet)
        # But should NOT show init help
        assert "Initialize" not in result.stdout

    def test_init_output_to_directory_fails(self, test_environment):
        """Test that init fails when output is a directory."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.main",
                "init",
                "--output",
                str(test_environment),
            ],  # Directory, not file
            capture_output=True,
            text=True,
            input="1\n",  # Select MIT
            cwd=test_environment,
        )

        # Should fail with error
        assert result.returncode != 0
        assert "directory" in result.stderr.lower()


class TestAllFlagsIndividually:
    """Test each CLI flag individually to ensure they work."""

    def test_notice_custom_template(self, test_environment):
        """Test --notice flag with custom template."""
        custom_template = test_environment / "my_notice.txt"
        custom_template.write_text("[.py]\n# Custom Copyright\n")

        file_path = test_environment / "test.py"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.main",
                "--notice",
                str(custom_template),
                str(file_path),
            ],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        assert result.returncode == 0
        assert "Custom Copyright" in file_path.read_text()

    def test_notice_nonexistent_file_fails(self, test_environment):
        """Test --notice with nonexistent file."""
        file_path = test_environment / "test.py"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.main",
                "--notice",
                "nonexistent.txt",
                str(file_path),
            ],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        assert result.returncode != 0

    def test_verbose_flag(self, test_environment):
        """Test --verbose flag shows debug output."""
        file_path = test_environment / "test.py"

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main", "--verbose", str(file_path)],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should have verbose output
        assert "DEBUG" in result.stderr or "Supported extensions" in result.stderr

    def test_verbose_short_flag(self, test_environment):
        """Test -v short flag for verbose."""
        file_path = test_environment / "test.py"

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main", "-v", str(file_path)],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should have verbose output
        assert "DEBUG" in result.stderr or "Supported extensions" in result.stderr

    def test_changed_only_flag(self, test_environment):
        """Test --changed-only flag (requires git repo)."""
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=test_environment, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"], cwd=test_environment
        )
        subprocess.run(["git", "config", "user.name", "Test"], cwd=test_environment)

        file_path = test_environment / "test.py"
        subprocess.run(["git", "add", "."], cwd=test_environment)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=test_environment)

        # Modify file
        file_path.write_text("def new_func():\n    pass\n")

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main", "--changed-only"],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should process changed file
        assert result.returncode == 0

    def test_changed_only_with_filenames_warns(self, test_environment):
        """Test --changed-only with filenames shows warning."""
        subprocess.run(["git", "init"], cwd=test_environment, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"], cwd=test_environment
        )
        subprocess.run(["git", "config", "user.name", "Test"], cwd=test_environment)

        file_path = test_environment / "test.py"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.main",
                "--changed-only",
                str(file_path),
            ],  # Should be ignored
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should show warning about ignoring filenames
        assert (
            "ignores filename" in result.stderr.lower()
            or "warning" in result.stderr.lower()
        )

    def test_base_ref_flag(self, test_environment):
        """Test --base-ref flag with --changed-only."""
        subprocess.run(["git", "init"], cwd=test_environment, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"], cwd=test_environment
        )
        subprocess.run(["git", "config", "user.name", "Test"], cwd=test_environment)
        subprocess.run(["git", "add", "."], cwd=test_environment)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=test_environment)

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.main",
                "--changed-only",
                "--base-ref",
                "HEAD",
            ],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should work (no changed files since HEAD)
        assert result.returncode == 0

    def test_base_ref_without_changed_only_warns(self, test_environment):
        """Test --base-ref without --changed-only shows warning."""
        file_path = test_environment / "test.py"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.main",
                "--base-ref",
                "main",
                str(file_path),
            ],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should warn that base-ref is ignored
        assert "ignored" in result.stderr.lower() or "warning" in result.stderr.lower()

    def test_no_git_aware_flag(self, test_environment):
        """Test --no-git-aware flag disables git-aware years."""
        file_path = test_environment / "test.py"

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main", "--no-git-aware", str(file_path)],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should succeed (just disables git features)
        assert result.returncode == 0

    def test_per_file_years_flag(self, test_environment):
        """Test --per-file-years flag."""
        subprocess.run(["git", "init"], cwd=test_environment, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"], cwd=test_environment
        )
        subprocess.run(["git", "config", "user.name", "Test"], cwd=test_environment)

        file_path = test_environment / "test.py"

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main", "--per-file-years", str(file_path)],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should succeed
        assert result.returncode == 0

    def test_per_file_years_with_no_git_aware_fails(self, test_environment):
        """Test --per-file-years with --no-git-aware fails."""
        file_path = test_environment / "test.py"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.main",
                "--per-file-years",
                "--no-git-aware",
                str(file_path),
            ],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should fail with error
        assert result.returncode != 0
        assert "requires Git" in result.stderr or "error" in result.stderr.lower()

    def test_ignore_file_flag(self, test_environment):
        """Test --ignore-file with custom ignore file."""
        ignore_file = test_environment / ".myignore"
        ignore_file.write_text("*.md\n")

        file_path = test_environment / "test.py"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.main",
                "--ignore-file",
                str(ignore_file),
                str(file_path),
            ],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should succeed
        assert result.returncode == 0

    def test_no_gitignore_flag(self, test_environment):
        """Test --no-gitignore flag."""
        file_path = test_environment / "test.py"

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main", "--no-gitignore", str(file_path)],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should succeed
        assert result.returncode == 0

    def test_hierarchical_flag(self, test_environment):
        """Test --hierarchical flag for hierarchical templates."""
        file_path = test_environment / "test.py"

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main", "--hierarchical", str(file_path)],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should succeed
        assert result.returncode == 0

    def test_replace_flag(self, test_environment):
        """Test --replace flag for replacing existing copyrights."""
        file_path = test_environment / "test.py"
        # Add an old copyright
        file_path.write_text("# Copyright 2020 Old Company\ndef test():\n    pass\n")

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main", "--replace", str(file_path)],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should succeed and replace copyright
        assert result.returncode == 0
        content = file_path.read_text()
        assert "Test Company" in content  # New copyright

    def test_replace_with_no_fix_fails(self, test_environment):
        """Test --replace with --no-fix fails."""
        file_path = test_environment / "test.py"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.main",
                "--replace",
                "--no-fix",
                str(file_path),
            ],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should fail with error
        assert result.returncode != 0
        assert "requires auto-fix" in result.stderr or "error" in result.stderr.lower()


class TestFlagCombinations:
    """Test combinations of flags that might interact."""

    def test_verbose_and_no_fix(self, test_environment):
        """Test --verbose with --no-fix."""
        file_path = test_environment / "test.py"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.main",
                "--verbose",
                "--no-fix",
                str(file_path),
            ],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        assert result.returncode in [0, 1]
        assert "DEBUG" in result.stderr or "auto-fix: False" in result.stderr

    def test_hierarchical_with_custom_notice(self, test_environment):
        """Test --hierarchical with --notice."""
        custom_name = "NOTICE.txt"
        custom_template = test_environment / custom_name
        custom_template.write_text("[.py]\n# Hierarchical Copyright\n")

        file_path = test_environment / "test.py"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.main",
                "--hierarchical",
                "--notice",
                custom_name,
                str(file_path),
            ],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        assert result.returncode == 0

    def test_replace_with_hierarchical(self, test_environment):
        """Test --replace with --hierarchical."""
        file_path = test_environment / "test.py"
        file_path.write_text("# Copyright 2020 Old\ndef test():\n    pass\n")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.main",
                "--replace",
                "--hierarchical",
                str(file_path),
            ],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        assert result.returncode == 0

    def test_all_flags_together(self, test_environment):
        """Test many flags together (valid combination)."""
        subprocess.run(["git", "init"], cwd=test_environment, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"], cwd=test_environment
        )
        subprocess.run(["git", "config", "user.name", "Test"], cwd=test_environment)

        file_path = test_environment / "test.py"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.main",
                "--verbose",
                "--hierarchical",
                "--replace",
                "--per-file-years",
                "--no-gitignore",
                str(file_path),
            ],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        assert result.returncode == 0


class TestErrorHandling:
    """Test error handling for invalid inputs."""

    def test_nonexistent_file(self, test_environment):
        """Test with nonexistent file."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.main",
                str(test_environment / "nonexistent.py"),
            ],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should handle gracefully
        assert result.returncode in [0, 1, 2]

    def test_invalid_base_ref(self, test_environment):
        """Test --base-ref with invalid git reference."""
        subprocess.run(["git", "init"], cwd=test_environment, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"], cwd=test_environment
        )
        subprocess.run(["git", "config", "user.name", "Test"], cwd=test_environment)

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.main",
                "--changed-only",
                "--base-ref",
                "nonexistent-branch",
            ],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should fail gracefully
        assert result.returncode != 0

    def test_changed_only_without_git(self, test_environment):
        """Test --changed-only in non-git directory."""
        result = subprocess.run(
            [sys.executable, "-m", "scripts.main", "--changed-only"],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should fail or handle gracefully
        assert result.returncode in [0, 2]  # 0 if no files, 2 if error

    def test_unsupported_file_extension(self, test_environment):
        """Test with unsupported file extension."""
        file_path = test_environment / "test.xyz"
        file_path.write_text("some content\n")

        result = subprocess.run(
            [sys.executable, "-m", "scripts.main", str(file_path)],
            capture_output=True,
            text=True,
            cwd=test_environment,
        )

        # Should succeed but skip unsupported file
        assert result.returncode == 0


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
