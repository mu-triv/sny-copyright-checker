#!/usr/bin/env python

# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

"""Debug string state before line 464"""

content = open("tests/test_duplicate_detection.py", "r").read()
lines = content.split("\n")


def trace_string_state(lines, end_line):
    """Trace string state up to end_line"""
    in_string = False
    string_delimiter = None

    for i in range(end_line + 1):
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
                pos += len(delimiter)

            if count > 0:
                # Toggle string state for each non-escaped delimiter found
                for _ in range(count):
                    old_state = in_string
                    if not in_string:
                        in_string = True
                        string_delimiter = delimiter
                    elif string_delimiter == delimiter:
                        in_string = False
                        string_delimiter = None
                    print(
                        f"Line {i}: {old_state} -> {in_string} after {repr(delimiter)}"
                    )

        if i == end_line:
            return in_string

    return in_string


# Trace up to line 466
print("Tracing string state from start to line 466:")
print("=" * 60)
result = trace_string_state(lines, 466)
print("=" * 60)
print(f"\nFinal state at line 466: in_string={result}")
