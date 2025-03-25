"""CLI Entry point module

Provides an entry point for package and runs main function
"""

import pkg_resources
import logging
import sys
import argparse
from pathlib import Path
from hysim import sim


def get_package_version(package: str) -> str:
    version = pkg_resources.get_distribution(package).version
    return f"{package} {version}"


def return_unix_path_string(path):
    return str(path).replace("\\", "/")


def run_case(run_directory: str):
    case_directory = Path(run_directory)

    if case_directory.is_absolute() is False:
        case_directory = Path.cwd() / case_directory

    if case_directory.exists() is False:
        logging.error("Invalid path to case directory. Terminating Hysim")
        exit()
        
    case_directory = return_unix_path_string(case_directory)
    logging.info(f"Case Directory: {case_directory}") 

    #sim.run_sim(case_directory)
    sim.run_sim2(case_directory)


# == CLI ARGUMENTS == #
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(
    prog="command", dest="command", metavar="command"
)

# Version Command
parser.add_argument(
    "-V", "--version", action="version", version=get_package_version("hysim")
)

# Run Command
run_command = subparsers.add_parser("run", help="Run simulator case")
run_command.set_defaults(func=run_case)
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

    # Logger
    logging.basicConfig(
        format=' %(levelname)-8s %(message)s',
        stream=sys.stdout,
        level=logging_level
    )

    args.func(args.case_directory)


if __name__ == "__main__":
    main()
