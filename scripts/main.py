#!/usr/bin/env python
# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file



"""Entry point for the sny copyright check pre-commit hook"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from .copyright_checker import CopyrightChecker


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=level
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    """
    Main entry point for sny-copyright-checker.

    :param argv: Command line arguments
    :return: Exit code (0 for success, 1 for failure)
    """
    # Import sys to handle argv properly
    import sys
    import os
    if argv is None:
        argv = sys.argv[1:]

    # Check if first argument is 'init' command (exact match, not a file path)
    # Must be exactly 'init' without any path separators
    if len(argv) > 0 and argv[0] == 'init' and '/' not in argv[0] and '\\' not in argv[0]:
        # Parse init command
        parser = argparse.ArgumentParser(
            prog='sny-copyright-checker init',
            description="Initialize copyright checker configuration"
        )
        parser.add_argument(
            "--output",
            "-o",
            default="copyright.txt",
            help="Output file path (default: copyright.txt)"
        )
        # Remove 'init' from argv before parsing
        args = parser.parse_args(argv[1:])

        # Validate output path
        output_path = Path(args.output)
        if output_path.exists() and output_path.is_dir():
            parser.error(f"Output path is a directory: {args.output}")

        # Check if parent directory is writable
        parent_dir = output_path.parent if output_path.parent.exists() else Path.cwd()
        if not os.access(parent_dir, os.W_OK):
            parser.error(f"Output directory is not writable: {parent_dir}")

        from .init_wizard import run_init_wizard
        return run_init_wizard(args.output)

    # Default: parse as check command
    parser = argparse.ArgumentParser(
        prog='sny-copyright-checker',
        description="Check and add copyright notices to source files"
    )

    # Positional arguments for check behavior
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Files to check for copyright notices",
    )

    # Options for check command (on main parser for backward compatibility)
    parser.add_argument(
        "--notice",
        default="copyright.txt",
        help="Filename of copyright template to search for (default: copyright.txt). In hierarchical mode, this filename is searched in the directory tree.",
    )
    # Fix mode defaults to True, use --no-fix to disable
    parser.add_argument(
        "--no-fix",
        action="store_false",
        dest="fix",
        default=True,
        help="Only check for copyright notices without modifying files (default: auto-fix is enabled)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--changed-only",
        action="store_true",
        help="Only check files that have been changed in git (ignores filenames argument)",
    )
    parser.add_argument(
        "--base-ref",
        default="HEAD",
        help="Git reference to compare against when using --changed-only (default: HEAD)",
    )
    parser.add_argument(
        "--no-git-aware",
        action="store_false",
        dest="git_aware",
        default=True,
        help="Disable Git-aware year management (default: Git-aware is enabled)",
    )
    parser.add_argument(
        "--per-file-years",
        action="store_true",
        help="Use individual file creation years instead of project inception year (default: use project-wide years)",
    )
    parser.add_argument(
        "--ignore-file",
        default=None,
        help="Path to .copyrightignore file (default: auto-detect .copyrightignore)",
    )
    parser.add_argument(
        "--no-gitignore",
        action="store_false",
        dest="use_gitignore",
        default=True,
        help="Don't use .gitignore patterns (default: .gitignore is used)",
    )
    parser.add_argument(
        "--hierarchical",
        action="store_true",
        help="Enable hierarchical copyright templates (looks for --notice file in each directory)",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace existing similar copyright notices with the template notice (requires --fix)",
    )

    args = parser.parse_args(argv)

    # Validate flag combinations
    if args.replace and not args.fix:
        parser.error("--replace requires auto-fix to be enabled. Remove --no-fix or don't use --replace.")

    if args.per_file_years and not args.git_aware:
        parser.error("--per-file-years requires Git to be enabled. Remove --no-git-aware or don't use --per-file-years.")

    # Default behavior: check files
    setup_logging(args.verbose)

    # Warn about ignored flags
    if args.base_ref != "HEAD" and not args.changed_only:
        logging.warning("--base-ref is ignored without --changed-only")

    if args.changed_only and args.filenames:
        logging.warning("--changed-only ignores filename arguments. Only changed files from git will be checked.")

    try:
        checker = CopyrightChecker(
            args.notice,
            git_aware=args.git_aware,
            ignore_file=args.ignore_file,
            use_gitignore=args.use_gitignore,
            hierarchical=args.hierarchical,
            replace_mode=args.replace,
            per_file_years=args.per_file_years
        )

        # Determine which files to check
        if args.changed_only:
            logging.info("Checking only changed files from git")
            try:
                files_to_check = checker.get_changed_files(base_ref=args.base_ref)
                if not files_to_check:
                    logging.info("No changed files with supported extensions found")
                    return 0
            except RuntimeError as e:
                logging.error(str(e))
                return 2
        else:
            files_to_check = args.filenames
            if not files_to_check:
                logging.info("No files to check")
                return 0

        logging.info(
            f"Checking {len(files_to_check)} file(s) for copyright notices "
            f"(auto-fix: {args.fix})"
        )
        logging.debug(f"Supported extensions: {checker.get_supported_extensions()}")

        passed, failed, modified = checker.check_files(files_to_check, args.fix)

        # Print summary
        if modified:
            print(f"\nAdded copyright notice to {len(modified)} file(s):")
            for filepath in modified:
                print(f"  - {filepath}")

        if failed:
            print(f"\nFailed to add copyright notice to {len(failed)} file(s):")
            for filepath in failed:
                print(f"  - {filepath}")
            return 1

        if not modified and not failed:
            logging.info(f"All {len(passed)} file(s) have valid copyright notices")

        return 0

    except FileNotFoundError as e:
        logging.error(str(e))
        return 2
    except ValueError as e:
        logging.error(str(e))
        return 3
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 255


if __name__ == "__main__":
    sys.exit(main())
