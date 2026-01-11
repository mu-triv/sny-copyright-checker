<!--
Copyright 2026 Sony Group Corporation
Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
License: For licensing see the License.txt file
-->

# Project Setup Complete! 🎉

## SNY Copyright Check - Enhanced Pre-commit Hook

Your new pre-commit hook project has been successfully created!

### ✨ Key Features Implemented

1. **Multi-Format Support**: Different copyright formats for `.py`, `.sql`, `.c`, `.cpp`, `.h`, `.js`, `.ts`, `.java`, `.sh`
2. **Regex Pattern Matching**: Year matching with `{regex:\d{4}(-\d{4})?}` pattern
3. **Auto-Insertion**: Automatically adds missing copyright notices with current year (2026)
4. **Section-Based Template**: Easy-to-maintain `copyright.txt` with `[.ext]` sections
5. **Smart Positioning**: Respects shebang lines (`#!/usr/bin/env python`)

### 📁 Project Structure

```
sny-copyright-checker/
├── scripts/
│   ├── __init__.py
│   ├── main.py                      # CLI entry point
│   ├── copyright_checker.py         # Main checker logic
│   └── copyright_template_parser.py # Template parser with regex support
├── tests/
│   ├── __init__.py
│   ├── test_copyright_checker.py
│   └── test_template_parser.py
├── .pre-commit-hooks.yaml           # Hook definition for pre-commit
├── .pre-commit-config.yaml          # Example configuration
├── copyright.txt                     # Multi-format copyright templates
├── pyproject.toml                   # Project metadata
├── setup.py & setup.cfg             # Setup configuration
├── LICENSE                          # MIT License
├── README.md                        # Full documentation
├── QUICKSTART.md                    # Quick start guide
├── EXAMPLES.md                      # Usage examples
├── CHANGELOG.md                     # Version history
└── demo.py                          # Demo/test script
```

### 🚀 Quick Start

#### 1. Test the Tool

```powershell
cd sny-copyright-checker
python demo.py
```

The demo will create test files and show the copyright checker in action!

#### 2. Use in Command Line

```powershell
# Check and auto-fix a file
python -m scripts.main myfile.py

# Check multiple files
python -m scripts.main file1.py file2.sql file3.c

# Check only (no modifications)
python -m scripts.main --no-fix *.py

# Verbose output
python -m scripts.main -v myfile.py
```

#### 3. Install as Pre-commit Hook in Your Projects

For your `graphle_lib` project:

1. **Copy the copyright template**:
   ```powershell
   copy sny-copyright-checker\copyright.txt your-project\
   ```

2. **Add to `.pre-commit-config.yaml`**:
   ```yaml
   - repo: local
     hooks:
       - id: sny-copyright-checker
         name: SNY Copyright Check
         entry: python /path/to/sny-copyright-checker/scripts/main.py
         language: system
         types: [text]
         args: [--notice=copyright.txt]
   ```

3. **Install and test**:
   ```powershell
   cd your-project
   pre-commit install
   pre-commit run --all-files
   ```

### 📝 Copyright Template Format

Edit `copyright.txt` to customize for your needs:

```
[.py]
# Copyright {regex:\d{4}(-\d{4})?} SNY Group Corporation
# Author: R&D Center Europe Brussels Laboratory, SNY Group Corporation
# License: For licensing see the License.txt file

[.sql]
-- Copyright {regex:\d{4}(-\d{4})?} SNY Group Corporation
-- Author: R&D Center Europe Brussels Laboratory, SNY Group Corporation
-- License: For licensing see the License.txt file
```

**Key Points**:
- `[.extension]` defines the file type section
- `{regex:\d{4}(-\d{4})?}` matches years like `2026` or `2024-2026`
- When auto-inserting, the regex is replaced with the current year

### 🎯 Example Usage

**Before** (`script.py`):
```python
#!/usr/bin/env python

def main():
    print("Hello, World!")
```

**After running** `python -m scripts.main script.py`:
```python
#!/usr/bin/env python
# Copyright 2026 SNY Group Corporation
# Author: R&D Center Europe Brussels Laboratory, SNY Group Corporation
# License: For licensing see the License.txt file

def main():
    print("Hello, World!")
```

### 🔧 Command Line Options

```
python -m scripts.main [OPTIONS] FILES...

Options:
  --notice PATH    Path to copyright template (default: copyright.txt)
  --fix           Auto-add missing copyrights (default: enabled)
  --no-fix        Only check, don't modify files
  -v, --verbose   Show detailed output
```

### 📚 Documentation Files

- **README.md**: Complete documentation
- **QUICKSTART.md**: Quick start guide with examples
- **EXAMPLES.md**: Example copyright headers for different languages
- **CHANGELOG.md**: Version history

### 🔍 Known Limitations

1. **Duplicate Detection**: The pattern matching currently may add copyright to files that already have one if the year format doesn't match exactly. This can be improved by refining the matching logic.

2. **Binary Files**: Skips binary files automatically (cannot decode as UTF-8)

3. **Extension-Based**: Only processes files with extensions defined in `copyright.txt`

### 🛠️ Future Improvements

If you want to enhance the tool further:

1. **Better Matching**: Improve regex matching to avoid duplicates
2. **Year Range Updates**: Auto-update year ranges (e.g., `2024` → `2024-2026`)
3. **Custom Templates**: Support for project-specific templates
4. **Ignore Patterns**: Add `.copyrightignore` file support
5. **Testing**: Add comprehensive pytest test suite

### 💡 Tips

- **Customize templates**: Edit `copyright.txt` to add more file types or change the format
- **Test before commit**: Run `python -m scripts.main --no-fix *.py` to check without modifying
- **Verbose mode**: Use `-v` flag to see detailed processing logs
- **Pre-commit integration**: Use with `pre-commit` for automatic checking on commit

### 🆚 Comparison with Reference Project

Enhancements over [leoll2/copyright_notice_precommit](https://github.com/leoll2/copyright_notice_precommit):

| Feature | Reference Project | This Project |
|---------|------------------|--------------|
| Multi-format support | ❌ Single format | ✅ Multiple formats per extension |
| Regex matching | ❌ Exact match only | ✅ Regex pattern support |
| Auto-insertion | ❌ Check only | ✅ Auto-add with current year |
| Template format | Plain text | Section-based with `[.ext]` |
| Year handling | Static | Dynamic with regex patterns |

### 📞 Support

For issues or questions:
1. Check the documentation in `README.md`
2. Review examples in `EXAMPLES.md` and `QUICKSTART.md`
3. Run the demo: `python demo.py`
4. Use verbose mode: `-v` flag

---

**Enjoy your new copyright checking tool!** 🚀

The project is ready to use and can be integrated into your workflows immediately.
