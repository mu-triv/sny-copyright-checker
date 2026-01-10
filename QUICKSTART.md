# Sony Copyright Check

## Quick Start Guide

### 1. Installation

```bash
cd C:\Users\bevuk\Documents\sny-copyright-check
pip install -e .
```

### 2. Test the Tool

Create a test Python file without copyright:

```bash
# Create test file
echo "def hello():" > test.py
echo "    print('Hello')" >> test.py

# Run the checker
python -m scripts.main test.py

# Check the file - it should now have a copyright notice!
type test.py
```

### 3. Use in Your Project

Copy the `copyright.txt` template to your project root, then add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: sony-copyright-check
        name: Sony Copyright Check
        entry: python C:/Users/bevuk/Documents/sny-copyright-check/scripts/main.py
        language: system
        types: [text]
        args: [--notice=copyright.txt]
```

### 4. Test Examples

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
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

def main():
    pass
```

#### Example 3: Check multiple files
```bash
python -m scripts.main file1.py file2.sql file3.c
```

#### Example 4: Check only (no modifications)
```bash
python -m scripts.main --no-fix *.py
```

### 5. Customize Copyright Template

Edit `copyright.txt` to add more file types or modify the copyright text:

```
[.rs]
// Copyright {regex:\d{4}(-\d{4})?} Sony Group Corporation
// Author: Your Team
// License: For licensing see the License.txt file

[.go]
// Copyright {regex:\d{4}(-\d{4})?} Sony Group Corporation
// Author: Your Team
// License: For licensing see the License.txt file
```

### Troubleshooting

**Issue**: "ModuleNotFoundError: No module named 'scripts'"
**Solution**: Make sure you're running from the project directory or have installed with `pip install -e .`

**Issue**: Copyright not being added
**Solution**: Check that the file extension is defined in `copyright.txt`

**Issue**: Want to see detailed logs
**Solution**: Use the `-v` flag: `python -m scripts.main -v file.py`

### Command Line Options

```
python -m scripts.main [OPTIONS] FILES...

Options:
  --notice PATH    Path to copyright template (default: copyright.txt)
  --fix           Auto-add missing copyrights (default: True)
  --no-fix        Only check, don't modify files
  -v, --verbose   Show detailed output
```

### Integration with Pre-commit

For your `graphle_lib` project:

1. Copy `copyright.txt` to your project
2. Add to `.pre-commit-config.yaml`:

```yaml
  - repo: local
    hooks:
      - id: sony-copyright
        name: Sony Copyright Check
        entry: python C:/Users/bevuk/Documents/sny-copyright-check/scripts/main.py
        language: system
        types: [text]
        pass_filenames: true
```

3. Install hooks: `pre-commit install`
4. Test: `pre-commit run --all-files`
