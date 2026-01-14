<!--
SPDX-License-Identifier: MIT
Copyright 2026 Sony Group Corporation
Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
License: For licensing see the License.txt file
-->

# Git-Aware Year Management - Quick Examples

## Example 1: File with Existing Copyright (Unchanged)

**Before:**
```python
# Copyright 2020-2024 Sony Group Corporation
def my_function():
    pass
```

**Git Status:** No changes

**After running sny-copyright-checker:**
```python
# Copyright 2020-2024 Sony Group Corporation  # ← PRESERVED
def my_function():
    pass
```

**Result:** Years unchanged because file has no modifications

---

## Example 2: File with Existing Copyright (Modified)

**Before:**
```python
# Copyright 2020-2024 Sony Group Corporation
def my_function():
    pass
```

**Git Status:** File has uncommitted changes

**Current Year:** 2026

**After running sny-copyright-checker:**
```python
# Copyright 2020-2026 Sony Group Corporation  # ← EXTENDED to 2026
def my_function():
    pass
```

**Result:** Year range extended because file was modified

---

## Example 3: New File (First Time in Git)

**Before:**
```python
def new_feature():
    pass
```

**Git History:** File created in 2024

**Git Status:** Modified/new

**Current Year:** 2026

**After running sny-copyright-checker:**
```python
# Copyright 2024-2026 Sony Group Corporation  # ← Uses creation year from Git
def new_feature():
    pass
```

**Result:** Start year from Git, end year from current year (because it's modified)

---

## Example 4: New File (Just Created, Same Year)

**Before:**
```python
def brand_new_feature():
    pass
```

**Git History:** File created today (2026)

**Current Year:** 2026

**After running sny-copyright-checker:**
```python
# Copyright 2026 Sony Group Corporation  # ← Single year (no range)
def brand_new_feature():
    pass
```

**Result:** Single year when creation year equals current year

---

## Example 5: File Not in Git

**Before:**
```python
def untracked_function():
    pass
```

**Git History:** File not tracked

**Current Year:** 2026

**After running sny-copyright-checker:**
```python
# Copyright 2026 Sony Group Corporation  # ← Uses current year
def untracked_function():
    pass
```

**Result:** Falls back to current year when Git info not available

---

## Example 6: Extending Single Year to Range

**Before:**
```python
# Copyright 2020 Sony Group Corporation
def old_function():
    pass
```

**Git Status:** File modified

**Current Year:** 2026

**After running sny-copyright-checker:**
```python
# Copyright 2020-2026 Sony Group Corporation  # ← Single year becomes range
def old_function():
    pass
```

**Result:** Single year automatically converts to range when file is modified

---

## Command Examples

### Enable Git-aware mode (default)
```bash
# Automatically uses Git to manage years
sny-copyright-checker my_file.py
```

### Disable Git-aware mode
```bash
# Always uses current year (legacy behavior)
sny-copyright-checker --no-git-aware my_file.py
```

### Check only changed files
```bash
# Only processes files with Git changes
sny-copyright-checker --changed-only
```

### Verbose mode (see year decisions)
```bash
# Shows detailed information about year management
sny-copyright-checker --verbose my_file.py
```

Output example:
```
DEBUG: File my_file.py first committed in 2020
DEBUG: File modified, updating years to: 2020-2026
INFO: Adding copyright notice to: my_file.py
```

---

## Benefits Summary

✅ **Accurate History**: Copyright reflects actual file creation and modification dates

✅ **Minimal Git Noise**: Unchanged files don't get year updates, keeping diffs clean

✅ **Automatic Management**: No manual year updates needed

✅ **Smart Defaults**: Falls back gracefully when Git is unavailable

✅ **Backward Compatible**: Existing copyrights are preserved and extended appropriately
