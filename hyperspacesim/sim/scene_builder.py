#import sensors as sensors

# Scene builder class file
class SceneBuilder:
    def __init__(self):
        self.dict = ({
            "type": "scene"
        })

    def set_integrator(self, integrator_type="path", max_depth=-1):
        self.dict.update({
            "integrator": {
                "type": integrator_type,
                "max_depth": max_depth
            }
        })

    def choose_sensor(self, sensor_name="sensor"):
        self.dict.update(sensor_name.dict)

    def import_model(self):
        pass

    def import_shape(self):
        pass

    def set_chaser_location(self):
        pass

    def set_target_location(self):
        pass
