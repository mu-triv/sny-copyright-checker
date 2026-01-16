#!/usr/bin/env python

# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

"""Test the string literal detection"""

content = open("tests/test_duplicate_detection.py", "r").read()
lines = content.split("\n")


# Simulate the function
def is_inside_string_literal(lines, line_number):
    in_string = False
    string_delimiter = None

    for i in range(line_number + 1):
        line = lines[i]

        for delimiter in ['"""', "'''"]:
            count = line.count(delimiter)
            if count > 0:
                print(f"Line {i}: found {count} x {repr(delimiter)}")
                for _ in range(count):
                    if not in_string:
                        in_string = True
                        string_delimiter = delimiter
                        print(f"  -> Opening string with {repr(delimiter)}")
                    elif string_delimiter == delimiter:
                        in_string = False
                        string_delimiter = None
                        print(f"  -> Closing string with {repr(delimiter)}")

        if i == line_number:
            print(f"\nLine {line_number} state: in_string={in_string}")
            return in_string

    return in_string


# Test line 471 (0-indexed) - should be inside string
print("Testing line 471 (0-indexed):")
print(f"Line 467 content: {repr(lines[466][:60])}")
print(f"Line 472 content: {repr(lines[471][:60])}")
print()
result = is_inside_string_literal(lines, 471)
print(f"\nResult: Line 471 inside string = {result}")
