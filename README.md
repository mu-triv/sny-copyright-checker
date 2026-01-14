<!--
SPDX-License-Identifier: MIT
Copyright 2026 Sony Group Corporation
Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
License: For licensing see the License.txt file
-->

# SNY Copyright Check - Pre-commit Hook

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![PyPI version](https://badge.fury.io/py/sny-copyright-checker.svg)](https://badge.fury.io/py/sny-copyright-checker)
[![Tests](https://github.com/mu-triv/sny-copyright-checker/workflows/Tests/badge.svg)](https://github.com/mu-triv/sny-copyright-checker/actions)

A powerful [pre-commit](https://pre-commit.com/) hook to automatically check and add copyright notices to your source files with support for multiple file formats and regex patterns.

## Features

✨ **Multi-Format Support**: Define different copyright formats for different file extensions (`.py`, `.c`, `.sql`, etc.)

🔍 **Regex Pattern Matching**: Use regex patterns in your copyright templates to match year ranges (e.g., `2024`, `2024-2026`)

🔧 **Auto-Fix**: Automatically adds missing copyright notices with the current year

📝 **Flexible Templates**: Section-based template file for easy maintenance

🎯 **Smart Insertion**: Respects shebang lines and file structure

🔄 **Line Ending Preservation**: Automatically detects and preserves CRLF (Windows) or LF (Unix/Linux) line endings

🎯 **Git Integration**: Check only changed files with `--changed-only` flag

✅ **Non-Destructive**: Existing copyrights are preserved, even with old years - no duplicates created

🎓 **Git-Aware Year Management**: Intelligently manages copyright years based on Git history
   - Preserves earliest year from file creation or existing copyright
   - Extends year range only when files are modified
   - Reduces noise in Git diffs by not updating unchanged files

🚫 **Ignore Files Support**: Respect `.copyrightignore` and `.gitignore` patterns
   - Skip generated files, vendor code, and build artifacts
   - Gitignore-style pattern matching
   - Flexible ignore rules per project

## Installation

### Via pip (Recommended)

Install directly from PyPI:

```bash
pip install sny-copyright-checker
```

### As a pre-commit hook

Add the following to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/mu-triv/sny-copyright-checker
    rev: v1.0.3  # Use the latest release
    hooks:
      - id: sny-copyright-checker
        args: [--notice=copyright.txt]
```

Then install the hook:

```bash
pre-commit install
```

### From source

```bash
git clone https://github.com/mu-triv/sny-copyright-checker.git
cd sny-copyright-checker
pip install -e .
```

## Usage

### As a Pre-commit Hook

Once installed, the hook will automatically run when you commit files:

```bash
git add my_file.py
git commit -m "Add new feature"
# Hook will check and add copyright notice if missing
```

### Command Line

You can also run the tool directly:

```bash
# Check and auto-fix files
sny-copyright-checker file1.py file2.sql file3.c

# Check only (no modifications)
sny-copyright-checker --no-fix file1.py

# Specify custom template file
sny-copyright-checker --notice=my_copyright.txt *.py

# Verbose output
sny-copyright-checker -v file1.py

# Check only changed files in git
sny-copyright-checker --changed-only

# Check changed files compared to main branch
sny-copyright-checker --changed-only --base-ref origin/main
```

### Command Line Options

- `filenames`: Files to check for copyright notices
- `--notice PATH`: Path to copyright template file (default: `copyright.txt`)
- `--fix`: Automatically add missing copyright notices (default: enabled)
- `--no-fix`: Only check without modifying files
- `--verbose, -v`: Enable verbose output
- `--changed-only`: Only check files that have been changed in git (ignores filenames argument)
- `--base-ref REF`: Git reference to compare against when using `--changed-only` (default: HEAD)
- `--no-git-aware`: Disable Git-aware year management (default: Git-aware is enabled)
- `--ignore-file PATH`: Path to custom ignore file (default: auto-detect `.copyrightignore`)
- `--no-gitignore`: Don't use `.gitignore` patterns (default: `.gitignore` is used)

### Git-Aware Year Management

By default, the tool uses Git history to intelligently manage copyright years:
- **Preserves** the earliest year from file creation or existing copyright
- **Extends** the year range only when files are actually modified
- **Reduces** unnecessary changes to unchanged files

See [GIT_AWARE_YEAR_MANAGEMENT.md](GIT_AWARE_YEAR_MANAGEMENT.md) for detailed information.

### Ignore Files Support

The tool respects ignore patterns to skip generated files, vendor code, and build artifacts.

For detailed documentation on ignore patterns, see [IGNORE_FILES.md](IGNORE_FILES.md).

#### Quick Start

Create a `.copyrightignore` file in your project root:

```
# Ignore generated files
**/generated/
*.min.js
*.bundle.js

# Ignore vendor/third-party code
node_modules/
vendor/
third_party/

# Ignore build artifacts
dist/
build/
*.pyc
__pycache__/
```

#### Using .gitignore

By default, patterns from `.gitignore` are also respected. To disable this:

```bash
sny-copyright-checker --no-gitignore *.py
```

#### Pattern Syntax

Supports standard gitignore-style patterns:
- `*.ext` - Match files with extension
- `dir/` - Match entire directory
- `**/pattern` - Match in any directory
- `path/*.js` - Match files in specific path
- `# comment` - Comments (ignored)

## Copyright Template Format

The template file uses a section-based format with regex support and template variables for maximum maintainability.

### Using Variables (Recommended)

Define common values once in a `[VARIABLES]` section and reuse them throughout your template:

```
[VARIABLES]
SPDX_LICENSE = MIT
COMPANY = Sony Group Corporation
AUTHOR = R&D Center Europe Brussels Laboratory, Sony Group Corporation
YEAR_PATTERN = {regex:\d{4}(-\d{4})?}

[.py, .yaml, .yml]
# SPDX-License-Identifier: {SPDX_LICENSE}
# Copyright {YEAR_PATTERN} {COMPANY}
# Author: {AUTHOR}
# License: For licensing see the License.txt file

[.js, .ts, .go, .rs]
// SPDX-License-Identifier: {SPDX_LICENSE}
// Copyright {YEAR_PATTERN} {COMPANY}
// Author: {AUTHOR}
// License: For licensing see the License.txt file
```

**Benefits:**
- ✅ **DRY Principle**: Change company name or license in one place
- ✅ **SPDX Support**: Easy to add [SPDX License Identifiers](https://spdx.dev/learn/handling-license-info/)
- ✅ **Consistency**: All file types use the same information
- ✅ **Flexibility**: Different projects can have different licenses

### Traditional Format (Also Supported)

You can also use the format without variables:

```
[.py, .yaml, .yml]
# Copyright {regex:\d{4}(-\d{4})?} Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file
```

### Template Syntax

- **Variables Section**: `[VARIABLES]` - Define reusable values
  - Format: `VARIABLE_NAME = value`
  - Use in templates: `{VARIABLE_NAME}`
  - Example: `COMPANY = Sony Group Corporation`, then use `{COMPANY}`
- **Section Headers**:
  - Single extension: `[.extension]` (e.g., `[.py]`, `[.sql]`)
  - Multiple extensions: `[.ext1, .ext2, .ext3]` (e.g., `[.js, .ts, .go]`)
  - All extensions in a grouped header will use the same copyright format
- **Regex Patterns**: `{regex:PATTERN}` allows regex matching
  - Example: `{regex:\d{4}(-\d{4})?}` matches `2024` or `2024-2026`
  - Can be stored in a variable: `YEAR_PATTERN = {regex:\d{4}(-\d{4})?}`
- **Auto-insertion**: When adding a copyright, the regex pattern is replaced with the current year

### SPDX License Identifiers

The tool fully supports [SPDX license identifiers](https://spdx.dev/learn/handling-license-info/). Simply add them to your template:

```
[VARIABLES]
SPDX_LICENSE = Apache-2.0 OR MIT

[.py]
# SPDX-License-Identifier: {SPDX_LICENSE}
# Copyright {regex:\d{4}} {COMPANY}
```

Common SPDX identifiers: `MIT`, `Apache-2.0`, `GPL-3.0-only`, `BSD-3-Clause`, etc.

### Grouping Extensions

To reduce duplication and improve maintainability, group extensions that share the same comment syntax:

- **Hash comments**: `[.py, .yaml, .yml, .sh]` → `#` style
- **C-style line comments**: `[.js, .ts, .go, .rs, .java]` → `//` style
- **C block comments**: `[.c, .h, .cpp]` → `/* */` style
- **SQL comments**: `[.sql]` → `--` style
- **HTML comments**: `[.md, .html, .xml]` → `<!-- -->` style

### Supported Regex Patterns

The template includes regex patterns for year matching:
- `\d{4}`: Matches a single year (e.g., `2024`)
- `\d{4}-\d{4}`: Matches a year range (e.g., `2024-2026`)
- `\d{4}(-\d{4})?`: Matches either format

## Example

### Before

```python
#!/usr/bin/env python

def hello():
    print("Hello, World!")
```

### After (Auto-fixed)

```python
#!/usr/bin/env python
# Copyright 2026 SNY Group Corporation
# Author: R&D Center Europe Brussels Laboratory, SNY Group Corporation
# License: For licensing see the License.txt file

def hello():
    print("Hello, World!")
```

## How It Works

1. **Template Parsing**: Reads and parses the section-based template file
2. **File Extension Matching**: Determines which copyright template to use based on file extension
3. **Pattern Matching**: Uses regex to check if a valid copyright notice exists
4. **Copyright Detection**: If a valid copyright exists (even with an old year like 2025), the file is left unchanged
5. **Auto-Insertion**: If missing and `--fix` is enabled, adds the copyright notice with the current year
6. **Smart Positioning**: Respects shebang lines and inserts the notice appropriately
7. **Line Ending Preservation**: Automatically detects and preserves the original line ending style (CRLF or LF)
8. **Git Integration**: Optionally checks only files that have been modified in your git repository

## File Extensions Support

By default, the included `copyright.txt` supports:
- Python (`.py`)
- SQL (`.sql`)
- C/C++ (`.c`, `.cpp`, `.h`)
- JavaScript/TypeScript (`.js`, `.ts`)
- Java (`.java`)
- Shell scripts (`.sh`)
- Go (`.go`)
- Rust (`.rs`)
- YAML (`.yaml`, `.yml`)
- Markdown (`.md`)

You can easily add more by editing the `copyright.txt` file.

## Important Behavior

### Copyright Preservation
- **Existing copyrights are never replaced**: If a file already has a valid copyright notice (even from an old year like 2025), it will be left unchanged
- **No duplicates created**: Running the tool multiple times will not create duplicate copyright notices
- **Year matching**: The regex pattern `{regex:\d{4}(-\d{4})?}` matches any year or year range, ensuring old copyrights are recognized

### Line Ending Handling
- **Automatic detection**: The tool automatically detects whether your files use CRLF (Windows) or LF (Unix/Linux) line endings
- **Preservation**: Original line endings are preserved when adding copyright notices
- **Cross-platform compatibility**: Works seamlessly on Windows, Linux, and macOS

### Git Integration
When using `--changed-only`:
- Only files tracked by git and currently modified (staged or unstaged) are checked
- Files must have a supported extension
- Deleted files are automatically excluded
- Works with files in subdirectories

## Configuration

### Customizing Templates

Edit your `copyright.txt` file to add or modify copyright formats:

```
[.your_extension]
Your copyright format here
With multiple lines
And {regex:\d{4}} for year matching
```

### Pre-commit Configuration

Customize the pre-commit hook behavior with various arguments:

#### Basic Configuration

```yaml
- repo: https://github.com/mu-triv/sny-copyright-checker
  rev: v1.0.3
  hooks:
    - id: sny-copyright-checker
      args: [--notice=copyright.txt]
```

#### Check Only (No Auto-fix)

Run the checker without automatically adding copyright notices:

```yaml
- repo: https://github.com/mu-triv/sny-copyright-checker
  rev: v1.0.3
  hooks:
    - id: sny-copyright-checker
      args: [--no-fix, --notice=copyright.txt]
```

#### Verbose Output

Enable detailed output for debugging:

```yaml
- repo: https://github.com/mu-triv/sny-copyright-checker
  rev: v1.0.3
  hooks:
    - id: sny-copyright-checker
      args: [--verbose, --notice=copyright.txt]
```

#### Check Only Changed Files

Check only files modified compared to a specific git reference:

```yaml
- repo: https://github.com/mu-triv/sny-copyright-checker
  rev: v1.0.3
  hooks:
    - id: sny-copyright-checker
      args: [--changed-only, --base-ref=origin/main, --notice=copyright.txt]
```

#### Limit to Specific File Types

Only run on specific file types using the `files` regex:

```yaml
- repo: https://github.com/mu-triv/sny-copyright-checker
  rev: v1.0.3
  hooks:
    - id: sny-copyright-checker
      args: [--notice=copyright.txt]
      files: \.(py|sql|c|cpp)$
```

#### Combined Configuration

Combine multiple options:

```yaml
- repo: https://github.com/mu-triv/sny-copyright-checker
  rev: v1.0.3
  hooks:
    - id: sny-copyright-checker
      args: [--verbose, --notice=config/copyright.txt, --changed-only]
      files: \.(py|js|ts|java)$
```

#### Multiple Hooks with Different Configurations

Run separate hooks for different scenarios:

```yaml
repos:
  - repo: https://github.com/mu-triv/sny-copyright-checker
    rev: v1.0.3
    hooks:
      # Auto-fix Python files only
      - id: sny-copyright-checker
        name: Copyright Check (Python - Auto-fix)
        args: [--notice=copyright.txt]
        files: \.py$

      # Check-only for C/C++ files
      - id: sny-copyright-checker
        name: Copyright Check (C/C++ - Check Only)
        args: [--no-fix, --notice=copyright.txt, --verbose]
        files: \.(c|cpp|h)$
```

## Development

### Setting Up Development Environment

```bash
git clone https://github.com/mu-triv/sny-copyright-checker.git
cd sny-copyright-checker
pip install -e .
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=scripts --cov-report=term

# Run specific test file
pytest tests/test_copyright_checker.py -v
```

### Continuous Integration

The project uses GitHub Actions for CI/CD:

- **Tests**: Runs on Python 3.10-3.12 across Ubuntu, Windows, and macOS
- **Code Quality**: Checks with flake8, black, and isort
- **Coverage**: Generates test coverage reports

The workflow automatically runs on:
- Every push to the `main` branch
- Every pull request targeting `main`

### Project Structure

```
sny-copyright-checker/
├── scripts/
│   ├── __init__.py
│   ├── main.py                      # Entry point
│   ├── copyright_checker.py         # Main checker logic
│   └── copyright_template_parser.py # Template parser
├── tests/                            # Test files
├── .pre-commit-hooks.yaml           # Pre-commit hook definition
├── .pre-commit-config.yaml          # Example pre-commit config
├── copyright.txt                     # Example copyright template
├── pyproject.toml                   # Project metadata
├── setup.py                         # Setup script
├── LICENSE                          # MIT License
└── README.md                        # This file
```

## Comparison with Similar Tools

### vs. copyright_notice_precommit

While inspired by [leoll2/copyright_notice_precommit](https://github.com/leoll2/copyright_notice_precommit), this project adds:

1. **Multi-format support**: Different copyright formats for different file types
2. **Regex matching**: Flexible year range matching
3. **Auto-insertion**: Automatically adds missing copyright notices
4. **Section-based templates**: Easier to maintain multiple formats

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Known Issues and Limitations

### Template Changes May Create Duplicate Copyrights

**Issue**: When you update your `copyright.txt` template and re-run the checker on files that already have a copyright, it may add a second copyright notice instead of recognizing the existing one.

**Why**: The checker uses strict template matching. If the copyright format changes (e.g., different company name, license identifier, or text), the old copyright no longer matches the new template and is considered "missing."

**Example Scenario**:
```python
# Original copyright (Company A)
# Copyright 2025 Company A
# License: MIT

def hello():
    pass
```

After updating `copyright.txt` to use Company B and re-running:
```python
# Copyright 2026 Company B      # <- New copyright added
# SPDX-License-Identifier: Apache-2.0

# Copyright 2025 Company A      # <- Old copyright still present
# License: MIT

def hello():
    pass
```

**Workarounds**:
1. **Manual cleanup**: Before changing templates, manually remove or update existing copyrights
2. **Test first**: Run checker in check-only mode (`--no-fix`) to see which files would be modified
3. **Selective application**: Use git to only apply checker to new/modified files
4. **Batch find-replace**: Use text editor to update existing copyrights before running checker

**Future Enhancement**: A `--replace` mode could be added to detect and replace any copyright-like headers, not just exact template matches.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Tri VU Khac (khactri.vu@sony.com)<br>
SONY Group Corporation<br>
R&D Center Europe Brussels Laboratory<br>

## Acknowledgments

- Inspired by [leoll2/copyright_notice_precommit](https://github.com/leoll2/copyright_notice_precommit)
- Built for use with [pre-commit](https://pre-commit.com/)

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/mu-triv/sny-copyright-checker).
