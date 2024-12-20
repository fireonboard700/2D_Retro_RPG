from pygame import Vector2
import random
from .Layer import Layer

class TileMapLayer(Layer):
    def __init__(self, user_interface, tileset, game_state):
        super().__init__(user_interface, tileset)
        self.game_state = game_state
        self.tile_map = [[Vector2(0, 0) for _ in range(int(game_state.world_size.x))]
                        for _ in range(int(game_state.world_size.y))]
        self.generate_simple_map()
    
    def generate_simple_map(self):
        for y in range(len(self.tile_map)):
            for x in range(len(self.tile_map[0])):
                self.tile_map[y][x] = Vector2(1, 0) if random.random() < 0.1 else Vector2(0, 0)
    
    def render(self, surface):
        for y in range(len(self.tile_map)):
            for x in range(len(self.tile_map[0])):
                self.draw_tile(surface, Vector2(x, y), self.tile_map[y][x])