# Chaser class to represent the chasing spacecraft. All rendered images
# representative of sensors onboard.

class Chaser:
    def __init__(self):
        self.list_of_sensors = {}
        self.position = []
        self.attitude = []
    
    def update_position(self):
        pass

    def update_attitude(self):
        pass

    def add_sensor(self, sensor_name="sensor", sensor_type="default"):
        self.list_of_sensors.update()
        

    def remove_sensor(self):
        pass