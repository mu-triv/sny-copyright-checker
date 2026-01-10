#!/usr/bin/env python

"""Entry point for the Sony copyright check pre-commit hook"""

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
    Main entry point for sny-copyright-check.

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
        help="Path to copyright template file (default: copyright.txt)",
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

    args = parser.parse_args(argv)
    setup_logging(args.verbose)

    if not args.filenames:
        logging.info("No files to check")
        return 0

    try:
        checker = CopyrightChecker(args.notice)
        
        logging.info(
            f"Checking {len(args.filenames)} file(s) for copyright notices "
            f"(auto-fix: {args.fix})"
        )
        logging.debug(f"Supported extensions: {checker.get_supported_extensions()}")

        passed, failed, modified = checker.check_files(args.filenames, args.fix)

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
