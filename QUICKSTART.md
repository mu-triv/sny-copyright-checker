<!--
SPDX-License-Identifier: MIT
Copyright 2026 Sony Group Corporation
Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
License: For licensing see the License.txt file
-->

# SNY Copyright Check

## Quick Start Guide

### 1. Installation

#### Option A: Install from PyPI (Recommended)

```bash
pip install sny-copyright-checker
```

#### Option B: Install from source

```bash
git clone https://github.com/mu-triv/sny-copyright-checker.git
cd sny-copyright-checker
pip install -e .
```

### 2. Create Configuration (Easy Way)

Use the interactive wizard to create your `copyright.txt` configuration:

```bash
sny-copyright-checker init
```

The wizard will guide you through:
- Selecting a license (MIT, Apache, GPL, BSD, Proprietary, or Custom)
- Entering your company/organization name
- Choosing file extensions to support
- Generating a ready-to-use configuration

**That's it!** Your `copyright.txt` is ready to use.

For more details on the wizard, see [INIT_WIZARD.md](INIT_WIZARD.md).

### 2. Alternative: Manual Configuration

If you prefer to create `copyright.txt` manually, copy the example template from this repository to your project root and customize it with your company details.

### 3. Test the Tool

Create a test Python file without copyright:

```bash
# Create test file
echo "def hello():" > test.py
echo "    print('Hello')" >> test.py

# Run the checker
sny-copyright-checker test.py

# Check the file - it should now have a copyright notice!
type test.py
```

### 4. Use in Your Project

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: sny-copyright-checker
        name: SNY Copyright Check
        entry: python sny-copyright-check/scripts/main.py
        language: system
        types: [text]
        args: [--notice=copyright.txt]
```

### 5. Test Examples

#### Example 1: Python file without copyright
```python
# Before: test.py
def main():
    print("Hello")

# Run: python -m scripts.main test.py

# After: test.py
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

def main():
    print("Hello")
```

#### Example 2: Python file with shebang
```python
# Before: script.py
#!/usr/bin/env python
def main():
    pass

# Run: python -m scripts.main script.py

# After: script.py
#!/usr/bin/env python
# Copyright 2026 SNY Group Corporation
# Author: R&D Center Europe Brussels Laboratory, SNY Group Corporation
# License: For licensing see the License.txt file

def main():
    pass
```

#### Example 3: Check multiple files
```bash
sny-copyright-checker file1.py file2.sql file3.c
```

#### Example 4: Check only (no modifications)
```bash
sny-copyright-checker --no-fix *.py
```

#### Example 5: Check only changed files in git
```bash
# Check only files you've modified
sny-copyright-checker --changed-only

# Check changed files compared to main branch
sny-copyright-checker --changed-only --base-ref origin/main
```

#### Example 6: Existing copyrights are preserved
```python
# Before: old_file.py (with 2025 copyright)
# Copyright 2025 SNY Group Corporation
# Author: R&D Center Europe Brussels Laboratory, SNY Group Corporation
# License: For licensing see the License.txt file

def main():
    pass

# Run: sny-copyright-checker old_file.py

# After: old_file.py (UNCHANGED - existing copyright preserved)
# Copyright 2025 SNY Group Corporation
# Author: R&D Center Europe Brussels Laboratory, SNY Group Corporation
# License: For licensing see the License.txt file

def main():
    pass
```

### 5. Customize Copyright Template

Edit `copyright.txt` to add more file types or modify the copyright text.

#### Using Variables (Recommended):

Define common values once and reuse them:

```
[VARIABLES]
SPDX_LICENSE = MIT
COMPANY = Sony Group Corporation
AUTHOR = Your Team
YEAR_PATTERN = {regex:\d{4}(-\d{4})?}

[.js, .ts, .go, .rs]
// SPDX-License-Identifier: {SPDX_LICENSE}
// Copyright {YEAR_PATTERN} {COMPANY}
// Author: {AUTHOR}

[.py, .yaml, .yml]
# SPDX-License-Identifier: {SPDX_LICENSE}
# Copyright {YEAR_PATTERN} {COMPANY}
# Author: {AUTHOR}
```

**Benefits:**
- Change company name or license in ONE place
- SPDX compliance built-in
- Consistent across all file types

#### Grouped Extensions (Without Variables):

```
[.js, .ts, .go, .rs]
// Copyright {regex:\d{4}(-\d{4})?} Sony Group Corporation
// Author: Your Team

[.py, .yaml, .yml]
# Copyright {regex:\d{4}(-\d{4})?} Sony Group Corporation
# Author: Your Team
```

#### Single Extension Format:
```
[.rs]
// Copyright {regex:\d{4}(-\d{4})?} Sony Group Corporation
// Author: Your Team
```

### Troubleshooting

**Issue**: "Command 'sny-copyright-checker' not found"
**Solution**: Make sure you installed the package: `pip install sny-copyright-checker`

**Issue**: Copyright not being added
**Solution**: Check that the file extension is defined in `copyright.txt`

**Issue**: Want to see detailed logs
**Solution**: Use the `-v` flag: `sny-copyright-checker -v file.py`

### Command Line Options

```
sny-copyright-checker [OPTIONS] FILES...

Options:
  --notice FILENAME    Filename of copyright template (default: copyright.txt)
  --fix           Auto-add missing copyrights (default: True)
  --no-fix        Only check, don't modify files
  -v, --verbose   Show detailed output
  --changed-only  Check only changed files in git
  --base-ref REF  Git reference to compare against (default: HEAD)
```

### Integration with Pre-commit

For your `graphle_lib` project:

1. Copy `copyright.txt` to your project
2. Add to `.pre-commit-config.yaml`:

```yaml
  - repo: local
    hooks:
      - id: sny-copyright-checker
        name: SNY Copyright Check
        entry: python sny-copyright-checker/scripts/main.py
        language: system
        types: [text]
        pass_filenames: true
```

3. Install hooks: `pre-commit install`
4. Test: `pre-commit run --all-files`
