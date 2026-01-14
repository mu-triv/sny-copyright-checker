<!--
SPDX-License-Identifier: MIT
Copyright 2026 Sony Group Corporation
Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
License: For licensing see the License.txt file
-->

# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **Hierarchical copyright templates**: Support different copyright notices per directory (new `--hierarchical` flag)
  - Directory-based template discovery (nearest template wins)
  - Child directories override parent templates
  - Template caching for performance
  - Perfect for monorepos and vendor/third-party code
- Extended test suites: hierarchical templates (20 tests), Git-aware years (23 tests), ignore patterns (28 tests)
- Documentation: HIERARCHICAL_TEMPLATES.md with examples and best practices

### Changed
- `CopyrightChecker` now supports hierarchical mode with template discovery and caching

### Fixed
- Non-hierarchical mode correctly loads templates at initialization

## [1.0.4] - 2026-01-14

### Added
- **Git-aware year management**: Preserves earliest year and extends range only when files are modified (new `--no-git-aware` flag to disable)
- **Ignore files support**: `.copyrightignore` and `.gitignore` pattern matching (new `--ignore-file` and `--no-gitignore` flags)
- Comprehensive test coverage: 16 tests for Git-aware years, 26+ tests for ignore patterns
- Documentation: GIT_AWARE_YEAR_MANAGEMENT.md, IGNORE_FILES.md, EXAMPLES_GIT_AWARE.md, .copyrightignore.example

### Changed
- `CopyrightTemplate.get_notice_with_year()` now accepts int or string for year ranges
- Added `pathspec>=0.11.0` dependency for gitignore-style pattern matching

### Fixed
- Ignore patterns correctly handle absolute paths and symlinks on macOS

## [1.0.3] - 2026-01-12

### Added
- **Template variables feature**: Support for `[VARIABLES]` section to define reusable values
  - Variable substitution with `{VARIABLE_NAME}` syntax
  - Support for SPDX license identifiers as variables
  - Variables can contain any value including regex patterns
  - Undefined variables remain as placeholders
- Comprehensive test coverage for variables feature:
  - 10 unit tests in test_template_parser.py
  - 4 integration tests in test_integration.py
  - Edge cases: undefined variables, multiple VARIABLES sections, special characters, case sensitivity
- Test documenting template change behavior (test_template_change_creates_duplicate_copyright)
- SPDX-License-Identifier headers added to all project files
- Bug fix: Only the first `[VARIABLES]` section is processed (subsequent ones are ignored)

### Changed
- Updated `copyright.txt` to use variables format with SPDX identifiers
- Enhanced documentation with variables syntax and SPDX examples (README.md, QUICKSTART.md, EXAMPLES.md)
- Improved template parser to substitute variables before creating templates

### Documentation
- Added "Known Issues and Limitations" section to README.md
- Documented template change behavior: changing copyright.txt creates duplicate copyrights (by design)
- Provided workarounds for template migration scenarios

## [1.0.2] - 2026-01-11

### Added
- **Grouped extensions syntax**: Support for `[.ext1, .ext2, .ext3]` format to group multiple file extensions with the same copyright format
- Extended language support:
  - Go (`.go`)
  - Rust (`.rs`)
  - YAML (`.yaml`, `.yml`)
  - Markdown (`.md`)
- Comprehensive test coverage for grouped extensions feature (9 new tests)
- VERSION_MANAGEMENT.md documentation for centralized version control

### Changed
- Consolidated `copyright.txt` from 15 sections to 6 using grouped extensions (easier maintenance)
- Centralized version management: Version now defined only in `scripts/__init__.py`
- Updated `pyproject.toml` and `setup.cfg` to use dynamic versioning from `__init__.py`
- Enhanced README.md with:
  - Documentation links section
  - Grouped extensions syntax examples
  - Comprehensive pre-commit configuration examples
- Updated QUICKSTART.md and EXAMPLES.md with grouped extensions examples

### Improved
- Template parser now supports comma-separated extensions in section headers
- All grouped extensions share the same template instance (memory efficient)
- Better maintainability: Update copyright format once for multiple file types
- Documentation section in README with quick links to all guides

## [1.0.1] - 2026-01-11

### Added
- Line ending preservation: Automatically detects and preserves CRLF (Windows) or LF (Unix/Linux) line endings
- Git integration: New `--changed-only` flag to check only modified files in git repository
- Git reference comparison: `--base-ref` option to compare against specific branches or commits
- Copyright preservation: Existing copyrights are never replaced, even with old years
- Comprehensive test coverage for line ending handling (9 tests)
- Comprehensive test coverage for git integration (9 tests)

### Changed
- Reading files in binary mode to properly detect and preserve line endings
- File modification now preserves original line ending style
- Copyright detection now recognizes any year (not just current year)

### Fixed
- Files with existing copyrights no longer get duplicate copyright notices
- CRLF line endings are now properly preserved on Windows
- LF line endings are now properly preserved on Unix/Linux/macOS
- Mixed line ending files are handled correctly

## [1.0.0] - 2026-01-10

### Added
- Initial release of SNY Copyright Check pre-commit hook
- Multi-format copyright template support with section-based syntax
- Regex pattern matching for flexible year validation
- Automatic copyright notice insertion with current year
- Support for multiple file types (.py, .sql, .c, .cpp, .h, .js, .ts, .java, .sh)
- Smart handling of shebang lines
- Command-line interface with --fix/--no-fix options
- Pre-commit hook integration
- Comprehensive documentation and examples
- Unit and integration tests

### Features
- Section-based copyright.txt template format
- Regex support for year matching (e.g., `{regex:\d{4}(-\d{4})?}`)
- Auto-insertion of copyright notices with current year
- Skip files with unsupported extensions
- Preserve file structure (shebangs, formatting)
- Verbose logging option

### Improvements over similar tools
- Multiple file format support in single template
- Regex-based pattern matching
- Automatic copyright insertion (not just checking)
- More flexible template system
