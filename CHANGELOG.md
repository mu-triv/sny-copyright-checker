# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-01-10

### Added
- Initial release of Sony Copyright Check pre-commit hook
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
