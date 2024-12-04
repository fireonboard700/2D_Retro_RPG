import pygame
from pygame import Vector2
from pygame import Rect


class Unit:
    def __init__(self, game_state, position, tile, orientation):
        self.game_state = game_state
        self.position = position
        self.tile = tile
        self.orientation = orientation

    def move(self):
        raise NotImplementedError()

class Plane(Unit):
    def __init__(self, game_state, position, tile, orientation):
        super().__init__(game_state, position, tile, orientation)
        self.velocity = Vector2(0.05, 0)

    def move(self, move_vector):
        self.position += move_vector
        self.position += self.velocity
        
        if self.position.x > (self.game_state.world_size.x + 2) or (self.position.x < -2):
            self.velocity.x = -self.velocity.x
            self.orientation = (self.orientation + 180) % 360


class Layer:
    def __init__(self, user_interface, tileset):
        self.user_interface = user_interface
        self.tileset = pygame.image.load(tileset)
    
    def draw_tile(self, surface, position, tile, angle=None):
        sprite_point = position.elementwise() * self.user_interface.cell_size
        texture_point = tile.elementwise() * self.user_interface.cell_size
        texture_rect = Rect(int(texture_point.x), int(texture_point.y), self.user_interface.cell_size.x, self.user_interface.cell_size.y)

        if angle is None:
            surface.blit(self.tileset, sprite_point, texture_rect)
        else:
            texture_tile = pygame.surface.Surface(self.user_interface.cell_size, pygame.SRCALPHA)
            texture_tile.blit(self.tileset, (0, 0), texture_rect)

            rotated_tile = pygame.transform.rotate(texture_tile, angle)

            sprite_point.x -= (rotated_tile.get_width() - texture_tile.get_width()) // 2
            sprite_point.y -= (rotated_tile.get_height() - texture_tile.get_height()) // 2

            surface.blit(rotated_tile, sprite_point)
        
    def render(self, surface):
        raise NotImplementedError()

class UnitsLayer(Layer):
    def __init__(self, user_interface, tileset, game_state, units):
        super().__init__(user_interface, tileset)
        self.game_state = game_state
        self.units = units
    
    def render(self, surface):
        for unit in self.units:
            self.draw_tile(surface, unit.position, unit.tile, unit.orientation)



class GameState:
    def __init__(self):
        self.world_size = Vector2(25, 25)
        self.units = [Plane(self, Vector2(5, 4), Vector2(0, 0), 0)]

    def update(self, move_vector):
        for unit in self.units:
            unit.move(move_vector)


class UserInterface:
    def __init__(self):
        pygame.init()

        self.game_state = GameState()

        self.cell_size = Vector2(35, 15)
        self.move_vector = Vector2(0, 0)

        window_size = self.game_state.world_size.elementwise() *  self.cell_size
        self.window = pygame.display.set_mode((int(window_size.x), int(window_size.y)))

        self.layers = [UnitsLayer(self, "assets/image.png", self.game_state, self.game_state.units)]

        pygame.display.set_caption("Dogfight")
        self.clock = pygame.time.Clock()
        self.running = True
        

    def process_input(self):
        self.move_vector = Vector2(0, 0)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT:
                    self.move_vector = Vector2(0, 1)
                if event.key == pygame.K_UP or event.key == pygame.K_LEFT:
                    self.move_vector = Vector2(0, -1)
                
    def update(self):
        self.game_state.update(self.move_vector)

    def render(self):
        self.window.fill((0, 0, 0))

        for layer in self.layers:
            layer.render(self.window)
            

        pygame.display.update()


    def run(self):
        while self.running:
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(60)

ui = UserInterface()
ui.run()

pygame.quit()
