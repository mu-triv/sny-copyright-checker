<!--
SPDX-License-Identifier: MIT
Copyright 2026 Sony Group Corporation
Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
License: For licensing see the License.txt file
-->

# Git-Aware Year Management

## Overview

The sny-copyright-checker now supports Git-aware year management, which intelligently handles copyright year ranges based on a file's Git history and modification status.

## Features

### 1. **Preserve Earliest Year**
The tool preserves the earliest copyright year from:
- Existing copyright notices in the file
- The file's first Git commit date (if available)

### 2. **Smart Year Range Updates**
The tool only extends the year range when a file has been modified:
- **Unchanged files**: Copyright years remain as-is
- **Modified files**: Year range extends to current year
- **New files**: Uses Git creation date as start year (if available)

### 3. **Automatic Fallback**
When Git is not available or a file is not in Git:
- Defaults to current year for new copyright notices
- Preserves existing copyright years for files with existing notices

## How It Works

### Year Determination Logic

1. **Files with existing copyright**:
   - Extract current year(s) from copyright notice
   - If file is unchanged in Git → preserve existing years
   - If file is modified → extend range to current year

2. **Files without copyright**:
   - Check Git history for file creation year
   - If file is modified → create year range (creation-current)
   - If file is unchanged → use creation year only
   - If not in Git → use current year

### Examples

#### Example 1: Preserving Years for Unchanged Files
```python
# File: utils.py
# Existing copyright: "Copyright 2020-2023 Company"
# Git status: unchanged
# Result: "Copyright 2020-2023 Company" (preserved)
```

#### Example 2: Extending Range for Modified Files
```python
# File: utils.py
# Existing copyright: "Copyright 2020-2023 Company"
# Git status: modified
# Current year: 2026
# Result: "Copyright 2020-2026 Company" (extended)
```

#### Example 3: New File with Git History
```python
# File: new_feature.py (no copyright)
# First Git commit: 2024
# Current year: 2026
# Git status: modified
# Result: "Copyright 2024-2026 Company"
```

#### Example 4: New File, Just Created
```python
# File: latest.py (no copyright)
# First Git commit: 2026
# Current year: 2026
# Git status: new/modified
# Result: "Copyright 2026 Company" (single year)
```

## Usage

### Default Behavior (Git-Aware Enabled)

```bash
# Git-aware mode is enabled by default
sny-copyright-checker file1.py file2.py
```

### Disable Git-Aware Mode

```bash
# Use current year for all files (legacy behavior)
sny-copyright-checker --no-git-aware file1.py file2.py
```

### Use with Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: copyright-check
        name: Check Copyright Notices
        entry: sny-copyright-checker
        language: system
        # Git-aware mode is automatic
        pass_filenames: true
```

## Command Line Options

### `--no-git-aware`
Disables Git-aware year management. When disabled:
- All new copyright notices use the current year
- Existing copyright years are not modified
- Git commands are not executed

```bash
sny-copyright-checker --no-git-aware *.py
```

### `--per-file-years` (New)
Controls whether to use project-wide or per-file year tracking.

**Default Behavior (Project-Wide Years)**:
```bash
# All files use project inception year as start
sny-copyright-checker file1.py file2.py

# Example: Project created in 2018
# All files get: Copyright 2018-2026 Company
```

**Per-File Years Mode**:
```bash
# Each file uses its own creation year
sny-copyright-checker --per-file-years file1.py file2.py

# Example: file1.py created in 2020, file2.py created in 2023
# file1.py: Copyright 2020-2026 Company
# file2.py: Copyright 2023-2026 Company
```

### Project-Wide vs Per-File Years

#### Project-Wide Mode (Default)

**Best for**:
- Projects where all code belongs to the same entity
- Consistent copyright dates across the entire codebase
- Simple year management

**Behavior**:
- Uses the year of the first project commit as the start year
- All files show the same start year (project inception)
- End year is always the current year for all files
- Example: If project created in 2018, all files get `2018-2026`

**Benefits**:
- ✅ Uniform copyright dates across project
- ✅ Clearly shows project age/history
- ✅ Simpler to explain and manage
- ✅ Less variation in copyright notices

#### Per-File Mode (`--per-file-years`)

**Best for**:
- Projects with files added at different times by different contributors
- Monorepos with components created at different dates
- Accurate per-file historical tracking

**Behavior**:
- Uses each file's first Git commit year as start
- Different files can have different start years
- Unchanged files preserve their existing year ranges
- Modified files extend to current year

**Benefits**:
- ✅ Accurate file-level history
- ✅ Minimal Git diff noise (unchanged files not updated)
- ✅ Reflects actual file creation dates

#### Comparison Examples

| Scenario | Project-Wide (Default) | Per-File Mode |
|----------|------------------------|---------------|
| Project created in 2018 | All files: `2018-2026` | - |
| file1.py added in 2020 | `2018-2026` | `2020-2026` |
| file2.py added in 2023 | `2018-2026` | `2023-2026` |
| file3.py added in 2026 (new) | `2018-2026` | `2026` |
| Unchanged file from 2020 | `2018-2026` | `2020` (preserved) |

## Benefits

### 1. **Accurate Copyright Dates**
- Reflects the actual creation and modification history
- Eliminates manual year updates

### 2. **Minimal Noise in Git Diffs**
- Unchanged files don't get year updates
- Reduces unnecessary file modifications

### 3. **Automatic Range Management**
- Automatically extends year ranges when files are modified
- Preserves historical start years

### 4. **Pre-commit Hook Friendly**
- Works seamlessly with pre-commit hooks
- Only updates years for files being committed

## Technical Details

### Git Commands Used

The tool uses the following Git commands:

1. **Get file creation year**:
   ```bash
   git log --follow --format=%aI --reverse -- <file>
   ```

2. **Check modification status**:
   ```bash
   git status --porcelain <file>
   ```

### Performance Considerations

- Git commands are executed only when Git-aware mode is enabled
- Results are cached during a single run
- Minimal performance impact for most workflows

### Error Handling

The tool gracefully handles various scenarios:
- Git not installed → Falls back to current year
- File not in Git → Uses current year for new notices
- Git command errors → Logged and gracefully handled

## Migration Guide

### From Non-Git-Aware to Git-Aware

If you're upgrading from a version without Git-aware support:

1. **First run**: The tool will preserve existing copyright years
2. **Modified files**: Years will be extended on next modification
3. **New files**: Will use Git creation dates automatically

No action required - the transition is seamless!

### Maintaining Legacy Behavior

If you prefer the old behavior (always use current year):

```bash
# Add --no-git-aware to your commands or scripts
sny-copyright-checker --no-git-aware *.py
```

Or create an alias:
```bash
alias copyright-check='sny-copyright-checker --no-git-aware'
```

## Troubleshooting

### Issue: Years not updating for modified files

**Cause**: Git may not recognize the file as modified if:
- Changes are already committed
- File is in `.gitignore`

**Solution**: Ensure file has uncommitted changes or use `--no-git-aware`

### Issue: Wrong creation year detected

**Cause**: File may have been:
- Moved/renamed in Git history
- Imported from another repository

**Solution**: The tool uses `git log --follow` to track renames. If issues persist, manually set the correct year in the file, and it will be preserved.

### Issue: Git commands are slow

**Cause**: Large repositories with extensive history

**Solution**:
- Use `--no-git-aware` for faster checks
- Run only on changed files: `--changed-only`

## Examples

### Check All Python Files with Git-Aware Mode
```bash
sny-copyright-checker *.py
```

### Check Only Modified Files
```bash
sny-copyright-checker --changed-only
```

### Disable Git-Aware for CI/CD
```bash
# In CI/CD where Git history might not be available
sny-copyright-checker --no-git-aware src/**/*.py
```

### Verbose Mode to See Year Decisions
```bash
sny-copyright-checker --verbose utils.py
# Output shows:
# DEBUG: File utils.py first committed in 2020
# DEBUG: File modified, updating years to: 2020-2026
```

## API Usage

```python
from scripts.copyright_checker import CopyrightChecker

# Enable Git-aware mode (default)
checker = CopyrightChecker("copyright.txt", git_aware=True)

# Disable Git-aware mode
checker = CopyrightChecker("copyright.txt", git_aware=False)

# Check files
passed, failed, modified = checker.check_files(["file1.py", "file2.py"])
```

## Best Practices

1. **Use in Pre-commit Hooks**: Ensures copyright years are always accurate before committing

2. **Enable Verbose Mode**: When debugging year issues, use `-v` to see decision-making

3. **Keep Git History Clean**: The more accurate your Git history, the better the year detection

4. **Don't Manually Edit Years**: Let the tool manage years automatically - it will preserve and extend them correctly

5. **Use `--changed-only`**: In large projects, only check changed files for better performance
