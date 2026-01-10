#!/usr/bin/env python

"""Main copyright checker with auto-insertion functionality"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

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

        # Read file content
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding or skip binary files
            logging.warning(f"Cannot read file (binary or encoding issue): {filepath}")
            return True, False

        # Check if copyright notice exists
        if template.matches(content):
            logging.debug(f"Valid copyright notice found in: {filepath}")
            return True, False

        # Copyright notice is missing
        if auto_fix:
            logging.info(f"Adding copyright notice to: {filepath}")
            try:
                self._add_copyright_notice(filepath, template, content)
                return True, True
            except Exception as e:
                logging.error(f"Failed to add copyright notice to {filepath}: {e}")
                return False, False
        else:
            logging.warning(f"Missing copyright notice in: {filepath}")
            return False, False

    def _add_copyright_notice(
        self, filepath: str, template: CopyrightTemplate, content: str
    ) -> None:
        """
        Add copyright notice to a file.

        :param filepath: Path to the file
        :param template: Copyright template to use
        :param content: Current file content
        """
        current_year = datetime.now().year
        copyright_notice = template.get_notice_with_year(current_year)

        # Handle shebang lines - keep them at the top
        lines = content.split("\n")
        insert_position = 0

        if lines and lines[0].startswith("#!"):
            insert_position = 1
            # Add empty line after shebang if not present
            if len(lines) > 1 and lines[1].strip():
                copyright_notice = "\n" + copyright_notice
        
        # Add newlines around copyright notice
        if insert_position == 0:
            new_content = copyright_notice + "\n\n" + content
        else:
            new_content = (
                lines[0]
                + "\n"
                + copyright_notice
                + "\n\n"
                + "\n".join(lines[insert_position:])
            )

        # Write back to file
        with open(filepath, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_content)

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
