# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file


"""Integration tests for the copyright checker"""

import pytest
import tempfile
import os
import logging
import subprocess
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


def test_file_with_crlf_line_endings(temp_copyright_template):
    """Test that CRLF (Windows) line endings are preserved"""
    # Create a test file with CRLF line endings
    content = "def hello():\r\n    pass\r\n"
    
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.py') as f:
        f.write(content.encode('utf-8'))
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        assert has_notice is True
        assert was_modified is True
        
        # Read file in binary mode to check line endings
        with open(temp_file, 'rb') as f:
            updated_content = f.read().decode('utf-8')
        
        # Verify CRLF line endings are preserved
        assert '\r\n' in updated_content, "CRLF line endings should be preserved"
        assert updated_content.count('\r\n') > 0
        
        # Verify copyright was added
        assert 'Copyright' in updated_content
        assert 'SNY Group Corporation' in updated_content
    finally:
        os.unlink(temp_file)


def test_file_with_lf_line_endings(temp_copyright_template):
    """Test that LF (Unix/Linux) line endings are preserved"""
    # Create a test file with LF line endings only
    content = "def hello():\n    pass\n"
    
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.py') as f:
        f.write(content.encode('utf-8'))
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        assert has_notice is True
        assert was_modified is True
        
        # Read file in binary mode to check line endings
        with open(temp_file, 'rb') as f:
            updated_content = f.read().decode('utf-8')
        
        # Verify no CRLF, only LF
        assert '\r\n' not in updated_content, "Should not have CRLF line endings"
        assert '\n' in updated_content, "Should have LF line endings"
        
        # Verify copyright was added
        assert 'Copyright' in updated_content
        assert 'SNY Group Corporation' in updated_content
    finally:
        os.unlink(temp_file)


def test_file_with_crlf_existing_copyright(temp_copyright_template):
    """Test that files with existing copyright and CRLF endings are left unchanged"""
    # Create a test file with copyright and CRLF line endings
    content = "# Copyright 2025 SNY Group Corporation\r\n# Author: Test Author\r\n\r\ndef hello():\r\n    pass\r\n"
    
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.py') as f:
        f.write(content.encode('utf-8'))
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        # Should detect existing copyright and not modify
        assert has_notice is True
        assert was_modified is False
        
        # Read file in binary mode to check line endings
        with open(temp_file, 'rb') as f:
            updated_content = f.read().decode('utf-8')
        
        # Verify CRLF line endings are still present
        assert '\r\n' in updated_content, "CRLF line endings should be preserved"
        
        # Verify only one copyright block exists
        assert updated_content.count('Copyright') == 1
    finally:
        os.unlink(temp_file)


def test_file_with_lf_existing_copyright(temp_copyright_template):
    """Test that files with existing copyright and LF endings are left unchanged"""
    # Create a test file with copyright and LF line endings
    content = "# Copyright 2025 SNY Group Corporation\n# Author: Test Author\n\ndef hello():\n    pass\n"
    
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.py') as f:
        f.write(content.encode('utf-8'))
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        # Should detect existing copyright and not modify
        assert has_notice is True
        assert was_modified is False
        
        # Read file in binary mode to check line endings
        with open(temp_file, 'rb') as f:
            updated_content = f.read().decode('utf-8')
        
        # Verify no CRLF, only LF
        assert '\r\n' not in updated_content, "Should not have CRLF line endings"
        assert '\n' in updated_content, "Should have LF line endings"
        
        # Verify only one copyright block exists
        assert updated_content.count('Copyright') == 1
    finally:
        os.unlink(temp_file)


def test_mixed_line_endings_treated_as_crlf(temp_copyright_template):
    """Test that files with mixed line endings (containing any CRLF) are treated as CRLF files"""
    # Create a test file with mixed line endings (mostly LF but some CRLF)
    content = "def hello():\r\n    pass\n"  # First line CRLF, second LF
    
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.py') as f:
        f.write(content.encode('utf-8'))
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        assert has_notice is True
        assert was_modified is True
        
        # Read file in binary mode to check line endings
        with open(temp_file, 'rb') as f:
            updated_content = f.read().decode('utf-8')
        
        # Since original had CRLF, output should use CRLF throughout
        lines_in_copyright = updated_content.split('\n\n')[0]  # Get copyright section
        assert '\r\n' in lines_in_copyright, "Copyright should use CRLF when file had any CRLF"
    finally:
        os.unlink(temp_file)


def test_no_duplicate_copyright_when_run_twice(temp_copyright_template):
    """Test that running the checker twice doesn't create duplicate copyrights"""
    # Create a test file without copyright
    content = "def hello():\n    pass\n"
    
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.py') as f:
        f.write(content.encode('utf-8'))
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        
        # First run - should add copyright
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        assert has_notice is True
        assert was_modified is True
        
        # Read file after first run
        with open(temp_file, 'r', encoding='utf-8') as f:
            content_after_first = f.read()
        
        first_copyright_count = content_after_first.count('Copyright')
        assert first_copyright_count == 1, "Should have exactly one copyright after first run"
        
        # Second run - should detect existing copyright and not add another
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        assert has_notice is True
        assert was_modified is False, "Second run should not modify the file"
        
        # Read file after second run
        with open(temp_file, 'r', encoding='utf-8') as f:
            content_after_second = f.read()
        
        second_copyright_count = content_after_second.count('Copyright')
        assert second_copyright_count == 1, "Should still have exactly one copyright after second run"
        assert content_after_first == content_after_second, "File content should be identical after second run"
    finally:
        os.unlink(temp_file)


def test_old_year_copyright_not_replaced(temp_copyright_template):
    """Test that copyrights with old years (e.g., 2025) are not replaced with current year"""
    # Create a test file with 2025 copyright
    content = "# Copyright 2025 SNY Group Corporation\n# Author: Test Author\n\ndef hello():\n    pass\n"
    
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.py') as f:
        f.write(content.encode('utf-8'))
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        
        # Run checker
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        # Should detect existing copyright and not modify
        assert has_notice is True
        assert was_modified is False
        
        # Read file and verify
        with open(temp_file, 'r', encoding='utf-8') as f:
            updated_content = f.read()
        
        # Verify still has 2025, not replaced with 2026
        assert '2025' in updated_content, "Original year should be preserved"
        assert '2026' not in updated_content, "Should not add current year"
        assert updated_content.count('Copyright') == 1, "Should have exactly one copyright"
    finally:
        os.unlink(temp_file)


def test_multiple_runs_on_old_copyright_no_duplicates(temp_copyright_template):
    """Test that running checker multiple times on file with old copyright doesn't create duplicates"""
    # Create a test file with 2025 copyright
    content = "# Copyright 2025 SNY Group Corporation\n# Author: Test Author\n\ndef hello():\n    pass\n"
    
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.py') as f:
        f.write(content.encode('utf-8'))
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        
        original_content = content
        
        # Run checker 3 times
        for i in range(3):
            has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
            
            assert has_notice is True, f"Run {i+1}: Should detect copyright"
            assert was_modified is False, f"Run {i+1}: Should not modify file"
            
            # Read and verify
            with open(temp_file, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            assert current_content.count('Copyright') == 1, f"Run {i+1}: Should have exactly one copyright"
            assert '2025' in current_content, f"Run {i+1}: Should preserve 2025 year"
            assert '2026' not in current_content, f"Run {i+1}: Should not add 2026"
    finally:
        os.unlink(temp_file)


def test_copyright_insertion_position(temp_copyright_template):
    """Test that copyright is inserted at the correct position (beginning of file)"""
    # Create a test file without copyright
    content = "def hello():\n    return 'world'\n\nclass MyClass:\n    pass\n"
    
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.py') as f:
        f.write(content.encode('utf-8'))
        temp_file = f.name
    
    try:
        checker = CopyrightChecker(temp_copyright_template)
        has_notice, was_modified = checker.check_file(temp_file, auto_fix=True)
        
        assert has_notice is True
        assert was_modified is True
        
        # Read file and verify copyright is at the beginning
        with open(temp_file, 'r', encoding='utf-8') as f:
            updated_content = f.read()
        
        # First lines should contain copyright
        lines = updated_content.split('\n')
        assert 'Copyright' in lines[0], "First line should contain copyright"
        assert 'SNY Group Corporation' in lines[0], "First line should contain company name"
        assert 'Author:' in lines[1], "Second line should contain Author"
        
        # Original code should still be present after copyright
        assert 'def hello():' in updated_content
        assert 'class MyClass:' in updated_content
    finally:
        os.unlink(temp_file)


def test_get_changed_files_not_in_git_repo(temp_copyright_template):
    """Test that get_changed_files raises error when not in a git repository"""
    with tempfile.TemporaryDirectory() as temp_dir:
        checker = CopyrightChecker(temp_copyright_template)
        
        with pytest.raises(RuntimeError, match="Failed to get changed files from git"):
            checker.get_changed_files(repo_path=temp_dir)


def test_get_changed_files_in_git_repo(temp_copyright_template):
    """Test getting changed files from a git repository"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, check=True, capture_output=True)
        
        # Create and commit a file
        file1 = os.path.join(temp_dir, "file1.py")
        with open(file1, "w") as f:
            f.write("# Copyright 2025 SNY Group Corporation\\n# Author: Test Author\\n\\nprint('hello')\\n")
        
        subprocess.run(["git", "add", "file1.py"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=temp_dir, check=True, capture_output=True)
        
        # Create a new file (unstaged)
        file2 = os.path.join(temp_dir, "file2.py")
        with open(file2, "w") as f:
            f.write("print('new file')\\n")
        
        # Modify existing file
        with open(file1, "a") as f:
            f.write("print('modified')\\n")
        
        checker = CopyrightChecker(temp_copyright_template)
        
        # Get changed files
        changed_files = checker.get_changed_files(repo_path=temp_dir)
        
        # Should find file1.py (modified), but not file2.py (not in git yet)
        assert any("file1.py" in f for f in changed_files), "Should detect modified file1.py"


def test_get_changed_files_filters_by_extension(temp_copyright_template):
    """Test that get_changed_files only returns files with supported extensions"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, check=True, capture_output=True)
        
        # Create files with different extensions
        py_file = os.path.join(temp_dir, "test.py")
        txt_file = os.path.join(temp_dir, "test.txt")
        
        with open(py_file, "w") as f:
            f.write("print('hello')\\n")
        with open(txt_file, "w") as f:
            f.write("Some text\\n")
        
        subprocess.run(["git", "add", "."], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=temp_dir, check=True, capture_output=True)
        
        # Modify both files
        with open(py_file, "a") as f:
            f.write("print('modified')\\n")
        with open(txt_file, "a") as f:
            f.write("More text\\n")
        
        checker = CopyrightChecker(temp_copyright_template)
        changed_files = checker.get_changed_files(repo_path=temp_dir)
        
        # Should only return .py file (supported extension)
        assert any("test.py" in f for f in changed_files), "Should include .py file"
        assert not any("test.txt" in f for f in changed_files), "Should not include .txt file (unsupported extension)"


def test_get_changed_files_with_staged_changes(temp_copyright_template):
    """Test that get_changed_files detects both staged and unstaged files"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, check=True, capture_output=True)
        
        # Create and commit files
        file1 = os.path.join(temp_dir, "staged.py")
        file2 = os.path.join(temp_dir, "unstaged.py")
        
        with open(file1, "w") as f:
            f.write("print('original1')\\n")
        with open(file2, "w") as f:
            f.write("print('original2')\\n")
        
        subprocess.run(["git", "add", "."], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=temp_dir, check=True, capture_output=True)
        
        # Modify first file and stage it
        with open(file1, "a") as f:
            f.write("print('staged change')\\n")
        subprocess.run(["git", "add", "staged.py"], cwd=temp_dir, check=True, capture_output=True)
        
        # Modify second file but don't stage
        with open(file2, "a") as f:
            f.write("print('unstaged change')\\n")
        
        checker = CopyrightChecker(temp_copyright_template)
        changed_files = checker.get_changed_files(repo_path=temp_dir)
        
        # Should detect both staged and unstaged changes
        assert any("staged.py" in f for f in changed_files), "Should detect staged file"
        assert any("unstaged.py" in f for f in changed_files), "Should detect unstaged file"


def test_get_changed_files_with_new_staged_file(temp_copyright_template):
    """Test that get_changed_files detects new files that are staged"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, check=True, capture_output=True)
        
        # Create initial commit
        file1 = os.path.join(temp_dir, "existing.py")
        with open(file1, "w") as f:
            f.write("print('exists')\\n")
        subprocess.run(["git", "add", "."], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=temp_dir, check=True, capture_output=True)
        
        # Create new file and stage it
        new_file = os.path.join(temp_dir, "newfile.py")
        with open(new_file, "w") as f:
            f.write("print('new')\\n")
        subprocess.run(["git", "add", "newfile.py"], cwd=temp_dir, check=True, capture_output=True)
        
        checker = CopyrightChecker(temp_copyright_template)
        changed_files = checker.get_changed_files(repo_path=temp_dir)
        
        # Should detect new staged file
        assert any("newfile.py" in f for f in changed_files), "Should detect new staged file"


def test_get_changed_files_no_changes(temp_copyright_template):
    """Test that get_changed_files returns empty list when no changes"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, check=True, capture_output=True)
        
        # Create and commit a file
        file1 = os.path.join(temp_dir, "test.py")
        with open(file1, "w") as f:
            f.write("print('hello')\\n")
        subprocess.run(["git", "add", "."], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=temp_dir, check=True, capture_output=True)
        
        checker = CopyrightChecker(temp_copyright_template)
        changed_files = checker.get_changed_files(repo_path=temp_dir)
        
        # Should return empty list
        assert len(changed_files) == 0, "Should return no files when nothing changed"


def test_get_changed_files_in_subdirectory(temp_copyright_template):
    """Test that get_changed_files works with files in subdirectories"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, check=True, capture_output=True)
        
        # Create subdirectory with file
        subdir = os.path.join(temp_dir, "src", "utils")
        os.makedirs(subdir, exist_ok=True)
        
        file1 = os.path.join(subdir, "helper.py")
        with open(file1, "w") as f:
            f.write("print('helper')\\n")
        
        subprocess.run(["git", "add", "."], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=temp_dir, check=True, capture_output=True)
        
        # Modify the file in subdirectory
        with open(file1, "a") as f:
            f.write("print('modified')\\n")
        
        checker = CopyrightChecker(temp_copyright_template)
        changed_files = checker.get_changed_files(repo_path=temp_dir)
        
        # Should detect file in subdirectory
        assert len(changed_files) == 1, "Should detect one changed file"
        assert "helper.py" in changed_files[0], "Should detect helper.py in subdirectory"
        assert os.path.exists(changed_files[0]), "Returned path should be absolute and exist"


def test_get_changed_files_multiple_file_types(temp_copyright_template):
    """Test that get_changed_files handles multiple supported file types"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, check=True, capture_output=True)
        
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
        
        subprocess.run(["git", "add", "."], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=temp_dir, check=True, capture_output=True)
        
        # Modify all files
        with open(py_file, "a") as f:
            f.write("print('modified')\\n")
        with open(js_file, "a") as f:
            f.write("console.log('modified');\\n")
        with open(sql_file, "a") as f:
            f.write("-- comment\\n")
        
        checker = CopyrightChecker(temp_copyright_template)
        changed_files = checker.get_changed_files(repo_path=temp_dir)
        
        # Should detect all supported file types
        assert len(changed_files) == 3, f"Should detect 3 changed files, found {len(changed_files)}"
        assert any("script.py" in f for f in changed_files), "Should detect .py file"
        assert any("app.js" in f for f in changed_files), "Should detect .js file"
        assert any("schema.sql" in f for f in changed_files), "Should detect .sql file"


def test_get_changed_files_with_deleted_file(temp_copyright_template):
    """Test that get_changed_files handles deleted files gracefully"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, check=True, capture_output=True)
        
        # Create and commit files
        file1 = os.path.join(temp_dir, "keep.py")
        file2 = os.path.join(temp_dir, "delete.py")
        
        with open(file1, "w") as f:
            f.write("print('keep')\\n")
        with open(file2, "w") as f:
            f.write("print('delete')\\n")
        
        subprocess.run(["git", "add", "."], cwd=temp_dir, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=temp_dir, check=True, capture_output=True)
        
        # Delete one file and modify the other
        os.remove(file2)
        with open(file1, "a") as f:
            f.write("print('modified')\\n")
        
        checker = CopyrightChecker(temp_copyright_template)
        changed_files = checker.get_changed_files(repo_path=temp_dir)
        
        # Should only include the file that still exists
        assert any("keep.py" in f for f in changed_files), "Should detect modified file"
        assert not any("delete.py" in f for f in changed_files), "Should not include deleted file"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
