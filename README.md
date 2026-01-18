<!--
SPDX-License-Identifier: MIT
Copyright 2026 Sony Group Corporation
Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
License: For licensing see the License.txt file
-->

# SNY Copyright Checker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![PyPI version](https://badge.fury.io/py/sny-copyright-checker.svg)](https://badge.fury.io/py/sny-copyright-checker)
[![Tests](https://github.com/mu-triv/sny-copyright-checker/workflows/Tests/badge.svg)](https://github.com/mu-triv/sny-copyright-checker/actions)

A powerful pre-commit hook that automatically checks and adds copyright notices to your source files with support for multiple file formats and intelligent year management.

## Key Features

- ✨ **Multi-Format Support** - Different copyright formats for each file type (Python, C, SQL, JavaScript, etc.)
- 🔧 **Auto-Fix** - Automatically adds missing copyright notices
- 🧠 **Smart Replacement** - Intelligently updates similar copyrights while preserving year history
- 🎯 **Git-Aware** - Manages copyright years based on Git history
- 🚀 **Quick Setup** - Interactive wizard for first-time configuration
- 🔄 **Line Ending Safe** - Preserves CRLF/LF line endings
- 🚫 **Ignore Files** - Respects `.gitignore` and `.copyrightignore` patterns
- 📁 **Hierarchical Templates** - Different copyrights per directory for monorepos

## Quick Start

### 1. Install

```bash
pip install sny-copyright-checker
```

### 2. Configure

Run the interactive setup wizard:

```bash
sny-copyright-checker init
```

The wizard will guide you through license selection, company details, file type configuration, and **automatically creates or update`.pre-commit-config.yaml`** for you.

### 3. Use

#### As Pre-commit Hook

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/mu-triv/sny-copyright-checker
    rev: v1.0.7
    hooks:
      - id: sny-copyright-checker
        args: [--notice=copyright.txt]
```

Install and run:

```bash
pre-commit install
git commit -m "Your changes"  # Hook runs automatically
```

#### Command Line

```bash
# Check and fix files
sny-copyright-checker file1.py file2.js

# Check only (no modifications)
sny-copyright-checker --no-fix *.py

# Replace outdated copyrights
sny-copyright-checker --replace --changed-only
```

## Documentation

- **[USER_GUIDE.md](https://github.com/mu-triv/sny-copyright-checker/blob/main/USER_GUIDE.md)** - Complete usage guide with all features and options
- **[QUICKSTART.md](https://github.com/mu-triv/sny-copyright-checker/blob/main/QUICKSTART.md)** - Step-by-step getting started guide
- **[INIT_WIZARD.md](https://github.com/mu-triv/sny-copyright-checker/blob/main/INIT_WIZARD.md)** - Interactive setup wizard documentation
- **[EXAMPLES.md](https://github.com/mu-triv/sny-copyright-checker/blob/main/EXAMPLES.md)** - Usage examples and common scenarios
- **[CHANGELOG.md](https://github.com/mu-triv/sny-copyright-checker/blob/main/CHANGELOG.md)** - Version history and release notes

### Advanced Features

- **[GIT_AWARE_YEAR_MANAGEMENT.md](https://github.com/mu-triv/sny-copyright-checker/blob/main/GIT_AWARE_YEAR_MANAGEMENT.md)** - Git-based year tracking
- **[HIERARCHICAL_TEMPLATES.md](https://github.com/mu-triv/sny-copyright-checker/blob/main/HIERARCHICAL_TEMPLATES.md)** - Per-directory copyrights
- **[IGNORE_FILES.md](https://github.com/mu-triv/sny-copyright-checker/blob/main/IGNORE_FILES.md)** - Ignore pattern configuration
- **[REPLACE_FEATURE.md](https://github.com/mu-triv/sny-copyright-checker/blob/main/REPLACE_FEATURE.md)** - Smart copyright replacement

## How It Works

1. **Detects** file type by extension
2. **Checks** for existing copyright using regex patterns
3. **Adds** missing copyright with current year (if `--fix` enabled)
4. **Preserves** existing copyrights and line endings
5. **Updates** years based on Git history (Git-aware mode)

## Template Example

Create a `copyright.txt` with your company details:

```
[VARIABLES]
SPDX_LICENSE = MIT
COMPANY = Your Company Name
YEAR_PATTERN = {regex:\d{4}(-\d{4})?}

[.py, .yaml, .yml, .sh]
# SPDX-License-Identifier: {SPDX_LICENSE}
# Copyright {YEAR_PATTERN} {COMPANY}

[.js, .ts, .go, .rs, .java]
// SPDX-License-Identifier: {SPDX_LICENSE}
// Copyright {YEAR_PATTERN} {COMPANY}
```

Or use `sny-copyright-checker init` to generate this automatically.

## Supported Languages

Python • JavaScript • TypeScript • C • C++ • Java • Go • Rust • SQL • Shell • YAML • Markdown

Add more by editing your `copyright.txt` template.

## Development

```bash
# Clone and install
git clone https://github.com/mu-triv/sny-copyright-checker.git
cd sny-copyright-checker
pip install -e .

# Run tests
pytest tests/
```

## License

MIT License - see [LICENSE](https://github.com/mu-triv/sny-copyright-checker/blob/main/LICENSE) file for details.

## Author

**Tri VU Khac** (khactri.vu@sony.com)
Sony Group Corporation
R&D Center Europe Brussels Laboratory

## Acknowledgments

- Inspired by [leoll2/copyright_notice_precommit](https://github.com/leoll2/copyright_notice_precommit)
- Built for [pre-commit](https://pre-commit.com/) framework

## Support

- **Repository**: https://github.com/mu-triv/sny-copyright-checker
- **Issues**: https://github.com/mu-triv/sny-copyright-checker/issues
- **PyPI**: https://pypi.org/project/sny-copyright-checker/

---

For complete documentation, see **[USER_GUIDE.md](https://github.com/mu-triv/sny-copyright-checker/blob/main/USER_GUIDE.md)**.
