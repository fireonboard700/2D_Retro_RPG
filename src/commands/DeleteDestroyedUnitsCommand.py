from .Command import Command

class DeleteDestroyedUnitsCommand(Command):
    def __init__(self, item_list):
        self.item_list = item_list
    
    def run(self):
        new_list = [item for item in self.item_list if item.health != 0]
        self.item_list[:] = new_list