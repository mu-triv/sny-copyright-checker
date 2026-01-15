#!/usr/bin/env python
# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

"""
Demo: Project-Wide vs Per-File Year Management

This script demonstrates the difference between the two year management modes.
"""

print("""
╔══════════════════════════════════════════════════════════════════════╗
║     Project-Wide vs Per-File Year Management Demo                ║
╚══════════════════════════════════════════════════════════════════════╝

SCENARIO: Project created in 2018
         File1 added in 2020
         File2 added in 2023
         Current year: 2026

┌──────────────────────────────────────────────────────────────────────┐
│ DEFAULT MODE (Project-Wide Years)                                │
│ Command: sny-copyright-checker file1.py file2.py                    │
└──────────────────────────────────────────────────────────────────────┘

✓ File1.py:  Copyright 2018-2026 Sony Corporation
  └─ Uses project inception year (2018), not file year (2020)

✓ File2.py:  Copyright 2018-2026 Sony Corporation
  └─ Uses project inception year (2018), not file year (2023)

Benefits:
  • Uniform copyright dates across entire project
  • Shows project age/history
  • Simpler to explain and manage

┌──────────────────────────────────────────────────────────────────────┐
│ PER-FILE MODE                                                        │
│ Command: sny-copyright-checker --per-file-years file1.py file2.py   │
└──────────────────────────────────────────────────────────────────────┘

✓ File1.py:  Copyright 2020-2026 Sony Corporation
  └─ Uses individual file creation year (2020)

✓ File2.py:  Copyright 2023-2026 Sony Corporation
  └─ Uses individual file creation year (2023)

Benefits:
  • Accurate file-level history
  • Unchanged files preserve their existing years (less Git noise)
  • Reflects actual file creation dates

┌──────────────────────────────────────────────────────────────────────┐
│ USE CASES                                                            │
└──────────────────────────────────────────────────────────────────────┘

Project-Wide (Default):
  ✓ Corporate projects with unified copyright
  ✓ Projects where all code belongs to same entity
  ✓ Simple year management preferred

Per-File Mode:
  ✓ Monorepos with components added at different times
  ✓ Files from different contributors at different dates
  ✓ Accurate historical tracking important
  ✓ Minimize Git diff noise

┌──────────────────────────────────────────────────────────────────────┐
│ EXAMPLE COMMANDS                                                     │
└──────────────────────────────────────────────────────────────────────┘

# Default (project-wide years)
$ sny-copyright-checker --fix *.py

# Per-file years mode
$ sny-copyright-checker --per-file-years --fix *.py

# Check only changed files (works with both modes)
$ sny-copyright-checker --changed-only --fix

# Disable Git-aware year management entirely
$ sny-copyright-checker --no-git-aware --fix *.py

""")
