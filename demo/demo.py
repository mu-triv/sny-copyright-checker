#!/usr/bin/env python

# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

"""Demo script to test the SNY Copyright Check tool"""

import os
import tempfile
from pathlib import Path
import sys

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.copyright_checker import CopyrightChecker


def create_test_files():
    """Create temporary test files"""
    temp_dir = tempfile.mkdtemp(prefix="copyright_test_")
    print(f"Creating test files in: {temp_dir}\n")

    test_files = {
        "test1.py": """def hello():
    print("Hello World")
""",
        "test2.sql": """SELECT * FROM users;
""",
        "test3.c": """#include <stdio.h>

int main() {
    return 0;
}
""",
        "test_with_shebang.py": """#!/usr/bin/env python

def main():
    pass
""",
        "test_with_copyright.py": """# Copyright 2026 SNY Group Corporation
# Author: R&D Center Europe Brussels Laboratory, SNY Group Corporation
# License: For licensing see the License.txt file

def already_has_copyright():
    pass
"""
    }

    created_files = []
    for filename, content in test_files.items():
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        created_files.append(filepath)
        print(f"✓ Created: {filename}")

    return temp_dir, created_files


def demo_checker():
    """Run demo of the copyright checker"""
    print("=" * 70)
    print("SNY Copyright Check - Demo")
    print("=" * 70)
    print()

    # Create test files
    temp_dir, test_files = create_test_files()

    # Get the copyright template path
    template_path = os.path.join(Path(__file__).parent, "copyright.txt")

    if not os.path.exists(template_path):
        print(f"❌ Error: copyright.txt not found at {template_path}")
        return

    print(f"\nUsing template: {template_path}")
    print("=" * 70)

    # Create checker
    try:
        checker = CopyrightChecker(template_path)
        print(f"\n✓ Loaded templates for: {checker.get_supported_extensions()}")
    except Exception as e:
        print(f"❌ Error loading checker: {e}")
        return

    print("\n" + "=" * 70)
    print("Checking and fixing files...")
    print("=" * 70 + "\n")

    # Check each file
    for filepath in test_files:
        filename = os.path.basename(filepath)
        print(f"\n📄 {filename}")
        print("-" * 70)

        # Show original content
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()
        print("BEFORE:")
        print(original[:200] + ("..." if len(original) > 200 else ""))

        # Check and fix
        try:
            has_notice, was_modified = checker.check_file(filepath, auto_fix=True)

            if was_modified:
                print("\n✓ Copyright notice ADDED")
                with open(filepath, 'r', encoding='utf-8') as f:
                    updated = f.read()
                print("\nAFTER:")
                print(updated[:300] + ("..." if len(updated) > 300 else ""))
            elif has_notice:
                print("\n✓ Already has valid copyright (no changes)")
            else:
                print("\n❌ Check failed")
        except Exception as e:
            print(f"\n❌ Error: {e}")

        print("-" * 70)

    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)
    print(f"\nTest files are in: {temp_dir}")
    print("You can examine them and then delete the directory when done.")


if __name__ == "__main__":
    demo_checker()
