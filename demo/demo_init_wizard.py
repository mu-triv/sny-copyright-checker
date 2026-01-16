#!/usr/bin/env python
# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

"""
Demo script showing the init wizard in action.

This demonstrates how the interactive wizard helps users create
a copyright.txt configuration file without reading documentation.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.init_wizard import run_init_wizard


def demo_mit_license():
    """Demo: Creating MIT license configuration."""
    print("=" * 70)
    print("DEMO 1: Creating MIT License Configuration for Python Project")
    print("=" * 70)
    print()

    # Simulate user inputs
    inputs = [
        "mit",  # Choose MIT license
        "Acme Corporation",  # Company name
        "y",  # Include author
        "Engineering Team",  # Author name
        "n",  # Don't customize
        "7",  # Python extensions (option 7)
        "y",  # Save
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "copyright_mit.txt"

        with patch("scripts.init_wizard.input", side_effect=inputs):
            result = run_init_wizard(str(output_file))

        if result == 0:
            print("\n" + "=" * 70)
            print("Generated Configuration:")
            print("=" * 70)
            print(output_file.read_text())
            print("=" * 70)
        else:
            print("Failed to generate configuration")


def demo_proprietary_multi_language():
    """Demo: Creating proprietary license for multi-language project."""
    print("\n\n")
    print("=" * 70)
    print("DEMO 2: Proprietary License for Multi-Language Project")
    print("=" * 70)
    print()

    inputs = [
        "proprietary",  # Proprietary license
        "SecretCorp Inc.",  # Company
        "n",  # No author field
        "n",  # Don't customize
        "1,5,7",  # C/C++, JavaScript, and Python
        "y",  # Save
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "copyright_proprietary.txt"

        with patch("scripts.init_wizard.input", side_effect=inputs):
            result = run_init_wizard(str(output_file))

        if result == 0:
            print("\n" + "=" * 70)
            print("Generated Configuration:")
            print("=" * 70)
            print(output_file.read_text())
            print("=" * 70)
        else:
            print("Failed to generate configuration")


def demo_apache_all_languages():
    """Demo: Apache license with all supported languages."""
    print("\n\n")
    print("=" * 70)
    print("DEMO 3: Apache License 2.0 with All Languages")
    print("=" * 70)
    print()

    inputs = [
        "apache",  # Apache license
        "OpenSource Inc.",  # Company
        "y",  # Include author
        "Contributors",  # Author
        "n",  # Don't customize
        "all",  # All extensions
        "y",  # Save
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "copyright_apache.txt"

        with patch("scripts.init_wizard.input", side_effect=inputs):
            result = run_init_wizard(str(output_file))

        if result == 0:
            print("\n" + "=" * 70)
            print("Generated Configuration (showing first 50 lines):")
            print("=" * 70)
            lines = output_file.read_text().split("\n")
            print("\n".join(lines[:50]))
            if len(lines) > 50:
                print(f"\n... ({len(lines) - 50} more lines)")
            print("=" * 70)
        else:
            print("Failed to generate configuration")


def demo_custom_license():
    """Demo: Custom license with specific requirements."""
    print("\n\n")
    print("=" * 70)
    print("DEMO 4: Custom License Configuration")
    print("=" * 70)
    print()

    inputs = [
        "custom",  # Custom license
        "Custom Corp",  # Company
        "y",  # Include author
        "Legal Department",  # Author
        "Custom-License-1.0",  # SPDX identifier
        "See LICENSE.md for full terms",  # License notice
        "7,4",  # Python and Java
        "y",  # Save
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "copyright_custom.txt"

        with patch("scripts.init_wizard.input", side_effect=inputs):
            result = run_init_wizard(str(output_file))

        if result == 0:
            print("\n" + "=" * 70)
            print("Generated Configuration:")
            print("=" * 70)
            print(output_file.read_text())
            print("=" * 70)
        else:
            print("Failed to generate configuration")


def main():
    """Run all demos."""
    print("\n")
    print("*" * 70)
    print("SNY Copyright Checker - Init Wizard Demonstrations")
    print("*" * 70)
    print()
    print("This script demonstrates various scenarios for using the")
    print("init wizard to quickly create copyright configurations.")
    print()

    try:
        demo_mit_license()
        demo_proprietary_multi_language()
        demo_apache_all_languages()
        demo_custom_license()

        print("\n\n")
        print("*" * 70)
        print("Summary")
        print("*" * 70)
        print()
        print("The init wizard makes it easy to:")
        print("  ✓ Choose from common license templates")
        print("  ✓ Configure company and author information")
        print("  ✓ Select relevant file extensions")
        print("  ✓ Generate ready-to-use copyright.txt files")
        print()
        print("To try it yourself, run:")
        print("  sny-copyright-checker init")
        print()
        print("*" * 70)

    except KeyboardInterrupt:
        print("\n\nDemo interrupted.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
