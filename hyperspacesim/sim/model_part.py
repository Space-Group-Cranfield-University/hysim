# Class to represent single component of model.
# Each component has a single mesh and material

class ModelPart:
    def __init__(self):
        self.part_name = ""
        self.mesh_file_location = ""
        self.material = {}

    def assign_mat_from_file(self):
        pass

    def assign_mat_from_user(self):
        pass