# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file


import pytest
import tempfile
import os
import subprocess

@pytest.fixture
    content = """[.py]
[.sql]
[.js]
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write(content)
        temp_path = f.name

    yield temp_path

    os.unlink(temp_path)


@pytest.fixture
def temp_simple_template():
    """Create a simple template without regex"""
    content = """[.txt]
All Rights Reserved
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write(content)
        temp_path = f.name

    yield temp_path

    os.unlink(temp_path)


# ============================================================================
# POSITIVE TEST CASES - Normal expected functionality
# ============================================================================


def hello():
    pass
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
        f.write(content)
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is False
    finally:
        os.unlink(temp_file)


    content = """def hello():
    pass
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
        f.write(content)
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        with open(temp_file, "r") as f:
            updated_content = f.read()

        assert "SNY Group Corporation" in updated_content
    finally:
        os.unlink(temp_file)


    """Test that shebang lines are preserved"""
    content = """#!/usr/bin/env python

def hello():
    pass
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
        f.write(content)
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        # Verify shebang is still first line
        with open(temp_file, "r") as f:
            lines = f.readlines()

        assert lines[0].startswith("#!/usr/bin/env python")
    finally:
        os.unlink(temp_file)


def hello():
    pass
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
        f.write(content)
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is False
    finally:
        os.unlink(temp_file)


SELECT * FROM users;
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".sql") as f:
        f.write(content)
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is False
    finally:
        os.unlink(temp_file)


    content = """SELECT * FROM users;
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".sql") as f:
        f.write(content)
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        with open(temp_file, "r") as f:
            updated_content = f.read()

        assert "SNY Group Corporation" in updated_content
    finally:
        os.unlink(temp_file)


    """Test checking multiple files at once"""
    # Create test files
def func1():
    pass
"""
    file2_content = """def func2():
    pass
"""

    temp_files = []

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
        f.write(file1_content)
        temp_files.append(f.name)

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
        f.write(file2_content)
        temp_files.append(f.name)

    try:
        passed, failed, modified = checker.check_files(temp_files, auto_fix=True)

        assert len(passed) == 2
        assert len(failed) == 0
        assert len(modified) == 1  # Only second file was modified
    finally:
        for temp_file in temp_files:
            os.unlink(temp_file)


    """Test getting list of supported file extensions"""
    extensions = checker.get_supported_extensions()

    assert ".py" in extensions
    assert ".sql" in extensions
    assert ".js" in extensions
    assert len(extensions) == 3


    """Test checking file without auto-fix (report only)"""
    content = """def hello():
    pass
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
        f.write(content)
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=False)

        assert has_notice is False
        assert was_modified is False

        # Verify file wasn't modified
        with open(temp_file, "r") as f:
            content_after = f.read()

        assert content == content_after
    finally:
        os.unlink(temp_file)


    content = """def hello():
    pass
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
        f.write(content)
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        with open(temp_file, "r") as f:
            updated_content = f.read()

        from datetime import datetime

        current_year = str(datetime.now().year)
        assert current_year in updated_content
    finally:
        os.unlink(temp_file)


function hello() {
    console.log('hello');
}
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".js") as f:
        f.write(content)
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is False
    finally:
        os.unlink(temp_file)


# ============================================================================
# NEGATIVE TEST CASES - Error conditions and invalid inputs
# ============================================================================


def test_init_with_nonexistent_template():
    """Test initializing checker with non-existent template file"""

def test_init_with_invalid_template():
    """Test initializing checker with invalid template format"""
    content = """This is not a valid template
No sections here
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write(content)
        temp_path = f.name

    try:
    finally:
        os.unlink(temp_path)


    """Test checking a file that doesn't exist"""
    with pytest.raises(FileNotFoundError, match="Source file not found"):
        checker.check_file("/nonexistent/file.py", auto_fix=True)


    """Test file with unsupported extension is skipped"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".xyz") as f:
        f.write("test content")
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        # Should return True (skipped, not an error) and not modified
        assert has_notice is True
        assert was_modified is False
    finally:
        os.unlink(temp_file)


    """Test checking file without extension"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix="") as f:
        f.write("test content")
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        # Should skip file without extension
        assert has_notice is True
        assert was_modified is False
    finally:
        os.unlink(temp_file)


    """Test checking a binary file (should skip)"""
    # Create a simple binary file
    with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".py") as f:
        f.write(b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a")  # PNG header
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        # Should skip binary file gracefully
        assert has_notice is True
        assert was_modified is False
    finally:
        os.unlink(temp_file)


def hello():
    pass
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
        f.write(content)
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is False
        assert was_modified is False
    finally:
        os.unlink(temp_file)


    """Test check_files with mix of valid and non-existent files"""
    # Create one valid file
    content = """def hello():
    pass
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
        f.write(content)
        temp_file = f.name

    try:
        files = [temp_file, "/nonexistent/file.py"]
        passed, failed, modified = checker.check_files(files, auto_fix=True)

        assert len(passed) == 1
        assert len(failed) == 1
        assert len(modified) == 1
    finally:
        os.unlink(temp_file)


def hello():
    pass
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
        f.write(content)
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        # Template requires both lines, so this should be modified
        assert has_notice is True
        assert was_modified is True
    finally:
        os.unlink(temp_file)


# ============================================================================
# EDGE CASES - Boundary conditions and special scenarios
# ============================================================================


    """Test checking an empty file"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
        f.write("")
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        with open(temp_file, "r") as f:
            content = f.read()

    finally:
        os.unlink(temp_file)


    """Test checking file with only whitespace"""
    content = """



"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
        f.write(content)
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True
    finally:
        os.unlink(temp_file)


    """Test shebang handling with immediate content"""
    content = """#!/usr/bin/env python
def hello():
    pass
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
        f.write(content)
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        # Check structure
        with open(temp_file, "r") as f:
            lines = f.readlines()

        assert lines[0].startswith("#!/usr/bin/env python")
    finally:
        os.unlink(temp_file)


    """Test file with multiple lines starting with #! (only first should be preserved)"""
    content = """#!/usr/bin/env python
#! This is a comment

def hello():
    pass
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
        f.write(content)
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        with open(temp_file, "r") as f:
            content = f.read()

        assert content.startswith("#!/usr/bin/env python")
    finally:
        os.unlink(temp_file)


    """Test file with UTF-8 BOM"""
    content = """\ufeffdef hello():
    pass
"""

    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".py", encoding="utf-8-sig"
    ) as f:
        f.write(content)
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        # Should handle BOM gracefully
        assert has_notice is True
        assert was_modified is True
    finally:
        os.unlink(temp_file)


    """Test file with very long lines"""
    long_line = "x = '" + "a" * 10000 + "'"
    content = f"""{long_line}
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
        f.write(content)
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True
    finally:
        os.unlink(temp_file)


    """Test file with mixed line endings (CRLF and LF)"""
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".py", newline=""
    ) as f:
        f.write(content)
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        # Should handle mixed line endings
        assert has_notice is True
    finally:
        os.unlink(temp_file)


    """Test check_files with empty file list"""
    passed, failed, modified = checker.check_files([], auto_fix=True)

    assert len(passed) == 0
    assert len(failed) == 0
    assert len(modified) == 0


    """Test check_files with all unsupported extensions"""
    temp_files = []

    for ext in [".xyz", ".abc", ".def"]:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=ext) as f:
            f.write("content")
            temp_files.append(f.name)

    try:
        passed, failed, modified = checker.check_files(temp_files, auto_fix=True)

        # All should pass (skipped) with no modifications
        assert len(passed) == 3
        assert len(failed) == 0
        assert len(modified) == 0
    finally:
        for temp_file in temp_files:
            os.unlink(temp_file)


def hello():
    print("world")
    return 42

class MyClass:
    pass
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
        f.write(content)
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is False

        # Verify content is unchanged
        with open(temp_file, "r") as f:
            content_after = f.read()

        assert content == content_after
    finally:
        os.unlink(temp_file)


    """Test file with single line of code"""
    content = """print('hello')"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
        f.write(content)
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        with open(temp_file, "r") as f:
            updated = f.read()

        assert "print('hello')" in updated
    finally:
        os.unlink(temp_file)


    content = """def hello():
    pass

def world():
    pass
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
        f.write(content)
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is False
    finally:
        os.unlink(temp_file)


    content = """def hello():
    pass
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
        f.write(content)
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        # Check spacing
        with open(temp_file, "r") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
                break

    finally:
        os.unlink(temp_file)


    """Test handling of file permission errors"""
    content = """def hello():
    pass
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
        f.write(content)
        temp_file = f.name

    try:
        # Make file read-only
        os.chmod(temp_file, 0o444)

        # On Windows, this might succeed. On Unix, it should fail.
        # We just check it doesn't crash
        try:
            has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
            # If it succeeds, that's fine
        except PermissionError:
            # If it fails with permission error, that's also expected
            pass
    finally:
        # Restore permissions and delete
        os.chmod(temp_file, 0o644)
        os.unlink(temp_file)


def test_template_with_no_extensions(temp_simple_template):
    """Test checker behavior with simple template"""
    extensions = checker.get_supported_extensions()

    assert ".txt" in extensions
    assert len(extensions) == 1


    """Test that CRLF (Windows) line endings are preserved"""
    # Create a test file with CRLF line endings
    content = "def hello():\r\n    pass\r\n"

    with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".py") as f:
        f.write(content.encode("utf-8"))
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        # Read file in binary mode to check line endings
        with open(temp_file, "rb") as f:
            updated_content = f.read().decode("utf-8")

        # Verify CRLF line endings are preserved
        assert "\r\n" in updated_content, "CRLF line endings should be preserved"
        assert updated_content.count("\r\n") > 0

        assert "SNY Group Corporation" in updated_content
    finally:
        os.unlink(temp_file)


    """Test that LF (Unix/Linux) line endings are preserved"""
    # Create a test file with LF line endings only
    content = "def hello():\n    pass\n"

    with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".py") as f:
        f.write(content.encode("utf-8"))
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        # Read file in binary mode to check line endings
        with open(temp_file, "rb") as f:
            updated_content = f.read().decode("utf-8")

        # Verify no CRLF, only LF
        assert "\r\n" not in updated_content, "Should not have CRLF line endings"
        assert "\n" in updated_content, "Should have LF line endings"

        assert "SNY Group Corporation" in updated_content
    finally:
        os.unlink(temp_file)


    with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".py") as f:
        f.write(content.encode("utf-8"))
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is False

        # Read file in binary mode to check line endings
        with open(temp_file, "rb") as f:
            updated_content = f.read().decode("utf-8")

        # Verify CRLF line endings are still present
        assert "\r\n" in updated_content, "CRLF line endings should be preserved"

    finally:
        os.unlink(temp_file)


    with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".py") as f:
        f.write(content.encode("utf-8"))
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is False

        # Read file in binary mode to check line endings
        with open(temp_file, "rb") as f:
            updated_content = f.read().decode("utf-8")

        # Verify no CRLF, only LF
        assert "\r\n" not in updated_content, "Should not have CRLF line endings"
        assert "\n" in updated_content, "Should have LF line endings"

    finally:
        os.unlink(temp_file)


    """Test that files with mixed line endings (containing any CRLF) are treated as CRLF files"""
    # Create a test file with mixed line endings (mostly LF but some CRLF)
    content = "def hello():\r\n    pass\n"  # First line CRLF, second LF

    with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".py") as f:
        f.write(content.encode("utf-8"))
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        # Read file in binary mode to check line endings
        with open(temp_file, "rb") as f:
            updated_content = f.read().decode("utf-8")

        # Since original had CRLF, output should use CRLF throughout
        )
    finally:
        os.unlink(temp_file)


    content = "def hello():\n    pass\n"

    with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".py") as f:
        f.write(content.encode("utf-8"))
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        assert has_notice is True
        assert was_modified is True

        # Read file after first run
        with open(temp_file, "r", encoding="utf-8") as f:
            content_after_first = f.read()

        )

        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        assert has_notice is True
        assert was_modified is False, "Second run should not modify the file"

        # Read file after second run
        with open(temp_file, "r", encoding="utf-8") as f:
            content_after_second = f.read()

        )
        assert content_after_first == content_after_second, (
            "File content should be identical after second run"
        )
    finally:
        os.unlink(temp_file)


    with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".py") as f:
        f.write(content.encode("utf-8"))
        temp_file = f.name

    try:
        # Run checker
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is False

        # Read file and verify
        with open(temp_file, "r", encoding="utf-8") as f:
            updated_content = f.read()

        # Verify still has 2025, not replaced with 2026
        assert "2025" in updated_content, "Original year should be preserved"
        assert "2026" not in updated_content, "Should not add current year"
        )
    finally:
        os.unlink(temp_file)


    with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".py") as f:
        f.write(content.encode("utf-8"))
        temp_file = f.name

    try:
        # Run checker 3 times
        for i in range(3):
            has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

            assert was_modified is False, f"Run {i + 1}: Should not modify file"

            # Read and verify
            with open(temp_file, "r", encoding="utf-8") as f:
                current_content = f.read()

            )
            assert "2025" in current_content, f"Run {i + 1}: Should preserve 2025 year"
            assert "2026" not in current_content, f"Run {i + 1}: Should not add 2026"
    finally:
        os.unlink(temp_file)


    content = "def hello():\n    return 'world'\n\nclass MyClass:\n    pass\n"

    with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".py") as f:
        f.write(content.encode("utf-8"))
        temp_file = f.name

    try:
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        with open(temp_file, "r", encoding="utf-8") as f:
            updated_content = f.read()

        lines = updated_content.split("\n")
        assert "SNY Group Corporation" in lines[0], (
            "First line should contain company name"
        )
        assert "def hello():" in updated_content
        assert "class MyClass:" in updated_content
    finally:
        os.unlink(temp_file)


    """Test that get_changed_files raises error when not in a git repository"""
    with tempfile.TemporaryDirectory() as temp_dir:
        with pytest.raises(RuntimeError, match="Failed to get changed files from git"):
            checker.get_changed_files(repo_path=temp_dir)


    """Test getting changed files from a git repository"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Create and commit a file
        file1 = os.path.join(temp_dir, "file1.py")
        with open(file1, "w") as f:
            f.write(
            )

        subprocess.run(
            ["git", "add", "file1.py"], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Create a new file (unstaged)
        file2 = os.path.join(temp_dir, "file2.py")
        with open(file2, "w") as f:
            f.write("print('new file')\\n")

        # Modify existing file
        with open(file1, "a") as f:
            f.write("print('modified')\\n")

        # Get changed files
        changed_files = checker.get_changed_files(repo_path=temp_dir)

        # Should find file1.py (modified), but not file2.py (not in git yet)
        assert any("file1.py" in f for f in changed_files), (
            "Should detect modified file1.py"
        )


    """Test that get_changed_files only returns files with supported extensions"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Create files with different extensions
        py_file = os.path.join(temp_dir, "test.py")
        txt_file = os.path.join(temp_dir, "test.txt")

        with open(py_file, "w") as f:
            f.write("print('hello')\\n")
        with open(txt_file, "w") as f:
            f.write("Some text\\n")

        subprocess.run(
            ["git", "add", "."], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Modify both files
        with open(py_file, "a") as f:
            f.write("print('modified')\\n")
        with open(txt_file, "a") as f:
            f.write("More text\\n")

        changed_files = checker.get_changed_files(repo_path=temp_dir)

        # Should only return .py file (supported extension)
        assert any("test.py" in f for f in changed_files), "Should include .py file"
        assert not any("test.txt" in f for f in changed_files), (
            "Should not include .txt file (unsupported extension)"
        )


    """Test that get_changed_files detects both staged and unstaged files"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Create and commit files
        file1 = os.path.join(temp_dir, "staged.py")
        file2 = os.path.join(temp_dir, "unstaged.py")

        with open(file1, "w") as f:
            f.write("print('original1')\\n")
        with open(file2, "w") as f:
            f.write("print('original2')\\n")

        subprocess.run(
            ["git", "add", "."], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Modify first file and stage it
        with open(file1, "a") as f:
            f.write("print('staged change')\\n")
        subprocess.run(
            ["git", "add", "staged.py"], cwd=temp_dir, check=True, capture_output=True
        )

        # Modify second file but don't stage
        with open(file2, "a") as f:
            f.write("print('unstaged change')\\n")

        changed_files = checker.get_changed_files(repo_path=temp_dir)

        # Should detect both staged and unstaged changes
        assert any("staged.py" in f for f in changed_files), "Should detect staged file"
        assert any("unstaged.py" in f for f in changed_files), (
            "Should detect unstaged file"
        )


    """Test that get_changed_files detects new files that are staged"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Create initial commit
        file1 = os.path.join(temp_dir, "existing.py")
        with open(file1, "w") as f:
            f.write("print('exists')\\n")
        subprocess.run(
            ["git", "add", "."], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Create new file and stage it
        new_file = os.path.join(temp_dir, "newfile.py")
        with open(new_file, "w") as f:
            f.write("print('new')\\n")
        subprocess.run(
            ["git", "add", "newfile.py"], cwd=temp_dir, check=True, capture_output=True
        )

        changed_files = checker.get_changed_files(repo_path=temp_dir)

        # Should detect new staged file
        assert any("newfile.py" in f for f in changed_files), (
            "Should detect new staged file"
        )


    """Test that get_changed_files returns empty list when no changes"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Create and commit a file
        file1 = os.path.join(temp_dir, "test.py")
        with open(file1, "w") as f:
            f.write("print('hello')\\n")
        subprocess.run(
            ["git", "add", "."], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        changed_files = checker.get_changed_files(repo_path=temp_dir)

        # Should return empty list
        assert len(changed_files) == 0, "Should return no files when nothing changed"


    """Test that get_changed_files works with files in subdirectories"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Create subdirectory with file
        subdir = os.path.join(temp_dir, "src", "utils")
        os.makedirs(subdir, exist_ok=True)

        file1 = os.path.join(subdir, "helper.py")
        with open(file1, "w") as f:
            f.write("print('helper')\\n")

        subprocess.run(
            ["git", "add", "."], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Modify the file in subdirectory
        with open(file1, "a") as f:
            f.write("print('modified')\\n")

        changed_files = checker.get_changed_files(repo_path=temp_dir)

        # Should detect file in subdirectory
        assert len(changed_files) == 1, "Should detect one changed file"
        assert "helper.py" in changed_files[0], (
            "Should detect helper.py in subdirectory"
        )
        assert os.path.exists(changed_files[0]), (
            "Returned path should be absolute and exist"
        )


    """Test that get_changed_files handles multiple supported file types"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Create files of different supported types
        py_file = os.path.join(temp_dir, "script.py")
        js_file = os.path.join(temp_dir, "app.js")
        sql_file = os.path.join(temp_dir, "schema.sql")

        with open(py_file, "w") as f:
            f.write("print('python')\\n")
        with open(js_file, "w") as f:
            f.write("console.log('js');\\n")
        with open(sql_file, "w") as f:
            f.write("SELECT * FROM table;\\n")

        subprocess.run(
            ["git", "add", "."], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Modify all files
        with open(py_file, "a") as f:
            f.write("print('modified')\\n")
        with open(js_file, "a") as f:
            f.write("console.log('modified');\\n")
        with open(sql_file, "a") as f:
            f.write("-- comment\\n")

        changed_files = checker.get_changed_files(repo_path=temp_dir)

        # Should detect all supported file types
        assert len(changed_files) == 3, (
            f"Should detect 3 changed files, found {len(changed_files)}"
        )
        assert any("script.py" in f for f in changed_files), "Should detect .py file"
        assert any("app.js" in f for f in changed_files), "Should detect .js file"
        assert any("schema.sql" in f for f in changed_files), "Should detect .sql file"


    """Test that get_changed_files handles deleted files gracefully"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Create and commit files
        file1 = os.path.join(temp_dir, "keep.py")
        file2 = os.path.join(temp_dir, "delete.py")

        with open(file1, "w") as f:
            f.write("print('keep')\\n")
        with open(file2, "w") as f:
            f.write("print('delete')\\n")

        subprocess.run(
            ["git", "add", "."], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Delete one file and modify the other
        os.remove(file2)
        with open(file1, "a") as f:
            f.write("print('modified')\\n")

        changed_files = checker.get_changed_files(repo_path=temp_dir)

        # Should only include the file that still exists
        assert any("keep.py" in f for f in changed_files), "Should detect modified file"
        assert not any("delete.py" in f for f in changed_files), (
            "Should not include deleted file"
        )


    """
    This is expected behavior given the current strict template matching implementation.

    See README.md "Known Issues and Limitations" for workarounds.
    """
    content = "def hello():\n    pass\n"

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
        f.write(content)
        temp_file = f.name

    # Create first template
    template_content_v1 = """[.py]
"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write(template_content_v1)
        template_file_v1 = f.name

    try:
        has_notice, was_modified = checker1.check_file(temp_file, auto_fix=True)
        assert has_notice is True
        assert was_modified is True

        # Read content after first run
        with open(temp_file, "r", encoding="utf-8") as f:
            content_v1 = f.read()

        assert "Company A" in content_v1
        template_content_v2 = """[.py]
"""

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write(template_content_v2)
            template_file_v2 = f.name

        try:
            # Second run with new template - creates duplicate (known limitation)
            has_notice, was_modified = checker2.check_file(temp_file, auto_fix=True)

            # Read content after second run
            with open(temp_file, "r", encoding="utf-8") as f:
                content_v2 = f.read()

            # Known limitation: strict template matching creates duplicates
            )
            lines = content_v2.split("\n")
            assert "Company B" in lines[0] or "Company B" in lines[1], (
            )
        finally:
            os.unlink(template_file_v2)
    finally:
        os.unlink(temp_file)
        os.unlink(template_file_v1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
