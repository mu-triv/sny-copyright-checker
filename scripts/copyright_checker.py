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

from .copyright_template_parser import CopyrightTemplate, CopyrightTemplateParser


class CopyrightChecker:
    """Copyright checker with support for multiple file formats and auto-insertion"""

    def __init__(self, template_path: str):
        """
        Initialize the copyright checker.

        :param template_path: Path to the copyright template file
        """
        self.template_path = template_path
        self.templates: Dict[str, CopyrightTemplate] = {}
        self._load_templates()

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
        current_year = datetime.now().year
        copyright_notice = template.get_notice_with_year(current_year)

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
