#!/usr/bin/env python
# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

"""Tests for the init wizard functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from scripts.init_wizard import (
    generate_copyright_template,
    COPYRIGHT_TEMPLATES,
    EXTENSION_GROUPS,
)


class TestGenerateCopyrightTemplate:
    """Test copyright template generation."""

    def test_mit_license_basic(self):
        """Test MIT license template generation with basic options."""
        template = generate_copyright_template(
            license_type="mit",
            company="Test Company",
            author="Test Author",
            spdx_license=None,
            license_notice=None,
            extensions=[".py", ".js"],
            include_author=True
        )

        assert "[VARIABLES]" in template
        assert "SPDX_LICENSE = MIT" in template
        assert "COMPANY = Test Company" in template
        assert "AUTHOR = Test Author" in template
        assert "YEAR_PATTERN = {regex:\\d{4}(-\\d{4})?}" in template
        assert "[.py]" in template or "[.js, .py]" in template or "[.py, .js]" in template
        assert "# SPDX-License-Identifier: {SPDX_LICENSE}" in template
        assert "# Copyright {YEAR_PATTERN} {COMPANY}" in template

    def test_proprietary_license(self):
        """Test proprietary license template generation."""
        template = generate_copyright_template(
            license_type="proprietary",
            company="Secret Corp",
            author=None,
            spdx_license=None,
            license_notice=None,
            extensions=[".py"],
            include_author=False
        )

        assert "SPDX_LICENSE = PROPRIETARY" in template
        assert "COMPANY = Secret Corp" in template
        assert "AUTHOR" not in template
        assert "All rights reserved" in template

    def test_custom_license(self):
        """Test custom license with user-provided values."""
        template = generate_copyright_template(
            license_type="custom",
            company="Custom Inc",
            author="Dev Team",
            spdx_license="Custom-1.0",
            license_notice="Custom license text",
            extensions=[".py"],
            include_author=True
        )

        assert "SPDX_LICENSE = Custom-1.0" in template
        assert "COMPANY = Custom Inc" in template
        assert "AUTHOR = Dev Team" in template
        assert "LICENSE_NOTICE = Custom license text" in template

    def test_multiple_file_extensions(self):
        """Test template with multiple file extensions."""
        template = generate_copyright_template(
            license_type="mit",
            company="Multi Corp",
            author="Team",
            spdx_license=None,
            license_notice=None,
            extensions=[".py", ".js", ".c", ".java", ".sql"],
            include_author=True
        )

        # Should have sections for different comment styles
        assert "# SPDX-License-Identifier" in template  # Python
        assert "// SPDX-License-Identifier" in template  # JavaScript
        assert "-- SPDX-License-Identifier" in template  # SQL
        assert "/*" in template  # C/Java block comments

    def test_c_cpp_block_comment(self):
        """Test C/C++ block comment style."""
        template = generate_copyright_template(
            license_type="mit",
            company="C Corp",
            author="C Team",
            spdx_license=None,
            license_notice=None,
            extensions=[".c", ".h", ".cpp"],
            include_author=True
        )

        assert "/**************************************************************************" in template
        assert "* SPDX-License-Identifier: {SPDX_LICENSE}" in template
        assert "**************************************************************************/" in template

    def test_java_block_comment(self):
        """Test Java block comment style."""
        template = generate_copyright_template(
            license_type="apache",
            company="Java Corp",
            author="Java Team",
            spdx_license=None,
            license_notice=None,
            extensions=[".java"],
            include_author=True
        )

        assert "/*" in template
        assert " * SPDX-License-Identifier: {SPDX_LICENSE}" in template
        assert " */" in template
        assert "Apache-2.0" in template

    def test_xml_html_comment(self):
        """Test XML/HTML comment style."""
        template = generate_copyright_template(
            license_type="mit",
            company="Web Corp",
            author="Web Team",
            spdx_license=None,
            license_notice=None,
            extensions=[".xml", ".html", ".md"],
            include_author=True
        )

        assert "<!--" in template
        assert "-->" in template
        assert "SPDX-License-Identifier: {SPDX_LICENSE}" in template

    def test_shell_script_shebang(self):
        """Test shell script includes shebang."""
        template = generate_copyright_template(
            license_type="mit",
            company="Shell Corp",
            author="Shell Team",
            spdx_license=None,
            license_notice=None,
            extensions=[".sh"],
            include_author=True
        )

        assert "#!/bin/bash" in template
        assert "# SPDX-License-Identifier: {SPDX_LICENSE}" in template

    def test_without_author(self):
        """Test template without author field."""
        template = generate_copyright_template(
            license_type="mit",
            company="No Author Corp",
            author="Someone",
            spdx_license=None,
            license_notice=None,
            extensions=[".py"],
            include_author=False
        )

        assert "COMPANY = No Author Corp" in template
        assert "AUTHOR" not in template
        assert "Author:" not in template

    def test_without_spdx(self):
        """Test template without SPDX identifier."""
        template = generate_copyright_template(
            license_type="custom",
            company="No SPDX Corp",
            author="Team",
            spdx_license="",
            license_notice="Custom notice",
            extensions=[".py"],
            include_author=True
        )

        assert "SPDX_LICENSE" not in template
        assert "SPDX-License-Identifier" not in template
        assert "Copyright {YEAR_PATTERN} {COMPANY}" in template
        assert "LICENSE_NOTICE = Custom notice" in template


class TestInitWizardIntegration:
    """Integration tests for the init wizard."""

    @patch('scripts.init_wizard.input')
    def test_init_wizard_mit_default(self, mock_input):
        """Test init wizard with MIT license and default options."""
        from scripts.init_wizard import run_init_wizard

        # Mock user inputs
        mock_input.side_effect = [
            "",  # MIT license (default)
            "Test Company",  # Company name
            "y",  # Include author
            "Dev Team",  # Author name
            "n",  # Don't customize license
            "all",  # All extensions
            "n",  # Don't save (for test)
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "copyright.txt"
            result = run_init_wizard(str(output_path))

            # Should return 1 (cancelled at save step)
            assert result == 1
            # File should not exist since we cancelled
            assert not output_path.exists()

    @patch('scripts.init_wizard.input')
    def test_init_wizard_creates_file(self, mock_input):
        """Test that init wizard creates a valid file."""
        from scripts.init_wizard import run_init_wizard

        # Mock user inputs - complete flow
        mock_input.side_effect = [
            "mit",  # MIT license (by key)
            "My Company",  # Company name
            "y",  # Include author
            "Engineering Team",  # Author name
            "n",  # Don't customize license
            "7",  # Python only (option 7)
            "y",  # Save the file
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_copyright.txt"
            result = run_init_wizard(str(output_path))

            assert result == 0
            assert output_path.exists()

            content = output_path.read_text()
            assert "COMPANY = My Company" in content
            assert "AUTHOR = Engineering Team" in content
            assert "SPDX_LICENSE = MIT" in content
            # Python extensions should be present
            assert ".py" in content

    @patch('scripts.init_wizard.input')
    def test_init_wizard_proprietary(self, mock_input):
        """Test init wizard with proprietary license."""
        from scripts.init_wizard import run_init_wizard

        mock_input.side_effect = [
            "proprietary",  # Proprietary (by key)
            "SecretCorp Inc.",  # Company
            "n",  # No author
            "n",  # Don't customize
            "7",  # Python (option 7)
            "y",  # Save
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "copyright.txt"
            result = run_init_wizard(str(output_path))

            assert result == 0
            assert output_path.exists()

            content = output_path.read_text()
            assert "SPDX_LICENSE = PROPRIETARY" in content
            assert "COMPANY = SecretCorp Inc." in content
            assert "AUTHOR" not in content
            assert "All rights reserved" in content


class TestCopyrightTemplates:
    """Test that all predefined templates are valid."""

    def test_all_templates_defined(self):
        """Verify all expected templates exist."""
        expected = ["mit", "apache", "gpl3", "bsd3", "proprietary", "custom"]
        for template_key in expected:
            assert template_key in COPYRIGHT_TEMPLATES
            assert "name" in COPYRIGHT_TEMPLATES[template_key]
            assert "spdx" in COPYRIGHT_TEMPLATES[template_key]
            assert "description" in COPYRIGHT_TEMPLATES[template_key]

    def test_template_spdx_identifiers(self):
        """Verify SPDX identifiers are correctly formatted."""
        assert COPYRIGHT_TEMPLATES["mit"]["spdx"] == "MIT"
        assert COPYRIGHT_TEMPLATES["apache"]["spdx"] == "Apache-2.0"
        assert COPYRIGHT_TEMPLATES["gpl3"]["spdx"] == "GPL-3.0-or-later"
        assert COPYRIGHT_TEMPLATES["bsd3"]["spdx"] == "BSD-3-Clause"
        assert COPYRIGHT_TEMPLATES["proprietary"]["spdx"] == "PROPRIETARY"


class TestExtensionGroups:
    """Test extension group definitions."""

    def test_common_extensions_exist(self):
        """Verify common extension groups are defined."""
        assert "python" in EXTENSION_GROUPS
        assert "c_cpp" in EXTENSION_GROUPS
        assert "java" in EXTENSION_GROUPS
        assert "javascript" in EXTENSION_GROUPS

    def test_python_extensions(self):
        """Verify Python extensions."""
        assert ".py" in EXTENSION_GROUPS["python"]

    def test_javascript_extensions(self):
        """Verify JavaScript/TypeScript extensions."""
        js_exts = EXTENSION_GROUPS["javascript"]
        assert ".js" in js_exts
        assert ".ts" in js_exts
        assert ".jsx" in js_exts
        assert ".tsx" in js_exts

    def test_c_cpp_extensions(self):
        """Verify C/C++ extensions."""
        c_exts = EXTENSION_GROUPS["c_cpp"]
        assert ".c" in c_exts
        assert ".h" in c_exts
        assert ".cpp" in c_exts
        assert ".hpp" in c_exts


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
