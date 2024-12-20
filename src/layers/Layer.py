import pygame
from pygame import Rect
from .GameStateObserver import GameStateObserver

class Layer(GameStateObserver):
    def __init__(self, user_interface, tileset):
        self.user_interface = user_interface
        self.tileset = pygame.image.load(tileset)
    
    def draw_tile(self, surface, position, tile):
        sprite_coords = position.elementwise() * self.user_interface.cell_size
        tile_coords = tile.elementwise() * self.user_interface.cell_size
        tile_rect = Rect(int(tile_coords.x), int(tile_coords.y), 
                        self.user_interface.cell_size.x, self.user_interface.cell_size.y)
        surface.blit(self.tileset, sprite_coords, tile_rect)
    
    def render(self, surface):
        raise NotImplementedError()