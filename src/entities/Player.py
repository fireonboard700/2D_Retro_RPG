from pygame import Vector2
from .GameUnit import GameUnit

class Player(GameUnit):
    def __init__(self, game_state, position, tile):
        super().__init__(game_state, position, tile)
        self.velocity = 0.1
        self.last_bullet_epoch = 0 
        self.orientation = Vector2(1, 0)
        self.is_moving = False