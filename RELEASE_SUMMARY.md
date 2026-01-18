<!--
SPDX-License-Identifier: MIT
Copyright 2026 Sony Group Corporation
Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
License: For licensing see the License.txt file
-->

# Version 1.0.7 - Release Summary

**Release Date:** January 18, 2026

## 🎉 Major Enhancement: Pre-commit Config Automation

The `sny-copyright-checker init` wizard now automatically creates and configures `.pre-commit-config.yaml` for you!

### What's New

**Before:**
1. Run `sny-copyright-checker init`
2. Manually create/edit `.pre-commit-config.yaml`
3. Add the checker configuration by hand
4. Hope you got the file patterns right

**After (v1.0.7):**
1. Run `sny-copyright-checker init`
2. Answer a few questions
3. ✨ **Done!** Everything is configured automatically

### Key Benefits

- ✅ **Zero Manual Configuration**: No YAML editing required
- ✅ **Smart Updates**: Updates existing configs without breaking other hooks
- ✅ **Correct Patterns**: Auto-generates file patterns from your selected extensions
- ✅ **Common Arguments**: Pre-configured with sensible defaults
- ✅ **Beginner Friendly**: Perfect for first-time users

### Example Workflow

```bash
# Install
pip install sny-copyright-checker

# Configure (fully automated!)
sny-copyright-checker init

# Wizard output:
# Select a license type: [select MIT]
# Enter company name: My Company
# Select file extensions: 1,5,7 (C/C++, JavaScript, Python)
# Create/update .pre-commit-config.yaml? Y
#
# ✓ Configuration saved to: copyright.txt
# ✓ Created .pre-commit-config.yaml
#
# To enable pre-commit hooks, run:
#   pre-commit install

# Enable hooks
pre-commit install

# That's it! Now your copyrights are checked automatically on every commit
git add my_file.py
git commit -m "Add feature"  # Copyright check runs automatically
```

### Generated Configuration

The wizard creates a `.pre-commit-config.yaml` like this:

```yaml
repos:
- repo: https://github.com/mu-triv/sny-copyright-checker
  rev: v1.0.7
  hooks:
  - id: sny-copyright-checker
    args:
    - --notice=copyright.txt
    files: \.(c|h|cpp|js|jsx|ts|tsx|py)$
```

Note how the `files` pattern matches exactly the extensions you selected!

## 📚 Documentation Improvements

### New Structure

- **README.md**: Now concise and beginner-friendly (150 lines vs 700+ before)
- **USER_GUIDE.md**: Complete documentation moved here for reference
- **Better Navigation**: Easy path from simple to advanced topics

### Updated Docs

- **INIT_WIZARD.md**: Added section on pre-commit automation
- **CHANGELOG.md**: Detailed new features
- All documentation links now use GitHub URLs for PyPI compatibility

## 🔧 Technical Changes

### New Dependency

- Added `PyYAML>=6.0` for `.pre-commit-config.yaml` handling

### Code Improvements

- Enhanced `init_wizard.py` with `create_or_update_precommit_config()` function
- Smart YAML merging that preserves existing hooks
- Improved string literal detection in test code

## 📦 Installation

### Upgrade from Previous Version

```bash
pip install --upgrade sny-copyright-checker
```

### Fresh Install

```bash
pip install sny-copyright-checker
```

## 🚀 Getting Started

### For New Users

```bash
sny-copyright-checker init  # Fully automated setup
pre-commit install          # Enable hooks
```

### For Existing Users

If you already have `copyright.txt`, you can still use the wizard to create/update your `.pre-commit-config.yaml`:

```bash
sny-copyright-checker init --output copyright.txt
# Answer "no" to overwrite
# Answer "yes" to update .pre-commit-config.yaml
```

## 📖 Documentation Links

- [README.md](https://github.com/mu-triv/sny-copyright-checker/blob/main/README.md) - Quick introduction
- [USER_GUIDE.md](https://github.com/mu-triv/sny-copyright-checker/blob/main/USER_GUIDE.md) - Complete guide
- [INIT_WIZARD.md](https://github.com/mu-triv/sny-copyright-checker/blob/main/INIT_WIZARD.md) - Wizard documentation
- [CHANGELOG.md](https://github.com/mu-triv/sny-copyright-checker/blob/main/CHANGELOG.md) - Full version history

## 🐛 Bug Fixes

- Improved string literal detection for better handling of copyright notices in test code
- Enhanced test coverage for edge cases with escaped quotes and multiline strings

## ⬆️ Upgrade Notes

- **No Breaking Changes**: Drop-in replacement for v1.0.6
- **New Dependency**: PyYAML is now required (automatically installed with pip)
- **Backward Compatible**: All existing configurations continue to work

## 🙏 Feedback

We'd love to hear your feedback! Please open an issue on GitHub if you have suggestions or encounter any problems.

---

**Happy Coding!** 🎉
