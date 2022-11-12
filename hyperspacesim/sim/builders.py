"""Classes to construct complex chaser and target instances"""


class Case:
    def __init__(self) -> None:
        self._sensor_config = {}
        self._target_config = {}
        self._render_config = {}


class SceneBuilder:
    """Constructs the overall scene object"""

    def __init__(self):
        self._scene_dict = {"type": "scene"}

    def build_sensor(sensor_config):
        pass

    def set_integrator(self):
        pass

    def choose_sensor(self):
        pass

    def import_model(self):
        pass

    def import_shape(self):
        pass

    def set_chaser_location(self):
        pass

    def set_target_location(self):
        pass
