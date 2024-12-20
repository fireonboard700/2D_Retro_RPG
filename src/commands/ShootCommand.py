from .Command import Command
from ..entities.Fireball import Fireball

class ShootCommand(Command):
    def __init__(self, game_state, unit, direction):
        self.game_state = game_state    
        self.unit = unit
        self.direction = direction
        self.bullet_delay = 15
    
    def run(self):
        if self.unit.health == 0 or self.game_state.epoch - self.unit.last_bullet_epoch < self.bullet_delay:
            return
        
        self.unit.last_bullet_epoch = self.game_state.epoch
        bullet = Fireball(self.game_state, self.unit, self.unit.orientation)
        self.game_state.bullets.append(bullet)