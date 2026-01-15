#!/usr/bin/env python
# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file



"""Main copyright checker with auto-insertion functionality"""

import logging
import os
import re
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
                 ignore_file: Optional[str] = None, use_gitignore: bool = True,
                 hierarchical: bool = False, replace_mode: bool = False,
                 per_file_years: bool = False):
        """
        Initialize the copyright checker.

        :param template_path: Path to the copyright template file (or filename for hierarchical mode)
        :param git_aware: If True, use Git history for year management (default: True)
        :param ignore_file: Path to .copyrightignore file (default: None, auto-detect)
        :param use_gitignore: If True, also respect .gitignore patterns (default: True)
        :param hierarchical: If True, look for template_path in each directory hierarchy (default: False)
        :param replace_mode: If True, replace similar existing copyrights (default: False)
        :param per_file_years: If True, use individual file creation years; if False, use project inception year (default: False)
        """
        self.template_path = template_path
        self.templates: Dict[str, CopyrightTemplate] = {}
        self.git_aware = git_aware
        self.use_gitignore = use_gitignore
        self.hierarchical = hierarchical
        self.replace_mode = replace_mode
        self.per_file_years = per_file_years
        self.ignore_spec = None
        # Cache for hierarchical templates: directory -> templates dict
        self.template_cache: Dict[str, Optional[Dict[str, CopyrightTemplate]]] = {}
        # Cache for project creation year
        self._repo_year_cache: Optional[int] = None

        if not hierarchical:
            self.templates = self._load_templates()
        else:
            logging.info(f"Hierarchical mode enabled: looking for '{template_path}' in directory tree")

        self._load_ignore_patterns(ignore_file)

    def _load_templates(self, template_file: Optional[str] = None) -> Dict[str, CopyrightTemplate]:
        """Load and parse copyright templates from file.

        :param template_file: Path to template file (uses self.template_path if None)
        :return: Dictionary of templates by extension
        """
        template_file = template_file or self.template_path
        try:
            templates = CopyrightTemplateParser.parse(template_file)
            logging.debug(
                f"Loaded {len(templates)} copyright templates from {template_file} "
                f"for extensions: {', '.join(templates.keys())}"
            )
            return templates
        except FileNotFoundError:
            if not self.hierarchical:
                raise FileNotFoundError(
                    f"Copyright template file not found: {template_file}"
                )
            return {}
        except ValueError as e:
            if not self.hierarchical:
                raise ValueError(f"Failed to parse copyright template: {e}")
            logging.warning(f"Failed to parse {template_file}: {e}")
            return {}

    def _find_copyright_file(self, directory: str) -> Optional[str]:
        """
        Find the nearest copyright template file by traversing up the directory tree.

        :param directory: Starting directory to search from
        :return: Path to copyright file, or None if not found
        """
        current_dir = os.path.abspath(directory)
        root = os.path.abspath(os.sep)

        while True:
            copyright_path = os.path.join(current_dir, self.template_path)
            if os.path.exists(copyright_path):
                logging.debug(f"Found copyright file: {copyright_path}")
                return copyright_path

            # Move up one directory
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir or current_dir == root:
                # Reached the root
                break
            current_dir = parent_dir

        return None

    def _get_templates_for_directory(self, directory: str) -> Dict[str, CopyrightTemplate]:
        """
        Get copyright templates for a specific directory (hierarchical mode).
        Uses caching to avoid re-parsing the same file.

        :param directory: Directory to get templates for
        :return: Dictionary of templates by extension
        """
        directory = os.path.abspath(directory)

        # Check cache first
        if directory in self.template_cache:
            cached = self.template_cache[directory]
            return cached if cached is not None else {}

        # Find nearest copyright file
        copyright_file = self._find_copyright_file(directory)

        if copyright_file:
            # Load templates from found file
            templates = self._load_templates(copyright_file)
            self.template_cache[directory] = templates
            return templates
        else:
            # No copyright file found in hierarchy
            logging.debug(f"No copyright file found for directory: {directory}")
            self.template_cache[directory] = None
            return {}

    def _get_template_for_file(self, filepath: str) -> Dict[str, CopyrightTemplate]:
        """
        Get the appropriate templates for a file.

        :param filepath: Path to the file
        :return: Dictionary of templates by extension
        """
        if not self.hierarchical:
            return self.templates

        # In hierarchical mode, find templates based on file's directory
        file_dir = os.path.dirname(os.path.abspath(filepath))
        return self._get_templates_for_directory(file_dir)

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
            self.ignore_spec = pathspec.PathSpec.from_lines('gitignore', patterns)
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

        # Get appropriate templates for this file
        templates = self._get_template_for_file(filepath)

        # Check if we have a template for this extension
        if file_ext not in templates:
            if self.hierarchical:
                logging.debug(
                    f"No copyright template found for '{file_ext}' in hierarchy for: {filepath}"
                )
            else:
                logging.debug(
                    f"No copyright template for extension '{file_ext}', skipping: {filepath}"
                )
            return True, False

        template = templates[file_ext]

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

        # Check if copyright notice exists and matches template
        if template.matches(content):
            logging.debug(f"Valid copyright notice found in: {filepath}")
            return True, False

        # Copyright notice doesn't match template exactly
        # In replace mode, try to replace similar copyrights
        if self.replace_mode and auto_fix:
            logging.debug(f"Replace mode enabled, checking for similar copyright in: {filepath}")
            try:
                was_replaced = self._replace_copyright_notice(filepath, template, content, line_ending)
                if was_replaced:
                    return True, True
                else:
                    # No similar copyright found, fall through to add new copyright
                    logging.debug(f"No similar copyright found, will add new copyright to: {filepath}")
            except Exception as e:
                logging.error(f"Failed to replace copyright notice in {filepath}: {e}")
                # Fall through to try adding new copyright

        # Copyright notice is missing or couldn't be replaced
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
        In hierarchical mode, returns extensions from root template if available.

        :return: Set of file extensions (e.g., {'.py', '.c', '.sql'})
        """
        if not self.hierarchical:
            return set(self.templates.keys())

        # In hierarchical mode, try to find a template at current directory
        cwd_templates = self._get_templates_for_directory(os.getcwd())
        if cwd_templates:
            return set(cwd_templates.keys())

        # Fallback: collect all unique extensions from cache
        all_extensions = set()
        for templates in self.template_cache.values():
            if templates:
                all_extensions.update(templates.keys())

        return all_extensions if all_extensions else set()

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

    def _get_repository_creation_year(self, filepath: str) -> Optional[int]:
        """
        Get the year when the Git repository was created (first commit).

        :param filepath: Path to any file in the repository (used to find repo root)
        :return: Year of first repository commit, or None if not in Git or error occurred
        """
        if not self.git_aware:
            return None

        # Return cached value if available
        if self._repo_year_cache is not None:
            return self._repo_year_cache

        try:
            # Get the first commit in the repository
            result = subprocess.run(
                ["git", "log", "--reverse", "--format=%aI", "--max-count=1"],
                capture_output=True,
                text=True,
                check=True,
                cwd=os.path.dirname(filepath) or os.getcwd()
            )

            output = result.stdout.strip()
            if output:
                # Extract year from ISO format (e.g., "2018-01-15T10:30:00+01:00")
                year = int(output.split('-')[0])
                logging.debug(f"Repository first committed in {year}")
                self._repo_year_cache = year
                return year
            else:
                logging.debug("No commits found in repository")
                return None

        except subprocess.CalledProcessError as e:
            logging.debug(f"Failed to get repository history: {e.stderr}")
            return None
        except (ValueError, IndexError) as e:
            logging.debug(f"Failed to parse repository date: {e}")
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

            # When using project-wide years, consider project inception year
            if not self.per_file_years:
                repo_year = self._get_repository_creation_year(filepath)
                if repo_year and repo_year < start_year:
                    logging.debug(f"Using project year {repo_year} instead of existing {start_year}")
                    start_year = repo_year

            # Determine end year based on mode
            if not self.per_file_years:
                # Project-wide mode: always extend to current year
                if current_year > start_year:
                    year_str = f"{start_year}-{current_year}"
                else:
                    year_str = str(start_year)
                logging.debug(f"Project-wide mode, years: {year_str}")
            elif self._is_file_modified(filepath):
                # Per-file mode with modified file: extend to current year
                if current_year > start_year:
                    year_str = f"{start_year}-{current_year}"
                else:
                    year_str = str(start_year)
                logging.debug(f"File modified, updating years to: {year_str}")
            else:
                # Per-file mode with unchanged file: preserve existing years
                if end_year:
                    year_str = f"{start_year}-{end_year}"
                else:
                    year_str = str(start_year)
                logging.debug(f"File unchanged, preserving years: {year_str}")
        else:
            # No existing copyright, determine from Git history
            if self.per_file_years:
                # Use individual file creation year
                creation_year = self._get_file_creation_year(filepath)

                if creation_year:
                    # Per-file mode: check if file is modified before extending year
                    if self._is_file_modified(filepath) and current_year > creation_year:
                        year_str = f"{creation_year}-{current_year}"
                    else:
                        year_str = str(creation_year)
                    logging.debug(f"New copyright using Git file history: {year_str}")
                else:
                    # File not in Git, use current year
                    year_str = str(current_year)
                    logging.debug(f"New copyright using current year: {year_str}")
            else:
                # Use project inception year (project-wide mode)
                creation_year = self._get_repository_creation_year(filepath)

                if creation_year:
                    # Project-wide mode: always extend to current year
                    if current_year > creation_year:
                        year_str = f"{creation_year}-{current_year}"
                    else:
                        year_str = str(creation_year)
                    logging.debug(f"New copyright using Git project history: {year_str}")
                else:
                    # Project not in Git, use current year
                    year_str = str(current_year)
                    logging.debug(f"New copyright using current year: {year_str}")

        return year_str

    def _extract_author_entity(self, text: str) -> Optional[str]:
        """
        Extract the specific author/entity identifier from copyright text.

        This identifies the organizational unit or department to ensure
        we don't replace copyrights from different units within the same company.

        :param text: Copyright text
        :return: Key entity identifier or None
        """
        # Look for Author: line
        author_match = re.search(r'author\s*:\s*([^\n]+)', text, re.IGNORECASE)
        if not author_match:
            return None

        author_line = author_match.group(1).strip()

        # Extract the first significant part before comma or "Laboratory" or company name
        # This captures the unit/department identifier
        # Examples:
        #   "R&D Center Europe Brussels Laboratory" -> "r&d center europe"
        #   "Haptic Europe, Brussels Laboratory" -> "haptic europe"
        #   "NSCE, Brussels Laboratory" -> "nsce"

        # Remove company name to focus on the unit
        author_line = re.sub(r',?\s*sony\s+group\s+corporation.*', '', author_line, flags=re.IGNORECASE)

        # Take the part before "Laboratory" or first comma
        parts = re.split(r',|\s+laboratory', author_line, maxsplit=1, flags=re.IGNORECASE)
        if parts:
            entity = parts[0].strip()
            # Normalize: lowercase, keep &, normalize whitespace
            # Preserve & as it's important for "R&D"
            entity = re.sub(r'[^\w\s&]', ' ', entity)
            entity = re.sub(r'\s+', ' ', entity)
            entity = entity.lower().strip()
            return entity if entity else None

        return None

    def _normalize_copyright_text(self, text: str) -> str:
        """
        Normalize copyright text for similarity comparison.

        Removes year information, special characters, and normalizes whitespace
        to focus on the business entity and structure.

        :param text: Copyright text to normalize
        :return: Normalized text for comparison
        """
        # Remove years (4-digit numbers and year ranges)
        text = re.sub(r'\b\d{4}(-\d{4})?\b', '', text)

        # Remove common copyright symbols and markers
        text = re.sub(r'[©Ⓒⓒ(c)(C)]', '', text, flags=re.IGNORECASE)

        # Remove common prefixes/keywords to focus on entity
        text = re.sub(r'\b(copyright|author|license|spdx-license-identifier)\s*:?\s*', '', text, flags=re.IGNORECASE)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters except basic punctuation
        text = re.sub(r'[^\w\s.,&-]', '', text)

        # Convert to lowercase for case-insensitive comparison
        text = text.lower().strip()

        return text

    def _calculate_ngram_similarity(self, text1: str, text2: str, n: int = 3) -> float:
        """
        Calculate n-gram similarity between two texts.

        :param text1: First text
        :param text2: Second text
        :param n: Size of n-grams (default: 3 for trigrams)
        :return: Similarity score between 0.0 and 1.0
        """
        def get_ngrams(text: str, n: int) -> set:
            """Extract n-grams from text"""
            if len(text) < n:
                return {text}
            return {text[i:i+n] for i in range(len(text) - n + 1)}

        ngrams1 = get_ngrams(text1, n)
        ngrams2 = get_ngrams(text2, n)

        if not ngrams1 or not ngrams2:
            return 0.0

        intersection = ngrams1.intersection(ngrams2)
        union = ngrams1.union(ngrams2)

        return len(intersection) / len(union) if union else 0.0

    def _calculate_sequence_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate sequence similarity using longest common subsequence ratio.

        :param text1: First text
        :param text2: Second text
        :return: Similarity score between 0.0 and 1.0
        """
        def lcs_length(s1: str, s2: str) -> int:
            """Calculate longest common subsequence length"""
            m, n = len(s1), len(s2)
            if m == 0 or n == 0:
                return 0

            # Use space-optimized DP (only keep two rows)
            prev = [0] * (n + 1)
            curr = [0] * (n + 1)

            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if s1[i-1] == s2[j-1]:
                        curr[j] = prev[j-1] + 1
                    else:
                        curr[j] = max(prev[j], curr[j-1])
                prev, curr = curr, prev

            return prev[n]

        lcs_len = lcs_length(text1, text2)
        max_len = max(len(text1), len(text2))

        return lcs_len / max_len if max_len > 0 else 0.0

    def _calculate_token_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate token-based similarity (Jaccard coefficient).

        :param text1: First text
        :param text2: Second text
        :return: Similarity score between 0.0 and 1.0
        """
        tokens1 = set(text1.split())
        tokens2 = set(text2.split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)

        return len(intersection) / len(union) if union else 0.0

    def _calculate_copyright_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity score between two copyright texts using multiple methods.

        IMPORTANT: Enforces strict author/entity matching to prevent replacing
        copyrights from different organizational units within the same company.

        Uses a weighted combination of:
        - Token similarity (Jaccard coefficient): Fast, good for entity matching
        - Character n-gram similarity: Robust to typos and variations
        - Sequence similarity (LCS ratio): Considers structural similarity
        - Author entity matching: CRITICAL check to prevent cross-unit replacement

        :param text1: First copyright text
        :param text2: Second copyright text
        :return: Similarity score between 0.0 and 1.0
        """
        # CRITICAL: Extract and compare author entities first
        # Different organizational units must NOT replace each other
        entity1 = self._extract_author_entity(text1)
        entity2 = self._extract_author_entity(text2)

        logging.debug(f"  Entity1 (existing): {entity1}")
        logging.debug(f"  Entity2 (template): {entity2}")

        # If both have author entities specified, they must match closely
        if entity1 and entity2:
            # Calculate entity similarity using token-based comparison
            entity_tokens1 = set(entity1.split())
            entity_tokens2 = set(entity2.split())

            if entity_tokens1 and entity_tokens2:
                entity_intersection = entity_tokens1.intersection(entity_tokens2)
                entity_union = entity_tokens1.union(entity_tokens2)
                entity_similarity = len(entity_intersection) / len(entity_union) if entity_union else 0.0

                # Require at least 70% entity match to proceed
                # This prevents replacing "NSCE" with "SCDE" or "Haptic Europe" with "R&D Center"
                ENTITY_MATCH_THRESHOLD = 0.7

                if entity_similarity < ENTITY_MATCH_THRESHOLD:
                    logging.debug(
                        f"  Entity mismatch: {entity_similarity:.2f} < {ENTITY_MATCH_THRESHOLD} "
                        f"('{entity1}' vs '{entity2}') - preventing replacement"
                    )
                    return 0.0  # Return 0 to prevent replacement

        norm1 = self._normalize_copyright_text(text1)
        norm2 = self._normalize_copyright_text(text2)

        if not norm1 or not norm2:
            return 0.0

        # Calculate multiple similarity metrics
        token_sim = self._calculate_token_similarity(norm1, norm2)
        ngram_sim = self._calculate_ngram_similarity(norm1, norm2, n=3)
        sequence_sim = self._calculate_sequence_similarity(norm1, norm2)

        # Weighted combination:
        # - Token similarity (40%): Primary indicator of same business entity
        # - N-gram similarity (40%): Robust to variations and typos
        # - Sequence similarity (20%): Captures structural similarity
        similarity = (0.4 * token_sim) + (0.4 * ngram_sim) + (0.2 * sequence_sim)

        logging.debug(f"Copyright similarity: {similarity:.2f} (token={token_sim:.2f}, ngram={ngram_sim:.2f}, seq={sequence_sim:.2f})")
        logging.debug(f"  Text1 normalized: {norm1}")
        logging.debug(f"  Text2 normalized: {norm2}")

        return similarity

    def _extract_copyright_block(self, content: str, template: CopyrightTemplate) -> Optional[Tuple[str, int, int]]:
        """
        Extract existing copyright block from file content.

        :param content: File content
        :param template: Copyright template for the file type
        :return: Tuple of (copyright_text, start_line, end_line) or None if not found
        """
        content_lines = content.split("\n")

        # Get the comment prefix from the template
        if not template.lines:
            return None

        first_template_line = template.lines[0]
        # Extract comment prefix (e.g., "# ", "// ", "-- ")
        comment_prefix_match = re.match(r'^(\s*[#/\-*]+\s*)', first_template_line)
        if not comment_prefix_match:
            return None

        comment_prefix = comment_prefix_match.group(1).strip()

        # Search for copyright block
        # Look for lines that start with the comment prefix and contain copyright-related keywords
        copyright_keywords = ['copyright', '©', '(c)', 'author', 'license', 'spdx']

        start_line = None
        end_line = None

        for i, line in enumerate(content_lines):
            line_lower = line.lower()
            # Skip shebang
            if i == 0 and line.startswith('#!'):
                continue

            # Check if line looks like a copyright comment
            if any(keyword in line_lower for keyword in copyright_keywords):
                if start_line is None:
                    start_line = i
                end_line = i
            elif start_line is not None and line.strip() == '':
                # Empty line after copyright block
                break
            elif start_line is not None and not line.strip().startswith(comment_prefix) and line.strip():
                # Non-comment line after copyright started
                break

        if start_line is not None and end_line is not None:
            copyright_lines = content_lines[start_line:end_line + 1]
            copyright_text = '\n'.join(copyright_lines)
            return (copyright_text, start_line, end_line)

        return None

    def _merge_year_ranges(self, existing_years: Tuple[int, Optional[int]], new_start: int, new_end: int) -> str:
        """
        Merge existing and new year ranges intelligently.

        :param existing_years: Tuple of (start_year, end_year or None) from existing copyright
        :param new_start: New start year to consider
        :param new_end: New end year to consider
        :return: Merged year string (e.g., "2020-2026")
        """
        old_start, old_end = existing_years

        # Determine the overall range
        merged_start = min(old_start, new_start)
        merged_end = max(old_end if old_end else old_start, new_end)

        if merged_start == merged_end:
            return str(merged_start)
        else:
            return f"{merged_start}-{merged_end}"

    def _extract_years_general(self, text: str) -> Optional[Tuple[int, Optional[int]]]:
        """
        Extract year or year range from text using general patterns.
        This is more permissive than template-specific extraction.

        :param text: Text to extract years from
        :return: Tuple of (start_year, end_year) or None
        """
        # Look for year patterns: YYYY or YYYY-YYYY
        # Also handle (c), ©, and other copyright markers before the year
        year_pattern = r'\b(\d{4})(?:\s*-\s*(\d{4}))?\b'

        matches = re.findall(year_pattern, text)

        if matches:
            # Take the first match (usually the copyright year)
            first_match = matches[0]
            start_year = int(first_match[0])
            end_year = int(first_match[1]) if first_match[1] else None

            logging.debug(f"General year extraction found: {start_year}-{end_year if end_year else start_year}")
            return (start_year, end_year)

        return None

    def _replace_copyright_notice(
        self, filepath: str, template: CopyrightTemplate, content: str,
        line_ending: str = "\n"
    ) -> bool:
        """
        Replace an existing similar copyright notice with the template notice.

        :param filepath: Path to the file
        :param template: Copyright template to use
        :param content: Current file content
        :param line_ending: Line ending style to use
        :return: True if replacement was made, False otherwise
        """
        # Extract existing copyright block
        copyright_info = self._extract_copyright_block(content, template)

        if not copyright_info:
            logging.debug(f"No existing copyright block found in {filepath}")
            return False

        existing_copyright, start_line, end_line = copyright_info

        # Generate template copyright text for comparison (without year)
        template_text = template.get_notice_with_year("YEAR")

        # Calculate similarity
        similarity = self._calculate_copyright_similarity(existing_copyright, template_text)

        # Use a threshold of 0.4 (40% similarity) to determine if copyrights are related
        # This allows for variations in author, license details, etc.
        SIMILARITY_THRESHOLD = 0.4

        if similarity < SIMILARITY_THRESHOLD:
            logging.debug(
                f"Copyright similarity {similarity:.2f} below threshold {SIMILARITY_THRESHOLD}, "
                f"not replacing in {filepath}"
            )
            return False

        logging.info(
            f"Found similar copyright (similarity: {similarity:.2f}) in {filepath}, replacing..."
        )

        # Extract years from existing copyright using both template-specific and general methods
        existing_years = template.extract_years(existing_copyright)

        # If template extraction failed, try a general year extraction
        if not existing_years:
            existing_years = self._extract_years_general(existing_copyright)

        logging.debug(f"Extracted years from existing copyright: {existing_years}")

        # Determine the new year range
        current_year = datetime.now().year
        creation_year = self._get_file_creation_year(filepath)
        is_modified = self._is_file_modified(filepath)

        if existing_years:
            # Merge existing years with current context
            old_start, old_end = existing_years

            # For files not in Git history (creation_year is None),
            # preserve the existing years and extend if "modified" (which for new files means "use current year")
            if creation_year is None:
                # File not tracked by Git yet
                if is_modified:
                    # Extend the range to current year
                    year_str = self._merge_year_ranges(
                        existing_years,
                        old_start,
                        current_year
                    )
                else:
                    # Preserve existing years
                    if old_end:
                        year_str = f"{old_start}-{old_end}"
                    else:
                        year_str = str(old_start)
            else:
                # File is in Git history
                if is_modified:
                    # File is modified, extend to current year
                    year_str = self._merge_year_ranges(
                        existing_years,
                        creation_year,
                        current_year
                    )
                else:
                    # File unchanged, preserve existing years but ensure range is valid
                    if old_end:
                        year_str = f"{old_start}-{old_end}"
                    else:
                        year_str = str(old_start)
        else:
            # No years found in existing copyright, use standard logic
            if creation_year and creation_year < current_year:
                year_str = f"{creation_year}-{current_year}"
            else:
                year_str = str(current_year)

        logging.debug(f"Using year range: {year_str}")

        # Generate new copyright notice with merged years
        new_copyright = template.get_notice_with_year(year_str)

        # Replace the copyright block in content
        content_lines = content.replace("\r\n", "\n").split("\n")

        # Remove old copyright lines
        new_lines = content_lines[:start_line] + content_lines[end_line + 1:]

        # Determine insertion position (after shebang if present)
        insert_position = 0
        if new_lines and new_lines[0].startswith("#!"):
            insert_position = 1

        # Insert new copyright
        if insert_position == 0:
            new_content = new_copyright + "\n\n" + "\n".join(new_lines)
        else:
            # After shebang
            if insert_position < len(new_lines) and new_lines[insert_position].strip():
                # Add spacing after shebang if needed
                new_content = (
                    new_lines[0] + "\n" +
                    new_copyright + "\n\n" +
                    "\n".join(new_lines[insert_position:])
                )
            else:
                new_content = (
                    new_lines[0] + "\n" +
                    new_copyright + "\n\n" +
                    "\n".join(new_lines[insert_position:])
                )

        # Convert to the original line ending style
        if line_ending == "\r\n":
            new_content = new_content.replace("\n", "\r\n")

        # Write back to file
        with open(filepath, "wb") as f:
            f.write(new_content.encode("utf-8"))

        logging.info(f"Successfully replaced copyright notice in {filepath}")
        return True
