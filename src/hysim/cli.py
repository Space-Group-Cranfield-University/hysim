"""CLI Entry point module

Provides an entry point for package and runs main function
"""

import argparse
import logging
from pathlib import Path

from hysim import simulator
from hysim.util.logging import init_logger, hysim_version

# == CLI ARGUMENTS == #
parser = argparse.ArgumentParser(prog="HySim")
subparsers = parser.add_subparsers(
    prog="command", dest="command", metavar="command"
)

# Version Command
parser.add_argument(
    "-V", "--version", action="version", version=f"%(prog)s {hysim_version()}"
)

# Run Command
run_command = subparsers.add_parser("run", help="Run simulator case")
run_command.set_defaults(func=simulator.run)
run_command.add_argument("--debug", action="store_true")
run_command.add_argument("-C", "--case_directory", default=Path.cwd(), help="Path to case directory")

create_json_command = subparsers.add_parser("create_json")


def main():
    """Main function

    Retrieves cli arguments runs command if one is passed
    and initiates logger
    """
    # Command Line Interface
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        parser.exit(1)

    if args.debug is True:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO

    init_logger(logging_level)

    args.func(args.case_directory)


if __name__ == "__main__":
    main()
