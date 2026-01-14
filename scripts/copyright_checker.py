#!/usr/bin/env python
# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file



"""Main copyright checker with auto-insertion functionality"""

import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

try:
    import pathspec
    HAS_PATHSPEC = True
except ImportError:
    HAS_PATHSPEC = False

from .copyright_template_parser import CopyrightTemplate, CopyrightTemplateParser


class CopyrightChecker:
    """Copyright checker with support for multiple file formats and auto-insertion"""

    def __init__(self, template_path: str, git_aware: bool = True,
                 ignore_file: Optional[str] = None, use_gitignore: bool = True):
        """
        Initialize the copyright checker.

        :param template_path: Path to the copyright template file
        :param git_aware: If True, use Git history for year management (default: True)
        :param ignore_file: Path to .copyrightignore file (default: None, auto-detect)
        :param use_gitignore: If True, also respect .gitignore patterns (default: True)
        """
        self.template_path = template_path
        self.templates: Dict[str, CopyrightTemplate] = {}
        self.git_aware = git_aware
        self.use_gitignore = use_gitignore
        self.ignore_spec = None
        self._load_templates()
        self._load_ignore_patterns(ignore_file)

    def _load_templates(self) -> None:
        """Load and parse copyright templates from file."""
        try:
            self.templates = CopyrightTemplateParser.parse(self.template_path)
            logging.info(
                f"Loaded {len(self.templates)} copyright templates for extensions: "
                f"{', '.join(self.templates.keys())}"
            )
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Copyright template file not found: {self.template_path}"
            )
        except ValueError as e:
            raise ValueError(f"Failed to parse copyright template: {e}")

    def _load_ignore_patterns(self, ignore_file: Optional[str] = None) -> None:
        """
        Load ignore patterns from .copyrightignore and optionally .gitignore.

        :param ignore_file: Path to .copyrightignore file (if None, auto-detect)
        """
        if not HAS_PATHSPEC:
            logging.debug("pathspec not installed, ignore patterns disabled")
            return

        patterns = []

        # Load .copyrightignore
        copyright_ignore_path = ignore_file or ".copyrightignore"
        if os.path.exists(copyright_ignore_path):
            patterns.extend(self._read_ignore_file(copyright_ignore_path))
            logging.debug(f"Loaded patterns from {copyright_ignore_path}")

        # Load .gitignore if enabled
        if self.use_gitignore and os.path.exists(".gitignore"):
            patterns.extend(self._read_ignore_file(".gitignore"))
            logging.debug("Loaded patterns from .gitignore")

        if patterns:
            self.ignore_spec = pathspec.PathSpec.from_lines('gitwildmatch', patterns)
            logging.info(f"Loaded {len(patterns)} ignore patterns")
        else:
            logging.debug("No ignore patterns found")

    def _read_ignore_file(self, filepath: str) -> List[str]:
        """
        Read and parse an ignore file.

        :param filepath: Path to the ignore file
        :return: List of pattern strings
        """
        patterns = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        patterns.append(line)
        except Exception as e:
            logging.warning(f"Failed to read ignore file {filepath}: {e}")
        return patterns

    def should_ignore(self, filepath: str) -> bool:
        """
        Check if a file should be ignored based on ignore patterns.

        :param filepath: Path to the file to check
        :return: True if file should be ignored
        """
        if not self.ignore_spec:
            return False

        # Convert to relative path if absolute
        original_filepath = filepath
        if os.path.isabs(filepath):
            try:
                # Resolve symlinks to get the real path for accurate relative path calculation
                cwd = os.path.realpath(os.getcwd())
                real_filepath = os.path.realpath(filepath)

                # Check if file is under the current directory
                try:
                    filepath = os.path.relpath(real_filepath, cwd)
                except ValueError:
                    # Can't get relative path (different drive on Windows)
                    return False

                # If the relative path goes outside the current directory tree
                # (starts with ..), don't apply ignore patterns
                if filepath.startswith('..'):
                    logging.debug(f"File outside project directory, not applying ignore patterns: {original_filepath}")
                    return False
            except (ValueError, OSError):
                # Error resolving paths
                return False

        # Normalize path separators for matching
        filepath = filepath.replace('\\', '/')

        is_ignored = self.ignore_spec.match_file(filepath)
        if is_ignored:
            logging.debug(f"File ignored by pattern: {filepath}")
        return is_ignored

    def check_file(self, filepath: str, auto_fix: bool = True) -> Tuple[bool, bool]:
        """
        Check if a file contains valid copyright notice.

        :param filepath: Path to the file to check
        :param auto_fix: If True, automatically add missing copyright notices
        :return: Tuple of (has_valid_notice, was_modified)
        :raises FileNotFoundError: If the file doesn't exist
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Source file not found: {filepath}")

        # Get file extension
        file_ext = Path(filepath).suffix
        if not file_ext:
            logging.debug(f"Skipping file without extension: {filepath}")
            return True, False

        # Check if we have a template for this extension
        if file_ext not in self.templates:
            logging.debug(
                f"No copyright template for extension '{file_ext}', skipping: {filepath}"
            )
            return True, False

        template = self.templates[file_ext]

        # Read file content (preserve line endings for later)
        try:
            with open(filepath, "rb") as f:
                raw_content = f.read()
            content = raw_content.decode("utf-8")
        except UnicodeDecodeError:
            # Try with different encoding or skip binary files
            logging.warning(f"Cannot read file (binary or encoding issue): {filepath}")
            return True, False

        # Detect line ending style
        line_ending = self._detect_line_ending(content)

        # Check if copyright notice exists
        if template.matches(content):
            logging.debug(f"Valid copyright notice found in: {filepath}")
            return True, False

        # Copyright notice is missing
        if auto_fix:
            logging.info(f"Adding copyright notice to: {filepath}")
            try:
                self._add_copyright_notice(filepath, template, content, line_ending)
                return True, True
            except Exception as e:
                logging.error(f"Failed to add copyright notice to {filepath}: {e}")
                return False, False
        else:
            logging.warning(f"Missing copyright notice in: {filepath}")
            return False, False

    def _detect_line_ending(self, content: str) -> str:
        """
        Detect the line ending style used in content.

        :param content: File content
        :return: Line ending string ("\r\n" for Windows, "\n" for Unix)
        """
        if "\r\n" in content:
            return "\r\n"
        return "\n"

    def _add_copyright_notice(
        self, filepath: str, template: CopyrightTemplate, content: str, line_ending: str = "\n"
    ) -> None:
        """
        Add copyright notice to a file.

        :param filepath: Path to the file
        :param template: Copyright template to use
        :param content: Current file content
        :param line_ending: Line ending style to use ("\r\n" or "\n")
        """
        year_str = self._determine_copyright_year(filepath, template, content)
        copyright_notice = template.get_notice_with_year(year_str)

        # Normalize content to LF for processing
        normalized_content = content.replace("\r\n", "\n")
        lines = normalized_content.split("\n")
        insert_position = 0

        if lines and lines[0].startswith("#!"):
            insert_position = 1
            # Add empty line after shebang if not present
            if len(lines) > 1 and lines[1].strip():
                copyright_notice = "\n" + copyright_notice

        # Add newlines around copyright notice
        if insert_position == 0:
            new_content = copyright_notice + "\n\n" + normalized_content
        else:
            new_content = (
                lines[0]
                + "\n"
                + copyright_notice
                + "\n\n"
                + "\n".join(lines[insert_position:])
            )

        # Convert to the original line ending style
        if line_ending == "\r\n":
            new_content = new_content.replace("\n", "\r\n")

        # Write back to file in binary mode to preserve exact line endings
        with open(filepath, "wb") as f:
            f.write(new_content.encode("utf-8"))

    def check_files(
        self, filepaths: List[str], auto_fix: bool = True
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Check multiple files for copyright notices.

        :param filepaths: List of file paths to check
        :param auto_fix: If True, automatically add missing copyright notices
        :return: Tuple of (passed_files, failed_files, modified_files)
        """
        passed = []
        failed = []
        modified = []

        for filepath in filepaths:
            # Skip ignored files
            if self.should_ignore(filepath):
                logging.debug(f"Skipping ignored file: {filepath}")
                passed.append(filepath)  # Consider ignored files as "passed"
                continue

            try:
                has_notice, was_modified = self.check_file(filepath, auto_fix)
                if has_notice:
                    passed.append(filepath)
                    if was_modified:
                        modified.append(filepath)
                else:
                    failed.append(filepath)
            except FileNotFoundError:
                logging.error(f"File not found: {filepath}")
                failed.append(filepath)
            except Exception as e:
                logging.error(f"Error checking {filepath}: {e}")
                failed.append(filepath)

        return passed, failed, modified

    def get_supported_extensions(self) -> Set[str]:
        """
        Get the set of supported file extensions.

        :return: Set of file extensions (e.g., {'.py', '.c', '.sql'})
        """
        return set(self.templates.keys())

    def get_changed_files(self, base_ref: str = "HEAD", repo_path: Optional[str] = None) -> List[str]:
        """
        Get list of changed files from git.

        :param base_ref: Git reference to compare against (default: HEAD)
        :param repo_path: Path to git repository (default: current directory)
        :return: List of changed file paths (absolute paths)
        :raises RuntimeError: If git command fails
        """
        try:
            # Get the working directory for git commands
            work_dir = repo_path if repo_path else os.getcwd()

            # Get staged and unstaged changes
            cmd = ["git", "diff", "--name-only", base_ref]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                cwd=work_dir
            )

            changed_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]

            # Also get unstaged changes
            result_unstaged = subprocess.run(
                ["git", "diff", "--name-only"],
                capture_output=True,
                text=True,
                check=True,
                cwd=work_dir
            )

            unstaged_files = [f.strip() for f in result_unstaged.stdout.split('\n') if f.strip()]

            # Combine and deduplicate
            all_changed = list(set(changed_files + unstaged_files))

            # Convert to absolute paths and filter to only supported extensions
            filtered_files = []
            for f in all_changed:
                abs_path = os.path.join(work_dir, f) if not os.path.isabs(f) else f
                if Path(abs_path).suffix in self.templates and os.path.exists(abs_path):
                    filtered_files.append(abs_path)

            logging.debug(f"Found {len(filtered_files)} changed files with supported extensions")
            return filtered_files

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get changed files from git: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError("Git is not installed or not available in PATH")

    def _get_file_creation_year(self, filepath: str) -> Optional[int]:
        """
        Get the year when a file was first committed to Git.

        :param filepath: Path to the file
        :return: Year of first commit, or None if not in Git or error occurred
        """
        if not self.git_aware:
            return None

        try:
            # Get the first commit year for the file
            # Use --follow to track file renames and --diff-filter=A to get when it was added
            result = subprocess.run(
                ["git", "log", "--follow", "--format=%aI", "--reverse", "--", filepath],
                capture_output=True,
                text=True,
                check=True,
                cwd=os.path.dirname(filepath) or os.getcwd()
            )

            output = result.stdout.strip()
            if output:
                # Get first line (earliest commit)
                first_commit_date = output.split('\n')[0]
                # Extract year from ISO format (e.g., "2020-03-15T10:30:00+01:00")
                year = int(first_commit_date.split('-')[0])
                logging.debug(f"File {filepath} first committed in {year}")
                return year
            else:
                # File not in Git history yet
                logging.debug(f"File {filepath} not in Git history")
                return None

        except subprocess.CalledProcessError as e:
            logging.debug(f"Failed to get Git history for {filepath}: {e.stderr}")
            return None
        except (ValueError, IndexError) as e:
            logging.debug(f"Failed to parse Git date for {filepath}: {e}")
            return None
        except FileNotFoundError:
            logging.debug("Git is not installed or not available")
            return None

    def _is_file_modified(self, filepath: str) -> bool:
        """
        Check if a file has uncommitted changes or is not yet tracked by Git.

        :param filepath: Path to the file
        :return: True if file is modified/new, False if unchanged
        """
        if not self.git_aware:
            return True  # If not Git-aware, always treat as modified

        try:
            # Check if file is in working tree with changes
            result = subprocess.run(
                ["git", "status", "--porcelain", filepath],
                capture_output=True,
                text=True,
                check=True,
                cwd=os.path.dirname(filepath) or os.getcwd()
            )

            output = result.stdout.strip()
            # If output is not empty, file has changes or is untracked
            is_modified = bool(output)
            logging.debug(f"File {filepath} modified: {is_modified}")
            return is_modified

        except subprocess.CalledProcessError as e:
            logging.debug(f"Failed to check Git status for {filepath}: {e.stderr}")
            return True  # Assume modified if we can't check
        except FileNotFoundError:
            logging.debug("Git is not installed or not available")
            return True  # Assume modified if Git not available

    def _determine_copyright_year(self, filepath: str, template: CopyrightTemplate, content: str) -> str:
        """
        Determine the appropriate copyright year or year range for a file.

        Logic:
        1. If file has existing copyright, extract existing years
        2. If file is unchanged in Git, preserve existing years
        3. If file is modified, extend year range to current year
        4. If no existing copyright:
           - Use Git creation year as start (if available)
           - Use current year as end if file is modified

        :param filepath: Path to the file
        :param template: Copyright template for the file type
        :param content: Current file content
        :return: Year string (e.g., "2024" or "2020-2024")
        """
        current_year = datetime.now().year

        # Try to extract existing years from copyright notice
        existing_years = template.extract_years(content)

        if existing_years:
            start_year, end_year = existing_years
            logging.debug(f"Existing copyright years: {start_year}-{end_year or start_year}")

            # Check if file is modified
            if self._is_file_modified(filepath):
                # File is modified, update end year to current
                if current_year > start_year:
                    year_str = f"{start_year}-{current_year}"
                else:
                    year_str = str(start_year)
                logging.debug(f"File modified, updating years to: {year_str}")
            else:
                # File unchanged, preserve existing years
                if end_year:
                    year_str = f"{start_year}-{end_year}"
                else:
                    year_str = str(start_year)
                logging.debug(f"File unchanged, preserving years: {year_str}")
        else:
            # No existing copyright, determine from Git history
            creation_year = self._get_file_creation_year(filepath)

            if creation_year:
                # File is in Git, use creation year as start
                if self._is_file_modified(filepath) and current_year > creation_year:
                    year_str = f"{creation_year}-{current_year}"
                else:
                    year_str = str(creation_year)
                logging.debug(f"New copyright using Git history: {year_str}")
            else:
                # File not in Git or Git not available, use current year
                year_str = str(current_year)
                logging.debug(f"New copyright using current year: {year_str}")

        return year_str
