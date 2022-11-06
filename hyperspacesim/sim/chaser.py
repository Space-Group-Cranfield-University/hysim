'''Classes to represent the chasing spacecraft'''
import mitsuba as mi

class IncompatableTransformError(Exception):
    '''Raised when two different transforms are used together'''
    pass


class Chaser:
    '''Chasing spacecraft: sensors and their location'''
    def __init__(self, sensor):
        self.sensor = sensor
        self.position = []
        self.attitude = []
        self.__transform_type = None

    def set_simple_position(self, position_input):
        self.position = position_input
        self.__transform_type = "simple"

    def set_simple_attitude(self, attitude_input):
        try:
            self.__transform_type == "simple"
        except IncompatableTransformError:
            print("Must use simple lookat attitude with simple position")

        self.attitude = attitude_input

    def __return_mitsuba_transform(self):
        return mi.ScalarTransform4f.translate(
                self.position
            ).rotate(
                axis=[1, 0, 0], 
                angle=self.attitude[0]
            ).rotate(
                axis=[0, 1, 0], 
                angle=self.attitude[1]
            ).rotate(
                axis=[0, 0, 1], 
                angle=self.attitude[2]
            )

    def build_dict(self):
        sensor_dict = self.sensor.build_dict()
        sensor_dict.update({
            "to_world": self.__return_mitsuba_transform()
        })
        return sensor_dict  
            


