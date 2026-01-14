<!--
SPDX-License-Identifier: MIT
Copyright 2026 Sony Group Corporation
Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
License: For licensing see the License.txt file
-->

# Ignore Files Support

## Overview

The sny-copyright-checker supports ignoring files and directories using `.copyrightignore` and `.gitignore` patterns. This allows you to skip generated files, vendor code, build artifacts, and other files that shouldn't have copyright notices.

## Features

- **Gitignore-style patterns**: Uses the same pattern syntax as `.gitignore`
- **Multiple sources**: Combines patterns from `.copyrightignore` and `.gitignore`
- **Flexible control**: Enable/disable `.gitignore` support as needed
- **Custom ignore files**: Specify custom ignore file paths

## Quick Start

### Create `.copyrightignore`

Create a `.copyrightignore` file in your project root:

```
# Generated files
**/generated/
*.min.js
*.min.css
*.bundle.js

# Vendor/third-party code
node_modules/
vendor/
third_party/

# Build artifacts
dist/
build/
*.pyc
__pycache__/
```

### Run the checker

```bash
# Automatically uses .copyrightignore and .gitignore
sny-copyright-checker src/**/*.py

# Disable .gitignore patterns
sny-copyright-checker --no-gitignore src/**/*.py

# Use custom ignore file
sny-copyright-checker --ignore-file .custom-ignore src/**/*.py
```

## Pattern Syntax

The ignore files use gitignore-style pattern matching:

### Basic Patterns

| Pattern | Description | Example Matches |
|---------|-------------|-----------------|
| `file.txt` | Exact filename | `file.txt` |
| `*.js` | All files with extension | `app.js`, `test.js` |
| `*.min.*` | Multiple extensions | `app.min.js`, `style.min.css` |
| `dir/` | Entire directory | All files in `dir/` |
| `dir/*.py` | Files in directory | `dir/test.py` |

### Advanced Patterns

| Pattern | Description | Example Matches |
|---------|-------------|-----------------|
| `**/generated/` | Directory anywhere | `src/generated/`, `test/generated/` |
| `**/node_modules/` | Nested directories | Any `node_modules/` folder |
| `**/*.min.js` | Files in any location | `src/app.min.js`, `dist/bundle.min.js` |
| `build/**` | All files under directory | Everything in `build/` recursively |

### Comments and Empty Lines

```
# This is a comment - ignored
  # Indented comments work too

# Empty lines are ignored

*.pyc  # Inline comments are NOT supported
```

## Usage Examples

### Example 1: Python Project

`.copyrightignore`:
```
# Generated files
**/__pycache__/
*.pyc
*.pyo
*.pyd

# Build directories
build/
dist/
*.egg-info/

# Virtual environments
venv/
.venv/
env/

# Generated documentation
docs/_build/
docs/_static/
docs/_templates/
```

### Example 2: JavaScript/Node.js Project

`.copyrightignore`:
```
# Dependencies
node_modules/
bower_components/

# Build output
dist/
build/
coverage/

# Minified files
*.min.js
*.min.css
*.bundle.js

# Source maps
*.map

# Lock files
package-lock.json
yarn.lock
```

### Example 3: Mixed Project

`.copyrightignore`:
```
# Generated code (all languages)
**/generated/
**/auto-generated/
*.generated.*

# Vendor/third-party
vendor/
third_party/
external/

# Build artifacts
build/
dist/
out/
target/

# Language-specific
*.pyc
*.class
*.o
*.so
*.dll
```

### Example 4: Using Both .copyrightignore and .gitignore

`.copyrightignore`:
```
# Copyright-specific ignores
# Files that are tracked in git but shouldn't have copyrights
LICENSE
README.md
docs/
examples/external/
```

`.gitignore`:
```
# Build outputs (automatically ignored)
*.pyc
__pycache__/
node_modules/
```

Both patterns are combined automatically!

## Command Line Options

### Using .gitignore (Default)

```bash
# Both .copyrightignore and .gitignore are used
sny-copyright-checker src/
```

### Disable .gitignore

```bash
# Only use .copyrightignore
sny-copyright-checker --no-gitignore src/
```

### Custom Ignore File

```bash
# Use a custom ignore file instead of .copyrightignore
sny-copyright-checker --ignore-file .my-ignore src/
```

### Combine Options

```bash
# Custom ignore file + no gitignore
sny-copyright-checker --ignore-file .custom --no-gitignore src/
```

## Behavior Details

### File Matching

- **Relative paths**: Patterns match against relative paths from the project root
- **Normalized separators**: Both `/` and `\` work on all platforms
- **Case sensitivity**: Follows platform defaults (case-insensitive on Windows)

### Ignored File Treatment

- Ignored files are **skipped** during checks
- They are counted as **passed** (not failed)
- No copyright notices are added or checked
- Logged in verbose mode for visibility

### Pattern Priority

1. `.copyrightignore` patterns are loaded first
2. `.gitignore` patterns are loaded second (if enabled)
3. All patterns are combined into a single matcher
4. Files matching any pattern are ignored

## Common Patterns

### Generated Code

```
**/generated/
**/auto-generated/
*.generated.js
*.generated.py
*_pb2.py          # Protocol buffer generated files
*_pb2_grpc.py
```

### Vendor/Third-Party Code

```
node_modules/
vendor/
third_party/
bower_components/
packages/
```

### Build Artifacts

```
build/
dist/
out/
target/
*.o
*.so
*.dll
*.pyc
*.class
```

### Minified/Bundled Files

```
*.min.js
*.min.css
*.bundle.js
*.chunk.js
*.map
```

### Documentation/Examples

```
docs/
examples/
*.md          # Markdown files typically don't need copyrights
LICENSE*
CHANGELOG*
```

### Configuration Files

```
*.json
*.yml
*.yaml
*.toml
*.ini
*.cfg
.env*
```

## Troubleshooting

### Files Not Being Ignored

**Check pattern syntax:**
```bash
# Run with verbose to see which files are being ignored
sny-copyright-checker --verbose src/
```

**Debug patterns:**
```python
# Test if your pattern works
import pathspec
spec = pathspec.PathSpec.from_lines('gitwildmatch', ['**/build/'])
print(spec.match_file('src/build/output.py'))  # Should be True
```

### .gitignore Not Working

**Ensure it's enabled:**
```bash
# Check if --no-gitignore was accidentally used
sny-copyright-checker src/  # Good
sny-copyright-checker --no-gitignore src/  # .gitignore disabled
```

### Absolute Paths

Patterns work with both relative and absolute paths. The tool automatically converts absolute paths to relative for matching.

### Performance

Ignore patterns have minimal performance impact. Pattern matching is very fast even with hundreds of patterns.

## Best Practices

### 1. **Separate Concerns**

Use `.copyrightignore` for copyright-specific exclusions:
```
# In .copyrightignore
LICENSE
COPYING
docs/api/
```

Let `.gitignore` handle build artifacts and generated files.

### 2. **Document Your Patterns**

Add comments explaining why files are ignored:
```
# Ignore third-party libraries - they have their own copyrights
vendor/

# Generated API documentation - auto-created from source
docs/api/generated/
```

### 3. **Be Specific**

Avoid overly broad patterns:
```
# Too broad - might ignore too much
*.py

# Better - specific to what you want to ignore
*_pb2.py
**/__pycache__/*.py
```

### 4. **Test Your Patterns**

Run with `--verbose` to verify files are being ignored:
```bash
sny-copyright-checker --verbose src/ | grep "ignored"
```

### 5. **Version Control**

Commit `.copyrightignore` to your repository so all team members use the same rules:
```bash
git add .copyrightignore
git commit -m "Add copyright ignore patterns"
```

## Integration with Pre-commit

The ignore patterns work automatically with pre-commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: copyright-check
        name: Check Copyright Notices
        entry: sny-copyright-checker
        language: system
        # .copyrightignore and .gitignore are used automatically
```

Custom configuration:
```yaml
repos:
  - repo: local
    hooks:
      - id: copyright-check
        name: Check Copyright Notices
        entry: sny-copyright-checker
        args: ['--ignore-file=.custom-ignore', '--no-gitignore']
        language: system
```

## API Usage

```python
from scripts.copyright_checker import CopyrightChecker

# Use default ignore files
checker = CopyrightChecker("copyright.txt")

# Disable .gitignore
checker = CopyrightChecker("copyright.txt", use_gitignore=False)

# Use custom ignore file
checker = CopyrightChecker("copyright.txt", ignore_file=".custom-ignore")

# Check if a file should be ignored
if checker.should_ignore("build/output.py"):
    print("File will be skipped")

# Check files (ignored files are automatically skipped)
passed, failed, modified = checker.check_files(["src/app.py", "build/gen.py"])
```

## Requirements

The ignore files feature requires the `pathspec` library:

```bash
pip install pathspec
```

If `pathspec` is not installed, the tool will work but ignore patterns will be disabled. A debug message will be logged.

## Limitations

1. **Negation patterns** (`!pattern`) have limited support - they work with pathspec but may not behave exactly like git
2. **Pattern order** doesn't affect precedence - all patterns are combined
3. **No directory-specific .copyrightignore** - only the root file is used

## See Also

- [Git Documentation - gitignore](https://git-scm.com/docs/gitignore)
- [pathspec library](https://github.com/cpburnz/python-pathspec)
- [Pre-commit hooks](https://pre-commit.com/)
