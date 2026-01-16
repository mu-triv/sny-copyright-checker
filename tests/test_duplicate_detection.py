# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

import os
import tempfile
from pathlib import Path

import pytest


class TestDuplicateDetection:
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
        template_content = """[VARIABLES]
COMPANY = Sony Group Corporation

[.py]
[.yaml]
"""
        with open(template_path, "w") as f:
            f.write(template_content)
        return template_path

        test_file = os.path.join(temp_dir, "test.py")
print("test")
"""
        with open(test_file, "w") as f:
            f.write(content)

        has_valid, was_modified = checker.check_file(test_file, auto_fix=False)

        # Should detect duplicates but not fix without auto_fix
        assert not has_valid
        assert not was_modified

        test_file = os.path.join(temp_dir, "test.py")
print("test")
"""
        with open(test_file, "w") as f:
            f.write(content)

        has_valid, was_modified = checker.check_file(test_file, auto_fix=True)

        # Should detect and fix duplicates
        assert has_valid
        assert was_modified

        with open(test_file, "r") as f:
            result = f.read()

        test_file = os.path.join(temp_dir, "test.py")
print("test")
"""
        with open(test_file, "w") as f:
            f.write(content)

        has_valid, was_modified = checker.check_file(test_file, auto_fix=True)

        # Should detect and fix duplicates
        assert has_valid
        assert was_modified

        with open(test_file, "r") as f:
            result = f.read()

        test_file = os.path.join(temp_dir, "test.yaml")
name: Test Workflow
"""
        with open(test_file, "w") as f:
            f.write(content)

        has_valid, was_modified = checker.check_file(test_file, auto_fix=True)

        # Should detect and remove the incomplete duplicate
        assert has_valid
        assert was_modified

        with open(test_file, "r") as f:
            result = f.read()

        test_file = os.path.join(temp_dir, "test.py")
print("test")
"""
        with open(test_file, "w") as f:
            f.write(content)

        has_valid, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_valid
        assert was_modified

        with open(test_file, "r") as f:
            result = f.read()

        """Test duplicate removal preserves shebang"""
        test_file = os.path.join(temp_dir, "test.py")
        content = """#!/usr/bin/env python
print("test")
"""
        with open(test_file, "w") as f:
            f.write(content)

        has_valid, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_valid
        assert was_modified

        with open(test_file, "r") as f:
            result = f.read()

        assert result.startswith("#!/usr/bin/env python")
        test_file = os.path.join(temp_dir, "test.py")
print("test")
"""
        with open(test_file, "w") as f:
            f.write(content)

        has_valid, was_modified = checker.check_file(test_file, auto_fix=True)

        # Should be valid and not modified
        assert has_valid
        assert not was_modified

        # Content should be unchanged
        with open(test_file, "r") as f:
            result = f.read()

        assert result == content

        test_file = os.path.join(temp_dir, "test.py")
import os

print("test")
"""
        with open(test_file, "w") as f:
            f.write(content)

        has_valid, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_valid
        assert was_modified

        with open(test_file, "r") as f:
            result = f.read()

        assert "import os" in result
        """Test that CRLF line endings are preserved during duplicate removal"""
        test_file = os.path.join(temp_dir, "test.py")
        with open(test_file, "wb") as f:
            f.write(content.encode("utf-8"))

        has_valid, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_valid
        assert was_modified

        # Verify CRLF line endings are preserved
        with open(test_file, "rb") as f:
            result = f.read()

        assert b"\r\n" in result

class TestDuplicateDetectionTemplateParser:
    """Test the template parser's duplicate detection methods"""

    def test_find_all_matches_single(self):
        """Test finding a single match"""
            extension=".py",
            lines=[
            ],
            regex_patterns=[None, None],
        )

print("test")
"""
        matches = template.find_all_matches(content)
        assert len(matches) == 1
        assert matches[0] == 0

    def test_find_all_matches_duplicates(self):
        """Test finding multiple matches"""
            extension=".py",
            lines=[
            ],
            regex_patterns=[None, None],
        )

print("test")
"""
        matches = template.find_all_matches(content)
        assert len(matches) == 2
        assert 0 in matches
        assert 3 in matches

    def test_has_duplicates_true(self):
        """Test has_duplicates returns True for duplicates"""
            extension=".py",
            regex_patterns=[None],
        )

print("test")
"""
        assert template.has_duplicates(content)

    def test_has_duplicates_false(self):
            extension=".py",
            regex_patterns=[None],
        )

print("test")
"""
        assert not template.has_duplicates(content)
