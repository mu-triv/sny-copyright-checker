<!--
SPDX-License-Identifier: MIT
Copyright 2026 Sony Group Corporation
Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
License: For licensing see the License.txt file
-->

# Copyright Replacement Feature (`--replace`)

## Overview

The `--replace` flag enables intelligent replacement of existing similar copyright notices with your standardized template. This feature uses similarity matching to identify copyrights from the same business entity, even when they have variations in formatting, wording, or licensing details.

## Key Features

### 1. Similarity-Based Matching
- Uses multi-metric similarity algorithm combining:
  - **Token similarity** (40%): Jaccard coefficient for entity matching
  - **N-gram similarity** (40%): Trigram comparison for typo tolerance
  - **Sequence similarity** (20%): LCS ratio for structural matching
- Threshold of 40% overall similarity to identify related copyrights
- Focuses on business entity name and structure, ignoring years and special characters
- Normalizes text for accurate comparison (case-insensitive, whitespace-normalized)

### 2. **Critical: Organizational Unit Protection**
**Prevents replacing copyrights from different units within the same company.**

The feature extracts and compares the specific organizational unit/department from the Author field to ensure copyrights from different entities are never replaced:

```python
# These different Sony units will NOT replace each other:
Author: R&D Center Europe Brussels Laboratory  # Will NOT replace ↓
Author: Haptic Europe, Brussels Laboratory     # Different unit
Author: NSCE, Brussels Laboratory              # Different unit
Author: MSE Laboratory                         # Different unit
Author: Entertainment Europe, Brussels Lab     # Different unit
```

- **70% entity match threshold**: Author entities must match closely (≥70%)
- Protects against cross-unit replacement even within the same company
- Extracts key unit identifiers (e.g., "R&D Center Europe", "Haptic Europe", "NSCE")
- Returns similarity of 0.0 if entities don't match, preventing replacement

### 2. **Critical: Organizational Unit Protection**
**Prevents replacing copyrights from different units within the same company.**

The feature extracts and compares the specific organizational unit/department from the Author field to ensure copyrights from different entities are never replaced:

```python
# These different Sony units will NOT replace each other:
Author: R&D Center Europe Brussels Laboratory  # Will NOT replace ↓
Author: Haptic Europe, Brussels Laboratory     # Different unit
Author: NSCE, Brussels Laboratory              # Different unit
Author: MSE Laboratory                         # Different unit
Author: Entertainment Europe, Brussels Lab     # Different unit
```

- **70% entity match threshold**: Author entities must match closely (≥70%)
- Protects against cross-unit replacement even within the same company
- Extracts key unit identifiers (e.g., "R&D Center Europe", "Haptic Europe", "NSCE")
- Returns similarity of 0.0 if entities don't match, preventing replacement

### 3. Intelligent Year Merging
- Extracts existing year ranges from old copyrights
- Merges with current year to preserve copyright history
- Examples:
  - `2021-2024` → `2021-2026` (extends to current year)
  - `2023` → `2023-2026` (creates range)
  - Respects Git history when available

### 4. Flexible Year Extraction
- Template-based extraction using regex patterns
- Fallback to general year pattern matching
- Handles various formats:
  - `Copyright 2024`
  - `Copyright (c) 2021-2024`
  - `© 2022-2025`

## Usage

### Basic Usage

```bash
# Replace similar copyrights in specific files
sny-copyright-check --replace file1.py file2.py

# Replace in all changed files (Git-aware)
sny-copyright-check --replace --changed-only

# Verbose mode to see similarity scores
sny-copyright-check --replace --verbose files.py
```

### Requirements

The `--replace` flag requires `--fix` to be enabled (which is the default). If you use `--no-fix`, replacement will not occur.

```bash
# This works (--fix is default)
sny-copyright-check --replace file.py

# This won't replace (explicitly disabled)
sny-copyright-check --replace --no-fix file.py
```

## How It Works

### Similarity Calculation Process

1. **Normalization**: Both copyrights are normalized:
   - Remove years (4-digit numbers and ranges)
   - Remove copyright symbols (©, (c), etc.)
   - Remove common keywords (Copyright, Author, License, etc.)
   - Normalize whitespace
   - Convert to lowercase

2. **Tokenization**: Text is split into words/tokens

3. **Jaccard Similarity**: Calculate intersection over union
   ```
   similarity = len(tokens1 ∩ tokens2) / len(tokens1 ∪ tokens2)
   ```

4. **Threshold Check**: If similarity ≥ 0.4 (40%), copyrights are considered related

### Example Similarity Scores

#### High Similarity (>70%)
```python
# Original
# Copyright 2025 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

# Template
# SPDX-License-Identifier: MIT
# Copyright YEAR Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

# Similarity: 0.84 (84%) ✓ Will replace
```

#### Medium Similarity (40-70%)
```python
# Original
# Copyright (c) 2021-2022 Sony Group Corporation
# Author: Research & Development Center Europe, Sony Group Corporation
# License: For licensing see this MyOldLicense.txt file

# Template
# SPDX-License-Identifier: MIT
# Copyright YEAR Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

# Similarity: 0.46 (46%) ✓ Will replace
```

#### Low Similarity (<40%)
```python
# Original
# Copyright 2024 Different Company Inc.
# All Rights Reserved

# Template
# SPDX-License-Identifier: MIT
# Copyright YEAR Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory

# Similarity: 0.15 (15%) ✗ Won't replace (will add new copyright)
```

## Year Merging Logic

### For Files in Git

```
Existing: 2021-2024
File Creation (Git): 2020
File Modified: Yes
Current Year: 2026

Result: 2020-2026  (min(2021, 2020) to max(2024, 2026))
```

### For Files Not in Git

```
Existing: 2021-2024
File Modified: Yes (untracked files are considered "modified")
Current Year: 2026

Result: 2021-2026  (preserves existing start, extends to current)
```

### For Unchanged Files

```
Existing: 2021-2024
File Modified: No
Current Year: 2026

Result: 2021-2024  (preserves existing range unchanged)
```

## Integration with Other Features

### Git-Aware Mode (Default)
```bash
# Replace mode works with Git-aware year management
sny-copyright-check --replace --changed-only
```

When combined with `--git-aware` (default), the replacement feature:
- Uses Git history to determine file creation year
- Checks if files are modified
- Merges year ranges intelligently based on Git state

### Hierarchical Templates
```bash
# Replace mode with hierarchical templates
sny-copyright-check --replace --hierarchical
```

Works with hierarchical template discovery, allowing different templates in different directories.

### Ignore Patterns
```bash
# Replace mode respects .copyrightignore and .gitignore
sny-copyright-check --replace --fix
```

Ignored files are skipped by the replacement logic.

## Examples

### Example 1: Standardizing Legacy Copyrights

Before:
```python
# File1.py
# Copyright 2020 Sony Group Corporation
# Author: Old Department Name

# File2.py
# Copyright (c) 2021 Sony Group Corporation
# License: See LICENSE file

# File3.py
# © 2022-2023 Sony Group Corporation
```

Command:
```bash
sny-copyright-check --replace --verbose File1.py File2.py File3.py
```

After:
```python
# All files now have:
# SPDX-License-Identifier: MIT
# Copyright 2020-2026 Sony Group Corporation  # (year ranges vary per file)
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file
```

### Example 2: Batch Update with Git

```bash
# Replace copyrights in all changed files
sny-copyright-check --replace --changed-only --verbose
```

### Example 3: Dry Run (Check Without Modifying)

```bash
# See what would be replaced without making changes
sny-copyright-check --replace --no-fix --verbose file.py
```

This will log similarity scores and indicate which files would be replaced.

## Troubleshooting

### Copyright Not Being Replaced

**Problem**: File has copyright but it's not being replaced

**Possible Causes**:
1. **Similarity too low** (<40%)
   - Check similarity score with `--verbose`
   - The copyrights may be too different

2. **No copyright block detected**
   - The copyright format might not be recognized
   - Ensure it uses comment syntax matching the file type

3. **Copyright matches template exactly**
   - If the copyright already matches the template, no replacement occurs

### Years Not Merging Correctly

**Problem**: Year range not preserved or extended

**Check**:
1. Enable `--verbose` to see extracted years
2. Verify Git history exists for the file
3. Check if file is tracked by Git
4. Ensure `--git-aware` is enabled (default)

### Unwanted Replacements

**Problem**: Copyrights being replaced when they shouldn't

**Solutions**:
1. Adjust your template to be more specific
2. Use `--no-fix` to preview changes first
3. Consider using `.copyrightignore` for specific files

## Best Practices

1. **Test First**: Run with `--verbose --no-fix` to preview changes
2. **Use Git**: Commit your changes before running `--replace` for easy rollback
3. **Review Changes**: Check diffs after replacement to ensure correctness
4. **Incremental Updates**: Start with a subset of files to validate behavior
5. **Backup Important Files**: For critical codebases, make backups first

## API Usage

For programmatic use:

```python
from scripts.copyright_checker import CopyrightChecker

# Enable replace mode
checker = CopyrightChecker(
    template_path="copyright.txt",
    git_aware=True,
    replace_mode=True
)

# Check and replace
has_notice, was_modified = checker.check_file("file.py", auto_fix=True)

if was_modified:
    print("Copyright was replaced")
```

## Related Configuration

The replacement feature respects all standard configuration:
- `--notice`: Template file path
- `--git-aware`/`--no-git-aware`: Git integration
- `--hierarchical`: Hierarchical template discovery
- `--ignore-file`: Custom ignore patterns
- `--use-gitignore`/`--no-gitignore`: Respect .gitignore

## Testing

The replacement feature is extensively tested with **98 comprehensive test cases** covering:

### Test Categories

1. **Unit Tests (27 tests)**: Core functionality testing
   - Similarity calculation algorithms
   - Year extraction and range merging
   - Copyright block extraction
   - Entity identification and matching
   - Code preservation during replacement

2. **Positive Tests (17 parametrized cases)**: Replacement scenarios
   - Same unit with variations (abbreviations, formatting)
   - Year range merging with different starting years
   - License reference updates

3. **Negative Tests (15 parametrized cases)**: Protection scenarios
   - Different companies (Microsoft, Google, Amazon, Meta, Apple)
   - Different Sony organizational units (10 different units tested)

4. **Edge Cases (28 parametrized cases)**: Unusual scenarios
   - Unicode characters in author names (6 languages)
   - Various whitespace patterns (tabs, extra spaces)
   - Different copyright block lengths
   - Multiple file types (.py, .cpp, .c, .java, .js)

5. **Stress Tests (11 parametrized cases)**: Performance and robustness
   - Large files (up to 10,000 lines)
   - Batch processing (10-50 files)
   - Similarity calculation performance
   - Complex year extraction patterns

### Running Tests

```bash
# Run all tests
pytest tests/test_replace_feature.py

# Run specific test categories
pytest tests/test_replace_feature.py -k "parametrized"
pytest tests/test_replace_feature.py -k "positive"
pytest tests/test_replace_feature.py -k "negative"
pytest tests/test_replace_feature.py -k "stress"

# Run with verbose output
pytest tests/test_replace_feature.py -v

# Skip slow tests
pytest tests/test_replace_feature.py -m "not slow"
```

### Test Coverage

The test suite uses **pytest parametrize** for efficient coverage:
- Multiple test variations from single test functions
- Easy to extend with new test cases
- Clear test names showing exact parameters tested
- Comprehensive validation of all feature aspects

## See Also

- [Git-Aware Year Management](GIT_AWARE_YEAR_MANAGEMENT.md)
- [Hierarchical Templates](HIERARCHICAL_TEMPLATES.md)
- [Ignore Files](IGNORE_FILES.md)
- [Quick Start Guide](QUICKSTART.md)
