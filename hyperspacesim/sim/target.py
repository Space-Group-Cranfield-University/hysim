''' Classes to build up target object'''

class Target:
    '''Class that holds meshes and coordinates of model to represent target. '''
    def __init__(self) -> None:
        self.target_model=[]
        self.position = []
        self.attitude = []
    
    def set_position(self):
        pass

    def set_attitude(self):
        pass

    def add_part(self):
        pass

    def remove_part(self):
        pass

    def import_model(self):
        pass
