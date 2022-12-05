from pathlib import Path
from hyperspacesim import sim


def main():
    """Entry point main function"""
    run_directory = Path.cwd()
    sim.run_sim(run_directory)
