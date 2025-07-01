import logging
from pathlib import Path

from hysim.configs.config import Config
from hysim.simulator.renderer import RenderController
from hysim.simulator.exporter import export


def run(directory: str):
    """Runs a simulator case.

    The function is called by the entry script to run a
    case. For a case the user input files are parsed,
    the orbit data is converted to LVLH, and the scene is
    assembled. The scene is rendered, and the output
    is converted to the format specified in the configs.

    The run directory must be the root of the folders
    containing all configuration files.

    Parameters
    ----------
    directory : str
        Path to the case directory containing configuration
        files and user data.

    """

    case_directory = Path(directory)

    if case_directory.is_absolute() is False:
        case_directory = Path.cwd() / case_directory

    if case_directory.exists() is False:
        logging.error('Case directory "%s" does not exist. Terminating HySim', case_directory)
        import sys
        sys.exit()

    # ------------------------------- #
    # Get user Inputs
    # ------------------------------- #
    logging.info('Running Simulation Case "%s"', case_directory)
    config = Config(case_directory)
    # ------------------------------- #
    # Rendering
    # ------------------------------- #
    render_control = RenderController(config)
    render_control.render()
    # ------------------------------- #
    # Export Outputs
    # ------------------------------- #
    export(config, render_control)
    logging.info("Done")
