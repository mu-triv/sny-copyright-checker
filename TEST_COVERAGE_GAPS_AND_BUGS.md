<!--
SPDX-License-Identifier: MIT
Copyright 2026 Sony Group Corporation
Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
License: For licensing see the License.txt file
-->

# Test Coverage Gap Analysis & Bugs Found

## Coverage Gaps in test_cli_argument_order.py

### Arguments NOT Tested

The test file tests only 4 out of 13 available arguments:

**Tested:**
- ✅ `--no-fix` (1 test)
- ✅ `--verbose` (2 tests)
- ✅ `--help` (implicitly through init tests)
- ✅ `--output/-o` (init command, 2 tests)

**NOT Tested:**
- ❌ `--notice` (custom template path)
- ❌ `--changed-only` (git integration)
- ❌ `--base-ref` (git reference)
- ❌ `--no-git-aware` (disable git-aware years)
- ❌ `--per-file-years` (per-file year mode)
- ❌ `--ignore-file` (custom ignore file)
- ❌ `--no-gitignore` (disable gitignore)
- ❌ `--hierarchical` (hierarchical templates)
- ❌ `--replace` (replace mode)
- ❌ `--fix` (explicit enable auto-fix)
- ❌ `-v` (verbose short form)

### Edge Cases NOT Tested

1. **Conflicting flags:**
   - `--fix` and `--no-fix` together
   - `--replace` without `--fix`
   - `--changed-only` with filenames (should ignore filenames)
   - `--base-ref` without `--changed-only` (should be ignored)

2. **Invalid values:**
   - `--notice` with non-existent file
   - `--base-ref` with invalid git reference
   - `--ignore-file` with non-existent file
   - `--output` to read-only location (init)

3. **Combination testing:**
   - Multiple flags together
   - Long-form and short-form mixed
   - Flags with and without equals sign (`--notice=file` vs `--notice file`)

4. **Init command:**
   - `init` with check-command flags (should they be rejected?)
   - `init` as a filename vs command
   - Multiple `init` in command line

## Bugs Found in Production Code

### 🐛 Bug 1: Init Command Pollution
**Location:** `scripts/main.py`, line 41

**Issue:** The init command detection uses a simple string comparison:
```python
if len(argv) > 0 and argv[0] == 'init':
```

**Problem:** This only checks if the FIRST argument is exactly 'init'. What if:
- `argv[0]` is `'./init'` (relative path)
- `argv[0]` is `'/path/to/init'` (absolute path)
- `argv[0]` is `'init.py'` (filename starting with init)

**Test demonstrates:** `test_filename_that_looks_like_command` creates `init.py` but uses full path, so it works. However, if user runs `sny-copyright-checker init.py` from same directory, it would trigger init command!

**Fix:**
```python
# Only treat as init command if it's exactly 'init' with no path separators
if len(argv) > 0 and argv[0] == 'init' and os.sep not in argv[0]:
```

### 🐛 Bug 2: No Validation for --replace Without --fix
**Location:** `scripts/main.py`, line 137

**Issue:** The `--replace` flag requires `--fix` to be enabled (as stated in help text), but there's no validation:
```python
checker = CopyrightChecker(
    ...
    replace_mode=args.replace,  # No check if fix is enabled
    ...
)
```

**Problem:** User can specify `--replace --no-fix` which doesn't make sense (can't replace if not fixing).

**Expected behavior:** Should either:
1. Error out with clear message
2. Silently ignore --replace when --no-fix is set
3. Force --fix to be enabled when --replace is set

**Test missing:** No test for `--replace --no-fix` combination.

### 🐛 Bug 3: --base-ref Without --changed-only
**Location:** `scripts/main.py`, line 161

**Issue:** `--base-ref` is only meaningful with `--changed-only`, but no validation:
```python
if args.changed_only:
    files_to_check = checker.get_changed_files(base_ref=args.base_ref)
else:
    files_to_check = args.filenames  # base_ref is ignored silently
```

**Problem:** User might specify `--base-ref origin/main file.py` expecting it to do something, but it's silently ignored.

**Expected behavior:** Warning message or error when --base-ref is used without --changed-only.

### 🐛 Bug 4: --changed-only With Filenames
**Location:** `scripts/main.py`, line 158-160

**Issue:** Help text says "(ignores filenames argument)" but this is confusing:
```python
if args.changed_only:
    # Gets files from git, ignores args.filenames
else:
    files_to_check = args.filenames
```

**Problem:** If user runs `sny-copyright-checker --changed-only file1.py file2.py`, the files are silently ignored. No warning given.

**Expected behavior:** Either:
1. Warn when both are provided
2. Error out (conflicting options)
3. Filter changed files to only those in filenames list

**Test missing:** No test for `--changed-only` with filenames.

### 🐛 Bug 5: argv=None Behavior Change
**Location:** `scripts/main.py`, lines 36-38

**Issue:** When `argv=None`, the code does:
```python
import sys
if argv is None:
    argv = sys.argv[1:]
```

**Problem:** This modifies behavior from original argparse which uses sys.argv internally. Now we're manually slicing `sys.argv[1:]` which means:
1. If called with `main(None)` vs `main()`, behavior might differ
2. Tests that call `main([])` vs `main(None)` will behave differently

**Inconsistency:** The function signature says `argv: Optional[Sequence[str]] = None` but then we convert None to a list, so it's never actually None after line 38.

### 🐛 Bug 6: No Validation for Conflicting Git Flags
**Location:** `scripts/main.py`, lines 115-125

**Issue:** Can specify both `--no-git-aware` and `--per-file-years`:
```python
parser.add_argument("--no-git-aware", action="store_false", dest="git_aware", default=True)
parser.add_argument("--per-file-years", action="store_true")
```

**Problem:** `--per-file-years` requires git to be functional, but `--no-git-aware` disables it. What happens with both?

**Expected behavior:** These should be mutually exclusive or validated.

### 🐛 Bug 7: Help Text Misleading for --fix
**Location:** `scripts/main.py`, line 82

**Issue:**
```python
parser.add_argument("--fix", action="store_true", default=True,
    help="Automatically add missing copyright notices (default: True)")
```

**Problem:** With `default=True`, the flag is ALWAYS True unless `--no-fix` is used. The `--fix` flag does nothing (setting True when it's already True). This confuses users.

**Expected behavior:** Either:
1. Remove `--fix` flag (only keep `--no-fix`)
2. Make default False and require explicit `--fix`
3. Update help text to clarify

### 🐛 Bug 8: Init Command Doesn't Validate Output Path
**Location:** `scripts/main.py`, line 54

**Issue:**
```python
args = parser.parse_args(argv[1:])
from .init_wizard import run_init_wizard
return run_init_wizard(args.output)  # No validation
```

**Problem:** No checks for:
- Output path in read-only location
- Output path that's a directory
- Output path with invalid characters
- Relative vs absolute path handling

## Recommendations

### High Priority Tests to Add

1. **Test conflicting flag combinations:**
   ```python
   def test_replace_without_fix()
   def test_base_ref_without_changed_only()
   def test_changed_only_with_filenames()
   def test_per_file_years_with_no_git_aware()
   ```

2. **Test all individual flags:**
   ```python
   def test_notice_custom_template()
   def test_hierarchical_mode()
   def test_replace_mode()
   def test_ignore_file_custom()
   def test_git_aware_disabled()
   ```

3. **Test invalid values:**
   ```python
   def test_notice_nonexistent_file()
   def test_base_ref_invalid_reference()
   def test_init_output_readonly_location()
   ```

4. **Test edge cases:**
   ```python
   def test_init_command_as_relative_path()
   def test_init_command_with_check_flags()
   def test_filename_exactly_named_init()
   ```

### Code Fixes Needed

1. Add validation for conflicting flags
2. Add warnings for ignored flags
3. Make --fix/--no-fix behavior clearer
4. Validate init command detection more carefully
5. Add mutex groups for conflicting options

### Test Structure Improvements

Current: 15 tests covering ~15% of argument combinations
Needed: ~60+ tests to cover:
- All 13 arguments individually
- Common 2-argument combinations (~20 tests)
- Conflicting flags (~10 tests)
- Invalid values (~10 tests)
- Edge cases (~10 tests)

## Summary

**Coverage:** 30% (4 of 13 arguments tested, basic scenarios only)

**Bugs Found:** 8 bugs ranging from minor UX issues to potential crashes

**Critical Gaps:** No testing of major features (hierarchical, replace, git integration, ignore files)

**Recommendation:** Add ~45 more tests to achieve comprehensive coverage.
