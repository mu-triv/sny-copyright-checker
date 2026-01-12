<!--
SPDX-License-Identifier: MIT
Copyright 2026 Sony Group Corporation
Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
License: For licensing see the License.txt file
-->

# Version Management

The version number is now centralized in a single location for easier maintenance.

## Single Source of Truth

The version is defined in:
- **[scripts/__init__.py](scripts/__init__.py)** - `__version__ = "1.0.1"`

All other files (pyproject.toml, setup.cfg) automatically read from this single source.

## How to Update Version

To release a new version, you only need to update **ONE file**:

1. Edit [scripts/__init__.py](scripts/__init__.py)
2. Change `__version__ = "1.0.1"` to your new version
3. Update [CHANGELOG.md](CHANGELOG.md) with the new version notes
4. Update [README.md](README.md) examples to use the new version tag (if needed)

### Example:

```python
# scripts/__init__.py
"""sny copyright check pre-commit hook"""

__version__ = "1.0.3"  # ← Change only this
```

## Files That Auto-Update

These files automatically use the version from `scripts.__init__.__version__`:
- ✅ `pyproject.toml` - Uses `dynamic = ["version"]` with `setuptools.dynamic.version`
- ✅ `setup.cfg` - Uses `version = attr: scripts.__version__`
- ✅ `setup.py` - Reads from setup.cfg/pyproject.toml

## Files That May Need Manual Update

These files may contain version references for documentation/examples:
- 📝 `README.md` - Pre-commit hook examples use `rev: v1.0.1`
- 📝 `CHANGELOG.md` - Version history

## Verification

After updating the version, verify it's correctly propagated:

```bash
# Check the version is correct
python -c "from scripts import __version__; print(__version__)"

# Or after installation
pip install -e .
sny-copyright-checker --version  # (if you add --version flag)
```

## Git Tags

When releasing a new version:

```bash
# After updating __version__ and committing changes
git tag -a v1.0.3 -m "Release version 1.0.3"
git push origin v1.0.3
```
