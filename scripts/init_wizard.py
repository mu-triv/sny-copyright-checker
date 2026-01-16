#!/usr/bin/env python
# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file

"""Interactive wizard for initializing copyright configuration."""

import sys
from pathlib import Path
from typing import Dict, List, Optional


# Pre-built copyright templates for common scenarios
COPYRIGHT_TEMPLATES = {
    "mit": {
        "name": "MIT License",
        "spdx": "MIT",
        "description": "Permissive open source license",
        "license_notice": "For licensing see the LICENSE file",
    },
    "apache": {
        "name": "Apache License 2.0",
        "spdx": "Apache-2.0",
        "description": "Permissive with patent grant",
        "license_notice": "Licensed under the Apache License, Version 2.0",
    },
    "gpl3": {
        "name": "GNU General Public License v3.0",
        "spdx": "GPL-3.0-or-later",
        "description": "Copyleft open source license",
        "license_notice": "This is free software: you can redistribute it and/or modify it under the terms of the GNU GPL v3",
    },
    "bsd3": {
        "name": "BSD 3-Clause License",
        "spdx": "BSD-3-Clause",
        "description": "Permissive with attribution",
        "license_notice": "For licensing see the LICENSE file",
    },
    "proprietary": {
        "name": "Proprietary License",
        "spdx": "PROPRIETARY",
        "description": "All rights reserved",
        "license_notice": "All rights reserved. Not for distribution.",
    },
    "custom": {
        "name": "Custom License",
        "spdx": "",
        "description": "Specify your own license",
        "license_notice": "",
    },
}


# Common file extension groups
EXTENSION_GROUPS = {
    "python": [".py"],
    "c_cpp": [".c", ".h", ".cpp", ".hpp", ".cc", ".cxx"],
    "java": [".java"],
    "javascript": [".js", ".jsx", ".ts", ".tsx"],
    "shell": [".sh", ".bash"],
    "sql": [".sql"],
    "go": [".go"],
    "rust": [".rs"],
    "yaml": [".yaml", ".yml"],
    "markdown": [".md"],
    "xml_html": [".xml", ".html", ".htm"],
    "css": [".css", ".scss", ".sass"],
}


def prompt_input(prompt_text: str, default: Optional[str] = None) -> str:
    """Prompt user for input with optional default value."""
    if default:
        display_prompt = f"{prompt_text} [{default}]: "
    else:
        display_prompt = f"{prompt_text}: "

    try:
        value = input(display_prompt).strip()
        return value if value else (default or "")
    except (KeyboardInterrupt, EOFError):
        print("\n\nWizard cancelled.")
        sys.exit(0)


def prompt_choice(
    prompt_text: str, choices: Dict[str, str], default: Optional[str] = None
) -> str:
    """Prompt user to select from a list of choices."""
    print(f"\n{prompt_text}")
    print("-" * 60)

    sorted_keys = sorted(choices.keys())
    for i, key in enumerate(sorted_keys, 1):
        default_marker = " (default)" if key == default else ""
        print(f"  {i}. {key}: {choices[key]}{default_marker}")

    while True:
        choice_input = prompt_input("\nEnter number or key", default or "")

        # If empty and we have a default, use it
        if not choice_input and default:
            return default

        # Try to parse as number
        try:
            choice_num = int(choice_input)
            if 1 <= choice_num <= len(sorted_keys):
                return sorted_keys[choice_num - 1]
        except ValueError:
            pass

        # Try to match as key
        if choice_input in choices:
            return choice_input

        print(
            f"Invalid choice. Please enter a number (1-{len(sorted_keys)}) or a valid key."
        )


def prompt_yes_no(prompt_text: str, default: bool = True) -> bool:
    """Prompt user for yes/no question."""
    default_str = "Y/n" if default else "y/N"
    response = prompt_input(
        f"{prompt_text} ({default_str})", "y" if default else "n"
    ).lower()

    if not response:
        return default
    return response in ("y", "yes", "true", "1")


def prompt_multiselect(prompt_text: str, options: Dict[str, List[str]]) -> List[str]:
    """Prompt user to select multiple options."""
    print(f"\n{prompt_text}")
    print("-" * 60)
    print("Enter numbers separated by commas (e.g., 1,3,5) or 'all' for all options")

    sorted_keys = sorted(options.keys())
    for i, key in enumerate(sorted_keys, 1):
        extensions = ", ".join(options[key])
        print(f"  {i}. {key}: {extensions}")

    while True:
        choice_input = prompt_input("\nSelect options", "all").strip().lower()

        if choice_input == "all":
            result = []
            for exts in options.values():
                result.extend(exts)
            return result

        try:
            selected_nums = [int(x.strip()) for x in choice_input.split(",")]
            if all(1 <= num <= len(sorted_keys) for num in selected_nums):
                result = []
                for num in selected_nums:
                    result.extend(options[sorted_keys[num - 1]])
                return result
        except ValueError:
            pass

        print(
            f"Invalid input. Enter numbers 1-{len(sorted_keys)} separated by commas, or 'all'."
        )


def generate_copyright_template(
    license_type: str,
    company: str,
    author: Optional[str],
    spdx_license: Optional[str],
    license_notice: Optional[str],
    extensions: List[str],
    include_author: bool,
) -> str:
    """Generate copyright.txt content based on user inputs."""

    # Get template info
    template_info = COPYRIGHT_TEMPLATES.get(license_type, COPYRIGHT_TEMPLATES["custom"])

    # Use custom values if provided, otherwise use template defaults
    if not spdx_license:
        spdx_license = template_info["spdx"]
    if not license_notice:
        license_notice = template_info["license_notice"]

    # Build variables section
    variables = ["[VARIABLES]"]
    if spdx_license:
        variables.append(f"SPDX_LICENSE = {spdx_license}")
    variables.append(f"COMPANY = {company}")
    if include_author and author:
        variables.append(f"AUTHOR = {author}")
    variables.append("YEAR_PATTERN = {regex:\\d{4}(-\\d{4})?}")
    if license_notice:
        variables.append(f"LICENSE_NOTICE = {license_notice}")

    # Start building template
    template_parts = ["\n".join(variables), ""]

    # Helper function to create copyright notice
    def create_notice(comment_prefix: str, comment_suffix: str = "") -> List[str]:
        lines = []
        if spdx_license:
            lines.append(
                f"{comment_prefix}SPDX-License-Identifier: {{SPDX_LICENSE}}{comment_suffix}"
            )
        lines.append(
            f"{comment_prefix}Copyright {{YEAR_PATTERN}} {{COMPANY}}{comment_suffix}"
        )
        if include_author and author:
            lines.append(f"{comment_prefix}Author: {{AUTHOR}}{comment_suffix}")
        if license_notice:
            lines.append(f"{comment_prefix}License: {{LICENSE_NOTICE}}{comment_suffix}")
        return lines

    # Group extensions by comment style
    hash_comment_exts = []
    slash_comment_exts = []
    block_comment_exts = []
    double_dash_exts = []
    xml_comment_exts = []

    for ext in extensions:
        if ext in [".py", ".yaml", ".yml", ".sh", ".bash"]:
            hash_comment_exts.append(ext)
        elif ext in [
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".go",
            ".rs",
            ".css",
            ".scss",
            ".sass",
        ]:
            slash_comment_exts.append(ext)
        elif ext in [".c", ".h", ".cpp", ".hpp", ".cc", ".cxx", ".java"]:
            block_comment_exts.append(ext)
        elif ext in [".sql"]:
            double_dash_exts.append(ext)
        elif ext in [".xml", ".html", ".htm", ".md"]:
            xml_comment_exts.append(ext)

    # Generate sections for each comment style
    if hash_comment_exts:
        ext_list = ", ".join(hash_comment_exts)
        template_parts.append(f"[{ext_list}]")
        if ".sh" in hash_comment_exts or ".bash" in hash_comment_exts:
            template_parts.append("#!/bin/bash")
        template_parts.extend(create_notice("# "))
        template_parts.append("")

    if double_dash_exts:
        ext_list = ", ".join(double_dash_exts)
        template_parts.append(f"[{ext_list}]")
        template_parts.extend(create_notice("-- "))
        template_parts.append("")

    if slash_comment_exts:
        ext_list = ", ".join(slash_comment_exts)
        template_parts.append(f"[{ext_list}]")
        template_parts.extend(create_notice("// "))
        template_parts.append("")

    if block_comment_exts:
        # Separate Java from C/C++
        java_exts = [e for e in block_comment_exts if e == ".java"]
        c_exts = [e for e in block_comment_exts if e != ".java"]

        if c_exts:
            ext_list = ", ".join(c_exts)
            template_parts.append(f"[{ext_list}]")
            template_parts.append(
                "/**************************************************************************"
            )
            template_parts.extend(create_notice("* ", " " * (73 - len("* "))))
            template_parts.append(
                "**************************************************************************/"
            )
            template_parts.append("")

        if java_exts:
            ext_list = ", ".join(java_exts)
            template_parts.append(f"[{ext_list}]")
            template_parts.append("/*")
            template_parts.extend(create_notice(" * "))
            template_parts.append(" */")
            template_parts.append("")

    if xml_comment_exts:
        ext_list = ", ".join(xml_comment_exts)
        template_parts.append(f"[{ext_list}]")
        template_parts.append("<!--")
        template_parts.extend(create_notice(""))
        template_parts.append("-->")
        template_parts.append("")

    return "\n".join(template_parts)


def run_init_wizard(output_path: Optional[str] = None) -> int:
    """
    Run the interactive initialization wizard.

    :param output_path: Optional path for output file (defaults to copyright.txt)
    :return: Exit code (0 for success)
    """
    print("=" * 60)
    print("  SNY Copyright Checker - Initialization Wizard")
    print("=" * 60)
    print("\nThis wizard will help you create a copyright.txt configuration file.")
    print("Press Ctrl+C at any time to cancel.\n")

    # Step 1: Choose license type
    license_choices = {k: v["description"] for k, v in COPYRIGHT_TEMPLATES.items()}
    license_type = prompt_choice(
        "Select a license type", license_choices, default="mit"
    )

    # Step 2: Company/Organization name
    company = prompt_input("\nEnter company/organization name", "My Company Inc.")
    while not company:
        print("Company name is required.")
        company = prompt_input("Enter company/organization name", "My Company Inc.")

    # Step 3: Author (optional)
    include_author = prompt_yes_no(
        "\nInclude author information in copyright?", default=True
    )
    author = None
    if include_author:
        author = prompt_input("Enter author name or team", "Development Team")

    # Step 4: Custom license details (if needed)
    spdx_license = None
    license_notice = None

    if license_type == "custom":
        spdx_license = prompt_input(
            "\nEnter SPDX license identifier (or leave empty)", ""
        )
        license_notice = prompt_input(
            "Enter license notice text", "All rights reserved"
        )
    else:
        # Allow overriding defaults
        if prompt_yes_no("\nCustomize license details?", default=False):
            template_info = COPYRIGHT_TEMPLATES[license_type]
            spdx_license = prompt_input("SPDX identifier", template_info["spdx"])
            license_notice = prompt_input(
                "License notice", template_info["license_notice"]
            )

    # Step 5: Select file extensions
    extensions = prompt_multiselect(
        "\nSelect file extensions to include", EXTENSION_GROUPS
    )

    # Generate the template
    template_content = generate_copyright_template(
        license_type=license_type,
        company=company,
        author=author,
        spdx_license=spdx_license,
        license_notice=license_notice,
        extensions=extensions,
        include_author=include_author,
    )

    # Determine output path
    if not output_path:
        output_path = prompt_input("\nOutput file path", "copyright.txt")

    output_file = Path(output_path)

    # Check if file exists
    if output_file.exists():
        overwrite = prompt_yes_no(
            f"\n'{output_path}' already exists. Overwrite?", default=False
        )
        if not overwrite:
            print("\nOperation cancelled. File was not modified.")
            return 1

    # Preview the template
    print("\n" + "=" * 60)
    print("Preview of generated copyright.txt:")
    print("=" * 60)
    print(template_content)
    print("=" * 60)

    # Confirm and save
    if prompt_yes_no("\nSave this configuration?", default=True):
        try:
            output_file.write_text(template_content, encoding="utf-8")
            print(f"\n✓ Configuration saved to: {output_path}")
            print("\nNext steps:")
            print(f"  1. Review and customize {output_path} if needed")
            print("  2. Run: sny-copyright-checker --fix <files>")
            print("  3. Or add to .pre-commit-config.yaml for automatic checking")
            return 0
        except Exception as e:
            print(f"\n✗ Error saving file: {e}")
            return 1
    else:
        print("\nOperation cancelled.")
        return 1
