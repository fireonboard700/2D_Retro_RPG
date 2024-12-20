import random
from pygame import Vector2
from .GameUnit import GameUnit

class SimpleParticle(GameUnit):
    def __init__(self, game_state, position, velocity, lifetime):
        super().__init__(game_state, position, Vector2(0, 0))
        self.lifetime = lifetime
        self.tile = Vector2(0, 0)
        self.next_move_time = random.randint(0, 10)
        self.moves = [Vector2(0, -0.1), Vector2(0.1, 0)]
        self.move_interval = 12
        
    def update(self):
        self.lifetime -= 1
        if self.game_state.epoch >= self.next_move_time:
            move = random.choice(self.moves)
            self.position += move
            self.next_move_time = self.game_state.epoch + self.move_interval + random.randint(-2, 2)