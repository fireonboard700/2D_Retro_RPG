from pygame import Vector2
from .Command import Command

class MoveUnitCommand(Command):
    def __init__(self, game_state, unit, direction):  
        self.game_state = game_state
        self.unit = unit
        self.direction = direction

    def run(self):
        if self.direction.length() > 0:
            new_position = self.unit.position + self.direction.normalize() * self.unit.velocity
            new_position.x = max(0, min(new_position.x, self.game_state.world_size.x - 1))
            new_position.y = max(0, min(new_position.y, self.game_state.world_size.y - 1))
            self.unit.position = new_position
            self.unit.orientation = self.direction.normalize()
            self.game_state.notify_unit_move(self.unit, self.direction)
        else:
            self.game_state.notify_unit_stop(self.unit)