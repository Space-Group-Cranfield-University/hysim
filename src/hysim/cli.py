"""Entry point module

Provides an entry point for package
"""

import argparse
from pathlib import Path
from hysim import sim


def return_unix_path_string(path):
    return str(path).replace("\\", "/")


def run_case(args):
    # TODO: Add support for relative case directory commands

    # if run_directory is None:
    #    run_directory = Path.cwd()
    # else:
    #    run_directory = Path.cwd() / Path(run_directory)

    run_directory = Path.cwd()

    run_directory = return_unix_path_string(run_directory)

    sim.run_sim(run_directory)


# == CLI ARGUMENTS == #
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

run_parser = subparsers.add_parser('run')
# run_parser.add_argument('path', type=str, default=".")
run_parser.set_defaults(func=run_case)


def main():
    """Main function

    Gets working directory and runs simulation
    """
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
