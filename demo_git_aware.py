#!/usr/bin/env python
# SPDX-License-Identifier: MIT
# Copyright 2020-2024 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file


"""
Demo file to demonstrate Git-aware year management.

This file has an existing copyright with a year range of 2020-2024.
When Git-aware mode is enabled:
- If the file is unchanged in Git, the years remain "2020-2024"
- If the file is modified, the years extend to "2020-<current_year>"
"""


def demonstrate_git_aware_feature():
    """
    This function demonstrates the Git-aware year management feature.

    The copyright notice at the top of this file will be managed automatically:
    1. The earliest year (2020) is preserved
    2. The end year is only updated when the file has actual changes
    3. This prevents noise in Git diffs from unnecessary year updates
    """
    print("Git-aware year management demonstration")
    print("=" * 50)
    print()
    print("Key benefits:")
    print("- Preserves earliest year from file history")
    print("- Extends year range only when file is modified")
    print("- Reduces unnecessary file changes")
    print()
    print("Try modifying this file and running:")
    print("  sny-copyright-checker demo_git_aware.py")
    print()
    print("Then check the copyright year - it should extend to current year!")


if __name__ == "__main__":
    demonstrate_git_aware_feature()
