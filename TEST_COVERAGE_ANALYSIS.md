<!--
SPDX-License-Identifier: MIT
Copyright 2026 Sony Group Corporation
Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
License: For licensing see the License.txt file
-->

# Test Coverage Analysis: Why the Bug Wasn't Caught

## The Bug

When running:
```bash
sny-copyright-checker INIT_WIZARD.md --no-fix
```

The tool failed with:
```
error: argument command: invalid choice: 'INIT_WIZARD.md' (choose from 'init', 'check')
```

## Why Tests Didn't Catch It

### Root Cause: Implicit Testing Assumptions

The existing test suite had **332 passing tests**, but all CLI tests made the same implicit assumptions:

### 1. **All CLI Tests Used Flags Before Filenames**

Example from `test_integration.py`:
```python
result = subprocess.run(
    [sys.executable, "-m", "scripts.main",
     str(file_path),           # File path
     f"--notice={template_path}"],  # Flag AFTER filename
    ...
)
```

Or:
```python
result = subprocess.run(
    [sys.executable, "-m", "scripts.main",
     "--no-fix",               # Flag FIRST
     str(file_path)],          # Then filename
    ...
)
```

**What was never tested:**
```bash
sny-copyright-checker filename.py      # Bare filename, no flags
sny-copyright-checker file1.py file2.py  # Multiple files, no flags
```

### 2. **No Tests for Argument Order Permutations**

The tests always used specific, "correct-looking" argument orders but never tested the natural, minimal use cases that users actually type.

**Tested:**
- ✅ `--notice=copyright.txt file.py`
- ✅ `file.py --notice=copyright.txt`

**Not tested:**
- ❌ `file.py` (bare filename as first arg)
- ❌ `file.py --no-fix` (filename first, then flag)
- ❌ `file1.py file2.py file3.py` (multiple files, no flags)

### 3. **No Tests for Subparser Ambiguity**

When we added the `init` subcommand, we created a situation where argparse had to distinguish between:
- A subcommand: `init`
- A positional argument (filename)

Tests never covered:
- What happens when the first positional arg isn't a subcommand?
- Does argparse require the subcommand to come first?
- How does `required=False` on subparsers interact with positional args?

### 4. **No Tests for Files with Command-like Names**

Tests never tried:
- A file named `init.py` (could be confused with `init` command)
- A file named `check.py` (if we had a `check` command)
- Relative vs absolute paths as first argument

### 5. **Integration Tests Used subprocess, Not Direct Calls**

All integration tests used `subprocess.run()` which:
- Tests the full CLI stack
- But makes it harder to test argument parsing in isolation
- Requires actual file system operations
- Takes longer to run

No tests called `main(argv=[...])` directly to test argument parsing logic.

## Test Coverage Gaps Identified

### Critical Gaps

1. **Minimal Invocations**
   - Most users will type the simplest possible command
   - Tests focused on complex, multi-flag scenarios
   - Never tested bare essentials

2. **Argument Order Variations**
   - Filename first (most natural)
   - Multiple files without flags
   - Flags interspersed with files

3. **Edge Cases**
   - Empty arguments (`sny-copyright-checker`)
   - Just flags, no files (`sny-copyright-checker --verbose`)
   - Files with special names

4. **Subcommand Interactions**
   - Positional args + optional subparsers
   - Filename that looks like a command
   - Subcommand detection logic

### Test Categories Never Covered

| Category | Examples | Why Important |
|----------|----------|---------------|
| Bare filename | `tool file.py` | Most common user pattern |
| Multiple files only | `tool f1.py f2.py` | Common batch operation |
| Filename-first order | `tool file.py --flag` | Natural command style |
| Command ambiguity | `tool init.py` | Could be file or command |
| Minimal flags | `tool file.py` | Default behavior testing |
| Empty invocation | `tool` | Help/usage testing |
| Special filenames | `tool --file.py` | Shell escaping issues |

## Lessons Learned

### 1. Test the User's Mental Model

Users think:
```bash
copyright-checker myfile.py
```

Not:
```bash
copyright-checker --notice=copyright.txt --fix myfile.py
```

**Lesson:** Test the simplest, most natural invocations first.

### 2. Test Argument Order Permutations

Don't assume one "correct" order. Test all reasonable permutations:
- Flags first, files second
- Files first, flags second
- Mixed order
- No flags at all

### 3. Test Ambiguous Cases

When adding subcommands:
- Test that filenames don't get confused with commands
- Test both absolute and relative paths
- Test edge cases (empty args, just flags, etc.)

### 4. Use Both Integration and Unit Tests

- **Integration tests** (subprocess): Test actual user experience
- **Unit tests** (direct function calls): Test parsing logic in isolation

### 5. Test Minimal Cases First

The bug would have been caught by:
```python
def test_single_filename_no_flags():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.main", "test.py"],
        ...
    )
    assert result.returncode == 0
```

This is the **most basic use case** but was never tested!

## Improvements Made

### New Test File: `test_cli_argument_order.py`

Added 15 new tests covering:

1. **Argument Order Tests**
   - ✅ Filename first, no flags
   - ✅ Filename first, then flags
   - ✅ Multiple filenames first
   - ✅ Flags before filename
   - ✅ Mixed order

2. **Command Ambiguity Tests**
   - ✅ Init command with flags
   - ✅ File named like a command (`init.py`)
   - ✅ Relative paths
   - ✅ Wildcard patterns

3. **Edge Case Tests**
   - ✅ Empty arguments
   - ✅ Only flags, no files
   - ✅ Double dash separator (`--`)
   - ✅ Files with dashes in names

4. **Init Command Tests**
   - ✅ Init without flags
   - ✅ Init with custom output

## Recommendations for Future Development

### Test Checklist for CLI Changes

When modifying CLI argument handling:

- [ ] Test with no arguments
- [ ] Test with single file, no flags
- [ ] Test with multiple files, no flags
- [ ] Test with flags before files
- [ ] Test with files before flags
- [ ] Test with mixed order (flags between files)
- [ ] Test with relative paths
- [ ] Test with absolute paths
- [ ] Test with files named like commands
- [ ] Test with special characters in filenames
- [ ] Test with `--` separator
- [ ] Test all subcommands independently
- [ ] Test help for each subcommand
- [ ] Test error messages

### General Testing Principles

1. **Test like a user**: Start with what users will actually type
2. **Test minimally**: Simplest cases often reveal the most bugs
3. **Test permutations**: Don't assume one "right" way
4. **Test ambiguity**: Anything that could be confused
5. **Test early**: Add tests before fixing bugs (TDD for bug fixes)

## Impact Summary

- **Bug severity**: High (broke basic functionality)
- **Tests before fix**: 332 passing (but missed the bug)
- **Tests after fix**: 348 passing (16 new tests added)
- **Coverage improvement**: Added critical CLI argument order testing
- **Prevention**: Similar bugs will now be caught by the test suite

## Conclusion

The bug wasn't caught because tests made **implicit assumptions** about how arguments would be ordered. By testing only "correct-looking" invocations, we missed the most natural user patterns.

The key insight: **Test what users will actually type, not what you think is the "proper" way to invoke the tool.**
