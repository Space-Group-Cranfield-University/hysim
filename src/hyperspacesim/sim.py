"""Simulator Module

This module contains the main run function for the simulator and classes to
handle Mitsuba.
"""
# Debugging
# import pretty_errors

# Packages
import mitsuba as mi

# I/O
from hyperspacesim import input_data

# Package data
from hyperspacesim.data import data_handling as dh

# Simulator
from hyperspacesim import output_data
from hyperspacesim.scene import simulator_scene as sc
from hyperspacesim.scene import frame_transforms as frames


class NoSceneLoaded(Exception):
    """Used to handle running a render without required data"""

    pass


class RendererControl:
    """Represents the render module

    Attributes
    ----------
    mitsuba_scene : object
        Mitsuba scene object
    params : SceneParameters
        Parameters in the scene represented by SceneParameters object
    render : TensorXf
        Output data from render represented by floating point tensor

    Methods
    -------
    load_scene(scene_dict)
        Loads scene dict into mitsuba and gets scene parameters
    run()
        Renders the scene using the loaded scene data

    """

    def __init__(self):
        """Initializer"""
        self.mitsuba_scene = None
        self.params = None
        self.render = None

    def load_scene(self, scene_dict: dict):
        """Loads scene dict into mitsuba and gets scene parameters

        Parameters
        ----------
        scene_dict : dict
            Dictionary containing all scene information
        """

        self.mitsuba_scene = mi.load_dict(scene_dict)
        self.params = mi.traverse(self.mitsuba_scene)

    def run(self):
        """Renders the loaded scene with mitsuba

        Raises
        -------
        NoSceneLoaded
            If the mitsuba_scene attribute is None

        """
        if self.mitsuba_scene is None:
            raise NoSceneLoaded("No scene to render")

        self.render = mi.render(self.mitsuba_scene)


def run_sim(run_directory):
    """Runs a single simulator case

    The function is called by the entry script to run a
    case. For a case the user input filed are parsed,
    the orbit data is converted to LVLH, and the scene is
    assembled. The scene is then rendered and the output
    is converted to the format specified in the configs.

    The run directory must be the root of the folders
    containing all configuration files.

    Parameters
    ----------
    run_directory : str
        Path to the case directory containing configuration
        files and user data.

    Returns
    -------
    None
    """

    # ------------------------------- #
    # Get user Inputs
    # ------------------------------- #

    user_inputs = input_data.Configs()
    user_inputs.load_configs(run_directory)
    kernel_paths = dh.get_kernel_paths()
    orbit_data = frames.MissionInputProcessor(
        user_inputs.mission_config, kernel_paths
    )
    mi.set_variant(user_inputs.case_config["mitsuba_variant"])

    # ------------------------------- #
    # Assemble Scene
    # ------------------------------- #
    scene = sc.SceneBuilder(user_inputs, orbit_data)
    scene.build_integrator()
    scene.build_sampler()
    scene.build_sun()
    scene.build_chaser()
    scene.build_target()
    scene.build_earth()

    scene.build_scene_dict()

    def calculate_relative_distance(p1: list, p2: list):
        """Calculates relative distance between two points

        Calculates distance between two points in a 3d
        cartesian coordinate system.

        Parameters
        ----------
        p1 : list
            First set of coordinates in 3 dimensions [x,y,z]
        p2 : list
            Second set of coordinates in 3 dimensions [x,y,z]

        Returns
        -------
        float
            Distance between two points
        """
        return (
            (p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2
        ) ** (0.5)

    relative_distance = calculate_relative_distance(
        scene.chaser.position, scene.target.position
    )
    print(f"Relative Distance: {relative_distance}")

    # ------------------------------- #
    # Load to mitsuba and run
    # ------------------------------- #

    sim = RendererControl()
    sim.load_scene(scene.scene_dict)
    sim.run()

    # ------------------------------- #
    # Export Outputs
    # ------------------------------- #
    output = output_data.OutputHandler(
        sim.render, scene.chaser.sensor.film, run_directory
    )
    output.produce_output_data(user_inputs)
