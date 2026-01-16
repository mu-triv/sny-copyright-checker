# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

"""Tests for duplicate copyright notice detection and removal"""

import os
import tempfile

import pytest

from scripts.copyright_checker import CopyrightChecker


class TestDuplicateDetection:
    """Test suite for duplicate copyright detection"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def copyright_template(self, temp_dir):
        """Create a basic copyright template file"""
        template_content = """[VARIABLES]
SPDX_LICENSE = MIT
COMPANY = Sony Group Corporation

[.py]
# SPDX-License-Identifier: {SPDX_LICENSE}
# Copyright {regex:\\d{4}(-\\d{4})?} {COMPANY}
# Author: R&D Center Europe Brussels Laboratory, {COMPANY}
# License: For licensing see the License.txt file

[.yaml]
# SPDX-License-Identifier: {SPDX_LICENSE}
# Copyright {regex:\\d{4}(-\\d{4})?} {COMPANY}
# Author: R&D Center Europe Brussels Laboratory, {COMPANY}
# License: For licensing see the License.txt file
"""
        template_path = os.path.join(temp_dir, "copyright.txt")
        with open(template_path, "w") as f:
            f.write(template_content)
        return template_path

    def test_detect_duplicate_copyrights_exact(self, temp_dir, copyright_template):
        """Test detection of exact duplicate copyright notices"""
        test_file = os.path.join(temp_dir, "test.py")
        content = """# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

print("test")
"""
        with open(test_file, "w") as f:
            f.write(content)

        checker = CopyrightChecker(copyright_template)
        has_valid, was_modified = checker.check_file(test_file, auto_fix=False)

        # Should detect duplicates but not fix without auto_fix
        assert not has_valid
        assert not was_modified

    def test_remove_duplicate_copyrights_exact(self, temp_dir, copyright_template):
        """Test removal of exact duplicate copyright notices"""
        test_file = os.path.join(temp_dir, "test.py")
        content = """# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

print("test")
"""
        with open(test_file, "w") as f:
            f.write(content)

        checker = CopyrightChecker(copyright_template)
        has_valid, was_modified = checker.check_file(test_file, auto_fix=True)

        # Should detect and fix duplicates
        assert has_valid
        assert was_modified

        # Verify only one copyright remains
        with open(test_file, "r") as f:
            result = f.read()

        # Count occurrences of the copyright line
        copyright_count = result.count("# Copyright 2026 Sony Group Corporation")
        assert copyright_count == 1, f"Expected 1 copyright, found {copyright_count}"

    def test_remove_duplicate_with_different_years(self, temp_dir, copyright_template):
        """Test removal when duplicate copyrights have different years"""
        test_file = os.path.join(temp_dir, "test.py")
        content = """# SPDX-License-Identifier: MIT
# Copyright 2025 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

print("test")
"""
        with open(test_file, "w") as f:
            f.write(content)

        checker = CopyrightChecker(copyright_template)
        has_valid, was_modified = checker.check_file(test_file, auto_fix=True)

        # Should detect and fix duplicates
        assert has_valid
        assert was_modified

        # Verify only one copyright remains
        with open(test_file, "r") as f:
            result = f.read()

        assert "# Copyright" in result
        copyright_count = result.count("# Copyright")
        assert copyright_count == 1

    def test_remove_duplicate_incomplete_copyright(self, temp_dir, copyright_template):
        """Test removal when one copyright is incomplete (like code-quality.yaml issue)"""
        test_file = os.path.join(temp_dir, "test.yaml")
        content = """# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

# Copyright 2025 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file
#
name: Test Workflow
"""
        with open(test_file, "w") as f:
            f.write(content)

        checker = CopyrightChecker(copyright_template)
        has_valid, was_modified = checker.check_file(test_file, auto_fix=True)

        # Should detect and remove the incomplete duplicate
        assert has_valid
        assert was_modified

        # Verify only the complete copyright remains
        with open(test_file, "r") as f:
            result = f.read()

        assert "# SPDX-License-Identifier: MIT" in result
        assert result.count("# Copyright") == 1
        assert "# Copyright 2026 Sony Group Corporation" in result
        assert "# Copyright 2025 Sony Group Corporation" not in result

    def test_three_duplicate_copyrights(self, temp_dir, copyright_template):
        """Test removal when there are 3 copyright notices"""
        test_file = os.path.join(temp_dir, "test.py")
        content = """# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

print("test")
"""
        with open(test_file, "w") as f:
            f.write(content)

        checker = CopyrightChecker(copyright_template)
        has_valid, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_valid
        assert was_modified

        # Verify only the first copyright remains
        with open(test_file, "r") as f:
            result = f.read()

        assert result.count("# Copyright") == 1
        assert "# Copyright 2026 Sony Group Corporation" in result

    def test_duplicate_with_shebang(self, temp_dir, copyright_template):
        """Test duplicate removal preserves shebang"""
        test_file = os.path.join(temp_dir, "test.py")
        content = """#!/usr/bin/env python
print("test")
"""
        with open(test_file, "w") as f:
            f.write(content)

        checker = CopyrightChecker(copyright_template)
        has_valid, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_valid
        assert was_modified

        # Verify shebang is preserved and only one copyright remains
        with open(test_file, "r") as f:
            result = f.read()

        assert result.startswith("#!/usr/bin/env python")
        assert result.count("# Copyright") == 1
        assert "# Copyright 2026 Sony Group Corporation" in result

    def test_no_duplicates_unchanged(self, temp_dir, copyright_template):
        """Test that file with single copyright is not modified"""
        test_file = os.path.join(temp_dir, "test.py")
        content = """# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

print("test")
"""
        with open(test_file, "w") as f:
            f.write(content)

        checker = CopyrightChecker(copyright_template)
        has_valid, was_modified = checker.check_file(test_file, auto_fix=True)

        # Should be valid and not modified
        assert has_valid
        assert not was_modified

        # Content should be unchanged
        with open(test_file, "r") as f:
            result = f.read()

        assert result == content

    def test_duplicate_detection_with_code_between(self, temp_dir, copyright_template):
        """Test detection when there's code between duplicate copyrights"""
        test_file = os.path.join(temp_dir, "test.py")
        content = """# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

import os

# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

print("test")
"""
        with open(test_file, "w") as f:
            f.write(content)

        checker = CopyrightChecker(copyright_template)
        has_valid, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_valid
        assert was_modified

        # Verify code is preserved and only first copyright remains
        with open(test_file, "r") as f:
            result = f.read()

        assert "import os" in result
        assert result.count("# Copyright") == 1
        assert "# Copyright 2026 Sony Group Corporation" in result

    def test_duplicate_preserves_line_endings_crlf(self, temp_dir, copyright_template):
        """Test that CRLF line endings are preserved during duplicate removal"""
        test_file = os.path.join(temp_dir, "test.py")
        content = "# SPDX-License-Identifier: MIT\r\n# Copyright 2026 Sony Group Corporation\r\n# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation\r\n# License: For licensing see the License.txt file\r\n\r\n# SPDX-License-Identifier: MIT\r\n# Copyright 2025 Sony Group Corporation\r\n# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation\r\n# License: For licensing see the License.txt file\r\n\r\nprint('test')\r\n"

        with open(test_file, "wb") as f:
            f.write(content.encode("utf-8"))

        checker = CopyrightChecker(copyright_template)
        has_valid, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_valid
        assert was_modified

        # Verify CRLF line endings are preserved
        with open(test_file, "rb") as f:
            result = f.read()

        assert b"\r\n" in result
        assert result.count(b"# Copyright") == 1


class TestDuplicateDetectionTemplateParser:
    """Test the template parser's duplicate detection methods"""

    def test_find_all_matches_single(self):
        """Test finding a single match"""
        from scripts.copyright_template_parser import CopyrightTemplate

        template = CopyrightTemplate(
            extension=".py",
            lines=[
                "# SPDX-License-Identifier: MIT",
                "# Copyright 2026 Sony",
            ],
            regex_patterns=[None, None],
        )

        content = """# SPDX-License-Identifier: MIT
# Copyright 2026 Sony

print("test")
"""
        matches = template.find_all_matches(content)
        assert len(matches) == 1
        assert matches[0] == 0

    def test_find_all_matches_duplicates(self):
        """Test finding multiple matches"""
        from scripts.copyright_template_parser import CopyrightTemplate

        template = CopyrightTemplate(
            extension=".py",
            lines=[
                "# SPDX-License-Identifier: MIT",
                "# Copyright 2026 Sony",
            ],
            regex_patterns=[None, None],
        )

        content = """# SPDX-License-Identifier: MIT
# Copyright 2026 Sony

# SPDX-License-Identifier: MIT
# Copyright 2026 Sony

print("test")
"""
        matches = template.find_all_matches(content)
        assert len(matches) == 2
        assert 0 in matches
        assert 3 in matches

    def test_has_duplicates_true(self):
        """Test has_duplicates returns True for duplicates"""
        from scripts.copyright_template_parser import CopyrightTemplate

        template = CopyrightTemplate(
            extension=".py",
            lines=["# Copyright 2026 Sony"],
            regex_patterns=[None],
        )

        content = """# Copyright 2026 Sony
# Copyright 2026 Sony
print("test")
"""
        assert template.has_duplicates(content)

    def test_has_duplicates_false(self):
        """Test has_duplicates returns False for single copyright"""
        from scripts.copyright_template_parser import CopyrightTemplate

        template = CopyrightTemplate(
            extension=".py",
            lines=["# Copyright 2026 Sony"],
            regex_patterns=[None],
        )

        content = """# Copyright 2026 Sony
print("test")
"""
        assert not template.has_duplicates(content)


class TestStringLiteralHandling:
    """Test suite to ensure copyright checker doesn't modify string literals"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def copyright_template(self, temp_dir):
        """Create a basic copyright template file"""
        template_content = """[VARIABLES]
SPDX_LICENSE = MIT
COMPANY = Sony Group Corporation

[.py]
# SPDX-License-Identifier: {SPDX_LICENSE}
# Copyright {regex:\\d{4}(-\\d{4})?} {COMPANY}
# Author: R&D Center Europe Brussels Laboratory, {COMPANY}
# License: For licensing see the License.txt file
"""
        template_path = os.path.join(temp_dir, "copyright.txt")
        with open(template_path, "w") as f:
            f.write(template_content)
        return template_path

    def test_string_literal_not_modified_simple(self, temp_dir, copyright_template):
        """Test that copyright text in string literals is not modified"""
        test_file = os.path.join(temp_dir, "test.py")
        content = """# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

def test_function():
    test_data = \"\"\"# SPDX-License-Identifier: MIT
# Copyright 2025 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

print("test")
\"\"\"
    return test_data
"""
        with open(test_file, "w") as f:
            f.write(content)

        checker = CopyrightChecker(copyright_template)
        has_valid, was_modified = checker.check_file(test_file, auto_fix=True)

        # Should be valid and not modified (string literal should be preserved)
        assert has_valid
        assert not was_modified

        # Verify string literal was not touched
        with open(test_file, "r") as f:
            result = f.read()

        # Count copyright notices - should still have 2 (one real, one in string)
        assert result.count("# Copyright 2026 Sony Group Corporation") == 1
        assert result.count("# Copyright 2025 Sony Group Corporation") == 1
        assert 'test_data = """' in result

    def test_string_literal_with_duplicate_real_copyright(
        self, temp_dir, copyright_template
    ):
        """Test that real duplicates are removed but string literals are preserved"""
        test_file = os.path.join(temp_dir, "test.py")
        content = """# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

def test_function():
    test_data = \"\"\"# SPDX-License-Identifier: MIT
# Copyright 2024 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

print("test")
\"\"\"
    return test_data
"""
        with open(test_file, "w") as f:
            f.write(content)

        checker = CopyrightChecker(copyright_template)
        has_valid, was_modified = checker.check_file(test_file, auto_fix=True)

        # Should remove duplicate but preserve string literal
        assert has_valid
        assert was_modified

        with open(test_file, "r") as f:
            result = f.read()

        # Should have only ONE real copyright at the top
        lines = result.split("\n")
        real_copyright_count = 0
        in_string = False

        for line in lines:
            if '"""' in line:
                in_string = not in_string
            if not in_string and "# Copyright 2026 Sony Group Corporation" in line:
                real_copyright_count += 1

        assert real_copyright_count == 1, (
            f"Expected 1 real copyright, found {real_copyright_count}"
        )

        # String literal should still be there
        assert "# Copyright 2024 Sony Group Corporation" in result
        assert 'test_data = """' in result

    def test_multiple_string_literals_preserved(self, temp_dir, copyright_template):
        """Test that multiple string literals with copyright text are all preserved"""
        test_file = os.path.join(temp_dir, "test.py")
        content = """# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

def test1():
    data1 = \"\"\"# Copyright 2020 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
\"\"\"
    return data1

def test2():
    data2 = '''# Copyright 2021 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
'''
    return data2
"""
        with open(test_file, "w") as f:
            f.write(content)

        checker = CopyrightChecker(copyright_template)
        has_valid, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_valid
        assert not was_modified

        with open(test_file, "r") as f:
            result = f.read()

        # Both string literals should be preserved
        assert "# Copyright 2020 Sony Group Corporation" in result
        assert "# Copyright 2021 Sony Group Corporation" in result
        assert "data1 =" in result
        assert "data2 =" in result

    def test_single_line_string_not_confused(self, temp_dir, copyright_template):
        """Test that single-line strings don't affect duplicate detection"""
        test_file = os.path.join(temp_dir, "test.py")
        content = """# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

message = "Copyright 2026 Sony Group Corporation"
another = '''short string'''
print("Copyright notice")
"""
        with open(test_file, "w") as f:
            f.write(content)

        checker = CopyrightChecker(copyright_template)
        has_valid, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_valid
        assert not was_modified

        with open(test_file, "r") as f:
            result = f.read()

        # Original content should be unchanged
        assert result == content

    def test_nested_strings_handled_correctly(self, temp_dir, copyright_template):
        """Test handling of strings within strings"""
        test_file = os.path.join(temp_dir, "test.py")
        content = """# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

def test():
    code = \"\"\"
def another():
    s = '''# Copyright 2020 Sony Group Corporation'''
    return s
\"\"\"
    return code
"""
        with open(test_file, "w") as f:
            f.write(content)

        checker = CopyrightChecker(copyright_template)
        has_valid, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_valid
        assert not was_modified

        with open(test_file, "r") as f:
            result = f.read()

        # Content should be preserved
        assert "# Copyright 2020 Sony Group Corporation" in result
        assert "code =" in result
