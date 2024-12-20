import pygame
from pygame import Vector2
from .Layer import Layer
from ..entities.Enemy import Enemy

class UnitsLayer(Layer):
    def __init__(self, user_interface, tileset, game_state, units):
        super().__init__(user_interface, tileset)
        self.game_state = game_state
        self.units = units
        self.frame_switch_threshold = 15
    
    def on_unit_move(self, unit, direction):
        unit.is_moving = True
    
    def on_unit_stop(self, unit):
        unit.is_moving = False
    
    def get_unit_tile(self, unit):
        tile = unit.tile.copy()
        base_row = 2 if isinstance(unit, Enemy) else 0
        
        if unit.is_moving:
            frame = (self.game_state.epoch // self.frame_switch_threshold) % 2
            tile.y = base_row + frame

        if unit.orientation.x > 0: tile.x = 0
        elif unit.orientation.x < 0: tile.x = 1
        elif unit.orientation.y > 0: tile.x = 2
        elif unit.orientation.y < 0: tile.x = 3
        
        return tile
    
    def render(self, surface):
        for unit in self.units:
            current_tile = self.get_unit_tile(unit)
            if self.game_state.epoch - unit.last_hit_epoch < 8:
                # Flash white when hit
                sprite_coords = unit.position.elementwise() * self.user_interface.cell_size
                tile_coords = current_tile.elementwise() * self.user_interface.cell_size
                tile_rect = pygame.Rect(int(tile_coords.x), int(tile_coords.y), 
                                      self.user_interface.cell_size.x, self.user_interface.cell_size.y)
                white_sprite = self.tileset.copy()
                white_sprite.fill((255, 255, 255), special_flags=pygame.BLEND_ADD)
                surface.blit(white_sprite, sprite_coords, tile_rect)
            else:
                self.draw_tile(surface, unit.position, current_tile)