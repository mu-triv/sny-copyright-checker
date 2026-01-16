# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

"""Tests to ensure checker doesn't break files with copyright text in code/strings"""

import os
import tempfile
import pytest
from scripts.copyright_checker import CopyrightChecker


class TestCopyrightInCode:
    """Test that copyright checker doesn't break files with copyright text in code"""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def copyright_template(self, temp_dir):
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

    def test_copyright_in_string_literal(self, temp_dir, copyright_template):
        """Test that copyright text in string literals is preserved"""
        test_file = os.path.join(temp_dir, "test.py")
        content = """# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

def get_copyright():
    return "Copyright 2024 Some Company"

TEST_DATA = '''
# Copyright 2023 Test Company
# This is test data
'''
"""
        with open(test_file, "w") as f:
            f.write(content)

        original_content = content

        checker = CopyrightChecker(copyright_template)
        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        # Should be valid and not modified
        assert has_notice is True
        assert was_modified is False

        # Content should be unchanged
        with open(test_file, "r") as f:
            result = f.read()

        assert result == original_content
        assert "Copyright 2024 Some Company" in result
        assert "Copyright 2023 Test Company" in result

    def test_copyright_in_docstring(self, temp_dir, copyright_template):
        """Test that copyright text in docstrings is preserved"""
        test_file = os.path.join(temp_dir, "test.py")
        content = """# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

def example():
    \"\"\"
    Example function.
    
    Copyright 2020 Example Corp
    Author: John Doe
    License: MIT
    \"\"\"
    pass
"""
        with open(test_file, "w") as f:
            f.write(content)

        original_content = content

        checker = CopyrightChecker(copyright_template)
        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is False

        with open(test_file, "r") as f:
            result = f.read()

        assert result == original_content
        assert "Copyright 2020 Example Corp" in result

    def test_copyright_in_test_data(self, temp_dir, copyright_template):
        """Test that copyright text in test data is preserved"""
        test_file = os.path.join(temp_dir, "test.py")
        content = """# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

def test_duplicate_copyrights():
    test_content = \"\"\"# Copyright 2025 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation

# Copyright 2024 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation

code = 1
\"\"\"
    # Test code here
    pass
"""
        with open(test_file, "w") as f:
            f.write(content)

        original_content = content

        checker = CopyrightChecker(copyright_template)
        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is False

        with open(test_file, "r") as f:
            result = f.read()

        # The copyright in test data should be preserved
        assert result == original_content
        assert result.count("# Copyright 2025 Sony Group Corporation") == 1
        assert result.count("# Copyright 2024 Sony Group Corporation") == 1

    def test_multiple_copyright_patterns_in_code(self, temp_dir, copyright_template):
        """Test files with many copyright-like patterns in code"""
        test_file = os.path.join(temp_dir, "test.py")
        content = """# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

COPYRIGHT_NOTICES = [
    "# Copyright 2020 Company A",
    "# Copyright 2021 Company B",
    "# Copyright 2022 Company C",
    "# Copyright 2023 Company D",
    "# Copyright 2024 Company E",
]

def process_copyright(text):
    if "copyright" in text.lower():
        return "# Copyright processed"
    return text
"""
        with open(test_file, "w") as f:
            f.write(content)

        original_content = content

        checker = CopyrightChecker(copyright_template)
        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is False

        with open(test_file, "r") as f:
            result = f.read()

        assert result == original_content
        assert all(year in result for year in ["2020", "2021", "2022", "2023", "2024"])

    def test_copyright_in_comments_mid_file(self, temp_dir, copyright_template):
        """Test that copyright-like comments in the middle of file are preserved"""
        test_file = os.path.join(temp_dir, "test.py")
        content = """# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

import sys

# This section is based on code from Project X
# Copyright 2019 Project X Contributors
# Used under BSD License

def important_function():
    pass

# Legacy code
# Copyright 2015 Old Company
# Author: Legacy Team
def old_function():
    pass
"""
        with open(test_file, "w") as f:
            f.write(content)

        original_content = content

        checker = CopyrightChecker(copyright_template)
        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is False

        with open(test_file, "r") as f:
            result = f.read()

        assert result == original_content
        assert "Copyright 2019 Project X Contributors" in result
        assert "Copyright 2015 Old Company" in result

    def test_copyright_in_variable_assignment(self, temp_dir, copyright_template):
        """Copyright text in variable assignments should be preserved"""
        test_file = os.path.join(temp_dir, "test.py")
        content = """# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

copyright_holder = "Copyright 2023 Some Company"
license_info = "Copyright (c) 2022 Another Corp"
notice = "See Copyright file"

def get_info():
    return copyright_holder
"""
        with open(test_file, "w") as f:
            f.write(content)

        original_content = content
        checker = CopyrightChecker(copyright_template)
        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        with open(test_file, "r") as f:
            result = f.read()

        assert result == original_content
        assert 'copyright_holder = "Copyright 2023 Some Company"' in result

    def test_negative_actual_duplicate_in_header(self, temp_dir, copyright_template):
        """NEGATIVE: Actual duplicate copyrights in header SHOULD be removed"""
        test_file = os.path.join(temp_dir, "test.py")
        content = """# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

def code():
    pass
"""
        with open(test_file, "w") as f:
            f.write(content)

        checker = CopyrightChecker(copyright_template)
        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        with open(test_file, "r") as f:
            result = f.read()

        # Should remove the duplicate
        assert was_modified is True
        assert result.count("# Copyright 2026 Sony Group Corporation") == 1

    def test_copyright_after_shebang_and_imports(self, temp_dir, copyright_template):
        """Copyright text after shebang and imports should be preserved"""
        test_file = os.path.join(temp_dir, "test.py")
        content = """#!/usr/bin/env python
import os
import sys

# This module handles copyright
# Copyright info in LICENSE file

def main():
    pass
"""
        with open(test_file, "w") as f:
            f.write(content)

        checker = CopyrightChecker(copyright_template)
        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        with open(test_file, "r") as f:
            result = f.read()

        # Should add copyright after shebang but preserve the comment
        assert "Copyright info in LICENSE file" in result
        assert result.startswith("#!/usr/bin/env python")

    def test_file_with_many_blank_lines(self, temp_dir, copyright_template):
        """File with many blank lines at top should work correctly"""
        test_file = os.path.join(temp_dir, "test.py")
        content = """


def function():
    pass
"""
        with open(test_file, "w") as f:
            f.write(content)

        checker = CopyrightChecker(copyright_template)
        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        with open(test_file, "r") as f:
            result = f.read()

        # Should add copyright and preserve the code
        assert "R&D Center Europe Brussels Laboratory" in result
        assert "def function():" in result
        assert was_modified is True
