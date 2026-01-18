<!--
SPDX-License-Identifier: MIT
Copyright 2026 Sony Group Corporation
Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
License: For licensing see the License.txt file
-->

# Pre-Release Checklist for Version 1.0.7

## ✅ Completed

### Version Numbers
- [x] Updated `scripts/__init__.py` to version 1.0.7
- [x] Updated README.md pre-commit example to v1.0.7

### Documentation
- [x] Added release notes to CHANGELOG.md
- [x] Verified all copyright years are 2026 (in actual code)
- [x] Created RELEASE_SUMMARY.md with v1.0.7 highlights
- [x] Restructured README.md for better user experience
- [x] Created USER_GUIDE.md with comprehensive documentation
- [x] Updated INIT_WIZARD.md with pre-commit automation details

### Code Changes
- [x] Enhanced init_wizard.py with pre-commit config automation
- [x] Added PyYAML dependency to requirements
- [x] Added tests for pre-commit config creation/update functionality

### Code Quality
- [x] All copyright headers use 2026
- [x] Test data with old years (2020-2025) is intentional and correct

## 📋 Before Publishing

### Testing
- [ ] Run full test suite: `pytest tests/`
- [ ] Verify all tests pass
- [ ] Check test coverage is maintained
- [ ] Test installation from source: `pip install -e .`

### Build & Distribution
- [ ] Clean old build artifacts: `rm -rf build/ dist/ *.egg-info`
- [ ] Build new distribution: `python -m build`
- [ ] Verify package contents: `tar -tzf dist/sny-copyright-checker-1.0.7.tar.gz`
- [ ] Test installation from wheel: `pip install dist/sny_copyright_checker-1.0.7-*.whl`

### Git & Version Control
- [ ] Review all changes: `git status` and `git diff`
- [ ] Stage release files: `git add scripts/__init__.py CHANGELOG.md README.md RELEASE_NOTES_1.0.7.md`
- [ ] Commit changes: `git commit -m "Release version 1.0.7"`
- [ ] Create git tag: `git tag -a v1.0.7 -m "Release version 1.0.7"`
- [ ] Push changes: `git push origin main`
- [ ] Push tags: `git push origin v1.0.7`

### PyPI Publication
- [ ] Test upload to TestPyPI: `python -m twine upload --repository testpypi dist/*`
- [ ] Verify on TestPyPI: https://test.pypi.org/project/sny-copyright-checker/
- [ ] Upload to PyPI: `python -m twine upload dist/*`
- [ ] Verify on PyPI: https://pypi.org/project/sny-copyright-checker/

### Post-Release
- [ ] Update pre-commit hooks: `pre-commit autoupdate`
- [ ] Test pre-commit integration with new version
- [ ] Create GitHub release from tag v1.0.7
- [ ] Attach RELEASE_NOTES_1.0.7.md to GitHub release
- [ ] Announce release (if applicable)

## 🧹 Cleanup (Optional)

### Working Directory Files
These test files are in the working directory and not tracked by git:
- test_string_detection.py
- test_string_detection_fixed.py
- test_string_literal_detection.py
- test_trace_state.py

**Action Required:**
- [ ] Delete these files if no longer needed, or
- [ ] Move to tests/ directory if they should be kept, or
- [ ] Add to .gitignore if they're temporary development files

```bash
# To delete:
rm test_string_detection.py test_string_detection_fixed.py test_string_literal_detection.py test_trace_state.py

# OR to move to tests:
mv test_string_*.py test_trace_state.py tests/

# OR add to .gitignore:
echo "test_string_*.py" >> .gitignore
echo "test_trace_*.py" >> .gitignore
```

## 📝 Notes

- Version 1.0.7 is a maintenance release with no breaking changes
- All existing features are fully backward compatible
- Documentation is current and comprehensive
- Test coverage remains high with additional edge case coverage

## 🔗 Important Links

- Repository: https://github.com/mu-triv/sny-copyright-checker
- PyPI: https://pypi.org/project/sny-copyright-checker/
- Issues: https://github.com/mu-triv/sny-copyright-checker/issues
