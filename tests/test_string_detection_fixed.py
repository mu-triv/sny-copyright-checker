#!/usr/bin/env python

# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

"""Test the FIXED string literal detection with escape handling"""

content = open("tests/test_duplicate_detection.py", "r").read()
lines = content.split("\n")


def is_inside_string_literal_fixed(lines, line_number):
    """Fixed version that handles escaped quotes"""
    in_string = False
    string_delimiter = None

    for i in range(line_number + 1):
        line = lines[i]

        # Check for triple-quoted strings (but not escaped ones)
        for delimiter in ['"""', "'''"]:
            # Find all non-escaped occurrences of the delimiter
            count = 0
            pos = 0
            while True:
                pos = line.find(delimiter, pos)
                if pos == -1:
                    break
                # Check if it's escaped (preceded by odd number of backslashes)
                num_backslashes = 0
                check_pos = pos - 1
                while check_pos >= 0 and line[check_pos] == "\\":
                    num_backslashes += 1
                    check_pos -= 1
                # If even number of backslashes (including 0), it's not escaped
                if num_backslashes % 2 == 0:
                    count += 1
                    if i in range(464, 488):
                        print(
                            f"Line {i}: found non-escaped {repr(delimiter)} at pos {pos} (backslashes={num_backslashes})"
                        )
                pos += len(delimiter)

            if count > 0:
                # Toggle string state for each non-escaped delimiter found
                for _ in range(count):
                    if not in_string:
                        in_string = True
                        string_delimiter = delimiter
                        if i in range(464, 488):
                            print(f"  -> Opening string with {repr(delimiter)}")
                    elif string_delimiter == delimiter:
                        in_string = False
                        string_delimiter = None
                        if i in range(464, 488):
                            print(f"  -> Closing string with {repr(delimiter)}")

        if i == line_number:
            print(f"\nLine {line_number} state: in_string={in_string}")
            return in_string

    return in_string


# Test line 471 (0-indexed) - should be inside string
print("Testing line 471 (0-indexed) with FIXED function:")
print(f"Line 467 content: {repr(lines[466][:60])}")
print(f"Line 472 content: {repr(lines[471][:60])}")
print(f"Line 478 content: {repr(lines[477][:60])}")
print()
result = is_inside_string_literal_fixed(lines, 471)
print(f"\nResult: Line 471 inside string = {result}")
