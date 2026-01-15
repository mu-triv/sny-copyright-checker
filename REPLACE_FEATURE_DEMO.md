<!--
SPDX-License-Identifier: MIT
Copyright 2026 Sony Group Corporation
Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
License: For licensing see the License.txt file
-->

# Test file showing all --replace scenarios

## Test File 1: test_replace.py
Original:
```python
# Copyright 2025 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file
```

After --replace:
```python
# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file
```

**Similarity: 0.84** - High similarity, replaced successfully

## Test File 2: test_replace2.py
Original:
```python
# Copyright (c) 2021-2022 Sony Group Corporation
# Author: Research & Development Center Europe, Sony Group Corporation
# License: For licensing see this MyOldLicense.txt file
```

After --replace:
```python
# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file
```

**Similarity: 0.40** - At threshold (40%), replaced successfully

## Test File 3: test_replace3.py
Original:
```python
# Copyright 2022 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
```

After --replace:
```python
# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file
```

**Similarity: 0.47** - Above threshold, replaced successfully

## Test File 4: test_year_merge.py
Original:
```python
# Copyright (c) 2021-2024 Sony Group Corporation
# Author: Research & Development Center Europe, Sony Group Corporation
# License: For licensing see the OldLicense.txt file
```

After --replace:
```python
# SPDX-License-Identifier: MIT
# Copyright 2021-2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file
```

**Year Range Merged: 2021-2024 → 2021-2026** - Years properly merged!

## How It Works

### Similarity Calculation
The `--replace` flag uses a multi-metric similarity algorithm that:
1. **Token Similarity (40%)**: Jaccard coefficient for entity matching
2. **N-gram Similarity (40%)**: Trigram comparison for typo tolerance
3. **Sequence Similarity (20%)**: LCS ratio for structural matching
4. Normalizes copyright text (removes years, special chars, whitespace)
5. Uses 40% overall similarity threshold to determine if copyrights are from the same entity

### Entity Protection
Before replacement:
1. Extracts organizational unit from Author field
2. Compares entity similarity (requires ≥70% match)
3. Prevents cross-unit replacement (e.g., Haptic Europe ≠ R&D Center)
4. Returns 0% similarity if entities don't match, blocking replacement

### Year Merging
When replacing copyrights:
1. Extracts existing year range from old copyright
2. Determines current year (2026)
3. Merges ranges: min(old_start, new_start) to max(old_end, current_year)
4. Result: Preserves history while updating to current year

### Usage
```bash
# Replace similar copyrights with template version
sny-copyright-check --replace --fix file1.py file2.py

# Check all changed files and replace
sny-copyright-check --replace --changed-only

# Verbose mode to see similarity scores
sny-copyright-check --replace --verbose files.py
```

## Test Coverage

The feature is tested with **98 comprehensive test cases**:
- ✅ 27 unit tests for core functionality
- ✅ 17 positive tests (same unit variations, year merging, license updates)
- ✅ 15 negative tests (different companies, Sony units protection)
- ✅ 28 edge case tests (unicode, whitespace, file types, block lengths)
- ✅ 11 stress tests (large files, batch processing, performance)

Run tests with: `pytest tests/test_replace_feature.py -v`
