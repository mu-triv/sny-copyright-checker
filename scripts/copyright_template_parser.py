#!/usr/bin/env python

"""Parser for multi-format copyright template file with regex support"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Pattern


@dataclass
class CopyrightTemplate:
    """Represents a copyright notice template for a specific file extension"""

    extension: str
    lines: List[str]
    regex_patterns: List[Optional[Pattern[str]]]

    def get_notice_with_year(self, year: int) -> str:
        """
        Generate the copyright notice with the specified year.

        :param year: Year to insert into the copyright notice
        :return: Complete copyright notice as string
        """
        result_lines = []
        for line in self.lines:
            #Replace {regex:...} with the actual year
            # Handle nested braces properly
            result_line = line
            start = result_line.find("{regex:")
            if start != -1:
                # Find the matching closing brace
                depth = 0
                end = -1
                for i in range(start, len(result_line)):
                    if result_line[i] == '{':
                        depth += 1
                    elif result_line[i] == '}':
                        depth -= 1
                        if depth == 0:
                            end = i
                            break
                if end != -1:
                    result_line = result_line[:start] + str(year) + result_line[end+1:]
            result_lines.append(result_line)
        return "\n".join(result_lines)

    def matches(self, content: str) -> bool:
        """
        Check if content contains a valid copyright notice matching this template.

        :param content: Content to check
        :return: True if content matches the template (with regex patterns)
        """
        content_lines = content.split("\n")
        
        # Try to find the template starting at different positions
        for start_idx in range(len(content_lines)):
            if self._matches_at_position(content_lines, start_idx):
                return True
        return False

    def _matches_at_position(self, content_lines: List[str], start_idx: int) -> bool:
        """
        Check if template matches at a specific position in content.

        :param content_lines: Lines of content to check
        :param start_idx: Starting line index
        :return: True if template matches at this position
        """
        if start_idx + len(self.lines) > len(content_lines):
            return False

        for i, (template_line, regex_pattern) in enumerate(
            zip(self.lines, self.regex_patterns)
        ):
            content_line = content_lines[start_idx + i].rstrip()
            
            if regex_pattern:
                # Build pattern from template line by replacing {regex:...} with the regex
                # Find the {regex:...} part and replace it
                start_marker = "{regex:"
                start_idx_marker = template_line.find(start_marker)
                
                if start_idx_marker != -1:
                    # Find the matching closing brace
                    start_pos = start_idx_marker + len(start_marker)
                    depth = 1
                    end_idx_marker = start_pos
                    
                    while end_idx_marker < len(template_line) and depth > 0:
                        if template_line[end_idx_marker] == '{':
                            depth += 1
                        elif template_line[end_idx_marker] == '}':
                            depth -= 1
                        end_idx_marker += 1
                    
                    # Build the pattern: escape the parts before and after, insert regex in between
                    before = re.escape(template_line[:start_idx_marker])
                    after = re.escape(template_line[end_idx_marker:])
                    regex_str = template_line[start_pos:end_idx_marker-1]
                    pattern_str = f"{before}({regex_str}){after}"
                    
                    if not re.match(pattern_str, content_line):
                        return False
                else:
                    # No {regex:} found but regex_pattern is set - shouldn't happen
                    if content_line != template_line.rstrip():
                        return False
            else:
                # Exact match required
                if content_line != template_line.rstrip():
                    return False

        return True


class CopyrightTemplateParser:
    """Parser for copyright template files with multiple sections"""

    @staticmethod
    def parse(template_path: str) -> Dict[str, CopyrightTemplate]:
        """
        Parse a copyright template file.

        The template file should have sections like:
        [.py]
        # Copyright {regex:\\d{4}(-\\d{4})?} SNY Group Corporation
        # Author: ...

        [.sql]
        -- Copyright {regex:\\d{4}(-\\d{4})?} SNY Group Corporation
        -- Author: ...

        :param template_path: Path to the template file
        :return: Dictionary mapping file extensions to CopyrightTemplate objects
        :raises FileNotFoundError: If template file doesn't exist
        :raises ValueError: If template file format is invalid
        """
        templates = {}
        current_extension = None
        current_lines = []

        with open(template_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.rstrip("\n")
                
                # Skip empty lines when not inside a section
                if not line.strip() and current_extension is None:
                    continue

                # Check for section header [.ext]
                section_match = re.match(r"^\[(\.\w+)\]$", line.strip())
                if section_match:
                    # Save previous section if exists
                    if current_extension is not None:
                        templates[current_extension] = CopyrightTemplateParser._create_template(
                            current_extension, current_lines
                        )
                    
                    # Start new section
                    current_extension = section_match.group(1)
                    current_lines = []
                elif current_extension is not None:
                    # Add line to current section (including empty lines within section)
                    if line or current_lines:  # Start collecting after first non-empty
                        current_lines.append(line)

        # Save last section
        if current_extension is not None and current_lines:
            # Remove trailing empty lines
            while current_lines and not current_lines[-1]:
                current_lines.pop()
            
            if current_lines:
                templates[current_extension] = CopyrightTemplateParser._create_template(
                    current_extension, current_lines
                )

        if not templates:
            raise ValueError(f"No valid sections found in template file: {template_path}")

        return templates

    @staticmethod
    def _create_template(extension: str, lines: List[str]) -> CopyrightTemplate:
        """
        Create a CopyrightTemplate from extension and lines.

        :param extension: File extension (e.g., '.py')
        :param lines: Template lines
        :return: CopyrightTemplate object
        """
        regex_patterns = []
        
        for line in lines:
            # Extract regex patterns from {regex:...}
            # Handle nested braces by finding the matching closing brace
            start_marker = "{regex:"
            start_idx = line.find(start_marker)
            
            if start_idx != -1:
                # Find the matching closing brace
                start_pos = start_idx + len(start_marker)
                depth = 1
                end_idx = start_pos
                
                while end_idx < len(line) and depth > 0:
                    if line[end_idx] == '{':
                        depth += 1
                    elif line[end_idx] == '}':
                        depth -= 1
                    end_idx += 1
                
                if depth == 0:
                    regex_str = line[start_pos:end_idx-1]
                    try:
                        pattern = re.compile(regex_str)
                        regex_patterns.append(pattern)
                    except re.error as e:
                        raise ValueError(f"Invalid regex pattern '{regex_str}': {e}")
                else:
                    raise ValueError(f"Unmatched braces in template line: {line}")
            else:
                regex_patterns.append(None)

        return CopyrightTemplate(
            extension=extension,
            lines=lines,
            regex_patterns=regex_patterns
        )
