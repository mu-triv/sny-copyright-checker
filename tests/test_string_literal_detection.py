#!/usr/bin/env python
"""Test to verify string literal detection works correctly"""

from scripts.copyright_checker import CopyrightChecker

checker = CopyrightChecker("copyright.txt")

# Test 1: Line inside actual triple-quote string
print("Test 1: Copyright inside actual triple-quote string")
test_lines1 = [
    "# Copyright 2026 Company",
    "",
    'content = """',
    "# This is inside a multiline string",
    "# Copyright 2026 Other Company",
    '"""',
]
result1 = checker._is_inside_string_literal(test_lines1, 4)
print(f"  Result: {result1} (expected: True)")
print(f"  {'✓ PASS' if result1 else '✗ FAIL'}")
print()

# Test 2: Line with single-quoted string containing """
print("Test 2: Line after single-quoted string containing triple quotes")
test_lines2 = [
    "# Copyright 2026 Company",
    "",
    'assert "test_data = \\"\\"\\""  in result',  # escaped to show literally
    "# Real code here - should NOT be in string",
]
result2 = checker._is_inside_string_literal(test_lines2, 3)
print(f"  Result: {result2} (expected: False)")
print(f"  {'✓ PASS' if not result2 else '✗ FAIL'}")
print()

# Test 3: The actual problematic case from test file
print("Test 3: Actual case from test_duplicate_detection.py")
test_lines3 = [
    '        assert result.count("# Copyright 2026 Sony Group Corporation") == 1',
    '        assert result.count("# Copyright 2025 Sony Group Corporation") == 1',
    '        assert "test_data = triple_quotes" in result',  # Line with """ inside quotes
    "",
    "    def test_string_literal_with_duplicate_real_copyright(",
    "# This line should NOT be detected as inside string",
]
result3 = checker._is_inside_string_literal(test_lines3, 5)
print(f"  Result: {result3} (expected: False)")
print(f"  {'✓ PASS' if not result3 else '✗ FAIL'}")
print()

# Test 4: Escaped triple quotes (like \"\"\" in test strings)
print("Test 4: Escaped triple quotes should not open multiline string")
test_lines4 = [
    "# Copyright 2026 Company",
    "",
    'content = """Text',
    'with content = \\"\\"\\"escaped',
    "# This line is still inside the multiline string started on line 2",
    '"""',
    "# This is outside",
]
result4a = checker._is_inside_string_literal(test_lines4, 4)
result4b = checker._is_inside_string_literal(test_lines4, 6)
print(f"  Line 4 (inside): {result4a} (expected: True)")
print(f"  Line 6 (outside): {result4b} (expected: False)")
print(f"  {'✓ PASS' if result4a and not result4b else '✗ FAIL'}")

print()
print("=" * 60)
all_pass = result1 and not result2 and not result3 and result4a and not result4b
if all_pass:
    print("✓ ALL TESTS PASSED - String literal detection is working correctly!")
else:
    print("✗ SOME TESTS FAILED - String literal detection needs improvement")
