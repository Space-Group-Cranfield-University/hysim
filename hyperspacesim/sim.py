"""
Main client script to run code. Called by user.
"""
# Packages
import mitsuba as mi

# I/O
from hyperspacesim import input_data

# Simulator
from hyperspacesim import output_data
from hyperspacesim.scene import simulator_scene as sc
from hyperspacesim.scene import frame_transforms as frames


class RendererControl:
    def __init__(self) -> None:
        self.mitsuba_scene = None
        self.params = None
        self.render = None

    def load_scene(self, scene_dict):
        self.mitsuba_scene = mi.load_dict(scene_dict)
        self.params = mi.traverse(self.mitsuba_scene)

    def run(self):
        self.render = mi.render(self.mitsuba_scene)


if __name__ == "__main__":

    # ------------------------------- #
    # Get user Inputs
    # ------------------------------- #
    case_directory = "example_case/"

    user_inputs = input_data.Configs()
    user_inputs.load_configs(case_directory)

    # Process orbit inputs
    kernel_path = "kernels/meta_kernel.tm" # TODO: Create access to internal kernel data
    orbit_data = frames.MissionInputProcessor(
        user_inputs.mission_config, kernel_path
    )

    # Initialise Mitsuba
    mi.set_variant(user_inputs.case_config["mitsuba_variant"])

    # ------------------------------- #
    # Assemble Scene
    # ------------------------------- #

    # Construct parts of the scene
    scene = sc.SceneBuilder(user_inputs, orbit_data)
    scene.build_integrator()
    scene.build_sampler()
    scene.build_sun()
    scene.build_chaser()
    scene.build_target()

    # Build scene dict
    scene.build_scene_dict()

    #####################################
    # Load to mitsuba and run
    #####################################

    sim = RendererControl()
    sim.load_scene(scene.scene_dict)
    sim.run()

    #####################################
    # Export Outputs
    #####################################
    output = output_data.OutputHandler(
        sim.render, scene.chaser.sensor.film, case_directory
    )
    output.produce_output_data(user_inputs)
