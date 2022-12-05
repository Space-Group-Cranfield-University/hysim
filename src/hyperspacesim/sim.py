"""
Main client script to run code. Called by user.
"""
# Debugging
import pretty_errors

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


# if __name__ == "__main__":
def run_sim(run_directory):

    # ------------------------------- #
    # Get user Inputs
    # ------------------------------- #
    # run_directory = "example_case/"

    user_inputs = input_data.Configs()
    user_inputs.load_configs(run_directory)

    # kernel_data = dh.Kernels
    # meta_kernel_path = dh.get_data_path(
    #     kernel_data.PATH.value,
    #     kernel_data.META_KERNEL.value,
    # )
    kernel_paths = dh.get_kernel_paths()
    orbit_data = frames.MissionInputProcessor(
        user_inputs.mission_config, kernel_paths
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
    scene.build_earth()

    # Build scene dict
    scene.build_scene_dict()

    #####################################
    # DEBUGGING

    # scene.scene_dict["sun_emitter"] = {
    #     "type": "constant",
    #     "radiance": {
    #         "type": "rgb",
    #         "value": 1.0,
    #     },
    # }

    def calculate_relative_distance(p1, p2):
        return (
            (p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2
        ) ** (0.5)

    # print(orbit_data.chaser_state_vectors)
    # print(orbit_data.target_state_vectors)

    # print(scene.chaser.position)
    # print(scene.target.position)
    relative_distance = calculate_relative_distance(
        scene.chaser.position, scene.target.position
    )
    print(f"Relative Distance: {relative_distance}")

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
        sim.render, scene.chaser.sensor.film, run_directory
    )
    output.produce_output_data(user_inputs)
