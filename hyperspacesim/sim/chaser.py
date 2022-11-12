"""Classes to represent the chasing spacecraft"""
import mitsuba as mi


class Chaser:
    """Chasing spacecraft: sensors and their location"""

    def __init__(self, sensor):
        self.sensor = sensor
        self.position = []
        self.attitude = None
        self.__transform_type = None
        self.chaser_dict = {}

    def set_simple_position(self, position_input):
        """Set the position of the chaser in simple cartesian coordinates"""
        self.position = position_input

    def set_simple_attitude(self, attitude_input):
        """Set the attitude of the sensor in degrees around each axis"""
        self.attitude = attitude_input

    def set_lookat_attitude(self):
        self.attitude = "lookat"

    def __return_mitsuba_transform(self):
        return (
            mi.ScalarTransform4f.translate(self.position)
            .rotate(axis=[1, 0, 0], angle=self.attitude[0])
            .rotate(axis=[0, 1, 0], angle=self.attitude[1])
            .rotate(axis=[0, 0, 1], angle=self.attitude[2])
        )

    def build_dict(self):
        """Builds the dictionary describing chaser sensor and
        location/attitude"""
        self.sensor.build_dict()
        self.chaser_dict.update(self.sensor.sensor_dict)

        if self.attitude == "lookat":
            self.chaser_dict["sensor"].update(
                {
                    "to_world": mi.ScalarTransform4f.look_at(
                        origin=self.position,
                        target=[0, 0, 0],
                        up=[0, 0, -1],  # Assumed +z is nadir
                    )
                }
            )

        else:
            self.chaser_dict["sensor"].update(
                {"to_world": self.__return_mitsuba_transform()}
            )
