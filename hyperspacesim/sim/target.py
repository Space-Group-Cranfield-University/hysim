# Target class to represent the chasing spacecraft. All rendered images
# representative of sensors onboard.

class Target:
    def __init__(self) -> None:
        self.model={}
        self.position = []
        self.attitude = []
    
    def update_position(self):
        pass

    def update_attitude(self):
        pass

    def add_part(self):
        pass

    def remove_part(self):
        pass

    def import_model(self):
        pass
