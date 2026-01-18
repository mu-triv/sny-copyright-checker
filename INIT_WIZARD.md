<!--
SPDX-License-Identifier: MIT
Copyright 2026 Sony Group Corporation
Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
License: For licensing see the License.txt file
-->

# Init Wizard - Quick Setup Guide

The `sny-copyright-checker init` command provides an interactive wizard to help you create a `copyright.txt` configuration file without having to read extensive documentation or understand the file format.

## Quick Start

Simply run:

```bash
sny-copyright-checker init
```

The wizard will guide you through:
1. Selecting a license type (MIT, Apache, GPL, BSD, Proprietary, or Custom)
2. Entering your company/organization name
3. Optionally including author information
4. Customizing license details if needed
5. Selecting which file extensions to support
6. Previewing and saving the configuration
7. **Automatically creating/updating `.pre-commit-config.yaml`**

## Usage

### Basic Usage

```bash
sny-copyright-checker init
```

This creates a `copyright.txt` file in the current directory.

### Custom Output Path

```bash
sny-copyright-checker init --output my-copyright.txt
```

or

```bash
sny-copyright-checker init -o config/copyright.txt
```

## Interactive Prompts

### 1. License Type Selection

Choose from pre-configured license templates:

- **MIT License**: Permissive open source license
- **Apache License 2.0**: Permissive with patent grant
- **GNU GPL v3.0**: Copyleft open source license
- **BSD 3-Clause**: Permissive with attribution
- **Proprietary**: All rights reserved
- **Custom**: Specify your own license details

**Example:**
```
Select a license type
------------------------------------------------------------
  1. apache: Permissive with patent grant
  2. bsd3: Permissive with attribution
  3. custom: Specify your own license
  4. gpl3: Copyleft open source license
  5. mit: Permissive open source license (default)
  6. proprietary: All rights reserved

Enter number or key [mit]: 1
```

### 2. Company/Organization Name

Enter your company or organization name. This will appear in all copyright notices.

**Example:**
```
Enter company/organization name [My Company Inc.]: Acme Corporation
```

### 3. Author Information

Choose whether to include author information in copyright notices.

**Example:**
```
Include author information in copyright? (Y/n): y
Enter author name or team [Development Team]: Engineering Team
```

### 4. Custom License Details

For custom licenses or to override defaults, you can specify:
- SPDX license identifier
- License notice text

**Example:**
```
Customize license details? (y/N): y
SPDX identifier [MIT]: MIT-0
License notice [For licensing see the LICENSE file]: See LICENSE.md for details
```

### 5. File Extensions

Select which file extensions your copyright notices should support.

**Example:**
```
Select file extensions to include
------------------------------------------------------------
Enter numbers separated by commas (e.g., 1,3,5) or 'all' for all options
  1. c_cpp: .c, .h, .cpp, .hpp, .cc, .cxx
  2. css: .css, .scss, .sass
  3. go: .go
  4. java: .java
  5. javascript: .js, .jsx, .ts, .tsx
  6. markdown: .md
  7. python: .py
  8. rust: .rs
  9. shell: .sh, .bash
  10. sql: .sql
  11. xml_html: .xml, .html, .htm
  12. yaml: .yaml, .yml

Select options [all]: 1,5,7
```

### 6. Preview and Confirmation

The wizard shows a preview of the generated configuration before saving.

**Example:**
```
============================================================
Preview of generated copyright.txt:
============================================================
[VARIABLES]
SPDX_LICENSE = MIT
COMPANY = Acme Corporation
AUTHOR = Engineering Team
YEAR_PATTERN = {regex:\d{4}(-\d{4})?}
LICENSE_NOTICE = For licensing see the LICENSE file

[.py]
# SPDX-License-Identifier: {SPDX_LICENSE}
# Copyright {YEAR_PATTERN} {COMPANY}
# Author: {AUTHOR}
# License: {LICENSE_NOTICE}
...
============================================================

Save this configuration? (Y/n): y

✓ Configuration saved to: copyright.txt

Create/update .pre-commit-config.yaml? (Y/n): y
✓ Created .pre-commit-config.yaml

To enable pre-commit hooks, run:
  pre-commit install

Next steps:
  1. Review and customize copyright.txt if needed
  2. Run: sny-copyright-checker --fix <files>
```

### 7. Pre-commit Configuration (NEW!)

After saving the copyright template, the wizard asks if you want to automatically create or update `.pre-commit-config.yaml`.

**Benefits:**
- ✅ **Automatic Setup**: No need to manually edit YAML files
- ✅ **Correct Configuration**: Uses the right file patterns based on your selected extensions
- ✅ **Updates Existing Config**: If you already have `.pre-commit-config.yaml`, it updates it intelligently
- ✅ **Common Arguments**: Pre-configured with sensible defaults

**What it does:**
1. Creates `.pre-commit-config.yaml` if it doesn't exist
2. Updates the sny-copyright-checker configuration if it already exists
3. Adds a `files` regex pattern that matches only your selected file extensions
4. Uses the correct path to your copyright template file

**Example:**
```
Create/update .pre-commit-config.yaml? (Y/n): y
✓ Created .pre-commit-config.yaml

To enable pre-commit hooks, run:
  pre-commit install
```

The generated configuration will look like:
```yaml
repos:
- repo: https://github.com/mu-triv/sny-copyright-checker
  rev: v1.0.7
  hooks:
  - id: sny-copyright-checker
    args:
    - --notice=copyright.txt
    files: \.(py|js|ts|c|h|cpp)$
```

## Examples

### Example 1: MIT License for Python Project

```bash
$ sny-copyright-checker init

Select a license type
------------------------------------------------------------
...
Enter number or key [mit]: mit

Enter company/organization name [My Company Inc.]: Acme Corp

Include author information in copyright? (Y/n): y
Enter author name or team [Development Team]: Python Team

Customize license details? (y/N): n

Select file extensions to include
------------------------------------------------------------
...
Select options [all]: 7

Output file path [copyright.txt]:

Save this configuration? (Y/n): y

✓ Configuration saved to: copyright.txt
```

### Example 2: Proprietary License for Multi-Language Project

```bash
$ sny-copyright-checker init

Select a license type
------------------------------------------------------------
...
Enter number or key [mit]: proprietary

Enter company/organization name [My Company Inc.]: SecretCorp Inc.

Include author information in copyright? (Y/n): n

Customize license details? (y/N): n

Select file extensions to include
------------------------------------------------------------
...
Select options [all]: all

Output file path [copyright.txt]:

Save this configuration? (Y/n): y

✓ Configuration saved to: copyright.txt
```

### Example 3: Custom License with Specific Extensions

```bash
$ sny-copyright-checker init --output config/copyright.txt

Select a license type
------------------------------------------------------------
...
Enter number or key [mit]: custom

Enter company/organization name [My Company Inc.]: Custom Corp

Include author information in copyright? (Y/n): y
Enter author name or team [Development Team]: Legal Team

Enter SPDX license identifier (or leave empty): Custom-License-1.0
Enter license notice text [All rights reserved]: See our website for license terms

Select file extensions to include
------------------------------------------------------------
...
Select options [all]: 1,5,7,10

Output file path [copyright.txt]:

Save this configuration? (Y/n): y

✓ Configuration saved to: config/copyright.txt
```

## Supported File Extensions

The wizard supports the following file extension groups:

| Group | Extensions | Comment Style |
|-------|-----------|---------------|
| Python | `.py` | `#` |
| C/C++ | `.c`, `.h`, `.cpp`, `.hpp`, `.cc`, `.cxx` | `/* ... */` (block) |
| Java | `.java` | `/* ... */` |
| JavaScript | `.js`, `.jsx`, `.ts`, `.tsx` | `//` |
| Shell | `.sh`, `.bash` | `#` (with shebang) |
| SQL | `.sql` | `--` |
| Go | `.go` | `//` |
| Rust | `.rs` | `//` |
| YAML | `.yaml`, `.yml` | `#` |
| Markdown | `.md` | `<!-- ... -->` |
| XML/HTML | `.xml`, `.html`, `.htm` | `<!-- ... -->` |
| CSS | `.css`, `.scss`, `.sass` | `//` |

## Generated File Format

The wizard generates a standard `copyright.txt` file with:

1. **[VARIABLES]** section with replaceable values:
   - `SPDX_LICENSE`: License identifier
   - `COMPANY`: Your company/organization name
   - `AUTHOR`: Author information (optional)
   - `YEAR_PATTERN`: Regex pattern for year matching
   - `LICENSE_NOTICE`: License notice text

2. **File extension sections** with appropriate comment styles for each language

## After Running Init

Once you've created your `copyright.txt` file:

1. **Review the file**: Open `copyright.txt` and verify the settings
2. **Customize if needed**: Add more file extensions or modify comment styles
3. **Test it**: Run `sny-copyright-checker --fix <file>` on a test file
4. **Integrate with pre-commit**: Add to `.pre-commit-config.yaml`:
   ```yaml
   repos:
     - repo: https://github.com/mu-triv/sny-copyright-checker
       rev: v1.0.7
       hooks:
         - id: sny-copyright-checker
           args: [--notice=copyright.txt]
   ```

## Tips

- **Use arrow keys or numbers**: You can select options by number or by typing the key name
- **Press Ctrl+C anytime**: Cancel the wizard without making changes
- **Review before saving**: The wizard shows a complete preview before saving
- **Non-destructive**: If the file exists, you'll be prompted before overwriting
- **Backup existing files**: If you already have a `copyright.txt`, consider backing it up first

## Advanced Customization

After running the wizard, you can manually edit the generated `copyright.txt` to:
- Add more file extensions
- Customize comment formatting
- Add different copyright notices for different file types
- Use hierarchical templates (see [HIERARCHICAL_TEMPLATES.md](HIERARCHICAL_TEMPLATES.md))
- Configure ignore patterns (see [IGNORE_FILES.md](IGNORE_FILES.md))

## Troubleshooting

### "File already exists"

If `copyright.txt` already exists, you'll be prompted to overwrite. Answer 'n' to cancel and preserve your existing file.

### "Invalid choice"

Make sure to enter a valid number or key from the displayed options.

### "Company name is required"

The company/organization name cannot be empty. Enter at least a placeholder value.

## See Also

- [README.md](README.md) - Main documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [EXAMPLES.md](EXAMPLES.md) - Usage examples
- [HIERARCHICAL_TEMPLATES.md](HIERARCHICAL_TEMPLATES.md) - Directory-specific copyrights
- [IGNORE_FILES.md](IGNORE_FILES.md) - Ignore file patterns
