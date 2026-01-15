#!/usr/bin/env python
# SPDX-License-Identifier: MIT
# Copyright 2026 Sony Group Corporation
# Author: R&D Center Europe Brussels Laboratory, Sony Group Corporation
# License: For licensing see the License.txt file



"""Entry point for the sny copyright check pre-commit hook"""

import argparse
import logging
import sys
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
    parser = argparse.ArgumentParser(
        description="Check and add copyright notices to source files"
    )
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Files to check for copyright notices",
    )
    parser.add_argument(
        "--notice",
        default="copyright.txt",
        help="Filename of copyright template to search for (default: copyright.txt). In hierarchical mode, this filename is searched in the directory tree.",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        default=True,
        help="Automatically add missing copyright notices (default: True)",
    )
    parser.add_argument(
        "--no-fix",
        action="store_false",
        dest="fix",
        help="Only check for copyright notices without modifying files",
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
    setup_logging(args.verbose)

    try:
        checker = CopyrightChecker(
            args.notice,
            git_aware=args.git_aware,
            ignore_file=args.ignore_file,
            use_gitignore=args.use_gitignore,
            hierarchical=args.hierarchical,
            replace_mode=args.replace
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
