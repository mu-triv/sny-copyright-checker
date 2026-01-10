"""Integration and system tests for the copyright checker"""

import pytest
import tempfile
import os
import subprocess
import sys
from pathlib import Path


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory with multiple files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        
        # Create copyright template
        template_content = """[.py]
# Copyright {regex:\\d{4}(-\\d{4})?} Sony Group Corporation
# Author: Test Lab

[.js]
// Copyright {regex:\\d{4}(-\\d{4})?} Sony Group Corporation

[.sql]
-- Copyright {regex:\\d{4}(-\\d{4})?} Sony Group Corporation
"""
        (project_dir / "copyright.txt").write_text(template_content)
        
        # Create test files
        (project_dir / "file1.py").write_text("def hello():\n    pass\n")
        (project_dir / "file2.py").write_text("#!/usr/bin/env python\ndef world():\n    pass\n")
        (project_dir / "file3.js").write_text("function test() {\n    console.log('test');\n}\n")
        (project_dir / "file4.sql").write_text("SELECT * FROM users;\n")
        (project_dir / "file5.txt").write_text("This is a text file\n")  # Unsupported
        
        # Create file with copyright
        with_copyright = """# Copyright 2026 Sony Group Corporation
# Author: Test Lab

def existing():
    pass
"""
        (project_dir / "with_copyright.py").write_text(with_copyright)
        
        # Create subdirectory with files
        subdir = project_dir / "subdir"
        subdir.mkdir()
        (subdir / "nested.py").write_text("def nested():\n    pass\n")
        
        yield project_dir


# ============================================================================
# CLI INTEGRATION TESTS
# ============================================================================

def test_cli_help():
    """Test CLI help message"""
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main", "--help"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert "copyright" in result.stdout.lower()
    assert "--notice" in result.stdout


def test_cli_version():
    """Test CLI version output"""
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main", "--version"],
        capture_output=True,
        text=True
    )
    
    # Should either succeed or show version info
    assert result.returncode in [0, 2]  # argparse may return 2 for --version


def test_cli_single_file_check(temp_project_dir):
    """Test CLI checking a single file without copyright"""
    file_path = temp_project_dir / "file1.py"
    template_path = temp_project_dir / "copyright.txt"
    
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main", 
         str(file_path), 
         f"--notice={template_path}"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )
    
    # Should succeed and add copyright
    assert result.returncode == 0
    
    # Verify copyright was added
    content = file_path.read_text()
    assert "Copyright" in content
    assert "Sony Group Corporation" in content


def test_cli_single_file_no_fix(temp_project_dir):
    """Test CLI checking without auto-fix"""
    file_path = temp_project_dir / "file1.py"
    template_path = temp_project_dir / "copyright.txt"
    
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main",
         str(file_path),
         f"--notice={template_path}",
         "--no-fix"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )
    
    # Should fail because copyright is missing
    assert result.returncode == 1
    
    # Verify file was NOT modified
    content = file_path.read_text()
    assert "Copyright" not in content


def test_cli_multiple_files(temp_project_dir):
    """Test CLI checking multiple files"""
    file1 = temp_project_dir / "file1.py"
    file2 = temp_project_dir / "file2.py"
    template_path = temp_project_dir / "copyright.txt"
    
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main",
         str(file1),
         str(file2),
         f"--notice={template_path}"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )
    
    assert result.returncode == 0
    
    # Both files should have copyright
    assert "Copyright" in file1.read_text()
    assert "Copyright" in file2.read_text()


def test_cli_mixed_extensions(temp_project_dir):
    """Test CLI with multiple file extensions"""
    py_file = temp_project_dir / "file1.py"
    js_file = temp_project_dir / "file3.js"
    sql_file = temp_project_dir / "file4.sql"
    template_path = temp_project_dir / "copyright.txt"
    
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main",
         str(py_file),
         str(js_file),
         str(sql_file),
         f"--notice={template_path}"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )
    
    assert result.returncode == 0
    
    # Check each file has appropriate copyright format
    py_content = py_file.read_text()
    js_content = js_file.read_text()
    sql_content = sql_file.read_text()
    
    assert py_content.startswith("# Copyright")
    assert js_content.startswith("// Copyright")
    assert sql_content.startswith("-- Copyright")


def test_cli_file_with_existing_copyright(temp_project_dir):
    """Test CLI with file that already has copyright"""
    file_path = temp_project_dir / "with_copyright.py"
    template_path = temp_project_dir / "copyright.txt"
    
    original_content = file_path.read_text()
    
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main",
         str(file_path),
         f"--notice={template_path}"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )
    
    assert result.returncode == 0
    
    # File should remain unchanged
    assert file_path.read_text() == original_content


def test_cli_unsupported_extension(temp_project_dir):
    """Test CLI with unsupported file extension"""
    file_path = temp_project_dir / "file5.txt"
    template_path = temp_project_dir / "copyright.txt"
    
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main",
         str(file_path),
         f"--notice={template_path}"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )
    
    # Should succeed (skipped files don't cause failure)
    assert result.returncode == 0


def test_cli_nonexistent_file(temp_project_dir):
    """Test CLI with non-existent file"""
    template_path = temp_project_dir / "copyright.txt"
    
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main",
         str(temp_project_dir / "nonexistent.py"),
         f"--notice={template_path}"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )
    
    # Should fail (return code 2 for FileNotFoundError or 1 for check failure)
    assert result.returncode in [1, 2]


def test_cli_nonexistent_template(temp_project_dir):
    """Test CLI with non-existent template file"""
    file_path = temp_project_dir / "file1.py"
    
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main",
         str(file_path),
         "--notice=nonexistent.txt"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )
    
    # Should fail with error (return code 2 for FileNotFoundError)
    assert result.returncode == 2
    assert "not found" in result.stderr.lower() or "not found" in result.stdout.lower()


def test_cli_verbose_output(temp_project_dir):
    """Test CLI verbose mode"""
    file_path = temp_project_dir / "file1.py"
    template_path = temp_project_dir / "copyright.txt"
    
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main",
         str(file_path),
         f"--notice={template_path}",
         "-v"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )
    
    assert result.returncode == 0
    # Verbose mode should produce more output
    assert len(result.stdout) > 0 or len(result.stderr) > 0


# ============================================================================
# END-TO-END WORKFLOW TESTS
# ============================================================================

def test_workflow_new_project_initialization(temp_project_dir):
    """Test initializing copyright notices in a new project"""
    template_path = temp_project_dir / "copyright.txt"
    
    # Process all Python files
    py_files = list(temp_project_dir.glob("**/*.py"))
    py_files = [str(f) for f in py_files if f.name != "__pycache__"]
    
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main", *py_files, f"--notice={template_path}"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )
    
    assert result.returncode == 0
    
    # All Python files should now have copyright
    for py_file in py_files:
        content = Path(py_file).read_text()
        assert "Copyright" in content or "copyright" in Path(py_file).name.lower()


def test_workflow_mixed_files_with_some_copyrights(temp_project_dir):
    """Test processing mix of files with and without copyrights"""
    template_path = temp_project_dir / "copyright.txt"
    
    files = [
        temp_project_dir / "file1.py",  # No copyright
        temp_project_dir / "with_copyright.py",  # Has copyright
        temp_project_dir / "file3.js",  # No copyright
    ]
    
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main", *[str(f) for f in files], f"--notice={template_path}"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )
    
    assert result.returncode == 0
    
    # All files should have copyright
    for file in files:
        assert "Copyright" in file.read_text()


def test_workflow_shebang_preservation(temp_project_dir):
    """Test that shebangs are preserved during processing"""
    file_path = temp_project_dir / "file2.py"
    template_path = temp_project_dir / "copyright.txt"
    
    # Verify shebang exists
    original = file_path.read_text()
    assert original.startswith("#!/usr/bin/env python")
    
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main", str(file_path), f"--notice={template_path}"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )
    
    assert result.returncode == 0
    
    # Shebang should still be first line
    updated = file_path.read_text()
    lines = updated.split("\n")
    assert lines[0] == "#!/usr/bin/env python"
    assert "Copyright" in updated


def test_workflow_directory_structure_preserved(temp_project_dir):
    """Test that directory structure is preserved"""
    nested_file = temp_project_dir / "subdir" / "nested.py"
    template_path = temp_project_dir / "copyright.txt"
    
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main", str(nested_file), f"--notice={template_path}"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )
    
    assert result.returncode == 0
    assert nested_file.exists()
    assert "Copyright" in nested_file.read_text()


# ============================================================================
# PRE-COMMIT SIMULATION TESTS
# ============================================================================

def test_precommit_simulation_all_files_valid(temp_project_dir):
    """Simulate pre-commit hook with all files having copyright"""
    template_path = temp_project_dir / "copyright.txt"
    
    # First pass - add copyrights
    files = [temp_project_dir / "file1.py", temp_project_dir / "file2.py"]
    subprocess.run(
        [sys.executable, "-m", "scripts.main", *[str(f) for f in files], f"--notice={template_path}"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )
    
    # Second pass - check mode (simulate pre-commit check)
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main", *[str(f) for f in files], f"--notice={template_path}"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )
    
    # Should pass (all files have copyright)
    assert result.returncode == 0


def test_precommit_simulation_some_files_invalid(temp_project_dir):
    """Simulate pre-commit hook with some files missing copyright"""
    template_path = temp_project_dir / "copyright.txt"
    
    files = [
        temp_project_dir / "file1.py",  # No copyright
        temp_project_dir / "with_copyright.py",  # Has copyright
    ]
    
    # Check mode - should fail because file1.py has no copyright
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main",
         *[str(f) for f in files],
         f"--notice={template_path}",
         "--no-fix"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )
    
    # Should fail
    assert result.returncode == 1


def test_precommit_simulation_auto_fix(temp_project_dir):
    """Simulate pre-commit hook with auto-fix enabled"""
    template_path = temp_project_dir / "copyright.txt"
    file_path = temp_project_dir / "file1.py"
    
    # Auto-fix mode
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main",
         str(file_path),
         f"--notice={template_path}"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )
    
    # Should succeed and fix the file
    assert result.returncode == 0
    assert "Copyright" in file_path.read_text()


# ============================================================================
# ERROR HANDLING AND EDGE CASES
# ============================================================================

def test_cli_empty_file_list():
    """Test CLI with no files provided"""
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main"],
        capture_output=True,
        text=True
    )
    
    # Should show usage or succeed with no action
    # Different behaviors are acceptable
    assert result.returncode in [0, 1, 2]


def test_cli_with_special_characters_in_filename(temp_project_dir):
    """Test CLI with special characters in filename"""
    template_path = temp_project_dir / "copyright.txt"
    
    # Create file with special characters
    special_file = temp_project_dir / "file with spaces.py"
    special_file.write_text("def test():\n    pass\n")
    
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main",
         str(special_file),
         f"--notice={template_path}"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )
    
    assert result.returncode == 0
    assert "Copyright" in special_file.read_text()


def test_workflow_concurrent_file_processing(temp_project_dir):
    """Test processing multiple files handles concurrency correctly"""
    template_path = temp_project_dir / "copyright.txt"
    
    # Create multiple files
    files = []
    for i in range(10):
        f = temp_project_dir / f"test_{i}.py"
        f.write_text(f"def func_{i}():\n    pass\n")
        files.append(str(f))
    
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main",
         *files,
         f"--notice={template_path}"],
        capture_output=True,
        text=True,
        cwd=temp_project_dir
    )
    
    assert result.returncode == 0
    
    # All files should be processed
    for file_path in files:
        assert "Copyright" in Path(file_path).read_text()


def test_cli_invalid_arguments():
    """Test CLI with invalid arguments"""
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main", "--invalid-arg"],
        capture_output=True,
        text=True
    )
    
    # Should fail with error
    assert result.returncode != 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
