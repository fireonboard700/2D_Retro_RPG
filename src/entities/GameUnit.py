from pygame import Vector2

class GameUnit:
    def __init__(self, game_state, position, tile):
        self.game_state = game_state
        self.health = 100
        self.position = position
        self.tile = tile
        self.last_hit_epoch = 0