from pathlib import Path
from hyperspacesim import sim


def main():
    """Entry point main function"""
    run_directory = Path.cwd()
    run_directory = str(run_directory).replace("\\", "/")
    sim.run_sim(run_directory)


if __name__ == "__main__":
    main()
