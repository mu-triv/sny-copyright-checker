"""Integration tests for the copyright checker"""

import pytest
import tempfile
import os
import logging
from pathlib import Path
from scripts.copyright_checker import CopyrightChecker


@pytest.fixture
def temp_copyright_template():
    """Create a temporary copyright template file"""
    content = """[.py]
# Copyright {regex:\\d{4}(-\\d{4})?} SNY Group Corporation
# Author: Test Author

[.sql]
-- Copyright {regex:\\d{4}(-\\d{4})?} SNY Group Corporation

[.js]
// Copyright {regex:\\d{4}(-\\d{4})?} SNY Group Corporation
// License: MIT
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    yield temp_path
    
    os.unlink(temp_path)


@pytest.fixture
def temp_simple_template():
    """Create a simple template without regex"""
    content = """[.txt]
Copyright Notice
All Rights Reserved
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    yield temp_path
    
    os.unlink(temp_path)


# ============================================================================
# POSITIVE TEST CASES - Normal expected functionality
# ============================================================================

def test_check_file_with_valid_copyright(temp_copyright_template):
    """Test checking a file that already has a valid copyright"""
    # Create a test file with copyright
    content = """# Copyright 2026 SNY Group Corporation
# Author: Test Author

def hello():
    pass
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        assert has_notice is True
        assert was_modified is False
    finally:
        os.unlink(temp_file)


def test_check_file_missing_copyright(temp_copyright_template):
    """Test checking a file missing copyright (with auto-fix)"""
    # Create a test file without copyright
    content = """def hello():
    pass
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        assert has_notice is True
        assert was_modified is True
        
        # Verify copyright was added
        with open(temp_file, 'r') as f:
            updated_content = f.read()
        
        assert 'Copyright' in updated_content
        assert 'SNY Group Corporation' in updated_content
    finally:
        os.unlink(temp_file)


def test_check_file_with_shebang(temp_copyright_template):
    """Test that shebang lines are preserved"""
    content = """#!/usr/bin/env python

def hello():
    pass
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        assert has_notice is True
        assert was_modified is True
        
        # Verify shebang is still first line
        with open(temp_file, 'r') as f:
            lines = f.readlines()
        
        assert lines[0].startswith('#!/usr/bin/env python')
        assert 'Copyright' in lines[1]
    finally:
        os.unlink(temp_file)


def test_check_file_with_year_range(temp_copyright_template):
    """Test checking a file with year range copyright"""
    content = """# Copyright 2020-2026 SNY Group Corporation
# Author: Test Author

def hello():
    pass
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        assert has_notice is True
        assert was_modified is False
    finally:
        os.unlink(temp_file)


def test_check_file_sql_extension(temp_copyright_template):
    """Test checking SQL file with correct copyright"""
    content = """-- Copyright 2026 SNY Group Corporation

SELECT * FROM users;
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sql') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        assert has_notice is True
        assert was_modified is False
    finally:
        os.unlink(temp_file)


def test_check_file_adds_copyright_to_sql(temp_copyright_template):
    """Test adding copyright to SQL file"""
    content = """SELECT * FROM users;
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sql') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        assert has_notice is True
        assert was_modified is True
        
        with open(temp_file, 'r') as f:
            updated_content = f.read()
        
        assert '-- Copyright' in updated_content
        assert 'SNY Group Corporation' in updated_content
    finally:
        os.unlink(temp_file)


def test_check_files_multiple(temp_copyright_template):
    """Test checking multiple files at once"""
    # Create test files
    file1_content = """# Copyright 2026 SNY Group Corporation
# Author: Test Author

def func1():
    pass
"""
    file2_content = """def func2():
    pass
"""
    
    temp_files = []
    
    # Create file with copyright
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write(file1_content)
        temp_files.append(f.name)
    
    # Create file without copyright
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write(file2_content)
        temp_files.append(f.name)
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        passed, failed, modified = checker.check_files(temp_files, auto_fix=True)
        
        assert len(passed) == 2
        assert len(failed) == 0
        assert len(modified) == 1  # Only second file was modified
    finally:
        for temp_file in temp_files:
            os.unlink(temp_file)


def test_get_supported_extensions(temp_copyright_template):
    """Test getting list of supported file extensions"""
    checker = CopyrightChecker(temp_copyright_template)
    extensions = checker.get_supported_extensions()
    
    assert '.py' in extensions
    assert '.sql' in extensions
    assert '.js' in extensions
    assert len(extensions) == 3


def test_check_file_without_auto_fix(temp_copyright_template):
    """Test checking file without auto-fix (report only)"""
    content = """def hello():
    pass
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=False)
        
        # Should detect missing copyright but not modify
        assert has_notice is False
        assert was_modified is False
        
        # Verify file wasn't modified
        with open(temp_file, 'r') as f:
            content_after = f.read()
        
        assert content == content_after
    finally:
        os.unlink(temp_file)


def test_check_file_adds_current_year(temp_copyright_template):
    """Test that added copyright uses current year"""
    content = """def hello():
    pass
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        assert has_notice is True
        assert was_modified is True
        
        # Verify current year is in copyright
        with open(temp_file, 'r') as f:
            updated_content = f.read()
        
        from datetime import datetime
        current_year = str(datetime.now().year)
        assert current_year in updated_content
    finally:
        os.unlink(temp_file)


def test_check_file_multiline_template(temp_copyright_template):
    """Test file with multi-line copyright template"""
    content = """// Copyright 2026 SNY Group Corporation
// License: MIT

function hello() {
    console.log('hello');
}
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.js') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
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
    with pytest.raises(FileNotFoundError, match="Copyright template file not found"):
        CopyrightChecker('/nonexistent/template.txt')


def test_init_with_invalid_template():
    """Test initializing checker with invalid template format"""
    content = """This is not a valid template
No sections here
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        with pytest.raises(ValueError, match="Failed to parse copyright template"):
            CopyrightChecker(temp_path)
    finally:
        os.unlink(temp_path)


def test_check_nonexistent_file(temp_copyright_template):
    """Test checking a file that doesn't exist"""
    checker = CopyrightChecker(temp_copyright_template)
    
    with pytest.raises(FileNotFoundError, match="Source file not found"):
        checker.check_file('/nonexistent/file.py', auto_fix=True)


def test_unsupported_extension(temp_copyright_template):
    """Test file with unsupported extension is skipped"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.xyz') as f:
        f.write("test content")
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        # Should return True (skipped, not an error) and not modified
        assert has_notice is True
        assert was_modified is False
    finally:
        os.unlink(temp_file)


def test_check_file_without_extension(temp_copyright_template):
    """Test checking file without extension"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='') as f:
        f.write("test content")
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        # Should skip file without extension
        assert has_notice is True
        assert was_modified is False
    finally:
        os.unlink(temp_file)


def test_check_binary_file(temp_copyright_template):
    """Test checking a binary file (should skip)"""
    # Create a simple binary file
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.py') as f:
        f.write(b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a')  # PNG header
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        # Should skip binary file gracefully
        assert has_notice is True
        assert was_modified is False
    finally:
        os.unlink(temp_file)


def test_check_file_wrong_copyright(temp_copyright_template):
    """Test file with incorrect copyright (different company)"""
    content = """# Copyright 2026 Another Company
# Author: Test Author

def hello():
    pass
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        # Should add correct copyright (template doesn't match)
        assert has_notice is True
        assert was_modified is True
    finally:
        os.unlink(temp_file)


def test_check_files_with_nonexistent(temp_copyright_template):
    """Test check_files with mix of valid and non-existent files"""
    # Create one valid file
    content = """def hello():
    pass
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        files = [temp_file, '/nonexistent/file.py']
        passed, failed, modified = checker.check_files(files, auto_fix=True)
        
        assert len(passed) == 1
        assert len(failed) == 1
        assert len(modified) == 1
    finally:
        os.unlink(temp_file)


def test_check_file_incomplete_copyright(temp_copyright_template):
    """Test file with incomplete copyright notice"""
    # Only first line of copyright present
    content = """# Copyright 2026 SNY Group Corporation

def hello():
    pass
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        # Template requires both lines, so this should be modified
        assert has_notice is True
        assert was_modified is True
    finally:
        os.unlink(temp_file)


# ============================================================================
# EDGE CASES - Boundary conditions and special scenarios
# ============================================================================

def test_check_empty_file(temp_copyright_template):
    """Test checking an empty file"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write("")
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        assert has_notice is True
        assert was_modified is True
        
        # Verify copyright was added
        with open(temp_file, 'r') as f:
            content = f.read()
        
        assert 'Copyright' in content
    finally:
        os.unlink(temp_file)


def test_check_file_only_whitespace(temp_copyright_template):
    """Test checking file with only whitespace"""
    content = """


    
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        assert has_notice is True
        assert was_modified is True
    finally:
        os.unlink(temp_file)


def test_check_file_shebang_with_content(temp_copyright_template):
    """Test shebang handling with immediate content"""
    content = """#!/usr/bin/env python
def hello():
    pass
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        assert has_notice is True
        assert was_modified is True
        
        # Check structure
        with open(temp_file, 'r') as f:
            lines = f.readlines()
        
        assert lines[0].startswith('#!/usr/bin/env python')
        assert 'Copyright' in ''.join(lines[1:3])
    finally:
        os.unlink(temp_file)


def test_check_file_multiple_shebangs(temp_copyright_template):
    """Test file with multiple lines starting with #! (only first should be preserved)"""
    content = """#!/usr/bin/env python
#! This is a comment

def hello():
    pass
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        assert has_notice is True
        assert was_modified is True
        
        # Copyright should be after first line (shebang)
        with open(temp_file, 'r') as f:
            content = f.read()
        
        assert content.startswith('#!/usr/bin/env python')
        assert 'Copyright' in content
        # Copyright should come before the second #! line
        assert content.index('Copyright') < content.index('#! This is a comment')
    finally:
        os.unlink(temp_file)


def test_check_file_with_utf8_bom(temp_copyright_template):
    """Test file with UTF-8 BOM"""
    content = """\ufeffdef hello():
    pass
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py', encoding='utf-8-sig') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        # Should handle BOM gracefully
        assert has_notice is True
        assert was_modified is True
    finally:
        os.unlink(temp_file)


def test_check_file_with_very_long_lines(temp_copyright_template):
    """Test file with very long lines"""
    long_line = "x = '" + "a" * 10000 + "'"
    content = f"""{long_line}
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        assert has_notice is True
        assert was_modified is True
    finally:
        os.unlink(temp_file)


def test_check_file_with_mixed_line_endings(temp_copyright_template):
    """Test file with mixed line endings (CRLF and LF)"""
    content = "# Copyright 2026 SNY Group Corporation\r\n# Author: Test Author\n\ndef hello():\r\n    pass"
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py', newline='') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        # Should handle mixed line endings
        assert has_notice is True
    finally:
        os.unlink(temp_file)


def test_check_files_empty_list(temp_copyright_template):
    """Test check_files with empty file list"""
    checker = CopyrightChecker(temp_copyright_template)
    passed, failed, modified = checker.check_files([], auto_fix=True)
    
    assert len(passed) == 0
    assert len(failed) == 0
    assert len(modified) == 0


def test_check_files_all_unsupported(temp_copyright_template):
    """Test check_files with all unsupported extensions"""
    temp_files = []
    
    for ext in ['.xyz', '.abc', '.def']:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=ext) as f:
            f.write("content")
            temp_files.append(f.name)
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        passed, failed, modified = checker.check_files(temp_files, auto_fix=True)
        
        # All should pass (skipped) with no modifications
        assert len(passed) == 3
        assert len(failed) == 0
        assert len(modified) == 0
    finally:
        for temp_file in temp_files:
            os.unlink(temp_file)


def test_check_file_preserves_exact_content(temp_copyright_template):
    """Test that check_file preserves file content when copyright is valid"""
    content = """# Copyright 2026 SNY Group Corporation
# Author: Test Author

def hello():
    print("world")
    return 42

class MyClass:
    pass
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        assert has_notice is True
        assert was_modified is False
        
        # Verify content is unchanged
        with open(temp_file, 'r') as f:
            content_after = f.read()
        
        assert content == content_after
    finally:
        os.unlink(temp_file)


def test_check_file_single_line(temp_copyright_template):
    """Test file with single line of code"""
    content = """print('hello')"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        assert has_notice is True
        assert was_modified is True
        
        # Verify copyright was added and code preserved
        with open(temp_file, 'r') as f:
            updated = f.read()
        
        assert 'Copyright' in updated
        assert "print('hello')" in updated
    finally:
        os.unlink(temp_file)


def test_check_file_copyright_at_wrong_position(temp_copyright_template):
    """Test file with copyright in middle instead of at top"""
    content = """def hello():
    pass

# Copyright 2026 SNY Group Corporation
# Author: Test Author

def world():
    pass
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        # Should find copyright notice at middle position
        assert has_notice is True
        assert was_modified is False
    finally:
        os.unlink(temp_file)


def test_check_file_adds_blank_lines_properly(temp_copyright_template):
    """Test that copyright is added with proper spacing"""
    content = """def hello():
    pass
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        assert has_notice is True
        assert was_modified is True
        
        # Check spacing
        with open(temp_file, 'r') as f:
            lines = f.readlines()
        
        # Should have copyright, blank line, then code
        copyright_end = None
        for i, line in enumerate(lines):
            if 'Author: Test Author' in line:
                copyright_end = i
                break
        
        assert copyright_end is not None
        # Check there's a blank line after copyright
        if copyright_end + 1 < len(lines):
            assert lines[copyright_end + 1].strip() == ''
    finally:
        os.unlink(temp_file)


def test_check_file_with_readonly_permission_error(temp_copyright_template):
    """Test handling of file permission errors"""
    content = """def hello():
    pass
"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write(content)
        temp_file = f.name
    
    try:
        # Make file read-only
        os.chmod(temp_file, 0o444)
        
        checker = CopyrightChecker(temp_copyright_template)
        
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
    checker = CopyrightChecker(temp_simple_template)
    extensions = checker.get_supported_extensions()
    
    assert '.txt' in extensions
    assert len(extensions) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
