"""Entry point module

Provides an entry point for package
"""

from pathlib import Path
from hyperspacesim import sim


def main():
    """Main function

    Gets working directory and runs simulation
    """
    run_directory = Path.cwd()
    run_directory = str(run_directory).replace("\\", "/")
    sim.run_sim(run_directory)


if __name__ == "__main__":
    main()
