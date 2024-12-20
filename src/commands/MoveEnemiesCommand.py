from .Command import Command
from ..entities.Enemy import Enemy

class MoveEnemiesCommand(Command):
    def __init__(self, game_state):
        self.game_state = game_state
    
    def run(self):
        for unit in self.game_state.units:
            if isinstance(unit, Enemy):
                unit.update_path(self.game_state.player_unit.position)
                unit.move_along_path()