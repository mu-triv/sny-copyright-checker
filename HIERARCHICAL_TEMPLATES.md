<!--
SPDX-License-Identifier: MIT
Copyright 2026 Sony Group Corporation
Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
License: For licensing see the License.txt file
-->

# Hierarchical Copyright Templates

## Overview

Hierarchical copyright templates allow you to use different copyright notices for different parts of your codebase. This is especially useful for:

- **Monorepos** with multiple projects
- **Vendor/third-party code** with different licenses
- **Multi-team projects** where different teams maintain different components
- **Mixed licensing** scenarios (e.g., GPL library with MIT application code)

## How It Works

When hierarchical mode is enabled with `--hierarchical`, the checker searches for copyright template files in the directory hierarchy:

1. For each source file, start in the file's directory
2. Walk up the directory tree looking for the template file (specified by `--notice`)
3. Use the **nearest** template file found
4. Templates in child directories **override** templates in parent directories

## Basic Usage

### Command Line

```bash
# Enable hierarchical mode
sny-copyright-check --hierarchical --notice=copyright.txt src/

# With other options
sny-copyright-check --hierarchical --notice=copyright.txt --fix src/
```

### Pre-commit Configuration

```yaml
repos:
  - repo: https://github.com/mu-triv/sny-copyright-checker
    rev: v1.0.5
    hooks:
      - id: sny-copyright-checker
        args: [--hierarchical, --notice=copyright.txt]
```

## Directory Structure Examples

### Example 1: Monorepo with Multiple Projects

```
monorepo/
├── copyright.txt                    # Default company copyright
├── app/
│   ├── main.py                     # Uses root copyright
│   └── utils.py                    # Uses root copyright
├── library/
│   ├── copyright.txt                # Library-specific copyright
│   ├── core.py                     # Uses library copyright
│   └── helpers.py                  # Uses library copyright
└── vendor/
    ├── copyright.txt                # Third-party copyright
    └── external.py                 # Uses vendor copyright
```

**Root `copyright.txt`:**
```
[.py]
# Copyright 2026 MyCompany Inc.
# License: MIT
```

**`library/copyright.txt`:**
```
[.py]
# Copyright 2026 MyCompany Inc.
# Library Component - Apache-2.0 License
```

**`vendor/copyright.txt`:**
```
[.py]
# Copyright 2020-2026 ThirdParty Corp
# License: BSD-3-Clause
```

**Result:**
- `app/main.py` gets MyCompany MIT copyright
- `library/core.py` gets MyCompany Apache-2.0 copyright
- `vendor/external.py` gets ThirdParty BSD copyright

### Example 2: Nested Overrides

```
project/
├── copyright.txt                    # Root: Company A
├── src/
│   ├── file1.py                    # Uses root (Company A)
│   └── internal/
│       ├── copyright.txt            # Override: Team B
│       ├── file2.py                # Uses Team B copyright
│       └── legacy/
│           ├── copyright.txt        # Override: Old format
│           └── file3.py            # Uses Old format copyright
```

**Behavior:**
- `src/file1.py` → Uses **root** copyright (Company A)
- `src/internal/file2.py` → Uses **internal/** copyright (Team B)
- `src/internal/legacy/file3.py` → Uses **internal/legacy/** copyright (Old format)

**Key Point:** Each level can override its parent, and the nearest template wins.

### Example 3: Mixed File Types

Each template file can define different formats for different file extensions:

```
project/
├── copyright.txt
│   [.py]
│   # Copyright 2026 Company
│   [.js]
│   // Copyright 2026 Company
├── vendor/
    └── copyright.txt
        [.py]
        # Copyright 2024 Vendor Corp
        [.js]
        // Copyright 2024 Vendor Corp
```

## Template File Requirements

1. **Same Filename**: All template files in the hierarchy must have the same name
   - Specified by `--notice` argument (default: `copyright.txt`)
   - Example: If using `--notice=license.txt`, all templates must be named `license.txt`

2. **Standard Format**: Each template file uses the same section-based format:
   ```
   [VARIABLES]
   COMPANY = Your Company

   [.py, .yaml]
   # Copyright {regex:\d{4}} {COMPANY}

   [.js, .ts]
   // Copyright {regex:\d{4}} {COMPANY}
   ```

3. **Independent Content**: Each template file is completely independent
   - Variables are not inherited from parent templates
   - Each file must be self-contained

## Use Cases

### Use Case 1: Vendor/Third-Party Code

When integrating external code with different licensing:

```
myproject/
├── copyright.txt              # Your company's copyright
├── src/
│   └── app.py                # Your code
└── vendor/
    ├── copyright.txt          # External vendor's copyright
    └── library.py            # Vendor code
```

### Use Case 2: GPL Library with MIT Application

Separating GPL library from MIT application code:

```
project/
├── copyright.txt              # MIT License (application)
├── app/
│   └── main.py               # MIT
└── lib/
    ├── copyright.txt          # GPL License (library)
    └── core.py               # GPL
```

### Use Case 3: Multi-Team Monorepo

Different teams with different copyright requirements:

```
company-monorepo/
├── copyright.txt              # Default company copyright
├── team-a/
│   ├── copyright.txt          # Team A specific
│   └── service.py
├── team-b/
│   ├── copyright.txt          # Team B specific
│   └── api.py
└── shared/
    └── utils.py              # Uses root copyright
```

### Use Case 4: Open Source Project with Proprietary Plugins

```
opensource-project/
├── copyright.txt              # Apache-2.0 (open source)
├── core/
│   └── engine.py             # Open source
└── plugins/
    └── enterprise/
        ├── copyright.txt      # Proprietary license
        └── premium.py        # Proprietary
```

## Behavior Details

### Template Discovery

For each file, the checker:
1. Gets the absolute path of the file's directory
2. Searches for the template file in that directory
3. If not found, moves up one directory level and repeats
4. Continues until a template is found or reaches the filesystem root
5. If no template is found, the file is skipped (no copyright added)

### Caching

Template files are cached per directory for performance:
- Each directory's templates are loaded once and cached
- Multiple files in the same directory share the cached templates
- Reduces file I/O and parsing overhead

### Non-Hierarchical Mode

When hierarchical mode is **not** enabled (default):
- Only the single template file specified by `--notice` is used
- Template files in subdirectories are ignored
- All source files use the same copyright template

**Example:**
```bash
# Non-hierarchical (default)
sny-copyright-check --notice=copyright.txt src/

# Even if src/vendor/copyright.txt exists, it's ignored
# All files use the root copyright.txt
```

## Combining with Other Features

### With Git-Aware Year Management

Hierarchical templates work seamlessly with Git-aware years:

```bash
sny-copyright-check --hierarchical --notice=copyright.txt src/
```

- Each template's year patterns are respected
- Git history determines year ranges
- Years are managed independently per template

### With Ignore Files

Combine with `.copyrightignore` to skip certain files:

```bash
sny-copyright-check --hierarchical --notice=copyright.txt \
                    --ignore-file=.copyrightignore src/
```

**.copyrightignore:**
```
# Ignore vendor binaries
vendor/**/*.min.js

# But check vendor Python files (they have copyright.txt)
```

### With Changed-Only Mode

Check only changed files in hierarchical mode:

```bash
sny-copyright-check --hierarchical --changed-only --notice=copyright.txt
```

## Best Practices

### 1. Document Your Structure

Create a `COPYRIGHT_STRUCTURE.md` in your project explaining:
- Which directories have custom copyright templates
- Why they have different templates (licensing, ownership, etc.)
- How to add new copyrights

### 2. Use Consistent Naming

Always use the same template filename throughout your project:
- ✅ Good: All templates named `copyright.txt`
- ❌ Bad: Mix of `copyright.txt`, `license.txt`, `NOTICE.txt`

### 3. Keep Templates Simple

Each template file should be straightforward:
- Define only the extensions you need
- Use variables for repeated values
- Keep copyright text concise

### 4. Test Before Committing

Run in check-only mode first:
```bash
sny-copyright-check --hierarchical --no-fix --verbose src/
```

This shows which template each file would use without making changes.

### 5. Use .copyrightignore

Don't rely solely on hierarchical mode to skip files:
```
# .copyrightignore
vendor/**/test_*.py      # Skip vendor tests
vendor/**/*.min.js       # Skip minified files
```

### 6. Version Control Template Files

Commit all `copyright.txt` files:
```bash
git add copyright.txt
git add vendor/copyright.txt
git add lib/copyright.txt
git commit -m "Add hierarchical copyright templates"
```

## Troubleshooting

### File Not Getting Expected Copyright

**Problem:** A file uses the wrong copyright template.

**Debug Steps:**
1. Run with `--verbose` to see which template is found:
   ```bash
   sny-copyright-check --hierarchical --verbose --no-fix file.py
   ```

2. Check the directory hierarchy:
   ```bash
   # Starting from file's directory, look for copyright.txt
   ls -la path/to/file/copyright.txt
   ls -la path/to/copyright.txt
   ls -la path/copyright.txt
   ls -la copyright.txt
   ```

3. Verify template filename matches `--notice` argument

### No Copyright Added in Hierarchical Mode

**Problem:** Files are skipped even though a root template exists.

**Cause:** In hierarchical mode, templates must be found by walking up from the file's directory.

**Solution:** Ensure the root `copyright.txt` is in a parent directory of the files being checked:
```
project/
├── copyright.txt       ← Must be here or above
└── src/
    └── file.py        ← File being checked
```

### Template Cache Issues

**Problem:** Updated template not being used.

**Cause:** Template cache is per-process.

**Solution:** The cache is memory-only and cleared between runs. No action needed.

## Migration Guide

### From Non-Hierarchical to Hierarchical

**Current Setup (Non-Hierarchical):**
```bash
sny-copyright-check --notice=copyright.txt src/ vendor/
```

**Migration Steps:**

1. **Identify different copyright needs:**
   ```
   src/     → Company copyright
   vendor/  → Third-party copyright
   ```

2. **Create template files:**
   ```bash
   # Keep existing root template
   cp copyright.txt copyright.txt.backup

   # Create vendor template
   cp vendor_copyright.txt vendor/copyright.txt
   ```

3. **Update pre-commit config:**
   ```yaml
   - id: sny-copyright-checker
     args: [--hierarchical, --notice=copyright.txt]  # Add --hierarchical
   ```

4. **Test the migration:**
   ```bash
   # Check what would change
   sny-copyright-check --hierarchical --no-fix --verbose src/ vendor/
   ```

5. **Commit the changes:**
   ```bash
   git add vendor/copyright.txt .pre-commit-config.yaml
   git commit -m "Enable hierarchical copyright templates"
   ```

## Performance Considerations

### Caching

- Templates are cached per directory
- Cache is memory-only (not persisted)
- Multiple files in same directory benefit from caching

### File I/O

- Each unique directory requires one template file read
- Templates are parsed once per directory
- Minimal overhead compared to checking individual files

### Comparison

**Non-Hierarchical:**
- 1 template file read (at startup)
- Same templates used for all files

**Hierarchical:**
- N template files read (N = number of unique directories with templates)
- Templates cached after first read per directory

**Recommendation:** For projects with <100 directories containing templates, performance difference is negligible.

## Advanced Patterns

### Pattern 1: Gradual Template Override

Start with a general template and override specific parts:

```
project/
├── copyright.txt              # Generic: MIT, Company
├── proprietary/
│   ├── copyright.txt          # Override: Proprietary, Company
│   └── secret.py
└── opensource/
    ├── copyright.txt          # Override: Apache-2.0, Company
    └── public.py
```

### Pattern 2: Language-Specific Overrides

Different copyrights for different languages within a directory:

```
multilang/
├── copyright.txt
│   [.py]  # Python: MIT
│   # Copyright 2026 Company
│   # License: MIT
│   [.js]  # JavaScript: Apache-2.0
│   // Copyright 2026 Company
│   // License: Apache-2.0
```

### Pattern 3: Legacy Code Preservation

Preserve old copyright formats in legacy directories:

```
project/
├── copyright.txt              # New format: SPDX identifiers
├── src/
│   └── new.py                # New format
└── legacy/
    ├── copyright.txt          # Old format: traditional
    └── old.py                # Old format
```

## See Also

- [README.md](README.md) - Main documentation
- [GIT_AWARE_YEAR_MANAGEMENT.md](GIT_AWARE_YEAR_MANAGEMENT.md) - Git-aware year management
- [IGNORE_FILES.md](IGNORE_FILES.md) - Ignore pattern documentation
- [EXAMPLES.md](EXAMPLES.md) - General examples
