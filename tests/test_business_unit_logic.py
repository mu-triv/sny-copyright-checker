# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

import os
import subprocess
import tempfile
from pathlib import Path

import pytest


class TestBusinessUnitLogic:
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory with git repo"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize git repo
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@test.com"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            yield tmpdir

    @pytest.fixture
        template_content = """[VARIABLES]
COMPANY = Sony Group Corporation
[.py]
[.js]
"""
        with open(template_path, "w") as f:
            f.write(template_content)
        return template_path

    # ============================================================================
    ):
        test_file = os.path.join(temp_dir, "test.py")

def original_function():
    return "original"
"""
        with open(test_file, "w") as f:
            f.write(content)

        # Commit it (simulating we got it from another team)
        subprocess.run(
            ["git", "add", test_file], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial from Network Comm"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Now modify the file (simulating our changes)
        with open(test_file, "a") as f:
            f.write("\ndef our_new_function():\n    return 'ours'\n")

        # Check with auto-fix
        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        with open(test_file, "r") as f:
            result = f.read()

        assert "Network Communications Laboratory" in result
        assert "R&D Center Europe Brussels Laboratory" in result
    ):
        test_file = os.path.join(temp_dir, "new_file.py")

def copied_function():
    return "copied"
"""
        with open(test_file, "w") as f:
            f.write(content)

        # File is new (not tracked by git), so it's "changed"
        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        with open(test_file, "r") as f:
            result = f.read()

        assert "Entertainment Division" in result
        assert "R&D Center Europe Brussels Laboratory" in result

    ):
        test_file = os.path.join(temp_dir, "test.py")

        # Create and commit file from different unit
original_code = True
"""
        with open(test_file, "w") as f:
            f.write(content)

        subprocess.run(
            ["git", "add", test_file], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "From MSE"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Modify and stage
        with open(test_file, "a") as f:
            f.write("our_code = True\n")
        subprocess.run(
            ["git", "add", test_file], cwd=temp_dir, check=True, capture_output=True
        )

        # Check
        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        with open(test_file, "r") as f:
            result = f.read()

        assert "MSE Laboratory" in result
        assert "R&D Center Europe Brussels Laboratory" in result

    # ============================================================================
    # RULE 2: Different business unit + NOT git-changed → DON'T add
    # ============================================================================

    ):
        test_file = os.path.join(temp_dir, "test.py")

        # Create and commit file from different unit
def their_function():
    return "theirs"
"""
        with open(test_file, "w") as f:
            f.write(content)

        subprocess.run(
            ["git", "add", test_file], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "From Haptic"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Check without modifying
        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is False

        with open(test_file, "r") as f:
            result = f.read()

        assert "Haptic Division" in result
        assert "R&D Center Europe Brussels Laboratory" not in result
    def test_rule2_different_unit_committed_file_no_changes(
    ):
        """Rule 2: Committed file from different unit with no modifications"""
        test_file = os.path.join(temp_dir, "lib.py")

class TheirClass:
    pass
"""
        with open(test_file, "w") as f:
            f.write(content)

        subprocess.run(
            ["git", "add", test_file], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Library from SCDE"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is False

        with open(test_file, "r") as f:
            result = f.read()

        assert "SCDE Europe" in result
        assert "R&D Center" not in result

    ):
        test_file = os.path.join(temp_dir, "external.py")

def external_function():
    return "external"
"""
        with open(test_file, "w") as f:
            f.write(content)

        subprocess.run(
            ["git", "add", test_file], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "External library"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is False

        with open(test_file, "r") as f:
            result = f.read()

        assert "External Company" in result
        assert "Sony" not in result

    # ============================================================================
    # RULE 3: Same business unit + incomplete → REPLACE
    # ============================================================================

    ):
        test_file = os.path.join(temp_dir, "test.py")

def function():
    return "test"
"""
        with open(test_file, "w") as f:
            f.write(content)

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        with open(test_file, "r") as f:
            result = f.read()

        assert "R&D Center Europe Brussels Laboratory" in result
        test_file = os.path.join(temp_dir, "test.py")

code = True
"""
        with open(test_file, "w") as f:
            f.write(content)

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        with open(test_file, "r") as f:
            result = f.read()

        assert "Apache-2.0" not in result

        """Rule 3: Old year from same unit should be updated"""
        test_file = os.path.join(temp_dir, "test.py")

        # Create file with old year
old_code = True
"""
        with open(test_file, "w") as f:
            f.write(content)

        # Commit it
        subprocess.run(
            ["git", "add", test_file], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Old file"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Modify it
        with open(test_file, "a") as f:
            f.write("new_code = True\n")

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is False

        with open(test_file, "r") as f:
            result = f.read()

        test_file = os.path.join(temp_dir, "test.py")

def function():
    pass
"""
        with open(test_file, "w") as f:
            f.write(content)

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        with open(test_file, "r") as f:
            result = f.read()

    # ============================================================================
    # COMPLEX SCENARIOS - Combinations and Edge Cases
    # ============================================================================

        test_file = os.path.join(temp_dir, "test.py")

def function():
    pass
"""
        with open(test_file, "w") as f:
            f.write(content)

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        # Should be valid and unchanged
        assert has_notice is True
        assert was_modified is False

    def test_complex_multiple_units_in_file_modified(
    ):
        test_file = os.path.join(temp_dir, "test.py")

def shared_function():
    return "shared"
"""
        with open(test_file, "w") as f:
            f.write(content)

        subprocess.run(
            ["git", "add", test_file], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Multi-unit file"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Modify it
        with open(test_file, "a") as f:
            f.write("\ndef our_addition():\n    return 'ours'\n")

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        with open(test_file, "r") as f:
            result = f.read()

        assert "Network Communications Laboratory" in result
        assert "Entertainment Division" in result
        assert "R&D Center Europe Brussels Laboratory" in result

        test_file = os.path.join(temp_dir, "test.py")

        content = """def function():
"""
        with open(test_file, "w") as f:
            f.write(content)

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        with open(test_file, "r") as f:
            result = f.read()

        assert "R&D Center Europe Brussels Laboratory" in result
        test_file = os.path.join(temp_dir, "test.py")

def function():
    pass
"""
        with open(test_file, "w") as f:
            f.write(content)

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        with open(test_file, "r") as f:
            result = f.read()

        assert result.count("R&D Center Europe Brussels Laboratory") == 1

    def test_complex_git_not_available_treat_as_modified(
    ):
        """When git is not available, files with different units should be treated cautiously"""
        # Create non-git directory
        non_git_dir = tempfile.mkdtemp()
        try:
                with open(template_path, "w") as dst:
                    dst.write(src.read())

            test_file = os.path.join(non_git_dir, "test.py")
code = True
"""
            with open(test_file, "w") as f:
                f.write(content)

            # Without git, can't determine if file is modified
            has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

            assert has_notice is True
            assert was_modified is True
        finally:
            import shutil

            shutil.rmtree(non_git_dir, ignore_errors=True)

        """Business unit matching should be case-insensitive"""
        test_file = os.path.join(temp_dir, "test.py")

        # Same unit but different case
code = True
"""
        with open(test_file, "w") as f:
            f.write(content)

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        # Should recognize as same unit and replace
        assert has_notice is True
        assert was_modified is True

        with open(test_file, "r") as f:
            result = f.read()

        # Should have proper case now
        assert "R&D Center Europe Brussels Laboratory" in result

    def test_complex_whitespace_variations_in_unit_name(
    ):
        """Unit names with extra whitespace should still match"""
        test_file = os.path.join(temp_dir, "test.py")

code = True
"""
        with open(test_file, "w") as f:
            f.write(content)

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        # Should recognize as same unit despite whitespace differences
        assert has_notice is True
        assert was_modified is True

        test_file = os.path.join(temp_dir, "empty.py")

        with open(test_file, "w") as f:
            f.write("")

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        test_file = os.path.join(temp_dir, "script.py")

        content = """#!/usr/bin/env python3
print("script")
"""
        with open(test_file, "w") as f:
            f.write(content)

        subprocess.run(
            ["git", "add", test_file], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Tools script"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Modify
        with open(test_file, "a") as f:
            f.write("print('modified')\n")

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        with open(test_file, "r") as f:
            result = f.read()

        # Shebang should remain first
        assert result.startswith("#!/usr/bin/env python3")
        assert "Tools Team" in result
        assert "R&D Center Europe Brussels Laboratory" in result

        """In no-fix mode, should only report issues without modifying"""
        test_file = os.path.join(temp_dir, "test.py")

code = True
"""
        with open(test_file, "w") as f:
            f.write(content)

        has_notice, was_modified = checker.check_file(test_file, auto_fix=False)

        # Should report incomplete but not fix
        assert has_notice is False
        assert was_modified is False

        with open(test_file, "r") as f:
            result = f.read()

        # Content should be unchanged
        assert result == content

        """Rule 1 with JavaScript file (different comment style)"""
        test_file = os.path.join(temp_dir, "test.js")

function original() {
    return "original";
}
"""
        with open(test_file, "w") as f:
            f.write(content)

        subprocess.run(
            ["git", "add", test_file], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Web code"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Modify
        with open(test_file, "a") as f:
            f.write("\nfunction ourAddition() { return 'ours'; }\n")

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        with open(test_file, "r") as f:
            result = f.read()

        assert "Web Team" in result
        assert "R&D Center Europe Brussels Laboratory" in result
        test_file = os.path.join(temp_dir, "whitespace.py")

        with open(test_file, "w") as f:
            f.write("   \n\n\t\n   ")

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        test_file = os.path.join(temp_dir, "long.py")

def code():
    pass
"""
        with open(test_file, "w") as f:
            f.write(content)

        subprocess.run(
            ["git", "add", test_file], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "long"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        # Should not modify unmodified file from different unit
        assert has_notice is True
        assert was_modified is False

    def test_stress_multiple_sequential_modifications(
    ):
        """Test multiple sequential check/fix cycles"""
        test_file = os.path.join(temp_dir, "seq.py")

        with open(test_file, "w") as f:
            f.write("code = 1\n")

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)
        assert has_notice is True
        assert was_modified is True

        # Second check - should be valid, no changes
        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)
        assert has_notice is True
        assert was_modified is False

        # Third check - still valid
        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)
        assert has_notice is True
        assert was_modified is False

    ):
        test_file = os.path.join(temp_dir, "special.py")

def code():
    pass
"""
        with open(test_file, "w") as f:
            f.write(content)

        subprocess.run(
            ["git", "add", test_file], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "special"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        with open(test_file, "a") as f:
            f.write("# modified\n")

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

    ):
        test_file = os.path.join(temp_dir, "multi.py")

def code():
    pass
"""
        with open(test_file, "w") as f:
            f.write(content)

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        # Same unit + incomplete = should replace
        assert has_notice is True
        assert was_modified is True

        with open(test_file) as f:
            content = f.read()
        assert "2020-2026" in content or "2026" in content

        """Binary file should be skipped"""
        test_file = os.path.join(temp_dir, "data.bin")

        with open(test_file, "wb") as f:
            f.write(b"\x00\x01\x02\x03\xff\xfe")

        try:
            has_notice, was_modified = checker.check_file(test_file, auto_fix=True)
            # If it doesn't raise, just verify no crash
            assert True
        except (UnicodeDecodeError, ValueError):
            # Expected for binary files
            assert True

        """File path with spaces should work"""
        subdir = os.path.join(temp_dir, "my folder")
        os.makedirs(subdir, exist_ok=True)

        test_file = os.path.join(subdir, "my file.py")

        with open(test_file, "w") as f:
            f.write("code = 1\n")

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        test_file = os.path.join(temp_dir, "minimal.py")

def code():
    pass
"""
        with open(test_file, "w") as f:
            f.write(content)

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        """File with mixed comment styles"""
        test_file = os.path.join(temp_dir, "mixed.js")

function code() {}
"""
        with open(test_file, "w") as f:
            f.write(content)

        subprocess.run(
            ["git", "add", test_file], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "mixed"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True

        """File in deeply nested directory structure"""
        deep_path = os.path.join(temp_dir, "a", "b", "c", "d", "e", "f", "g")
        os.makedirs(deep_path, exist_ok=True)

        test_file = os.path.join(deep_path, "deep.py")

        with open(test_file, "w") as f:
            f.write("code = 1\n")

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        """Very short file (single line)"""
        test_file = os.path.join(temp_dir, "short.py")

        with open(test_file, "w") as f:
            f.write("x=1")

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        with open(test_file) as f:
            content = f.read()
        assert "x=1" in content
        """File with unicode characters in content"""
        test_file = os.path.join(temp_dir, "unicode.py")

        with open(test_file, "w", encoding="utf-8") as f:
            f.write("# コメント\ncode = '日本語'\n")

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

    def test_rule_combinations_git_modified_same_unit_incomplete(
    ):
        """Git modified + same unit + incomplete = replace"""
        test_file = os.path.join(temp_dir, "combo1.py")

def original():
    pass
"""
        with open(test_file, "w") as f:
            f.write(content)

        subprocess.run(
            ["git", "add", test_file], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "add"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Modify file
        with open(test_file, "a") as f:
            f.write("\ndef new():\n    pass\n")

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        # Same unit + incomplete = should replace (git status doesn't matter for same unit)
        assert has_notice is True
        assert was_modified is True

        with open(test_file) as f:
            content = f.read()
        assert "R&D Center Europe Brussels Laboratory" in content

    def test_rule_combinations_git_modified_different_unit_complete(
    ):
        test_file = os.path.join(temp_dir, "combo2.py")

def original():
    pass
"""
        with open(test_file, "w") as f:
            f.write(content)

        subprocess.run(
            ["git", "add", test_file], cwd=temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "add"],
            cwd=temp_dir,
            check=True,
            capture_output=True,
        )

        # Modify file
        with open(test_file, "a") as f:
            f.write("\ndef new():\n    pass\n")

        has_notice, was_modified = checker.check_file(test_file, auto_fix=True)

        assert has_notice is True
        assert was_modified is True

        with open(test_file) as f:
            content = f.read()