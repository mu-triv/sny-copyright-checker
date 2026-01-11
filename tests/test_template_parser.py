"""Unit tests for copyright template parser"""

import pytest
import tempfile
import os
import re
from scripts.copyright_template_parser import CopyrightTemplateParser, CopyrightTemplate


# ============================================================================
# POSITIVE TEST CASES - Normal expected functionality
# ============================================================================

def test_parse_simple_template():
    """Test parsing a simple copyright template"""
    content = """[.py]
# Copyright {regex:\\d{4}(-\\d{4})?} SNY Group Corporation
# Author: Test Author
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        
        assert '.py' in templates
        template = templates['.py']
        assert template.extension == '.py'
        assert len(template.lines) == 2
        assert 'Copyright' in template.lines[0]
        assert 'Author' in template.lines[1]
    finally:
        os.unlink(temp_path)


def test_parse_multiple_sections():
    """Test parsing template with multiple sections"""
    content = """[.py]
# Copyright {regex:\\d{4}} sny

[.sql]
-- Copyright {regex:\\d{4}} sny
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        
        assert len(templates) == 2
        assert '.py' in templates
        assert '.sql' in templates
    finally:
        os.unlink(temp_path)


def test_parse_template_with_nested_braces():
    """Test parsing template with nested braces in regex pattern"""
    content = """[.py]
# Copyright {regex:\\d{4}(-\\d{4})?} sny Corporation
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        template = templates['.py']
        
        # Verify the regex pattern was correctly extracted
        assert template.regex_patterns[0] is not None
        assert template.regex_patterns[0].pattern == r'\d{4}(-\d{4})?'
    finally:
        os.unlink(temp_path)


def test_parse_template_with_multiple_extensions():
    """Test parsing template with various file extensions"""
    content = """[.py]
# Python copyright

[.js]
// JavaScript copyright

[.cpp]
// C++ copyright

[.html]
<!-- HTML copyright -->
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        
        assert len(templates) == 4
        assert '.py' in templates
        assert '.js' in templates
        assert '.cpp' in templates
        assert '.html' in templates
    finally:
        os.unlink(temp_path)


def test_template_matches_with_regex():
    """Test template matching with regex patterns"""
    content = """[.py]
# Copyright {regex:\\d{4}(-\\d{4})?} SNY Group Corporation
# Author: Test Author
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        template = templates['.py']
        
        # Test with single year
        file_content = """# Copyright 2026 SNY Group Corporation
# Author: Test Author

def main():
    pass
"""
        assert template.matches(file_content) is True
        
        # Test with year range
        file_content2 = """# Copyright 2020-2026 SNY Group Corporation
# Author: Test Author

def main():
    pass
"""
        assert template.matches(file_content2) is True
    finally:
        os.unlink(temp_path)


def test_template_matches_without_regex():
    """Test template matching with exact string match (no regex)"""
    content = """[.txt]
Copyright Notice
All rights reserved
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        template = templates['.txt']
        
        file_content = """Copyright Notice
All rights reserved

Some text content
"""
        assert template.matches(file_content) is True
        
        # Test with mismatch
        file_content2 = """Copyright Notice
Some other text
"""
        assert template.matches(file_content2) is False
    finally:
        os.unlink(temp_path)


def test_get_notice_with_year():
    """Test generating notice with specific year"""
    template = CopyrightTemplate(
        extension='.py',
        lines=['# Copyright {regex:\\d{4}} sny', '# Author: Test'],
        regex_patterns=[None, None]
    )
    
    notice = template.get_notice_with_year(2026)
    assert '2026' in notice
    assert 'Author: Test' in notice


def test_get_notice_with_year_replaces_regex():
    """Test that get_notice_with_year properly replaces regex placeholders"""
    content = """[.py]
# Copyright {regex:\\d{4}(-\\d{4})?} sny Corporation
# License: MIT
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        template = templates['.py']
        
        notice = template.get_notice_with_year(2026)
        
        assert '2026' in notice
        assert '{regex:' not in notice
        assert 'sny Corporation' in notice
        assert 'License: MIT' in notice
    finally:
        os.unlink(temp_path)


def test_parse_template_with_empty_lines():
    """Test parsing template that includes empty lines within sections"""
    content = """[.py]
# Copyright {regex:\\d{4}} sny

# This is a multi-line notice
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        template = templates['.py']
        
        # Should include the empty line in the middle
        assert len(template.lines) == 3
        assert template.lines[1] == ''
    finally:
        os.unlink(temp_path)


def test_parse_template_strips_trailing_empty_lines():
    """Test that parser removes trailing empty lines from sections"""
    content = """[.py]
# Copyright {regex:\\d{4}} sny


"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        template = templates['.py']
        
        # Trailing empty lines should be removed
        assert len(template.lines) == 1
        assert template.lines[-1] != ''
    finally:
        os.unlink(temp_path)


def test_template_matches_at_different_positions():
    """Test that template can match copyright at different positions in file"""
    content = """[.py]
# Copyright {regex:\\d{4}} sny
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        template = templates['.py']
        
        # Copyright at beginning
        file_content1 = """# Copyright 2026 sny
def main():
    pass
"""
        assert template.matches(file_content1) is True
        
        # Copyright after shebang
        file_content2 = """#!/usr/bin/env python
# Copyright 2026 sny
def main():
    pass
"""
        assert template.matches(file_content2) is True
    finally:
        os.unlink(temp_path)


# ============================================================================
# NEGATIVE TEST CASES - Error conditions and invalid inputs
# ============================================================================

def test_parse_nonexistent_file():
    """Test parsing a file that doesn't exist"""
    with pytest.raises(FileNotFoundError):
        CopyrightTemplateParser.parse('/nonexistent/path/to/file.txt')


def test_parse_empty_file():
    """Test parsing an empty template file"""
    content = ""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        with pytest.raises(ValueError, match="No valid sections found"):
            CopyrightTemplateParser.parse(temp_path)
    finally:
        os.unlink(temp_path)


def test_parse_file_without_sections():
    """Test parsing a file without any section headers"""
    content = """# Just some text
# No section headers
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        with pytest.raises(ValueError, match="No valid sections found"):
            CopyrightTemplateParser.parse(temp_path)
    finally:
        os.unlink(temp_path)


def test_parse_invalid_regex_pattern():
    """Test parsing template with invalid regex pattern"""
    content = """[.py]
# Copyright {regex:[[[invalid} sny
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        with pytest.raises(ValueError, match="Invalid regex pattern"):
            CopyrightTemplateParser.parse(temp_path)
    finally:
        os.unlink(temp_path)


def test_parse_unmatched_braces():
    """Test parsing template with unmatched braces in regex"""
    content = """[.py]
# Copyright {regex:\\d{4 sny
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        with pytest.raises(ValueError, match="Unmatched braces"):
            CopyrightTemplateParser.parse(temp_path)
    finally:
        os.unlink(temp_path)


def test_template_no_match_different_text():
    """Test that template doesn't match when text is different"""
    content = """[.py]
# Copyright {regex:\\d{4}} sny Corporation
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        template = templates['.py']
        
        # Different company name
        file_content = """# Copyright 2026 Microsoft Corporation
def main():
    pass
"""
        assert template.matches(file_content) is False
        
        # Missing copyright
        file_content2 = """def main():
    pass
"""
        assert template.matches(file_content2) is False
    finally:
        os.unlink(temp_path)


def test_template_no_match_wrong_year_format():
    """Test that template doesn't match when year format is wrong"""
    content = """[.py]
# Copyright {regex:\\d{4}} sny
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        template = templates['.py']
        
        # Wrong year format (3 digits instead of 4)
        file_content = """# Copyright 202 sny
def main():
    pass
"""
        assert template.matches(file_content) is False
        
        # No year at all
        file_content2 = """# Copyright sny
def main():
    pass
"""
        assert template.matches(file_content2) is False
    finally:
        os.unlink(temp_path)


def test_template_no_match_incomplete_lines():
    """Test that template doesn't match when file has incomplete copyright"""
    content = """[.py]
# Copyright {regex:\\d{4}} sny
# Author: Test Author
# License: MIT
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        template = templates['.py']
        
        # Only first line present
        file_content = """# Copyright 2026 sny
def main():
    pass
"""
        assert template.matches(file_content) is False
    finally:
        os.unlink(temp_path)


# ============================================================================
# EDGE CASES - Boundary conditions and special scenarios
# ============================================================================

def test_parse_section_with_only_empty_lines():
    """Test parsing a section that contains only empty lines"""
    content = """[.py]


[.sql]
-- Copyright 2026
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        
        # Empty section creates an empty template (current behavior)
        assert '.py' in templates
        assert len(templates['.py'].lines) == 0
        assert '.sql' in templates
        assert len(templates['.sql'].lines) == 1
    finally:
        os.unlink(temp_path)


def test_parse_template_with_leading_empty_lines():
    """Test parsing template with empty lines before first section"""
    content = """

[.py]
# Copyright {regex:\\d{4}} sny
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        
        assert '.py' in templates
        assert len(templates['.py'].lines) == 1
    finally:
        os.unlink(temp_path)


def test_template_matches_empty_content():
    """Test template matching against empty content"""
    template = CopyrightTemplate(
        extension='.py',
        lines=['# Copyright 2026'],
        regex_patterns=[None]
    )
    
    assert template.matches("") is False


def test_template_matches_content_shorter_than_template():
    """Test template matching when content has fewer lines than template"""
    template = CopyrightTemplate(
        extension='.py',
        lines=['# Copyright 2026', '# Author: Test', '# License: MIT'],
        regex_patterns=[None, None, None]
    )
    
    file_content = """# Copyright 2026
# Author: Test
"""
    assert template.matches(file_content) is False


def test_template_with_whitespace_variations():
    """Test template matching with various whitespace patterns"""
    content = """[.py]
# Copyright {regex:\\d{4}} sny
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        template = templates['.py']
        
        # Trailing whitespace should be handled
        file_content1 = """# Copyright 2026 sny   
def main():
    pass
"""
        assert template.matches(file_content1) is True
        
        # Tab characters
        file_content2 = """# Copyright 2026 sny\t
def main():
    pass
"""
        assert template.matches(file_content2) is True
    finally:
        os.unlink(temp_path)


def test_template_single_line():
    """Test template with only one line"""
    content = """[.py]
# Copyright {regex:\\d{4}} sny
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        template = templates['.py']
        
        assert len(template.lines) == 1
        file_content = """# Copyright 2026 sny"""
        assert template.matches(file_content) is True
    finally:
        os.unlink(temp_path)


def test_get_notice_with_year_edge_values():
    """Test get_notice_with_year with edge case year values"""
    template = CopyrightTemplate(
        extension='.py',
        lines=['# Copyright {regex:\\d{4}} sny'],
        regex_patterns=[None]
    )
    
    # Very old year
    notice1 = template.get_notice_with_year(1900)
    assert '1900' in notice1
    
    # Far future year
    notice2 = template.get_notice_with_year(9999)
    assert '9999' in notice2
    
    # Current century start
    notice3 = template.get_notice_with_year(2000)
    assert '2000' in notice3


def test_template_with_special_regex_characters():
    """Test template with special regex characters in literal text"""
    content = """[.py]
# Copyright {regex:\\d{4}} sny (R&D)
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        template = templates['.py']
        
        # Parentheses should be matched literally, not as regex groups
        file_content = """# Copyright 2026 sny (R&D)
def main():
    pass
"""
        assert template.matches(file_content) is True
        
        # Should not match without parentheses
        file_content2 = """# Copyright 2026 sny R&D
def main():
    pass
"""
        assert template.matches(file_content2) is False
    finally:
        os.unlink(temp_path)


def test_template_with_multiple_regex_patterns_per_line():
    """Test template with multiple {regex:...} patterns on one line (edge case)"""
    # This is an edge case - the current implementation only handles one regex per line
    # This test documents the current behavior
    content = """[.py]
# Copyright {regex:\\d{4}} by {regex:\\w+}
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        template = templates['.py']
        
        # Only the first regex pattern is extracted and compiled
        assert template.regex_patterns[0] is not None
    finally:
        os.unlink(temp_path)


def test_template_with_very_long_line():
    """Test template with very long copyright line"""
    long_text = "A" * 500
    content = f"""[.py]
# Copyright {{regex:\\d{{4}}}} sny - {long_text}
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        template = templates['.py']
        
        file_content = f"""# Copyright 2026 sny - {long_text}
def main():
    pass
"""
        assert template.matches(file_content) is True
    finally:
        os.unlink(temp_path)


def test_parse_section_header_variations():
    """Test various section header formats"""
    # Valid section header
    content1 = """[.py]
# Copyright 2026
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content1)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        assert '.py' in templates
    finally:
        os.unlink(temp_path)
    
    # Section header with spaces (should be valid since we strip)
    content2 = """  [.js]  
// Copyright 2026
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content2)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        assert '.js' in templates
    finally:
        os.unlink(temp_path)


def test_template_matches_with_line_endings():
    """Test template matching with different line ending styles"""
    content = """[.py]
# Copyright {regex:\\d{4}} sny
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        templates = CopyrightTemplateParser.parse(temp_path)
        template = templates['.py']
        
        # Unix line endings (LF)
        file_content_lf = "# Copyright 2026 sny\ndef main():\n    pass"
        assert template.matches(file_content_lf) is True
        
        # Windows line endings (CRLF) - will be handled as LF after split
        file_content_crlf = "# Copyright 2026 sny\r\ndef main():\r\n    pass"
        assert template.matches(file_content_crlf) is True
    finally:
        os.unlink(temp_path)


def test_template_get_notice_no_regex():
    """Test get_notice_with_year when template has no regex patterns"""
    template = CopyrightTemplate(
        extension='.txt',
        lines=['Copyright Notice', 'All rights reserved'],
        regex_patterns=[None, None]
    )
    
    notice = template.get_notice_with_year(2026)
    # Should return the template as-is since there's no {regex:...} to replace
    assert 'Copyright Notice' in notice
    assert 'All rights reserved' in notice
    assert '2026' not in notice


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
